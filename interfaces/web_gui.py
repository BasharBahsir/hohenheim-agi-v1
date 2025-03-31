"""
Web GUI - Professional interface for Hohenheim AGI
Provides a sleek, modern interface with advanced functionality
"""

import os
import time
import logging
import gradio as gr
from typing import Dict, List, Any, Optional, Tuple
import json
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import queue
import sounddevice as sd
import soundfile as sf
from elevenlabs import generate, play, set_api_key
import whisper

class WebGUI:
    """Professional web-based GUI for the Hohenheim AGI system"""
    
    def __init__(self, agi_core: Any):
        self.agi_core = agi_core
        self.logger = logging.getLogger("Hohenheim.WebGUI")
        self.chat_history = []
        
        # Voice settings
        self.voice_enabled = False
        self.recording = False
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.stream = None
        
        # Initialize Whisper model
        try:
            self.whisper_model = whisper.load_model("base")
            self.logger.info("Whisper model loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load Whisper model: {str(e)}")
            self.whisper_model = None
            
        # Initialize ElevenLabs API if key is available
        elevenlabs_key = self.agi_core.config.get("ELEVENLABS_API_KEY", "")
        if elevenlabs_key:
            set_api_key(elevenlabs_key)
            self.logger.info("ElevenLabs API initialized")
        else:
            self.logger.warning("ElevenLabs API key not found")
        
        self.voice_settings = {
            "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Default voice ID (Adam)
            "model": "eleven_monolingual_v1"
        }
        
        # Professional dark theme colors
        self.colors = {
            "background": "#0F1117",    # Dark background
            "surface": "#1F2128",       # Card background
            "surface_2": "#2F313A",     # Secondary surface
            "primary": "#2D7FF9",       # Primary blue
            "secondary": "#6366F1",     # Secondary color
            "accent": "#22D3EE",        # Accent color
            "success": "#22C55E",       # Success green
            "warning": "#F59E0B",       # Warning yellow
            "error": "#EF4444",         # Error red
            "text": "#F8FAFC",          # Primary text
            "text_secondary": "#94A3B8", # Secondary text
            "border": "#2E3440",        # Border color
            "hover": "#323644"          # Hover state
        }
        
        self.custom_css = self._load_custom_css()

    def _load_custom_css(self) -> str:
        return """
        .gradio-container {
            background-color: var(--background-color);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
            max-width: 1400px !important;
            margin: 0 auto;
        }

        :root {
            --background-color: #0F1117;
            --surface-color: #1F2128;
            --surface-2-color: #2F313A;
            --primary-color: #2D7FF9;
            --text-color: #F8FAFC;
            --text-secondary: #94A3B8;
            --border-color: #2E3440;
        }

        .container {
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .header {
            padding: 24px;
            border-bottom: 1px solid var(--border-color);
            background: var(--surface-color);
            margin-bottom: 32px;
        }

        .header h1 {
            color: var(--text-color);
            font-size: 28px;
            font-weight: 600;
            margin: 0;
            letter-spacing: -0.02em;
        }

        .header h3 {
            color: var(--text-secondary);
            font-size: 16px;
            font-weight: 400;
            margin: 8px 0 0 0;
        }

        .chat-container {
            display: flex;
            flex-direction: column;
            height: calc(100vh - 240px);
            background: var(--surface-color);
            border-radius: 12px;
            overflow: hidden;
        }

        .chat-messages {
            flex-grow: 1;
            overflow-y: auto;
            padding: 24px;
        }

        .message {
            display: flex;
            margin-bottom: 24px;
            opacity: 0;
            animation: fadeIn 0.3s ease forwards;
        }

        .message-content {
            max-width: 80%;
            padding: 16px 20px;
            border-radius: 12px;
            font-size: 15px;
            line-height: 1.5;
        }

        .user-message {
            justify-content: flex-end;
        }

        .user-message .message-content {
            background: var(--primary-color);
            color: white;
            border-radius: 12px 12px 0 12px;
        }

        .assistant-message {
            justify-content: flex-start;
        }

        .assistant-message .message-content {
            background: var(--surface-2-color);
            color: var(--text-color);
            border-radius: 12px 12px 12px 0;
        }

        .message-metadata {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 4px;
        }

        .input-container {
            padding: 24px;
            background: var(--surface-color);
            border-top: 1px solid var(--border-color);
        }

        .input-box {
            background: var(--surface-2-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px 16px;
            color: var(--text-color);
            font-size: 15px;
            resize: none;
            width: 100%;
            transition: border-color 0.2s;
        }

        .input-box:focus {
            border-color: var(--primary-color);
            outline: none;
        }

        .button-container {
            display: flex;
            gap: 12px;
            margin-top: 12px;
        }

        .button {
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
        }

        .button-primary {
            background: var(--primary-color);
            color: white;
        }

        .button-primary:hover {
            background: #2468CC;
            transform: translateY(-1px);
        }

        .button-secondary {
            background: var(--surface-2-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }

        .button-secondary:hover {
            background: var(--hover);
            transform: translateY(-1px);
        }

        .tab-nav {
            background: var(--surface-color);
            padding: 0;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 32px;
        }

        .tab-nav button {
            padding: 16px 24px;
            color: var(--text-secondary);
            font-size: 15px;
            font-weight: 500;
            background: none;
            border: none;
            border-bottom: 2px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
        }

        .tab-nav button:hover {
            color: var(--text-color);
        }

        .tab-nav button.selected {
            color: var(--text-color);
            border-bottom-color: var(--primary-color);
        }

        .status-card {
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 24px;
        }

        .status-row {
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 12px;
        }

        .status-active {
            background: var(--success);
            box-shadow: 0 0 8px rgba(34, 197, 94, 0.4);
        }

        .status-inactive {
            background: var(--error);
            box-shadow: 0 0 8px rgba(239, 68, 68, 0.4);
        }

        .memory-list {
            background: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            height: 400px;
            overflow-y: auto;
        }

        .memory-item {
            padding: 16px;
            border-bottom: 1px solid var(--border-color);
            transition: background 0.2s;
        }

        .memory-item:hover {
            background: var(--surface-2-color);
        }

        .memory-type {
            color: var(--text-secondary);
            font-size: 13px;
            margin-bottom: 4px;
        }

        .memory-content {
            color: var(--text-color);
            font-size: 14px;
            line-height: 1.5;
        }

        .search-box {
            background: var(--surface-2-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px 16px;
            color: var(--text-color);
            font-size: 14px;
            width: 100%;
            margin-bottom: 16px;
            transition: border-color 0.2s;
        }

        .search-box:focus {
            border-color: var(--primary-color);
            outline: none;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }

        ::-webkit-scrollbar-track {
            background: var(--surface-color);
        }

        ::-webkit-scrollbar-thumb {
            background: var(--surface-2-color);
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: var(--hover);
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .fade-in {
            animation: fadeIn 0.3s ease forwards;
        }
        """

    def process_command(self, command: str, history: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Process a command and update chat history"""
        if not command.strip():
            return history
        
        # Add user message
        history.append(("user", command))
        
        try:
            # Process command
            response = self.agi_core.process_command(command)
            
            # Format response
            output = response.get('message', 'No response generated.')
            if 'error' in response:
                output = f"Error: {response['error']}"
            
            # Add metadata if available
            if 'reasoning' in response:
                output += f"\n\nReasoning:\n{response['reasoning']}"
            if 'memories' in response and response['memories']:
                output += "\n\nRelevant Memories:\n"
                for i, memory in enumerate(response['memories'], 1):
                    if isinstance(memory, dict):
                        output += f"{i}. {memory.get('content', str(memory))}\n"
                    else:
                        output += f"{i}. {str(memory)}\n"
            
            # Add system response
            history.append(("assistant", output))
            
            # Convert response to speech if enabled
            if self.voice_enabled:
                # Extract just the main response without metadata for speech
                main_response = response.get('message', 'No response generated.')
                self.text_to_speech(main_response)
            
        except Exception as e:
            self.logger.error(f"Error processing command: {str(e)}")
            history.append(("assistant", f"Error: {str(e)}"))
        
        return history

    def start_recording(self):
        """Start recording audio from microphone"""
        if self.recording:
            return
        
        self.recording = True
        self.audio_data = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                self.logger.warning(f"Audio recording status: {status}")
            self.audio_queue.put(indata.copy())
        
        try:
            self.stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=16000)
            self.stream.start()
            self.logger.info("Started audio recording")
        except Exception as e:
            self.logger.error(f"Failed to start recording: {str(e)}")
            self.recording = False

    def stop_recording(self) -> str:
        """Stop recording and transcribe audio"""
        if not self.recording:
            return ""
        
        self.recording = False
        
        try:
            self.stream.stop()
            self.stream.close()
            
            # Get all audio data from queue
            audio_data = []
            while not self.audio_queue.empty():
                audio_data.append(self.audio_queue.get())
            
            if not audio_data:
                self.logger.warning("No audio data captured")
                return ""
            
            # Convert to numpy array and save as WAV
            audio_array = np.concatenate(audio_data, axis=0)
            temp_wav = "temp_recording.wav"
            sf.write(temp_wav, audio_array, 16000)
            
            # Transcribe with Whisper
            if self.whisper_model:
                result = self.whisper_model.transcribe(temp_wav)
                os.remove(temp_wav)
                transcribed_text = result["text"].strip()
                self.logger.info(f"Transcribed: {transcribed_text}")
                return transcribed_text
            else:
                self.logger.error("Whisper model not available")
                return ""
                
        except Exception as e:
            self.logger.error(f"Transcription error: {str(e)}")
            return ""
            
    def text_to_speech(self, text: str) -> None:
        """Convert text to speech using ElevenLabs"""
        if not text.strip():
            return
            
        try:
            # Check if API key is available
            api_key = self.agi_core.config.get("ELEVENLABS_API_KEY", "")
            if not api_key:
                self.logger.warning("ElevenLabs API key not found")
                return
            
            # Limit text length if needed
            if len(text) > 1000:
                self.logger.info("Text too long, truncating for TTS")
                text = text[:1000] + "..."
                
            # Generate audio using ElevenLabs
            audio = generate(
                text=text,
                voice=self.voice_settings["voice_id"],
                model=self.voice_settings["model"]
            )
            
            # Play audio directly
            play(audio)
            
        except Exception as e:
            self.logger.error(f"Text-to-speech error: {str(e)}")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get current memory statistics"""
        st_stats = self.agi_core.short_term_memory.get_stats()
        lt_stats = self.agi_core.long_term_memory.get_stats()
        
        return {
            "short_term": {
                "total": st_stats["total_items"],
                "by_type": st_stats["items_by_type"]
            },
            "long_term": {
                "total": lt_stats["total_items"],
                "embeddings": lt_stats.get("total_embeddings", 0)
            }
        }

    def get_command_suggestions(self, text: str) -> List[str]:
        """Get command suggestions based on user input"""
        # Basic command suggestions
        basic_commands = [
            "help",
            "status",
            "memory",
            "search",
            "learn",
            "analyze",
            "summarize",
            "create",
            "explain",
            "remember"
        ]
        
        # Filter suggestions based on input
        if not text:
            return basic_commands[:5]  # Return top 5 if no input
        
        # Filter commands that start with the input text
        filtered = [cmd for cmd in basic_commands if cmd.startswith(text.lower())]
        
        # If no direct matches, find commands that contain the input
        if not filtered:
            filtered = [cmd for cmd in basic_commands if text.lower() in cmd]
        
        return filtered[:5]  # Return top 5 matches

    def create_memory_visualization(self) -> go.Figure:
        """Create memory visualization using Plotly"""
        stats = self.get_memory_stats()
        memory_types = stats["short_term"]["by_type"]
        
        fig = go.Figure()
        
        # Add bar chart for memory types
        fig.add_trace(go.Bar(
            x=list(memory_types.keys()),
            y=list(memory_types.values()),
            name="Memory Types",
            marker_color=self.colors["primary"]
        ))
        
        # Update layout
        fig.update_layout(
            plot_bgcolor=self.colors["surface"],
            paper_bgcolor=self.colors["surface"],
            font_color=self.colors["text"],
            title={
                'text': 'Memory Distribution',
                'font': {'color': self.colors["text"]}
            },
            xaxis={
                'title': 'Memory Type',
                'color': self.colors["text"],
                'gridcolor': self.colors["border"]
            },
            yaxis={
                'title': 'Count',
                'color': self.colors["text"],
                'gridcolor': self.colors["border"]
            }
        )
        
        return fig

    def start(self, server_port: int = 50920) -> None:
        """Start the web GUI interface"""
        if not self.agi_core.is_running:
            self.agi_core.start()
        
        # Create custom theme
        theme = gr.themes.Base().set(
            body_background_fill=self.colors["background"],
            body_text_color=self.colors["text"],
            button_primary_background_fill=self.colors["primary"],
            button_primary_text_color="white",
            border_color_primary=self.colors["border"]
        )
        
        with gr.Blocks(theme=theme, css=self.custom_css) as interface:
            # Header
            with gr.Row(elem_classes="header"):
                with gr.Column():
                    gr.Markdown(f"# {self.agi_core.name}")
                    gr.Markdown(f"### {self.agi_core.codename} v{self.agi_core.version}")
            
            # Main content
            with gr.Tabs(elem_classes="tab-nav"):
                # Chat Interface
                with gr.Tab("Chat", elem_classes="main-panel"):
                    with gr.Column(elem_classes="chat-container"):
                        # Control buttons
                        with gr.Row(elem_classes="controls-container"):
                            voice_btn = gr.Button("Voice", elem_classes="control-button")
                            record_btn = gr.Button("Record", elem_classes="control-button")
                            clear_btn = gr.Button("Clear", elem_classes="control-button")
                        
                        chatbot = gr.Chatbot(
                            value=self.chat_history,
                            height=500,
                            show_label=False,
                            elem_classes="chat-messages",
                            render_markdown=True
                        )
                        
                        # Status indicator
                        status_text = gr.Markdown(visible=False)
                        
                        with gr.Row(elem_classes="input-container"):
                            with gr.Column(scale=4):
                                msg = gr.Textbox(
                                    placeholder="Enter a command or message... (Ctrl+Enter to send)",
                                    show_label=False,
                                    lines=2,
                                    elem_classes="input-box"
                                )
                            with gr.Column(scale=1):
                                with gr.Row():
                                    submit = gr.Button("Send", elem_classes="button button-primary")
                                    clear = gr.Button("Clear", elem_classes="button button-secondary")
                
                # Memory Hub
                with gr.Tab("Memory", elem_classes="main-panel"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            gr.Markdown("### Memory Overview")
                            memory_plot = gr.Plot(
                                self.create_memory_visualization(),
                                elem_classes="memory-viz"
                            )
                            refresh_memory = gr.Button(
                                "Refresh",
                                elem_classes="button button-secondary"
                            )
                        
                        with gr.Column(scale=1):
                            gr.Markdown("### Recent Memories")
                            memory_list = gr.HTML(
                                elem_classes="memory-list"
                            )
                            memory_search = gr.Textbox(
                                placeholder="Search memories...",
                                elem_classes="search-box"
                            )
                
                # System Dashboard
                with gr.Tab("System", elem_classes="main-panel"):
                    with gr.Row():
                        with gr.Column():
                            status_md = gr.Markdown(elem_classes="status-card")
                            refresh = gr.Button(
                                "Refresh Status",
                                elem_classes="button button-secondary"
                            )
                            
                            def get_status():
                                stats = self.get_memory_stats()
                                return f"""
                                ### System Status
                                <div class="status-card">
                                    <div class="status-row">
                                        <span class="status-indicator status-{'active' if self.agi_core.is_running else 'inactive'}"></span>
                                        System Status: {'Running' if self.agi_core.is_running else 'Stopped'}
                                    </div>
                                    <div class="status-row">
                                        <span class="status-indicator status-{'active' if self.agi_core.uncensored_mode else 'inactive'}"></span>
                                        Uncensored Mode: {'Enabled' if self.agi_core.uncensored_mode else 'Disabled'}
                                    </div>
                                </div>
                                
                                ### Memory Stats
                                <div class="status-card">
                                    <div>Short-term Memory: {stats['short_term']['total']} items</div>
                                    <div>Long-term Memory: {stats['long_term']['total']} items</div>
                                </div>
                                """
                            
                            refresh.click(get_status, None, status_md)
                            status_md.value = get_status()  # Initial status
                        
                        with gr.Column():
                            with gr.Row():
                                uncensored = gr.Checkbox(
                                    label="Uncensored Mode",
                                    value=self.agi_core.uncensored_mode
                                )
                                apply = gr.Button(
                                    "Apply",
                                    elem_classes="button button-primary"
                                )
                            
                            status_text = gr.Markdown()
                
                # Settings
                with gr.Tab("Settings", elem_classes="main-panel"):
                    with gr.Column():
                        with gr.Group(elem_classes="settings-group"):
                            gr.Markdown("### API Configuration")
                            with gr.Row():
                                deepseek_key = gr.Textbox(
                                    label="DeepSeek API Key",
                                    type="password",
                                    value=self.agi_core.config.get("DEEPSEEK_API_KEY", "")
                                )
                                claude_key = gr.Textbox(
                                    label="Claude API Key",
                                    type="password",
                                    value=self.agi_core.config.get("CLAUDE_API_KEY", "")
                                )
                        
                        with gr.Group(elem_classes="settings-group"):
                            gr.Markdown("### Memory Settings")
                            with gr.Row():
                                st_limit = gr.Slider(
                                    minimum=100,
                                    maximum=10000,
                                    value=1000,
                                    step=100,
                                    label="Short-term Memory Limit"
                                )
                                lt_backend = gr.Dropdown(
                                    choices=["Chroma", "FAISS"],
                                    value="Chroma",
                                    label="Long-term Memory Backend"
                                )
            
            # Event handlers
            def process_message(message: str, history: List) -> Tuple[List, str]:
                """Process message and update UI"""
                status_text.visible = True
                status_text.value = "Processing..."
                new_history = self.process_command(message, history)
                status_text.visible = False
                return new_history, ""

            # Chat interactions
            submit.click(
                fn=process_message,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )
            
            msg.submit(
                fn=process_message,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )
            
            clear.click(
                fn=lambda: ([], ""),
                outputs=[chatbot, msg]
            )
            
            clear_btn.click(
                fn=lambda: ([], ""),
                outputs=[chatbot, msg]
            )

            # Voice control
            def toggle_voice():
                self.voice_enabled = not self.voice_enabled
                status_text.visible = True
                return f"Voice {'enabled' if self.voice_enabled else 'disabled'}"

            voice_btn.click(
                fn=toggle_voice,
                outputs=[status_text]
            )

            # Recording control
            def toggle_recording():
                if self.recording:
                    text = self.stop_recording()
                    status_text.visible = True
                    status_text.value = "Transcription complete"
                    if text:
                        return text, "Record"
                    return "", "Record"
                else:
                    self.start_recording()
                    status_text.visible = True
                    status_text.value = "Recording... (click again to stop)"
                    return "", "Stop Recording"

            record_btn.click(
                fn=toggle_recording,
                outputs=[msg, record_btn]
            )
            
            refresh_memory.click(
                fn=self.create_memory_visualization,
                outputs=[memory_plot]
            )
            
            apply.click(
                fn=lambda x: f"Uncensored mode {'enabled' if x else 'disabled'}",
                inputs=[uncensored],
                outputs=[status_text]
            )
        
        # Launch the interface
        interface.launch(
            server_name="0.0.0.0",
            server_port=server_port,
            share=False,
            debug=True
        )
