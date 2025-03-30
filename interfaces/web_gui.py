"""
Web GUI - Modern web interface for Hohenheim AGI
Provides an aesthetic, multi-functional interface using Gradio
"""

import os
import time
import logging
import asyncio
import threading
import uuid
import hashlib
import json
import base64
import contextlib
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, TypeVar, cast
from io import BytesIO
import traceback
from pathlib import Path

# Third-party imports with proper error handling
try:
    import gradio as gr
    import pandas as pd
    import numpy as np
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    raise ImportError(f"Required package missing: {str(e)}. Please install all dependencies.") from e

# Type definitions for better code readability
JSON = Dict[str, Any]
ChatHistory = List[Tuple[str, str]]
ThemeParams = Dict[str, Any]
T = TypeVar('T')

# Constants for improved maintainability
DEFAULT_PORT = 57264
MEMORY_LIMIT_DEFAULT = 10
DEFAULT_LOGO_PATH = "interfaces/assets/default_logo.png"
ASSETS_DIR = Path("interfaces/assets")


class MessageType(Enum):
    """Enum for message types in the chat history."""
    USER = auto()
    SYSTEM = auto()
    ERROR = auto()
    WARNING = auto()
    SUCCESS = auto()


class APIKeyManager:
    """Secure manager for API keys with encryption"""
    
    def __init__(self, config_manager: Any):
        """
        Initialize the API key manager
        
        Args:
            config_manager: Reference to the configuration manager
        """
        self.config_manager = config_manager
        self._encryption_key = self._get_or_create_encryption_key()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create an encryption key for API keys"""
        key_path = Path("config/encryption.key")
        key_path.parent.mkdir(exist_ok=True)
        
        if key_path.exists():
            return key_path.read_bytes()
        else:
            # Generate a new key
            new_key = os.urandom(32)  # 256-bit key
            key_path.write_bytes(new_key)
            return new_key
    
    def encrypt(self, value: str) -> str:
        """
        Encrypt a string value
        
        Args:
            value: The string to encrypt
            
        Returns:
            Encrypted string in base64 format
        """
        if not value:
            return ""
            
        try:
            # Simple encryption using XOR with the key (for demo purposes)
            # In production, use proper encryption libraries like cryptography
            value_bytes = value.encode('utf-8')
            encrypted = bytearray()
            
            for i, b in enumerate(value_bytes):
                key_byte = self._encryption_key[i % len(self._encryption_key)]
                encrypted.append(b ^ key_byte)
                
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logging.error(f"Encryption error: {str(e)}")
            return ""
    
    def decrypt(self, encrypted_value: str) -> str:
        """
        Decrypt an encrypted string value
        
        Args:
            encrypted_value: The encrypted string in base64 format
            
        Returns:
            Decrypted string
        """
        if not encrypted_value:
            return ""
            
        try:
            # Decrypt using the same XOR method
            encrypted_bytes = base64.b64decode(encrypted_value)
            decrypted = bytearray()
            
            for i, b in enumerate(encrypted_bytes):
                key_byte = self._encryption_key[i % len(self._encryption_key)]
                decrypted.append(b ^ key_byte)
                
            return decrypted.decode('utf-8')
        except Exception as e:
            logging.error(f"Decryption error: {str(e)}")
            return ""
    
    def set_api_key(self, key_name: str, value: str) -> None:
        """
        Set an API key with encryption
        
        Args:
            key_name: The name of the API key
            value: The API key value
        """
        encrypted_value = self.encrypt(value)
        self.config_manager.set(key_name, encrypted_value)
    
    def get_api_key(self, key_name: str) -> str:
        """
        Get a decrypted API key
        
        Args:
            key_name: The name of the API key
            
        Returns:
            Decrypted API key
        """
        encrypted_value = self.config_manager.get(key_name, "")
        return self.decrypt(encrypted_value)


class PerformanceMetrics:
    """Track performance metrics for the GUI"""
    
    def __init__(self):
        """Initialize the performance metrics"""
        self.operation_times: Dict[str, List[float]] = {}
        self.request_counts: Dict[str, int] = {}
        self.lock = threading.RLock()
    
    def start_operation(self, operation_name: str) -> int:
        """
        Start timing an operation
        
        Args:
            operation_name: Name of the operation to time
            
        Returns:
            Operation ID for stopping the timer
        """
        operation_id = int(time.time() * 1000)
        
        with self.lock:
            if operation_name not in self.operation_times:
                self.operation_times[operation_name] = []
            
            if operation_name not in self.request_counts:
                self.request_counts[operation_name] = 0
                
            self.request_counts[operation_name] += 1
        
        return operation_id
    
    def stop_operation(self, operation_name: str, operation_id: int) -> float:
        """
        Stop timing an operation and record the time
        
        Args:
            operation_name: Name of the operation
            operation_id: ID returned from start_operation
            
        Returns:
            Elapsed time in milliseconds
        """
        end_time = int(time.time() * 1000)
        elapsed = end_time - operation_id
        
        with self.lock:
            if operation_name in self.operation_times:
                self.operation_times[operation_name].append(elapsed)
        
        return elapsed
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get the current performance metrics
        
        Returns:
            Dictionary with performance metrics
        """
        with self.lock:
            metrics = {}
            
            for op_name, times in self.operation_times.items():
                if not times:
                    continue
                    
                metrics[op_name] = {
                    "count": self.request_counts.get(op_name, 0),
                    "avg_time_ms": sum(times) / len(times),
                    "max_time_ms": max(times),
                    "min_time_ms": min(times)
                }
            
            return metrics


