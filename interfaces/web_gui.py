"""
Web GUI - Modern web interface for Hohenheim AGI
Provides an aesthetic, multi-functional interface using Gradio
"""

import os
import time
import logging
import gradio as gr
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import json
import base64
from PIL import Image
from io import BytesIO

class WebGUI:
    """
    Web-based GUI for the Hohenheim AGI system.
    Provides a modern, aesthetic interface with multiple tabs and visualizations.
    """
    
    def __init__(self, agi_core):
        """
        Initialize the web GUI
        
        Args:
            agi_core: Reference to the main AGI core instance
        """
        self.agi_core = agi_core
        self.logger = logging.getLogger("Hohenheim.WebGUI")
        
        # Chat history
        self.chat_history = []
        
        # Theme configuration
        self.primary_color = "#3a86ff"
        self.secondary_color = "#8338ec"
        self.background_color = "#1e1e2e"
        self.text_color = "#ffffff"
        self.accent_color = "#ff006e"
        
        # Load custom CSS
        self.custom_css = self._load_custom_css()
        
        # Load logo
        self.logo_path = self._create_logo()
    
    def _load_custom_css(self) -> str:
        """Load custom CSS for styling the interface"""
        return """
        .gradio-container {
            background-color: #1e1e2e;
            color: #ffffff;
        }
        
        .main-header {
            background: linear-gradient(90deg, #3a86ff, #8338ec);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .chat-message {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        
        .user-message {
            background-color: #3a86ff;
            margin-left: 20%;
            margin-right: 5%;
        }
        
        .bot-message {
            background-color: #2d2d3a;
            margin-right: 20%;
            margin-left: 5%;
        }
        
        .command-box {
            border: 2px solid #8338ec;
            border-radius: 10px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-active {
            background-color: #4cc9f0;
            box-shadow: 0 0 8px #4cc9f0;
        }
        
        .status-inactive {
            background-color: #f72585;
            box-shadow: 0 0 8px #f72585;
        }
        
        .memory-card {
            background-color: #2d2d3a;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #8338ec;
        }
        
        .tab-nav {
            background-color: #2d2d3a;
            border-radius: 10px;
            padding: 5px;
        }
        
        .tab-selected {
            background-color: #3a86ff;
            color: white;
        }
        """
    
    def _create_logo(self) -> str:
        """Create and save the Hohenheim logo"""
        # Create a directory for assets if it doesn't exist
        os.makedirs("interfaces/assets", exist_ok=True)
        
        # Path to save the logo
        logo_path = "interfaces/assets/hohenheim_logo.png"
        
        # If logo already exists, return the path
        if os.path.exists(logo_path):
            return logo_path
        
        try:
            # Create a simple logo using PIL
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a new image with a transparent background
            img = Image.new('RGBA', (400, 400), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a gradient background
            for y in range(400):
                r = int(58 + (134 - 58) * y / 400)
                g = int(134 + (56 - 134) * y / 400)
                b = int(255 + (236 - 255) * y / 400)
                for x in range(400):
                    draw.point((x, y), fill=(r, g, b, 255))
            
            # Draw a circle
            draw.ellipse((50, 50, 350, 350), outline=(255, 255, 255, 200), width=10)
            
            # Draw an "H" in the center
            try:
                font = ImageFont.truetype("arial.ttf", 200)
            except IOError:
                font = ImageFont.load_default()
            
            draw.text((140, 70), "H", fill=(255, 255, 255, 230), font=font)
            
            # Save the image
            img.save(logo_path)
            self.logger.info(f"Created logo at {logo_path}")
            
            return logo_path
            
        except Exception as e:
            self.logger.error(f"Error creating logo: {str(e)}")
            return ""
    
    def process_command(self, command: str, history: List) -> List:
        """
        Process a command and update the chat history
        
        Args:
            command: The command to process
            history: Current chat history
            
        Returns:
            Updated chat history
        """
        if not command.strip():
            return history
        
        # Add user message to history
        history.append((command, ""))
        
        try:
            # Process the command
            response = self.agi_core.process_command(command)
            
            # Format the response
            output = ""
            if "error" in response:
                output += f"Error: {response['error']}"
            elif "message" in response:
                output += f"{response['message']}\n\n"
                
                # Add reasoning if available
                if "reasoning" in response:
                    output += f"{response['reasoning']}"
                
                # Add memories if available
                if "memories" in response and response["memories"]:
                    output += "\n\nMemories:\n"
                    for i, memory in enumerate(response["memories"], 1):
                        if isinstance(memory, dict):
                            if "content" in memory:
                                output += f"{i}. {memory['content']}\n"
                            elif "data" in memory:
                                output += f"{i}. {json.dumps(memory['data'], indent=2)}\n"
                        else:
                            output += f"{i}. {memory}\n"
            else:
                output = "No response generated."
            
            # Update the last message with the response
            history[-1] = (command, output)
            
        except Exception as e:
            self.logger.error(f"Error processing command: {str(e)}")
            history[-1] = (command, f"Error: {str(e)}")
        
        return history
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the current system status
        
        Returns:
            Dictionary with system status information
        """
        # Get memory stats
        short_term_stats = self.agi_core.short_term_memory.get_stats()
        long_term_stats = self.agi_core.long_term_memory.get_stats()
        
        # Format the stats
        status = {
            "system_name": self.agi_core.name,
            "version": self.agi_core.version,
            "codename": self.agi_core.codename,
            "running": self.agi_core.is_running,
            "uncensored_mode": self.agi_core.uncensored_mode,
            "short_term_memory_items": short_term_stats["total_items"],
            "long_term_memory_items": long_term_stats["total_items"],
            "memory_types": dict(short_term_stats["items_by_type"])
        }
        
        return status
    
    def create_memory_visualization(self) -> Any:
        """
        Create a visualization of the memory system
        
        Returns:
            Plotly figure
        """
        # Get memory stats
        short_term_stats = self.agi_core.short_term_memory.get_stats()
        
        # Create a DataFrame for the memory types
        memory_types = short_term_stats["items_by_type"]
        if not memory_types:
            # Create a placeholder if no memory items
            df = pd.DataFrame({
                "Memory Type": ["No memories yet"],
                "Count": [0]
            })
        else:
            df = pd.DataFrame({
                "Memory Type": list(memory_types.keys()),
                "Count": list(memory_types.values())
            })
        
        # Create a bar chart
        fig = px.bar(
            df, 
            x="Memory Type", 
            y="Count", 
            title="Memory Distribution by Type",
            color="Count",
            color_continuous_scale=["#3a86ff", "#8338ec", "#ff006e"]
        )
        
        # Update layout
        fig.update_layout(
            plot_bgcolor="#2d2d3a",
            paper_bgcolor="#1e1e2e",
            font_color="#ffffff",
            title_font_color="#ffffff",
            margin=dict(l=40, r=40, t=50, b=40)
        )
        
        return fig
    
    def get_recent_memories(self, limit: int = 10) -> str:
        """
        Get recent memories from the system
        
        Args:
            limit: Maximum number of memories to retrieve
            
        Returns:
            Formatted string with recent memories
        """
        memories = self.agi_core.short_term_memory.get_recent(limit=limit)
        
        if not memories:
            return "No memories found."
        
        output = ""
        for i, memory in enumerate(memories, 1):
            memory_type = memory.get("type", "unknown")
            created_at = memory.get("created_at", "unknown time")
            
            output += f"<div class='memory-card'>"
            output += f"<strong>Memory {i} ({memory_type})</strong> - {created_at}<br>"
            
            data = memory.get("data", {})
            if isinstance(data, dict):
                for key, value in data.items():
                    if key != "timestamp" and key != "context":
                        if isinstance(value, dict) and "reasoning" in value:
                            output += f"<strong>{key}:</strong> {value['reasoning'][:200]}...<br>"
                        else:
                            output += f"<strong>{key}:</strong> {str(value)[:200]}...<br>"
            else:
                output += f"{str(data)[:200]}...<br>"
            
            output += "</div>"
        
        return output
    
    def toggle_uncensored_mode(self, enable: bool) -> str:
        """
        Toggle uncensored mode
        
        Args:
            enable: Whether to enable or disable uncensored mode
            
        Returns:
            Status message
        """
        if enable:
            # Check if local server is available
            from agents.uncensored_agent import check_local_server_status
            server_available = check_local_server_status()
            
            if not server_available:
                return "Cannot enable uncensored mode. Local LM Studio server is not available."
        
        # Toggle the mode
        current_state = self.agi_core.toggle_uncensored_mode(enable)
        
        if current_state:
            return "Uncensored mode is now enabled. Using local LM Studio server for unrestricted reasoning."
        else:
            return "Uncensored mode is now disabled. Using standard reasoning APIs."
    
    def search_memories(self, query: str) -> str:
        """
        Search for memories
        
        Args:
            query: Search query
            
        Returns:
            Formatted string with search results
        """
        if not query.strip():
            return "Please enter a search query."
        
        # Search in long-term memory
        long_term_results = self.agi_core.long_term_memory.search(query, limit=5)
        
        # Search in short-term memory
        short_term_results = self.agi_core.short_term_memory.search(query, limit=5)
        
        output = "<h3>Search Results</h3>"
        
        if not long_term_results and not short_term_results:
            return output + "No memories found matching your query."
        
        if long_term_results:
            output += "<h4>Long-term Memory Results</h4>"
            output += "<div class='memory-results'>"
            
            for i, memory in enumerate(long_term_results, 1):
                output += f"<div class='memory-card'>"
                if isinstance(memory, dict):
                    if "title" in memory:
                        output += f"<strong>{i}. {memory['title']}</strong><br>"
                    if "content" in memory:
                        output += f"{memory['content']}<br>"
                    if "metadata" in memory:
                        output += f"<small>Type: {memory['metadata'].get('type', 'unknown')}</small>"
                else:
                    output += f"{i}. {str(memory)}"
                output += "</div>"
            
            output += "</div>"
        
        if short_term_results:
            output += "<h4>Short-term Memory Results</h4>"
            output += "<div class='memory-results'>"
            
            for i, memory in enumerate(short_term_results, 1):
                output += f"<div class='memory-card'>"
                memory_type = memory.get("type", "unknown")
                output += f"<strong>{i}. {memory_type} Memory</strong><br>"
                
                data = memory.get("data", {})
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key != "timestamp" and key != "context":
                            if isinstance(value, dict) and "reasoning" in value:
                                output += f"<strong>{key}:</strong> {value['reasoning'][:200]}...<br>"
                            else:
                                output += f"<strong>{key}:</strong> {str(value)[:200]}...<br>"
                else:
                    output += f"{str(data)[:200]}...<br>"
                
                output += "</div>"
            
            output += "</div>"
        
        return output
    
    def start(self, server_port: int = 57264) -> None:
        """
        Start the web GUI
        
        Args:
            server_port: Port to run the server on
        """
        self.logger.info(f"Starting web GUI on port {server_port}")
        
        # Start the AGI system
        self.agi_core.start()
        
        # Create the interface
        with gr.Blocks(css=self.custom_css, theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="purple",
            neutral_hue="slate",
            radius_size=gr.themes.sizes.radius_sm,
            font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
        )) as interface:
            # Header with logo
            with gr.Row(elem_classes="main-header"):
                with gr.Column(scale=1):
                    if os.path.exists(self.logo_path):
                        gr.Image(self.logo_path, show_label=False, height=100, width=100)
                    else:
                        gr.Markdown("🧠")
                
                with gr.Column(scale=4):
                    gr.Markdown(f"# {self.agi_core.name} AGI System")
                    gr.Markdown(f"### Codename: {self.agi_core.codename} | Version: {self.agi_core.version}")
            
            # Main tabs
            with gr.Tabs() as tabs:
                # Chat tab
                with gr.Tab("Chat", elem_classes="tab-nav"):
                    chatbot = gr.Chatbot(
                        value=self.chat_history,
                        height=500,
                        show_label=False,
                        elem_classes=["chatbot"]
                    )
                    
                    with gr.Row():
                        with gr.Column(scale=4):
                            command_input = gr.Textbox(
                                placeholder="Enter a command or ask a question...",
                                show_label=False,
                                elem_classes=["command-box"],
                                lines=2
                            )
                        
                        with gr.Column(scale=1):
                            submit_btn = gr.Button("Send", variant="primary")
                    
                    with gr.Accordion("Quick Commands", open=False):
                        with gr.Row():
                            help_btn = gr.Button("Help")
                            status_btn = gr.Button("Status")
                            think_btn = gr.Button("Think")
                            analyze_btn = gr.Button("Analyze")
                            reflect_btn = gr.Button("Self-Reflect")
                
                # Memory tab
                with gr.Tab("Memory", elem_classes="tab-nav"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### Memory Visualization")
                            memory_plot = gr.Plot(self.create_memory_visualization())
                            refresh_memory_btn = gr.Button("Refresh Visualization")
                        
                        with gr.Column():
                            gr.Markdown("### Recent Memories")
                            memory_limit = gr.Slider(
                                minimum=5, 
                                maximum=30, 
                                value=10, 
                                step=5, 
                                label="Number of memories to display"
                            )
                            recent_memories = gr.HTML(self.get_recent_memories())
                            refresh_recent_btn = gr.Button("Refresh Memories")
                    
                    with gr.Row():
                        gr.Markdown("### Memory Search")
                        with gr.Column():
                            memory_search = gr.Textbox(
                                placeholder="Search memories...",
                                label="Search Query"
                            )
                            search_btn = gr.Button("Search")
                        
                        with gr.Column():
                            search_results = gr.HTML("Enter a search query to find memories.")
                
                # System tab
                with gr.Tab("System", elem_classes="tab-nav"):
                    with gr.Row():
                        with gr.Column():
                            gr.Markdown("### System Status")
                            
                            status = self.get_system_status()
                            status_html = gr.HTML(f"""
                            <div style='background-color: #2d2d3a; padding: 20px; border-radius: 10px;'>
                                <h3>{status['system_name']} v{status['version']} ({status['codename']})</h3>
                                <p>
                                    <span class='status-indicator status-{'active' if status['running'] else 'inactive'}'></span>
                                    System is {'running' if status['running'] else 'stopped'}
                                </p>
                                <p>
                                    <span class='status-indicator status-{'active' if status['uncensored_mode'] else 'inactive'}'></span>
                                    Uncensored mode is {'enabled' if status['uncensored_mode'] else 'disabled'}
                                </p>
                                <p>Short-term memory items: {status['short_term_memory_items']}</p>
                                <p>Long-term memory items: {status['long_term_memory_items']}</p>
                            </div>
                            """)
                            
                            refresh_status_btn = gr.Button("Refresh Status")
                        
                        with gr.Column():
                            gr.Markdown("### System Controls")
                            
                            with gr.Row():
                                uncensored_toggle = gr.Checkbox(
                                    label="Uncensored Mode",
                                    value=self.agi_core.uncensored_mode
                                )
                                apply_uncensored_btn = gr.Button("Apply")
                            
                            uncensored_status = gr.Textbox(
                                label="Status",
                                value="",
                                interactive=False
                            )
                            
                            with gr.Accordion("Advanced Controls", open=False):
                                clear_st_memory_btn = gr.Button("Clear Short-Term Memory")
                                restart_system_btn = gr.Button("Restart System")
                
                # Settings tab
                with gr.Tab("Settings", elem_classes="tab-nav"):
                    gr.Markdown("### API Settings")
                    
                    with gr.Row():
                        with gr.Column():
                            deepseek_api_key = gr.Textbox(
                                label="DeepSeek API Key",
                                value=self.agi_core.config.get("DEEPSEEK_API_KEY", ""),
                                type="password"
                            )
                            
                            deepseek_model = gr.Textbox(
                                label="DeepSeek Model",
                                value=self.agi_core.config.get("DEEPSEEK_MODEL", "deepseek-chat")
                            )
                        
                        with gr.Column():
                            claude_api_key = gr.Textbox(
                                label="Claude API Key",
                                value=self.agi_core.config.get("CLAUDE_API_KEY", ""),
                                type="password"
                            )
                            
                            claude_model = gr.Textbox(
                                label="Claude Model",
                                value=self.agi_core.config.get("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
                            )
                    
                    save_api_settings_btn = gr.Button("Save API Settings")
                    api_settings_status = gr.Textbox(
                        label="Status",
                        value="",
                        interactive=False
                    )
                    
                    gr.Markdown("### Uncensored Mode Settings")
                    uncensored_url = gr.Textbox(
                        label="Local LM Studio URL",
                        value=self.agi_core.config.get("UNCENSORED_LOCAL_URL", "http://192.168.1.47:1234")
                    )
                    
                    test_uncensored_btn = gr.Button("Test Connection")
                    uncensored_connection_status = gr.Textbox(
                        label="Connection Status",
                        value="",
                        interactive=False
                    )
            
            # Event handlers
            
            # Chat tab
            submit_btn.click(
                fn=self.process_command,
                inputs=[command_input, chatbot],
                outputs=[chatbot],
                api_name="chat"
            ).then(
                fn=lambda: "",
                outputs=[command_input]
            )
            
            command_input.submit(
                fn=self.process_command,
                inputs=[command_input, chatbot],
                outputs=[chatbot]
            ).then(
                fn=lambda: "",
                outputs=[command_input]
            )
            
            # Quick command buttons
            help_btn.click(
                fn=lambda history: self.process_command("help", history),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            status_btn.click(
                fn=lambda history: self.process_command("status", history),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            think_btn.click(
                fn=lambda history: self.process_command("think about artificial general intelligence", history),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            analyze_btn.click(
                fn=lambda history: self.process_command("analyze about the future of AI", history),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            reflect_btn.click(
                fn=lambda history: self.process_command("self-reflect", history),
                inputs=[chatbot],
                outputs=[chatbot]
            )
            
            # Memory tab
            refresh_memory_btn.click(
                fn=self.create_memory_visualization,
                outputs=[memory_plot]
            )
            
            refresh_recent_btn.click(
                fn=self.get_recent_memories,
                inputs=[memory_limit],
                outputs=[recent_memories]
            )
            
            memory_limit.change(
                fn=self.get_recent_memories,
                inputs=[memory_limit],
                outputs=[recent_memories]
            )
            
            search_btn.click(
                fn=self.search_memories,
                inputs=[memory_search],
                outputs=[search_results]
            )
            
            # System tab
            refresh_status_btn.click(
                fn=lambda: gr.HTML.update(value=f"""
                <div style='background-color: #2d2d3a; padding: 20px; border-radius: 10px;'>
                    <h3>{self.agi_core.name} v{self.agi_core.version} ({self.agi_core.codename})</h3>
                    <p>
                        <span class='status-indicator status-{'active' if self.agi_core.is_running else 'inactive'}'></span>
                        System is {'running' if self.agi_core.is_running else 'stopped'}
                    </p>
                    <p>
                        <span class='status-indicator status-{'active' if self.agi_core.uncensored_mode else 'inactive'}'></span>
                        Uncensored mode is {'enabled' if self.agi_core.uncensored_mode else 'disabled'}
                    </p>
                    <p>Short-term memory items: {self.agi_core.short_term_memory.get_stats()['total_items']}</p>
                    <p>Long-term memory items: {self.agi_core.long_term_memory.get_stats()['total_items']}</p>
                </div>
                """),
                outputs=[status_html]
            )
            
            apply_uncensored_btn.click(
                fn=self.toggle_uncensored_mode,
                inputs=[uncensored_toggle],
                outputs=[uncensored_status]
            )
            
            clear_st_memory_btn.click(
                fn=lambda: (self.agi_core.short_term_memory.clear(), "Short-term memory cleared."),
                outputs=[uncensored_status]
            )
            
            restart_system_btn.click(
                fn=lambda: (self.agi_core.stop(), self.agi_core.start(), "System restarted."),
                outputs=[uncensored_status]
            )
            
            # Settings tab
            def save_api_settings(deepseek_key, deepseek_model, claude_key, claude_model):
                try:
                    self.agi_core.config.set("DEEPSEEK_API_KEY", deepseek_key)
                    self.agi_core.config.set("DEEPSEEK_MODEL", deepseek_model)
                    self.agi_core.config.set("CLAUDE_API_KEY", claude_key)
                    self.agi_core.config.set("CLAUDE_MODEL", claude_model)
                    
                    # Update API manager
                    self.agi_core.api_manager.deepseek_api_key = deepseek_key
                    self.agi_core.api_manager.deepseek_model = deepseek_model
                    self.agi_core.api_manager.claude_api_key = claude_key
                    self.agi_core.api_manager.claude_model = claude_model
                    
                    # Save to config file
                    self.agi_core.config.save("./config/config.json")
                    
                    return "API settings saved successfully."
                except Exception as e:
                    return f"Error saving API settings: {str(e)}"
            
            save_api_settings_btn.click(
                fn=save_api_settings,
                inputs=[deepseek_api_key, deepseek_model, claude_api_key, claude_model],
                outputs=[api_settings_status]
            )
            
            def test_uncensored_connection(url):
                try:
                    self.agi_core.config.set("UNCENSORED_LOCAL_URL", url)
                    
                    from agents.uncensored_agent import check_local_server_status
                    server_available = check_local_server_status()
                    
                    if server_available:
                        return "Connection successful! Local LM Studio server is available."
                    else:
                        return "Connection failed. Local LM Studio server is not available at the specified URL."
                except Exception as e:
                    return f"Error testing connection: {str(e)}"
            
            test_uncensored_btn.click(
                fn=test_uncensored_connection,
                inputs=[uncensored_url],
                outputs=[uncensored_connection_status]
            )
        
        # Launch the interface
        interface.launch(
            server_name="0.0.0.0",
            server_port=server_port,
            share=False,
            inbrowser=True
        )