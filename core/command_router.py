"""
Command Router - Routes and processes commands for the AGI system
Handles command parsing, routing, and execution
"""

import re
import logging
from typing import Dict, List, Any, Optional, Callable

class CommandRouter:
    """
    Routes and processes commands for the Hohenheim AGI system.
    Handles command parsing, routing to appropriate handlers, and response formatting.
    """
    
    def __init__(self, agi_core):
        """
        Initialize the Command Router
        
        Args:
            agi_core: Reference to the main AGI core instance
        """
        self.agi_core = agi_core
        self.logger = logging.getLogger("Hohenheim.CommandRouter")
        
        # Command registry - maps command patterns to handler functions
        self.command_registry = {}
        
        # Register built-in commands
        self._register_built_in_commands()
    
    def _register_built_in_commands(self) -> None:
        """Register the built-in system commands"""
        # System commands
        self.register_command(
            r"^(help|commands)$", 
            self._handle_help_command,
            "Display available commands"
        )
        
        self.register_command(
            r"^(exit|quit|stop)$", 
            self._handle_exit_command,
            "Stop the AGI system"
        )
        
        self.register_command(
            r"^status$", 
            self._handle_status_command,
            "Show system status"
        )
        
        # Memory commands
        self.register_command(
            r"^remember\s+(.+)$", 
            self._handle_remember_command,
            "Store information in long-term memory"
        )
        
        self.register_command(
            r"^recall\s+(.+)$", 
            self._handle_recall_command,
            "Retrieve information from memory"
        )
        
        # Reasoning commands
        self.register_command(
            r"^(think|reason)\s+about\s+(.+)$", 
            self._handle_reasoning_command,
            "Use reasoning capabilities to think about a topic"
        )
        
        # Uncensored mode commands
        self.register_command(
            r"^(enable|activate)\s+uncensored(\s+mode)?$", 
            lambda match, context: self._handle_uncensored_mode_command(match, context, True),
            "Enable uncensored mode using local Qwen-14B"
        )
        
        self.register_command(
            r"^(disable|deactivate)\s+uncensored(\s+mode)?$", 
            lambda match, context: self._handle_uncensored_mode_command(match, context, False),
            "Disable uncensored mode"
        )
    
    def register_command(self, pattern: str, handler: Callable, description: str = "") -> None:
        """
        Register a new command pattern and handler
        
        Args:
            pattern: Regex pattern to match the command
            handler: Function to handle the command
            description: Description of the command
        """
        self.command_registry[pattern] = {
            "handler": handler,
            "description": description
        }
        self.logger.debug(f"Registered command pattern: {pattern}")
    
    def route_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route a command to the appropriate handler
        
        Args:
            command: The command string to process
            context: Additional context for the command
            
        Returns:
            Response dictionary with results
        """
        if not context:
            context = {}
        
        # Check each registered command pattern
        for pattern, command_info in self.command_registry.items():
            match = re.match(pattern, command, re.IGNORECASE)
            if match:
                self.logger.info(f"Command matched pattern: {pattern}")
                try:
                    return command_info["handler"](match, context)
                except Exception as e:
                    self.logger.error(f"Error handling command '{command}': {str(e)}")
                    return {
                        "error": f"Error processing command: {str(e)}",
                        "success": False
                    }
        
        # If no command matched, use reasoning to interpret the input
        self.logger.info(f"No command pattern matched, treating as conversation: {command}")
        return self._handle_conversation(command, context)
    
    def _handle_help_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the help command"""
        commands_list = []
        
        for pattern, command_info in self.command_registry.items():
            # Clean up the pattern for display
            display_pattern = pattern.replace(r"^", "").replace(r"$", "")
            display_pattern = re.sub(r"\((.+?)\)", r"[\1]", display_pattern)
            display_pattern = re.sub(r"\\\s+", " ", display_pattern)
            display_pattern = re.sub(r"\s+\(\.\+\)", " <text>", display_pattern)
            
            commands_list.append({
                "command": display_pattern,
                "description": command_info["description"]
            })
        
        return {
            "message": "Available commands:",
            "commands": commands_list,
            "success": True
        }
    
    def _handle_exit_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the exit command"""
        self.agi_core.stop()
        return {
            "message": f"{self.agi_core.name} AGI System is shutting down.",
            "success": True
        }
    
    def _handle_status_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the status command"""
        memory_stats = {
            "short_term": self.agi_core.short_term_memory.get_stats(),
            "long_term": self.agi_core.long_term_memory.get_stats()
        }
        
        return {
            "message": f"{self.agi_core.name} AGI System Status",
            "version": self.agi_core.version,
            "codename": self.agi_core.codename,
            "running": self.agi_core.is_running,
            "uncensored_mode": self.agi_core.uncensored_mode,
            "memory_stats": memory_stats,
            "success": True
        }
    
    def _handle_remember_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the remember command"""
        memory_text = match.group(1)
        
        # Store in long-term memory
        memory_id = self.agi_core.long_term_memory.add(
            "User Memory", 
            memory_text, 
            metadata={"type": "user_memory", "importance": 0.8}
        )
        
        return {
            "message": "I'll remember that.",
            "memory_id": memory_id,
            "success": True
        }
    
    def _handle_recall_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the recall command"""
        query = match.group(1)
        
        # Search long-term memory
        memories = self.agi_core.long_term_memory.search(query, limit=5)
        
        if memories:
            return {
                "message": "Here's what I remember:",
                "memories": memories,
                "success": True
            }
        else:
            return {
                "message": "I don't have any memories related to that.",
                "memories": [],
                "success": True
            }
    
    def _handle_reasoning_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the reasoning command"""
        query = match.group(2)
        
        # Use the reasoning capability
        reasoning_result = self.agi_core.reason(query, context)
        
        return {
            "message": "Here's my reasoning:",
            "reasoning": reasoning_result.get("reasoning", ""),
            "source": reasoning_result.get("source", "unknown"),
            "success": True
        }
    
    def _handle_uncensored_mode_command(self, match, context: Dict[str, Any], enable: bool) -> Dict[str, Any]:
        """Handle the uncensored mode command"""
        current_state = self.agi_core.toggle_uncensored_mode(enable)
        
        if current_state:
            return {
                "message": "Uncensored mode is now enabled. Using local Qwen-14B for unrestricted reasoning.",
                "uncensored_mode": True,
                "success": True
            }
        else:
            return {
                "message": "Uncensored mode is now disabled. Using standard reasoning APIs.",
                "uncensored_mode": False,
                "success": True
            }
    
    def _handle_conversation(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle conversational input (not matching any command)
        
        Args:
            text: The input text
            context: Conversation context
            
        Returns:
            Response dictionary
        """
        # Use reasoning to generate a response
        reasoning_result = self.agi_core.reason(text, context)
        
        return {
            "message": reasoning_result.get("reasoning", "I'm not sure how to respond to that."),
            "type": "conversation",
            "success": True
        }