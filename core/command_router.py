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
        
        self.register_command(
            r"^(analyze|advanced\s+think|deep\s+think)\s+about\s+(.+)$", 
            self._handle_advanced_reasoning_command,
            "Use advanced reasoning (Claude Sonnet) for complex analysis"
        )
        
        # Self-reflection command
        self.register_command(
            r"^(reflect|self[\s-]reflect)$", 
            self._handle_self_reflection_command,
            "Perform system self-reflection to identify improvements"
        )
        
        # Uncensored mode commands
        self.register_command(
            r"^(enable|activate)\s+uncensored(\s+mode)?$", 
            lambda match, context: self._handle_uncensored_mode_command(match, context, True),
            "Enable uncensored mode using local LM Studio server"
        )
        
        self.register_command(
            r"^(disable|deactivate)\s+uncensored(\s+mode)?$", 
            lambda match, context: self._handle_uncensored_mode_command(match, context, False),
            "Disable uncensored mode"
        )
        
        # Evolution commands (if evolution agent is available)
        self.register_command(
            r"^analyze\s+codebase$", 
            self._handle_analyze_codebase_command,
            "Analyze the codebase for potential improvements"
        )
        
        self.register_command(
            r"^improve\s+code\s+(.+)$", 
            self._handle_improve_code_command,
            "Generate code improvement for a specific issue"
        )
        
        self.register_command(
            r"^create\s+component\s+(\w+)\s+(\w+)\s+(.+)$", 
            self._handle_create_component_command,
            "Create a new component (e.g., 'create component agent MyAgent description')"
        )
        
        # Self-evolution commands
        self.register_command(
            r"^start\s+evolution$",
            self._handle_start_evolution_command,
            "Start the self-evolution process"
        )
        
        self.register_command(
            r"^evaluate\s+performance$",
            self._handle_evaluate_performance_command,
            "Evaluate the system's performance"
        )
        
        self.register_command(
            r"^approve\s+evolution\s+(\d{8}-\d{6})$",
            self._handle_approve_evolution_command,
            "Approve a pending evolution (e.g., 'approve evolution 20250330-123456')"
        )
        
        self.register_command(
            r"^evolution\s+status$",
            self._handle_evolution_status_command,
            "Check the status of the self-evolution process"
        )
        
        self.register_command(
            r"^evolution\s+config(?:\s+(.+))?$",
            self._handle_evolution_config_command,
            "Get or update the evolution configuration"
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
    
    def _handle_advanced_reasoning_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the advanced reasoning command"""
        query = match.group(2)
        
        # Use the advanced reasoning capability (Claude Sonnet)
        reasoning_result = self.agi_core.advanced_reason(query, context)
        
        return {
            "message": "Here's my advanced analysis:",
            "reasoning": reasoning_result.get("reasoning", ""),
            "source": reasoning_result.get("source", "unknown"),
            "success": True
        }
    
    def _handle_self_reflection_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the self-reflection command"""
        # Perform self-reflection
        reflection_result = self.agi_core.self_reflect()
        
        return {
            "message": "Self-reflection results:",
            "reasoning": reflection_result.get("reasoning", ""),
            "source": reflection_result.get("source", "unknown"),
            "success": True
        }
    
    def _handle_uncensored_mode_command(self, match, context: Dict[str, Any], enable: bool) -> Dict[str, Any]:
        """Handle the uncensored mode command"""
        # Check if local server is available before enabling
        if enable:
            from agents.uncensored_agent import check_local_server_status
            server_available = check_local_server_status()
            
            if not server_available:
                return {
                    "message": "Cannot enable uncensored mode. Local LM Studio server is not available at the configured URL.",
                    "uncensored_mode": False,
                    "success": False
                }
        
        current_state = self.agi_core.toggle_uncensored_mode(enable)
        
        if current_state:
            return {
                "message": "Uncensored mode is now enabled. Using local LM Studio server for unrestricted reasoning.",
                "uncensored_mode": True,
                "success": True
            }
        else:
            return {
                "message": "Uncensored mode is now disabled. Using standard reasoning APIs.",
                "uncensored_mode": False,
                "success": True
            }
    
    def _handle_analyze_codebase_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the analyze codebase command"""
        # Check if evolution agent is available
        if not hasattr(self.agi_core, 'evolution_agent') or self.agi_core.evolution_agent is None:
            return {
                "message": "Evolution agent is not initialized. Please start the system with --evolution flag.",
                "success": False
            }
        
        # Analyze the codebase
        analysis = self.agi_core.evolution_agent.analyze_codebase()
        
        # Format the response
        response = {
            "message": "Codebase Analysis Results:",
            "analysis": {
                "total_files": analysis.get("total_files", 0),
                "total_lines": analysis.get("total_lines", 0),
                "total_functions": analysis.get("total_functions", 0),
                "total_classes": analysis.get("total_classes", 0)
            },
            "improvement_suggestions": analysis.get("improvement_suggestions", ""),
            "success": True
        }
        
        return response
    
    def _handle_improve_code_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the improve code command"""
        # Check if evolution agent is available
        if not hasattr(self.agi_core, 'evolution_agent') or self.agi_core.evolution_agent is None:
            return {
                "message": "Evolution agent is not initialized. Please start the system with --evolution flag.",
                "success": False
            }
        
        # Get the issue description
        issue_description = match.group(1)
        
        # Ask for the file path
        if "file_path" not in context:
            return {
                "message": "Please specify the file path to improve.",
                "success": False,
                "needs_file_path": True
            }
        
        file_path = context["file_path"]
        
        # Generate the improvement
        improvement = self.agi_core.evolution_agent.generate_code_improvement(file_path, issue_description)
        
        if not improvement.get("success", False):
            return {
                "message": f"Failed to generate improvement: {improvement.get('error', 'Unknown error')}",
                "success": False
            }
        
        # Ask if the user wants to apply the improvement
        if "apply_improvement" not in context:
            return {
                "message": "Generated code improvement:",
                "original_content": improvement.get("original_content", ""),
                "improved_content": improvement.get("improved_content", ""),
                "reasoning": improvement.get("reasoning", ""),
                "success": True,
                "needs_confirmation": True
            }
        
        # Apply the improvement if requested
        if context["apply_improvement"]:
            result = self.agi_core.evolution_agent.apply_improvement(improvement)
            
            if result.get("success", False):
                return {
                    "message": f"Successfully applied improvement to {file_path}",
                    "backup_path": result.get("backup_path"),
                    "success": True
                }
            else:
                return {
                    "message": f"Failed to apply improvement: {result.get('error', 'Unknown error')}",
                    "success": False
                }
        else:
            return {
                "message": "Improvement not applied.",
                "success": True
            }
    
    def _handle_create_component_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the create component command"""
        # Check if evolution agent is available
        if not hasattr(self.agi_core, 'evolution_agent') or self.agi_core.evolution_agent is None:
            return {
                "message": "Evolution agent is not initialized. Please start the system with --evolution flag.",
                "success": False
            }
        
        # Get the component details
        component_type = match.group(1)
        component_name = match.group(2)
        description = match.group(3)
        
        # Generate the component
        result = self.agi_core.evolution_agent.generate_new_component(component_type, component_name, description)
        
        if not result.get("success", False):
            return {
                "message": f"Failed to create component: {result.get('error', 'Unknown error')}",
                "success": False
            }
        
        return {
            "message": f"Successfully created new {component_type} component: {component_name}",
            "file_path": result.get("file_path"),
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
        # Check for natural language evolution triggers if self-evolution is available
        if hasattr(self.agi_core, 'self_evolution') and self.agi_core.self_evolution is not None:
            trigger_result = self.agi_core.self_evolution.process_natural_language_trigger(text)
            if trigger_result.get("success", False):
                return {
                    "message": f"Evolution trigger detected: {trigger_result.get('message', '')}",
                    "status": trigger_result.get("status"),
                    "timestamp": trigger_result.get("timestamp"),
                    "success": True
                }
        
        # Use reasoning to generate a response
        reasoning_result = self.agi_core.reason(text, context)
        
        return {
            "message": reasoning_result.get("reasoning", "I'm not sure how to respond to that."),
            "type": "conversation",
            "success": True
        }
    def _handle_start_evolution_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the start evolution command"""
        # Check if self-evolution framework is available
        if not hasattr(self.agi_core, 'self_evolution') or self.agi_core.self_evolution is None:
            return {
                "message": "Self-evolution framework is not initialized. Please start the system with --evolution flag.",
                "success": False
            }
        
        # Start the evolution process
        result = self.agi_core.self_evolution.start_evolution_process()
        
        if result.get("success", False):
            return {
                "message": f"Self-evolution process started. {result.get('message', '')}",
                "status": result.get("status"),
                "timestamp": result.get("timestamp"),
                "success": True
            }
        else:
            return {
                "message": f"Failed to start self-evolution: {result.get('message', 'Unknown error')}",
                "success": False
            }
    
    def _handle_evaluate_performance_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the evaluate performance command"""
        # Check if self-evolution framework is available
        if not hasattr(self.agi_core, 'self_evolution') or self.agi_core.self_evolution is None:
            return {
                "message": "Self-evolution framework is not initialized. Please start the system with --evolution flag.",
                "success": False
            }
        
        # Evaluate performance
        metrics = self.agi_core.self_evolution.evaluate_performance()
        
        return {
            "message": "Performance evaluation completed",
            "metrics": metrics,
            "success": True
        }
    
    def _handle_approve_evolution_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the approve evolution command"""
        # Check if self-evolution framework is available
        if not hasattr(self.agi_core, 'self_evolution') or self.agi_core.self_evolution is None:
            return {
                "message": "Self-evolution framework is not initialized. Please start the system with --evolution flag.",
                "success": False
            }
        
        # Get the timestamp
        timestamp = match.group(1)
        
        # Approve the evolution
        result = self.agi_core.self_evolution.approve_evolution(timestamp)
        
        if result.get("success", False):
            return {
                "message": f"Evolution approved and applied: {result.get('message', '')}",
                "applied_files": result.get("applied_files", []),
                "success": True
            }
        else:
            return {
                "message": f"Failed to approve evolution: {result.get('message', 'Unknown error')}",
                "success": False
            }
    
    def _handle_evolution_status_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the evolution status command"""
        # Check if self-evolution framework is available
        if not hasattr(self.agi_core, 'self_evolution') or self.agi_core.self_evolution is None:
            return {
                "message": "Self-evolution framework is not initialized. Please start the system with --evolution flag.",
                "success": False
            }
        
        # Get evolution status
        is_evolving = self.agi_core.self_evolution.is_evolving
        last_evolution_time = self.agi_core.self_evolution.last_evolution_time
        
        if last_evolution_time:
            import datetime
            last_time_str = datetime.datetime.fromtimestamp(last_evolution_time).strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_time_str = "Never"
        
        # Get evolution history
        history = self.agi_core.self_evolution.get_evolution_history()
        
        return {
            "message": f"Evolution Status: {'Running' if is_evolving else 'Idle'}",
            "is_evolving": is_evolving,
            "last_evolution_time": last_time_str,
            "evolution_count": len(history),
            "success": True
        }
    
    def _handle_evolution_config_command(self, match, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the evolution config command"""
        # Check if self-evolution framework is available
        if not hasattr(self.agi_core, 'self_evolution') or self.agi_core.self_evolution is None:
            return {
                "message": "Self-evolution framework is not initialized. Please start the system with --evolution flag.",
                "success": False
            }
        
        # Check if we're updating or just getting the config
        config_str = match.group(1)
        
        if config_str:
            # Parse the config string
            try:
                import json
                new_config = json.loads(config_str)
                
                # Update the config
                updated_config = self.agi_core.self_evolution.update_config(new_config)
                
                return {
                    "message": "Evolution configuration updated",
                    "config": updated_config,
                    "success": True
                }
            except Exception as e:
                return {
                    "message": f"Error updating evolution configuration: {str(e)}",
                    "success": False
                }
        else:
            # Just get the current config
            config = self.agi_core.self_evolution.get_config()
            
            # Convert enum to string for display
            if "trigger_type" in config and hasattr(config["trigger_type"], "value"):
                config_display = config.copy()
                config_display["trigger_type"] = config["trigger_type"].value
            else:
                config_display = config
            
            return {
                "message": "Current evolution configuration",
                "config": config_display,
                "success": True
            }
