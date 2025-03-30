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
            "short_term_memory_items": short_term_stats.get("total_items", 0),
            "long_term_memory_items": long_term_stats.get("total_items", 0),
            "memory_types": dict(short_term_stats.get("items_by_type", {}))
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
    
    def _validate_components(self) -> None:
        """Validate all GUI components before initialization"""
        if not isinstance(self.chat_history, list):
            self.logger.error(f"chat_history must be list, got {type(self.chat_history)}")
            self.chat_history = []
            
        if not isinstance(self.agi_core.short_term_memory.get_stats(), dict):
            self.logger.error("Invalid short_term_memory stats format")
            
        if not isinstance(self.agi_core.long_term_memory.get_stats(), dict):
            self.logger.error("Invalid long_term_memory stats format")

    def start(self, server_port: int = 57264) -> None:
        """
        Start the web GUI
        
        Args:
            server_port: Port to run the server on
        """
        self.logger.info(f"Starting web GUI on port {server_port}")
        try:
            # Test all components before starting
            self._validate_components()
            
            # Start the AGI system
            self.agi_core.start()
            
            # Create the interface
            # Theme configuration with fallbacks
            try:
                theme_params = {
                    'primary_hue': os.getenv('THEME_PRIMARY', "indigo"),
                    'secondary_hue': os.getenv('THEME_SECONDARY', "purple"),
                    'neutral_hue': os.getenv('THEME_NEUTRAL', "slate"),
                    'radius_size': getattr(gr.themes.sizes, os.getenv('THEME_RADIUS', 'radius_sm')),
                    'font': [
                        gr.themes.GoogleFont(os.getenv('THEME_FONT', 'Inter')),
                        "ui-sans-serif",
                        "system-ui",
                        "sans-serif"
                    ]
                }
                theme = gr.themes.Soft(**theme_params)
            except Exception as e:
                self.logger.warning(f"Using default theme after config error: {str(e)}")
                theme = gr.themes.Soft()
            
            with gr.Blocks(css=self.custom_css, theme=theme) as interface:
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
                        # Chat interface components here
                        pass
                        
        except Exception as e:
            self.logger.error(f"WebGUI initialization failed: {str(e)}")
            raise
        finally:
            self.logger.info("WebGUI initialization attempt completed")
            self.logger.info("Web interface launch attempt completed")