class UIThemeManager:
    """Manage and customize UI themes"""
    
    def __init__(self):
        """Initialize the theme manager with default settings"""
        # Default theme colors
        self.primary_color = "#3a86ff"
        self.secondary_color = "#8338ec"
        self.background_color = "#1e1e2e"
        self.text_color = "#ffffff"
        self.accent_color = "#ff006e"
        
        # Theme variations
        self.themes = {
            "default": {
                "primary_color": "#3a86ff",
                "secondary_color": "#8338ec",
                "background_color": "#1e1e2e",
                "text_color": "#ffffff",
                "accent_color": "#ff006e"
            },
            "dark": {
                "primary_color": "#2563eb",
                "secondary_color": "#7c3aed",
                "background_color": "#111827",
                "text_color": "#f9fafb",
                "accent_color": "#ec4899"
            },
            "light": {
                "primary_color": "#3b82f6",
                "secondary_color": "#8b5cf6",
                "background_color": "#f3f4f6",
                "text_color": "#111827",
                "accent_color": "#ec4899"
            },
            "terminal": {
                "primary_color": "#00ff00",
                "secondary_color": "#00aa00",
                "background_color": "#000000",
                "text_color": "#ffffff",
                "accent_color": "#ff5555"
            }
        }
    
    def get_theme(self, theme_name: str) -> Dict[str, str]:
        """
        Get a theme by name
        
        Args:
            theme_name: Name of the theme
            
        Returns:
            Theme color dictionary
        """
        return self.themes.get(theme_name, self.themes["default"])
    
    def set_theme(self, theme_name: str) -> None:
        """
        Set the current theme by name
        
        Args:
            theme_name: Name of the theme
        """
        theme = self.get_theme(theme_name)
        self.primary_color = theme["primary_color"]
        self.secondary_color = theme["secondary_color"]
        self.background_color = theme["background_color"]
        self.text_color = theme["text_color"]
        self.accent_color = theme["accent_color"]
    
    def get_gradio_theme_params(self) -> ThemeParams:
        """
        Get theme parameters for Gradio
        
        Returns:
            Dictionary of theme parameters for Gradio
        """
        # Map our theme colors to Gradio theme parameters
        return {
            'primary_hue': self._color_to_hue(self.primary_color),
            'secondary_hue': self._color_to_hue(self.secondary_color),
            'neutral_hue': self._color_to_hue(self.background_color),
            'radius_size': gr.themes.sizes.radius_sm,
            'font': [gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"]
        }
    
    def _color_to_hue(self, color: str) -> str:
        """
        Convert a hex color to a Gradio theme hue name
        This is a simplified mapping - in reality would need a more sophisticated approach
        
        Args:
            color: Hex color code
            
        Returns:
            Gradio hue name
        """
        # Very basic mapping of hex colors to Gradio hue names
        color_map = {
            "#3a86ff": "blue",
            "#8338ec": "purple",
            "#ff006e": "pink",
            "#1e1e2e": "slate",
            "#ffffff": "gray",
            "#000000": "gray",
            "#00ff00": "green",
            "#00aa00": "green",
            "#ff5555": "red",
            "#2563eb": "blue",
            "#7c3aed": "purple",
            "#111827": "slate",
            "#f9fafb": "gray",
            "#ec4899": "pink",
            "#3b82f6": "blue",
            "#8b5cf6": "purple",
            "#f3f4f6": "gray"
        }
        
        return color_map.get(color.lower(), "blue")
    
    def get_custom_css(self) -> str:
        """
        Get custom CSS for current theme
        
        Returns:
            CSS string with current theme colors
        """
        return f"""
        .gradio-container {{
            background-color: {self.background_color};
            color: {self.text_color};
        }}
        
        .main-header {{
            background: linear-gradient(90deg, {self.primary_color}, {self.secondary_color});
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .chat-message {{
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        
        .user-message {{
            background-color: {self.primary_color};
            margin-left: 20%;
            margin-right: 5%;
        }}
        
        .bot-message {{
            background-color: {self.background_color}; 
            margin-right: 20%;
            margin-left: 5%;
            border: 1px solid {self.secondary_color};
        }}
        
        .command-box {{
            border: 2px solid {self.secondary_color};
            border-radius: 10px;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }}
        
        .status-active {{
            background-color: #4cc9f0;
            box-shadow: 0 0 8px #4cc9f0;
        }}
        
        .status-inactive {{
            background-color: #f72585;
            box-shadow: 0 0 8px #f72585;
        }}
        
        .memory-card {{
            background-color: {self.background_color};
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 4px solid {self.secondary_color};
        }}
        
        .tab-nav {{
            background-color: {self.background_color};
            border-radius: 10px;
            padding: 5px;
        }}
        
        .tab-selected {{
            background-color: {self.primary_color};
            color: {self.text_color};
        }}
        
        .info-box {{
            background-color: rgba(58, 134, 255, 0.1);
            border-left: 3px solid {self.primary_color};
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        
        .warning-box {{
            background-color: rgba(255, 204, 0, 0.1);
            border-left: 3px solid #ffcc00;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        
        .error-box {{
            background-color: rgba(255, 0, 0, 0.1);
            border-left: 3px solid #ff0000;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        
        .success-box {{
            background-color: rgba(0, 255, 0, 0.1);
            border-left: 3px solid #00ff00;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        
        .dashboard-card {{
            background-color: {self.background_color};
            border-radius: 10px;
            border: 1px solid {self.secondary_color};
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 15px;
            margin: 10px;
            min-height: 200px;
        }}
        
        .dashboard-card h3 {{
            color: {self.accent_color};
            margin-top: 0;
            border-bottom: 1px solid {self.secondary_color};
            padding-bottom: 10px;
        }}
        
        .visualization-container {{
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        
        .footer {{
            text-align: center;
            padding: 20px;
            font-size: 0.8em;
            opacity: 0.7;
        }}
        
        /* Animations */
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
        
        /* Scrollbars */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {self.background_color};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {self.secondary_color};
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {self.primary_color};
        }}
        """


class WebGUI:
    """
    Web-based GUI for the Hohenheim AGI system.
    Provides a modern, aesthetic interface with multiple tabs and visualizations.
    """
    
    def __init__(self, agi_core: Any):
        """
        Initialize the web GUI
        
        Args:
            agi_core: Reference to the main AGI core instance
        """
        self.agi_core = agi_core
        self.logger = logging.getLogger("Hohenheim.WebGUI")
        self.logger.setLevel(logging.INFO)
        
        # Setup file handler if it doesn't exist
        if not self.logger.handlers:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            file_handler = logging.FileHandler(log_dir / "webgui.log")
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(file_handler)
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Chat history with thread safety
        self._chat_history: ChatHistory = []
        self._chat_history_lock = threading.RLock()
        
        # Performance tracking
        self.metrics = PerformanceMetrics()
        
        # Theme management
        self.theme_manager = UIThemeManager()
        self.theme_manager.set_theme("default")
        
        # API key management
        self.api_key_manager = APIKeyManager(self.agi_core.config)
        
        # Set initial API keys from config but decrypt them
        self._initialize_api_keys()
        
        # Load logo
        self.logo_path = self._create_logo()
        
        # Operational state
        self.is_initialized = False
        self.active_sessions = 0
        self.start_time = time.time()
        
        # Interface components for updates
        self.interface_components = {}
        
        self.logger.info("WebGUI initialized")
    
    def _initialize_api_keys(self) -> None:
        """Initialize API keys from config with decryption"""
        # Get encrypted keys from config
        deepseek_key = self.agi_core.config.get("DEEPSEEK_API_KEY", "")
        claude_key = self.agi_core.config.get("CLAUDE_API_KEY", "")
        
        # If keys are not encrypted yet, encrypt them
        if deepseek_key and not deepseek_key.startswith("encrypted:"):
            # Encrypt the key and save it
            self.api_key_manager.set_api_key("DEEPSEEK_API_KEY", deepseek_key)
        
        if claude_key and not claude_key.startswith("encrypted:"):
            # Encrypt the key and save it
            self.api_key_manager.set_api_key("CLAUDE_API_KEY", claude_key)
    
    def _create_logo(self) -> str:
        """
        Create and save the Hohenheim logo
        
        Returns:
            Path to the logo file
        """
        # Create assets directory if it doesn't exist
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Path to save the logo
        logo_path = ASSETS_DIR / "hohenheim_logo.png"
        
        # If logo already exists, return the path
        if logo_path.exists():
            return str(logo_path)
        
        try:
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
            
            # Try to use a font
            try:
                # Try common system fonts
                font_paths = [
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                    "/System/Library/Fonts/Helvetica.ttc",  # macOS
                    "C:\\Windows\\Fonts\\arial.ttf",  # Windows
                ]
                
                font = None
                for path in font_paths:
                    if os.path.exists(path):
                        font = ImageFont.truetype(path, 200)
                        break
                
                if font is None:
                    font = ImageFont.load_default()
                
            except Exception as e:
                self.logger.warning(f"Could not load font: {e}")
                font = ImageFont.load_default()
            
            # Draw an "H" in the center
            draw.text((140, 70), "H", fill=(255, 255, 255, 230), font=font)
            
            # Save the image
            img.save(logo_path)
            self.logger.info(f"Created logo at {logo_path}")
            
            return str(logo_path)
            
        except Exception as e:
            self.logger.error(f"Error creating logo: {str(e)}")
            
            # Return path to default logo
            default_logo = ASSETS_DIR / "default_logo.png"
            
            # Create a simple default logo if it doesn't exist
            if not default_logo.exists():
                try:
                    # Create a simple colored square as default logo
                    img = Image.new('RGB', (200, 200), color=(58, 134, 255))
                    img.save(default_logo)
                except Exception as e2:
                    self.logger.error(f"Error creating default logo: {str(e2)}")
            
            return str(default_logo) if default_logo.exists() else ""
    
    @property
    def chat_history(self) -> ChatHistory:
        """
        Thread-safe access to chat history
        
        Returns:
            Copy of the current chat history
        """
        with self._chat_history_lock:
            return self._chat_history.copy()
    
    @chat_history.setter
    def chat_history(self, history: ChatHistory) -> None:
        """
        Thread-safe setter for chat history
        
        Args:
            history: New chat history
        """
        with self._chat_history_lock:
            self._chat_history = history
    
    def add_to_chat_history(self, user_message: str, system_response: str) -> None:
        """
        Add a message pair to chat history with thread safety
        
        Args:
            user_message: Message from the user
            system_response: Response from the system
        """
        with self._chat_history_lock:
            self._chat_history.append((user_message, system_response))
    
    def clear_chat_history(self) -> None:
        """Clear the chat history with thread safety"""
        with self._chat_history_lock:
            self._chat_history = []
    
    async def process_command_async(self, command: str, history: ChatHistory) -> ChatHistory:
        """
        Asynchronously process a command and update the chat history
        
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
        
        # Start timing the operation
        op_id = self.metrics.start_operation("process_command")
        
        try:
            # Process the command (in real impl. would use asyncio.to_thread for CPU-bound)
            response = await asyncio.to_thread(self.agi_core.process_command, command)
            
            # Format the response
            output = await self._format_response(response)
            
            # Update the last message with the response
            history[-1] = (command, output)
            
        except Exception as e:
            self.logger.error(f"Error processing command: {str(e)}")
            error_details = traceback.format_exc()
            self.logger.debug(f"Traceback: {error_details}")
            
            history[-1] = (command, f"<div class='error-box'>Error: {str(e)}</div>")
        
        # Stop timing the operation
        self.metrics.stop_operation("process_command", op_id)
        
        return history
    
    def process_command(self, command: str, history: ChatHistory) -> ChatHistory:
        """
        Synchronous wrapper for process_command_async
        
        Args:
            command: The command to process
            history: Current chat history
            
        Returns:
            Updated chat history
        """
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're already in an event loop (Gradio's)
            future = asyncio.run_coroutine_threadsafe(
                self.process_command_async(command, history), 
                loop
            )
            return future.result()
        else:
            # No event loop running, create one
            return asyncio.run(self.process_command_async(command, history))
    
    async def _format_response(self, response: Dict[str, Any]) -> str:
        """
        Format the response for display
        
        Args:
            response: Response dictionary from the AGI core
            
        Returns:
            Formatted HTML string
        """
        output = ""
        
        if "error" in response:
            output += f"<div class='error-box'>Error: {response['error']}</div>"
        elif "message" in response:
            output += f"<div>{response['message']}</div>"
            
            # Add reasoning with collapsible section if available
            if "reasoning" in response and response["reasoning"]:
                output += f"""
                <details class='info-box'>
                    <summary>Reasoning</summary>
                    <div>{response['reasoning']}</div>
                </details>
                """
            
            # Add memories if available
            if "memories" in response and response["memories"]:
                output += """
                <details class='info-box'>
                    <summary>Related Memories</summary>
                    <div class='memory-results'>
                """
                
                for i, memory in enumerate(response["memories"], 1):
                    output += f"<div class='memory-card'>"
                    
                    if isinstance(memory, dict):
                        if "title" in memory:
                            output += f"<strong>{i}. {memory['title']}</strong><br>"
                        if "content" in memory:
                            output += f"{memory['content']}<br>"
                        elif "data" in memory:
                            # Format JSON data more nicely
                            formatted_data = json.dumps(memory["data"], indent=2)
                            output += f"<pre>{formatted_data}</pre>"
                    else:
                        output += f"{i}. {str(memory)}"
                    
                    output += "</div>"
                
                output += "</div></details>"
        else:
            output = "<div class='warning-box'>No response generated.</div>"
        
        return output
    
    async def get_system_status_async(self) -> Dict[str, Any]:
        """
        Asynchronously get the current system status
        
        Returns:
            Dictionary with system status information
        """
        # Time this operation
        op_id = self.metrics.start_operation("get_system_status")
        
        try:
            # Get memory stats (in real impl. would use asyncio.to_thread)
            short_term_stats = await asyncio.to_thread(
                self.agi_core.short_term_memory.get_stats
            )
            long_term_stats = await asyncio.to_thread(
                self.agi_core.long_term_memory.get_stats
            )
            
            # Get performance metrics
            perf_metrics = self.metrics.get_metrics()
            
            # Calculate uptime
            uptime_seconds = time.time() - self.start_time
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            uptime_str = ""
            if days > 0:
                uptime_str += f"{int(days)}d "
            if hours > 0 or days > 0:
                uptime_str += f"{int(hours)}h "
            if minutes > 0 or hours > 0 or days > 0:
                uptime_str += f"{int(minutes)}m "
            uptime_str += f"{int(seconds)}s"
            
            # Format the stats
            status = {
                "system_name": self.agi_core.name,
                "version": self.agi_core.version,
                "codename": self.agi_core.codename,
                "running": self.agi_core.is_running,
                "uncensored_mode": self.agi_core.uncensored_mode,
                "short_term_memory_items": short_term_stats["total_items"],
                "long_term_memory_items": long_term_stats["total_items"],
                "memory_types": dict(short_term_stats["items_by_type"]),
                "active_sessions": self.active_sessions,
                "performance": perf_metrics,
                "uptime": uptime_str,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {str(e)}")
            return {
                "error": str(e),
                "system_name": self.agi_core.name,
                "version": self.agi_core.version,
                "codename": self.agi_core.codename
            }
        finally:
            # Stop timing
            self.metrics.stop_operation("get_system_status", op_id)
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Synchronous wrapper for get_system_status_async
        
        Returns:
            Dictionary with system status information
        """
        loop = asyncio.get_event_loop()
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(
                self.get_system_status_async(), loop
            )
            return future.result()
        else:
            return asyncio.run(self.get_system_status_async())
    
    def create_memory_visualization(self) -> Any:
        """
        Create a visualization of the memory system
        
        Returns:
            Plotly figure
        """
        op_id = self.metrics.start_operation("create_memory_visualization")
        
        try:
            # Get memory stats
            short_term_stats = self.agi_core.short_term_memory.get_stats()
            long_term_stats = self.agi_core.long_term_memory.get_stats()
            
            # Create subplots
            fig = make_subplots(
                rows=2, 
                cols=1, 
                subplot_titles=("Short-term Memory Types", "Memory Distribution"),
                vertical_spacing=0.1,
                row_heights=[0.6, 0.4]
            )
            
            # Process short-term memory by type
            memory_types = short_term_stats.get("items_by_type", {})
            if not memory_types:
                # Create a placeholder if no memory items
                memory_df = pd.DataFrame({
                    "Memory Type": ["No memories yet"],
                    "Count": [0]
                })
            else:
                memory_df = pd.DataFrame({
                    "Memory Type": list(memory_types.keys()),
                    "Count": list(memory_types.values())
                })
                
                # Sort by count descending
                memory_df = memory_df.sort_values("Count", ascending=False)
            
            # Create bar chart for memory types
            fig.add_trace(
                go.Bar(
                    x=memory_df["Memory Type"],
                    y=memory_df["Count"],
                    marker_color=px.colors.sequential.Viridis,
                    name="Memory Types"
                ),
                row=1, col=1
            )
            
            # Create pie chart for overall memory distribution
            fig.add_trace(
                go.Pie(
                    labels=["Short-term", "Long-term"],
                    values=[
                        short_term_stats.get("total_items", 0),
                        long_term_stats.get("total_items", 0)
                    ],
                    hole=0.4,
                    marker=dict(
                        colors=[self.theme_manager.primary_color, self.theme_manager.secondary_color]
                    ),
                    textinfo="label+percent",
                    name="Memory Distribution"
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=self.theme_manager.text_color,
                height=600,
                margin=dict(l=40, r=40, t=80, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Update axes
            fig.update_yaxes(gridcolor="rgba(255,255,255,0.1)")
            fig.update_xaxes(gridcolor="rgba(255,255,255,0.1)")
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating memory visualization: {str(e)}")
            # Create a simple error figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating visualization: {str(e)}",
                showarrow=False,
                font=dict(color="red")
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=self.theme_manager.text_color
            )
            return fig
        finally:
            self.metrics.stop_operation("create_memory_visualization", op_id)
    
    def create_performance_visualization(self) -> Any:
        """
        Create a visualization of system performance
        
        Returns:
            Plotly figure
        """
        op_id = self.metrics.start_operation("create_performance_visualization")
        
        try:
            # Get performance metrics
            perf_metrics = self.metrics.get_metrics()
            
            if not perf_metrics:
                # No metrics yet
                fig = go.Figure()
                fig.add_annotation(
                    text="No performance data available yet",
                    showarrow=False
                )
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color=self.theme_manager.text_color
                )
                return fig
            
            # Create subplots
            fig = make_subplots(
                rows=2, 
                cols=1,
                subplot_titles=("Operation Response Times (ms)", "Operation Counts"),
                vertical_spacing=0.25,
                row_heights=[0.6, 0.4]
            )
            
            # Prepare data
            op_names = list(perf_metrics.keys())
            avg_times = [perf_metrics[op]["avg_time_ms"] for op in op_names]
            max_times = [perf_metrics[op]["max_time_ms"] for op in op_names]
            min_times = [perf_metrics[op]["min_time_ms"] for op in op_names]
            counts = [perf_metrics[op]["count"] for op in op_names]
            
            # Add response time traces
            fig.add_trace(
                go.Bar(
                    x=op_names,
                    y=avg_times,
                    name="Average Time (ms)",
                    marker_color=self.theme_manager.primary_color,
                    text=avg_times,
                    texttemplate='%{text:.1f}',
                    textposition='auto'
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=op_names,
                    y=max_times,
                    mode='markers',
                    name="Max Time (ms)",
                    marker=dict(
                        color=self.theme_manager.accent_color,
                        size=10,
                        symbol='triangle-up'
                    )
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=op_names,
                    y=min_times,
                    mode='markers',
                    name="Min Time (ms)",
                    marker=dict(
                        color="#4cc9f0",
                        size=10,
                        symbol='triangle-down'
                    )
                ),
                row=1, col=1
            )
            
            # Add count trace
            fig.add_trace(
                go.Bar(
                    x=op_names,
                    y=counts,
                    name="Operation Count",
                    marker_color=self.theme_manager.secondary_color,
                    text=counts,
                    textposition='auto'
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=self.theme_manager.text_color,
                height=600,
                margin=dict(l=40, r=40, t=80, b=40),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            # Update axes
            fig.update_yaxes(
                gridcolor="rgba(255,255,255,0.1)",
                title_text="Time (ms)",
                row=1, col=1
            )
            
            fig.update_yaxes(
                gridcolor="rgba(255,255,255,0.1)",
                title_text="Count",
                row=2, col=1
            )
            
            fig.update_xaxes(
                gridcolor="rgba(255,255,255,0.1)"
            )
            
            return fig
            
        except Exception as e:
            self.logger.error(f"Error creating performance visualization: {str(e)}")
            # Create a simple error figure
            fig = go.Figure()
            fig.add_annotation(
                text=f"Error creating visualization: {str(e)}",
                showarrow=False,
                font=dict(color="red")
            )
            fig.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color=self.theme_manager.text_color
            )
            return fig
        finally:
            self.metrics.stop_operation("create_performance_visualization", op_id)
    
    def get_recent_memories(self, limit: int = 10) -> str:
        """
        Get recent memories from the system with enhanced formatting
        
        Args:
            limit: Maximum number of memories to retrieve
            
        Returns:
            Formatted HTML string with recent memories
        """
        op_id = self.metrics.start_operation("get_recent_memories")
        
        try:
            memories = self.agi_core.short_term_memory.get_recent(limit=limit)
            
            if not memories:
                return "<div class='info-box'>No memories found in short-term memory.</div>"
            
            output = "<div class='memory-results'>"
            
            for i, memory in enumerate(memories, 1):
                memory_type = memory.get("type", "unknown")
                created_at = memory.get("created_at", "unknown time")
                
                # Format timestamp if it's a float or int
                if isinstance(created_at, (float, int)):
                    created_at = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
                
                output += f"<div class='memory-card'>"
                output += f"<strong>Memory {i} ({memory_type})</strong> - {created_at}<br>"
                
                # Handle different memory structures
                data = memory.get("data", {})
                if isinstance(data, dict):
                    for key, value in data.items():
                        if key not in ["timestamp", "context", "created_at"]:
                            if isinstance(value, dict):
                                # Format nested dictionaries more nicely
                                if "reasoning" in value:
                                    output += f"<strong>{key}:</strong> {value['reasoning'][:300]}..."
                                    if len(value['reasoning']) > 300:
                                        output += " <span class='more-content'>[...]</span>"
                                    output += "<br>"
                                else:
                                    # For other nested dicts, show a summary
                                    keys = list(value.keys())
                                    output += f"<strong>{key}:</strong> {{{', '.join(keys[:3])}"
                                    if len(keys) > 3:
                                        output += f", ... ({len(keys)} keys)"
                                    output += "}<br>"
                            else:
                                # Truncate long values
                                str_value = str(value)
                                if len(str_value) > 300:
                                    output += f"<strong>{key}:</strong> {str_value[:300]}... <span class='more-content'>[...]</span><br>"
                                else:
                                    output += f"<strong>{key}:</strong> {str_value}<br>"
                elif isinstance(data, str):
                    # For string data
                    if len(data) > 500:
                        output += f"{data[:500]}... <span class='more-content'>[...]</span>"
                    else:
                        output += data
                else:
                    # For other data types
                    output += f"{str(data)[:300]}..."
                    if len(str(data)) > 300:
                        output += " <span class='more-content'>[...]</span>"
                
                output += "</div>"
            
            output += "</div>"
            
            return output
            
        except Exception as e:
            self.logger.error(f"Error getting recent memories: {str(e)}")
            return f"<div class='error-box'>Error retrieving memories: {str(e)}</div>"
        finally:
            self.metrics.stop_operation("get_recent_memories", op_id)
    
    def toggle_uncensored_mode(self, enable: bool) -> str:
        """
        Toggle uncensored mode with enhanced error handling
        
        Args:
            enable: Whether to enable or disable uncensored mode
            
        Returns:
            Status message
        """
        op_id = self.metrics.start_operation("toggle_uncensored_mode")
        
        try:
            if enable:
                # Check if local server is available
                try:
                    from agents.uncensored_agent import check_local_server_status
                    server_available = check_local_server_status()
                    
                    if not server_available:
                        return "<div class='error-box'>Cannot enable uncensored mode. Local LM Studio server is not available.</div>"
                except ImportError:
                    return "<div class='error-box'>Cannot enable uncensored mode. The uncensored_agent module is not available.</div>"
                except Exception as e:
                    return f"<div class='error-box'>Error checking local server: {str(e)}</div>"
            
            # Toggle the mode
            current_state = self.agi_core.toggle_uncensored_mode(enable)
            
            if current_state:
                return "<div class='success-box'>Uncensored mode is now enabled. Using local LM Studio server for unrestricted reasoning.</div>"
            else:
                return "<div class='info-box'>Uncensored mode is now disabled. Using standard reasoning APIs.</div>"
            
            debug_log_btn.click(
                fn=lambda: self._export_debug_logs(),
                outputs=[uncensored_status]
            )
            
            # Performance tab
            refresh_perf_btn.click(
                fn=self.create_performance_visualization,
                outputs=[performance_plot]
            )
            
            if monitoring_available:
                def create_resource_plot():
                    try:
                        # Create a figure with 2 subplots
                        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                        
                        # Get CPU usage over time
                        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
                        num_cores = len(cpu_percent)
                        
                        # Plot CPU usage per core
                        bars = ax1.bar(range(num_cores), cpu_percent, color=self.theme_manager.primary_color)
                        ax1.set_title('CPU Usage by Core (%)')
                        ax1.set_xlabel('CPU Core')
                        ax1.set_ylabel('Usage (%)')
                        ax1.set_ylim(0, 100)
                        
                        # Add percentage labels
                        for bar in bars:
                            height = bar.get_height()
                            ax1.annotate(f'{height:.1f}%',
                                        xy=(bar.get_x() + bar.get_width() / 2, height),
                                        xytext=(0, 3),
                                        textcoords="offset points",
                                        ha='center', va='bottom')
                        
                        # Get memory usage
                        memory = psutil.virtual_memory()
                        
                        # Create memory usage pie chart
                        labels = ['Used', 'Available']
                        sizes = [memory.used, memory.available]
                        colors = [self.theme_manager.secondary_color, self.theme_manager.primary_color]
                        
                        ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                        ax2.set_title(f'Memory Usage: {memory.used / (1024**3):.2f} GB / {memory.total / (1024**3):.2f} GB')
                        
                        # Adjust layout
                        plt.tight_layout()
                        
                        return fig
                    except Exception as e:
                        self.logger.error(f"Error creating resource plot: {str(e)}")
                        fig = plt.figure(figsize=(6, 4))
                        plt.text(0.5, 0.5, f"Error: {str(e)}", ha='center', va='center')
                        plt.axis('off')
                        return fig
                
                refresh_resource_btn.click(
                    fn=create_resource_plot,
                    outputs=[resource_plot]
                )
            
            # Settings tab
            apply_theme_btn.click(
                fn=lambda theme: (
                    self.theme_manager.set_theme(theme),
                    "<div class='success-box'>Theme applied successfully. Refresh the page to see all changes.</div>"
                )[1],
                inputs=[theme_dropdown],
                outputs=[theme_status]
            )
            
            def save_api_settings(deepseek_key, deepseek_model, claude_key, claude_model):
                try:
                    # Encrypt and save API keys
                    self.api_key_manager.set_api_key("DEEPSEEK_API_KEY", deepseek_key)
                    self.api_key_manager.set_api_key("CLAUDE_API_KEY", claude_key)
                    
                    # Save model names
                    self.agi_core.config.set("DEEPSEEK_MODEL", deepseek_model)
                    self.agi_core.config.set("CLAUDE_MODEL", claude_model)
                    
                    # Update API manager if available
                    if hasattr(self.agi_core, 'api_manager'):
                        # Only update if the key has changed
                        if self.agi_core.api_manager.deepseek_api_key != deepseek_key:
                            self.agi_core.api_manager.deepseek_api_key = deepseek_key
                        if self.agi_core.api_manager.deepseek_model != deepseek_model:
                            self.agi_core.api_manager.deepseek_model = deepseek_model
                        if self.agi_core.api_manager.claude_api_key != claude_key:
                            self.agi_core.api_manager.claude_api_key = claude_key
                        if self.agi_core.api_manager.claude_model != claude_model:
                            self.agi_core.api_manager.claude_model = claude_model
                    
                    # Save to config file
                    self.agi_core.config.save()
                    
                    return "<div class='success-box'>API settings saved successfully.</div>"
                except Exception as e:
                    self.logger.error(f"Error saving API settings: {str(e)}")
                    return f"<div class='error-box'>Error saving API settings: {str(e)}</div>"
            
            save_api_settings_btn.click(
                fn=save_api_settings,
                inputs=[deepseek_api_key, deepseek_model, claude_api_key, claude_model],
                outputs=[api_settings_status]
            )
            
            def test_uncensored_connection(url):
                try:
                    self.agi_core.config.set("UNCENSORED_LOCAL_URL", url)
                    
                    # Test the connection
                    try:
                        from agents.uncensored_agent import check_local_server_status
                        server_available = check_local_server_status(url)
                        
                        if server_available:
                            return "<div class='success-box'>Connection successful! Local LM Studio server is available.</div>"
                        else:
                            return "<div class='error-box'>Connection failed. Local LM Studio server is not available at the specified URL.</div>"
                    except ImportError:
                        return "<div class='warning-box'>Cannot test connection: The uncensored_agent module is not available.</div>"
                except Exception as e:
                    self.logger.error(f"Error testing connection: {str(e)}")
                    return f"<div class='error-box'>Error testing connection: {str(e)}</div>"
            
            test_uncensored_btn.click(
                fn=test_uncensored_connection,
                inputs=[uncensored_url],
                outputs=[uncensored_connection_status]
            )
            
            def apply_memory_limit(limit):
                try:
                    # Validate input
                    if limit <= 0:
                        return "<div class='error-box'>Memory limit must be greater than 0.</div>"
                    
                    # Convert to integer
                    limit = int(limit)
                    
                    # Update config
                    self.agi_core.config.set("SHORT_TERM_MEMORY_LIMIT", limit)
                    
                    # Update memory limit if the memory manager has this method
                    if hasattr(self.agi_core.short_term_memory, 'set_limit'):
                        self.agi_core.short_term_memory.set_limit(limit)
                    
                    # Save config
                    self.agi_core.config.save()
                    
                    return f"<div class='success-box'>Memory limit updated to {limit} items.</div>"
                except Exception as e:
                    self.logger.error(f"Error updating memory limit: {str(e)}")
                    return f"<div class='error-box'>Error updating memory limit: {str(e)}</div>"
            
            apply_memory_limit_btn.click(
                fn=apply_memory_limit,
                inputs=[memory_limit_setting],
                outputs=[memory_settings_status]
            )
        
        
        # Launch the interface
        interface.launch(
            server_name="0.0.0.0",
            server_port=server_port,
            share=False,
            inbrowser=True
        )
    
    def _export_debug_logs(self) -> str:
        """
        Export debug logs to a file
        
        Returns:
            Status message
        """
        try:
            # Create logs directory if it doesn't exist
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = logs_dir / f"debug_logs_{timestamp}.txt"
            
            # Collect system information
            system_info = self.get_system_status()
            
            # Get logger handlers
            handlers = []
            for logger_name in ["Hohenheim", "Hohenheim.WebGUI", "Hohenheim.Core"]:
                logger = logging.getLogger(logger_name)
                handlers.extend(logger.handlers)
            
            # Collect logs from handlers
            log_content = []
            for handler in handlers:
                if isinstance(handler, logging.FileHandler):
                    try:
                        with open(handler.baseFilename, 'r') as f:
                            # Get the last 100 lines
                            lines = f.readlines()[-100:]
                            log_content.extend([f"=== Logs from {handler.baseFilename} ===\n"])
                            log_content.extend(lines)
                            log_content.append("\n\n")
                    except Exception as e:
                        log_content.append(f"Error reading log file {handler.baseFilename}: {str(e)}\n")
            
            # Write to debug log file
            with open(log_file, 'w') as f:
                f.write(f"=== Debug Logs for {system_info['system_name']} v{system_info['version']} ===\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                f.write("=== System Status ===\n")
                for key, value in system_info.items():
                    f.write(f"{key}: {value}\n")
                f.write("\n\n")
                
                f.write("=== Performance Metrics ===\n")
                perf_metrics = self.metrics.get_metrics()
                for op_name, metrics in perf_metrics.items():
                    f.write(f"{op_name}:\n")
                    for metric_name, metric_value in metrics.items():
                        f.write(f"  {metric_name}: {metric_value}\n")
                f.write("\n\n")
                
                f.write("=== Log Entries ===\n")
                f.writelines(log_content)
            
            return f"<div class='success-box'>Debug logs exported to {log_file}</div>"
        except Exception as e:
            self.logger.error(f"Error exporting debug logs: {str(e)}")
            return f"<div class='error-box'>Error exporting debug logs: {str(e)}</div>"
    
    def shutdown(self) -> None:
        """Shutdown the web GUI and cleanup resources"""
        with contextlib.suppress(Exception):
            self.active_sessions -= 1
            
            if self.active_sessions <= 0:
                self.active_sessions = 0
                self.logger.info("Shutting down web GUI")
                self.is_initialized = False
    
    def _refresh_status_html(self) -> gr.HTML:
        """
        Generate updated status HTML
        
        Returns:
            Updated HTML component
        """
        status = self.get_system_status()
        status_html = f"""
        <div style='background-color: {self.theme_manager.background_color}; padding: 20px; border-radius: 10px;'>
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
            <p>Uptime: {status.get('uptime', 'N/A')}</p>
            <p>Active sessions: {status.get('active_sessions', 0)}</p>
            <p>Updated at: {status.get('updated_at', 'N/A')}</p>
        </div>
        """
        return gr.HTML.update(value=status_html)
    
    def update_interface(self) -> None:
        """Update all interface components with the latest data"""
        if not self.is_initialized or not self.interface_components:
            return
        
        try:
            # Update chatbot
            if "chatbot" in self.interface_components:
                self.interface_components["chatbot"].update(value=self.chat_history)
            
            # Update system status
            if "status_html" in self.interface_components:
                self.interface_components["status_html"].update(value=self._refresh_status_html().value)
            
            # Update memory visualization
            if "memory_plot" in self.interface_components:
                self.interface_components["memory_plot"].update(value=self.create_memory_visualization())
            
            # Update recent memories
            if "recent_memories" in self.interface_components:
                self.interface_components["recent_memories"].update(value=self.get_recent_memories())
            
            # Update performance plot
            if "performance_plot" in self.interface_components:
                self.interface_components["performance_plot"].update(value=self.create_performance_visualization())
            
        except Exception as e:
            self.logger.error(f"Error updating interface: {str(e)}")
    
    def start_background_updater(self, update_interval: int = 30) -> None:
        """
        Start a background thread to periodically update the interface
        
        Args:
            update_interval: Time between updates in seconds
        """
        if not self.is_initialized:
            self.logger.warning("Cannot start background updater until WebGUI is initialized")
            return
        
        def updater_thread():
            self.logger.info(f"Starting background updater with interval {update_interval}s")
            while self.is_initialized:
                try:
                    self.update_interface()
                except Exception as e:
                    self.logger.error(f"Error in background updater: {str(e)}")
                
                # Sleep for the interval
                time.sleep(update_interval)
        
        # Start the thread
        thread = threading.Thread(target=updater_thread, daemon=True)
        thread.start()
        self.logger.info("Background updater started")
    
    async def export_chat_history(self, format: str = "json") -> Optional[str]:
        """
        Export chat history to a file
        
        Args:
            format: Output format ("json", "txt", "html")
            
        Returns:
            Path to the exported file or None on error
        """
        op_id = self.metrics.start_operation("export_chat_history")
        
        try:
            if not self.chat_history:
                return None
            
            # Create exports directory if it doesn't exist
            export_dir = Path("exports")
            export_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format.lower() == "json":
                # Convert to JSON format
                chat_data = [{"user": msg, "assistant": resp} for msg, resp in self.chat_history]
                export_file = export_dir / f"chat_history_{timestamp}.json"
                
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump(chat_data, f, indent=2, ensure_ascii=False)
                
            elif format.lower() == "txt":
                # Simple text format
                export_file = export_dir / f"chat_history_{timestamp}.txt"
                
                with open(export_file, 'w', encoding='utf-8') as f:
                    for i, (user_msg, assistant_resp) in enumerate(self.chat_history, 1):
                        f.write(f"--- Message Pair {i} ---\n")
                        f.write(f"User: {user_msg}\n\n")
                        f.write(f"Assistant: {assistant_resp}\n\n")
                        f.write("-" * 40 + "\n\n")
            
            elif format.lower() == "html":
                # HTML format with styling
                export_file = export_dir / f"chat_history_{timestamp}.html"
                
                with open(export_file, 'w', encoding='utf-8') as f:
                    f.write(f"""<!DOCTYPE html>
                    <html>
                    <head>
                        <title>Chat History - {timestamp}</title>
                        <meta charset="utf-8">
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                            .message-pair {{ margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 20px; }}
                            .user-message {{ background-color: #e6f7ff; padding: 10px; border-radius: 10px; margin-bottom: 10px; }}
                            .assistant-message {{ background-color: #f6f6f6; padding: 10px; border-radius: 10px; }}
                            .timestamp {{ color: #888; font-size: 0.8em; margin-top: 5px; }}
                        </style>
                    </head>
                    <body>
                        <h1>Chat History</h1>
                        <p>Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    """)
                    
                    for i, (user_msg, assistant_resp) in enumerate(self.chat_history, 1):
                        f.write(f"""
                        <div class="message-pair">
                            <h3>Message Pair {i}</h3>
                            <div class="user-message">
                                <strong>User:</strong>
                                <div>{user_msg}</div>
                            </div>
                            <div class="assistant-message">
                                <strong>Assistant:</strong>
                                <div>{assistant_resp}</div>
                            </div>
                        </div>
                        """)
                    
                    f.write("""
                    </body>
                    </html>
                    """)
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return None
            
            self.logger.info(f"Chat history exported to {export_file}")
            return str(export_file)
            
        except Exception as e:
            self.logger.error(f"Error exporting chat history: {str(e)}")
            return None
        finally:
            self.metrics.stop_operation("export_chat_history", op_id)
    
    @classmethod
    def version(cls) -> str:
        """Get the WebGUI version"""
        return "2.0.0"
    
    def __repr__(self) -> str:
        """String representation of the WebGUI instance"""
        return f"WebGUI(version={self.version()}, active_sessions={self.active_sessions}, initialized={self.is_initialized})"

            else:
                return "<div class='info-box'>Uncensored mode is now disabled. Using standard reasoning APIs.</div>"
                
        except Exception as e:
            self.logger.error(f"Error toggling uncensored mode: {str(e)}")
            return f"<div class='error-box'>Error toggling uncensored mode: {str(e)}</div>"
        finally:
            self.metrics.stop_operation("toggle_uncensored_mode", op_id)
    
    def search_memories(self, query: str) -> str:
        """
        Search for memories with enhanced formatting and error handling
        
        Args:
            query: Search query
            
        Returns:
            Formatted HTML string with search results
        """
        op_id = self.metrics.start_operation("search_memories")
        
        try:
            if not query.strip():
                return "<div class='warning-box'>Please enter a search query.</div>"
            
            # Search in long-term memory
            long_term_results = self.agi_core.long_term_memory.search(query, limit=5)
            
            # Search in short-term memory
            short_term_results = self.agi_core.short_term_memory.search(query, limit=5)
            
            output = "<h3>Search Results</h3>"
            
            if not long_term_results and not short_term_results:
                return output + "<div class='info-box'>No memories found matching your query.</div>"
            
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
                        elif "data" in memory:
                            # Format JSON data more nicely
                            formatted_data = json.dumps(memory["data"], indent=2)
                            output += f"<pre>{formatted_data}</pre>"
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
                    created_at = memory.get("created_at", "unknown time")
                    
                    # Format timestamp if it's a float or int
                    if isinstance(created_at, (float, int)):
                        created_at = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M:%S")
                    
                    output += f"<strong>{i}. {memory_type} Memory</strong> - {created_at}<br>"
                    
                    data = memory.get("data", {})
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if key not in ["timestamp", "context", "created_at"]:
                                if isinstance(value, dict) and "reasoning" in value:
                                    output += f"<strong>{key}:</strong> {value['reasoning'][:300]}..."
                                    if len(value['reasoning']) > 300:
                                        output += " <span class='more-content'>[...]</span>"
                                    output += "<br>"
                                else:
                                    # Truncate long values
                                    str_value = str(value)
                                    if len(str_value) > 300:
                                        output += f"<strong>{key}:</strong> {str_value[:300]}... <span class='more-content'>[...]</span><br>"
                                    else:
                                        output += f"<strong>{key}:</strong> {str_value}<br>"
                    else:
                        output += f"{str(data)[:300]}..."
                        if len(str(data)) > 300:
                            output += " <span class='more-content'>[...]</span>"
                    
                    output += "</div>"
                
                output += "</div>"
            
            return output
            
        except Exception as e:
            self.logger.error(f"Error searching memories: {str(e)}")
            return f"<div class='error-box'>Error searching memories: {str(e)}</div>"
        finally:
            self.metrics.stop_operation("search_memories", op_id)
    
    def start(self, server_port: int = None) -> None:
        """
        Start the web GUI with enhanced error handling and configurability
        
        Args:
            server_port: Port to run the server on (defaults to DEFAULT_PORT)
        """
        if server_port is None:
            server_port = DEFAULT_PORT
            
        self.logger.info(f"Starting web GUI on port {server_port}")
        
        # Set initialization flag
        self.is_initialized = True
        
        # Record start time
        self.start_time = time.time()
        
        # Start the AGI system if not already running
        if not self.agi_core.is_running:
            self.agi_core.start()
        
        # Create the interface
        with gr.Blocks(css=self.theme_manager.get_custom_css(), 
                       theme=gr.themes.Soft(**self.theme_manager.get_gradio_theme_params())) as interface:
            # Header with logo
            with gr.Row(elem_classes="main-header"):
                with gr.Column(scale=1):
                    if self.logo_path and os.path.exists(self.logo_path):
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
                            clear_chat_btn = gr.Button("Clear Chat")
                    
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
                            <div style='background-color: {self.theme_manager.background_color}; padding: 20px; border-radius: 10px;'>
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
                                <p>Uptime: {status.get('uptime', 'N/A')}</p>
                                <p>Active sessions: {status.get('active_sessions', 0)}</p>
                                <p>Updated at: {status.get('updated_at', 'N/A')}</p>
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
                            
                            uncensored_status = gr.HTML(
                                value="<div class='info-box'>Toggle uncensored mode to use the local LM Studio server.</div>"
                            )
                            
                            with gr.Accordion("Advanced Controls", open=False):
                                clear_st_memory_btn = gr.Button("Clear Short-Term Memory")
                                restart_system_btn = gr.Button("Restart System")
                                debug_log_btn = gr.Button("Export Debug Logs")
                
                # Performance tab
                with gr.Tab("Performance", elem_classes="tab-nav"):
                    with gr.Row():
                        gr.Markdown("### System Performance")
                        performance_plot = gr.Plot(self.create_performance_visualization())
                        refresh_perf_btn = gr.Button("Refresh Performance Data")
                    
                    with gr.Row():
                        gr.Markdown("### Resource Monitoring")
                        with gr.Column():
                            import_matplotlib = """
                            try:
                                import matplotlib.pyplot as plt
                                import psutil
                                has_monitoring = True
                            except ImportError:
                                has_monitoring = False
                            """
                            
                            exec(import_matplotlib, globals())
                            
                            if 'has_monitoring' in globals() and globals()['has_monitoring']:
                                monitoring_available = True
                            else:
                                monitoring_available = False
                            
                            if monitoring_available:
                                resource_plot = gr.Plot()
                                refresh_resource_btn = gr.Button("Refresh Resource Data")
                            else:
                                gr.HTML("<div class='warning-box'>Resource monitoring requires matplotlib and psutil packages.</div>")
                
                # Settings tab
                with gr.Tab("Settings", elem_classes="tab-nav"):
                    gr.Markdown("### Theme Settings")
                    with gr.Row():
                        theme_dropdown = gr.Dropdown(
                            choices=list(self.theme_manager.themes.keys()),
                            value="default",
                            label="Select Theme"
                        )
                        apply_theme_btn = gr.Button("Apply Theme")
                    
                    theme_status = gr.HTML(
                        value="<div class='info-box'>Choose a theme from the dropdown and click Apply.</div>"
                    )
                    
                    gr.Markdown("### API Settings")
                    
                    with gr.Row():
                        with gr.Column():
                            deepseek_api_key = gr.Textbox(
                                label="DeepSeek API Key",
                                value=self.api_key_manager.get_api_key("DEEPSEEK_API_KEY"),
                                type="password"
                            )
                            
                            deepseek_model = gr.Textbox(
                                label="DeepSeek Model",
                                value=self.agi_core.config.get("DEEPSEEK_MODEL", "deepseek-chat")
                            )
                        
                        with gr.Column():
                            claude_api_key = gr.Textbox(
                                label="Claude API Key",
                                value=self.api_key_manager.get_api_key("CLAUDE_API_KEY"),
                                type="password"
                            )
                            
                            claude_model = gr.Textbox(
                                label="Claude Model",
                                value=self.agi_core.config.get("CLAUDE_MODEL", "claude-3-7-sonnet-20250219")
                            )
                    
                    save_api_settings_btn = gr.Button("Save API Settings")
                    api_settings_status = gr.HTML(
                        value="<div class='info-box'>Enter your API keys and click Save.</div>"
                    )
                    
                    gr.Markdown("### Uncensored Mode Settings")
                    uncensored_url = gr.Textbox(
                        label="Local LM Studio URL",
                        value=self.agi_core.config.get("UNCENSORED_LOCAL_URL", "http://localhost:1234")
                    )
                    
                    test_uncensored_btn = gr.Button("Test Connection")
                    uncensored_connection_status = gr.HTML(
                        value="<div class='info-box'>Enter the URL of your local LM Studio server and click Test.</div>"
                    )
                    
                    gr.Markdown("### Memory Settings")
                    with gr.Row():
                        memory_limit_setting = gr.Number(
                            label="Short-Term Memory Limit",
                            value=self.agi_core.config.get("SHORT_TERM_MEMORY_LIMIT", MEMORY_LIMIT_DEFAULT),
                            precision=0
                        )
                        apply_memory_limit_btn = gr.Button("Apply")
                    
                    memory_settings_status = gr.HTML(
                        value="<div class='info-box'>Set the maximum number of items to keep in short-term memory.</div>"
                    )
            
            # Footer
            with gr.Row(elem_classes="footer"):
                gr.HTML(f"""
                <div class="footer">
                    {self.agi_core.name} v{self.agi_core.version} | Codename: {self.agi_core.codename} | &copy; {datetime.now().year}
                </div>
                """)
            
            # Store interface components for updates
            self.interface_components = {
                "chatbot": chatbot,
                "status_html": status_html,
                "recent_memories": recent_memories,
                "memory_plot": memory_plot,
                "search_results": search_results,
                "performance_plot": performance_plot
            }
            
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
            
            clear_chat_btn.click(
                fn=lambda: (self.clear_chat_history(), []),
                outputs=[chatbot]
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
                fn=lambda: self._refresh_status_html(),
                outputs=[status_html]
            )
            
            apply_uncensored_btn.click(
                fn=self.toggle_uncensored_mode,
                inputs=[uncensored_toggle],
                outputs=[uncensored_status]
            )
            
            clear_st_memory_btn.click(
                fn=lambda: (
                    self.agi_core.short_term_memory.clear(), 
                    "<div class='success-box'>Short-term memory cleared successfully.</div>"
                )[1],
                outputs=[uncensored_status]
            )
            
            restart_system_btn.click(
                fn=lambda: (
                    self.agi_core.stop(), 
                    self.agi_core.start(), 
                    "<div class='success-box'>System restarted successfully.</div>"
                )[2],
                outputs=[uncensored_status]
            )
