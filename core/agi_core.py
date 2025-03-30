"""
AGI Core Class - The central brain of the Hohenheim system
Manages all subsystems, memory, reasoning, and autonomous evolution
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional

# Internal imports
from core.api_manager import APIManager
from core.command_router import CommandRouter
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from config.config_manager import ConfigManager

class HohenheimAGI:
    """
    The main AGI class that orchestrates all components of the Hohenheim system.
    Acts as the central coordinator for memory, reasoning, and autonomous actions.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Hohenheim AGI system with all its components
        
        Args:
            config_path: Path to the configuration file
        """
        self.name = "Hohenheim"
        self.version = "0.1.0"
        self.codename = "Neo Jarvis"
        
        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        self.logger = logging.getLogger("Hohenheim")
        self.logger.info(f"Initializing {self.name} AGI System v{self.version} ({self.codename})")
        
        # Load configuration
        self.config = ConfigManager(config_path)
        self.logger.info("Configuration loaded")
        
        # Initialize API connections
        self.api_manager = APIManager(self.config)
        self.logger.info("API connections established")
        
        # Initialize memory systems
        self.short_term_memory = ShortTermMemory(self.config)
        self.long_term_memory = LongTermMemory(self.config)
        self.logger.info("Memory systems initialized")
        
        # Initialize command router
        self.command_router = CommandRouter(self)
        self.logger.info("Command router initialized")
        
        # Uncensored mode flag
        self.uncensored_mode = False
        
        # System state
        self.is_running = False
        self.current_context = {}
        
        self.logger.info(f"{self.name} AGI System initialization complete")
    
    def start(self) -> None:
        """Start the AGI system and all its components"""
        self.is_running = True
        self.logger.info(f"{self.name} AGI System started")
        
        # Record system start in memory
        self.short_term_memory.add("system_event", {
            "type": "system_start",
            "timestamp": self.short_term_memory.get_timestamp(),
            "version": self.version
        })
    
    def stop(self) -> None:
        """Stop the AGI system and all its components"""
        self.is_running = False
        self.logger.info(f"{self.name} AGI System stopped")
        
        # Record system stop in memory
        self.short_term_memory.add("system_event", {
            "type": "system_stop",
            "timestamp": self.short_term_memory.get_timestamp(),
            "version": self.version
        })
    
    def process_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a command through the command router
        
        Args:
            command: The command string to process
            context: Additional context for the command
            
        Returns:
            Response dictionary with results
        """
        if not self.is_running:
            return {"error": "System is not running"}
        
        # Update current context
        if context:
            self.current_context.update(context)
        
        # Record command in short-term memory
        self.short_term_memory.add("command", {
            "input": command,
            "timestamp": self.short_term_memory.get_timestamp(),
            "context": self.current_context
        })
        
        # Route the command
        response = self.command_router.route_command(command, self.current_context)
        
        # Record response in short-term memory
        self.short_term_memory.add("response", {
            "command": command,
            "response": response,
            "timestamp": self.short_term_memory.get_timestamp()
        })
        
        return response
    
    def toggle_uncensored_mode(self, enable: bool = None) -> bool:
        """
        Toggle or set the uncensored mode
        
        Args:
            enable: If provided, set to this value, otherwise toggle
            
        Returns:
            Current state of uncensored mode
        """
        if enable is not None:
            self.uncensored_mode = enable
        else:
            self.uncensored_mode = not self.uncensored_mode
            
        self.logger.info(f"Uncensored mode {'enabled' if self.uncensored_mode else 'disabled'}")
        
        # Record mode change in memory
        self.short_term_memory.add("system_event", {
            "type": "mode_change",
            "mode": "uncensored",
            "value": self.uncensored_mode,
            "timestamp": self.short_term_memory.get_timestamp()
        })
        
        return self.uncensored_mode
    
    def reason(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Use the reasoning capabilities to think about a query
        
        Args:
            query: The question or problem to reason about
            context: Additional context for reasoning
            
        Returns:
            Reasoning results
        """
        # Combine current context with provided context
        reasoning_context = self.current_context.copy()
        if context:
            reasoning_context.update(context)
        
        # Get relevant memories
        relevant_memories = self.long_term_memory.search(query, limit=5)
        reasoning_context["relevant_memories"] = relevant_memories
        
        # Use API for reasoning
        if self.uncensored_mode:
            # Use local Qwen model for uncensored reasoning
            from agents.uncensored_agent import get_uncensored_reasoning
            result = get_uncensored_reasoning(query, reasoning_context)
        else:
            # Use DeepSeek-R1 or Sonnet for reasoning
            result = self.api_manager.get_reasoning(query, reasoning_context)
        
        # Store reasoning in memory
        self.short_term_memory.add("reasoning", {
            "query": query,
            "result": result,
            "context": reasoning_context,
            "timestamp": self.short_term_memory.get_timestamp()
        })
        
        # Store important reasoning in long-term memory
        if result.get("importance", 0) > 0.7:
            self.long_term_memory.add(
                query, 
                result.get("reasoning", ""), 
                metadata={"type": "reasoning", "importance": result.get("importance", 0)}
            )
        
        return result
    
    def self_reflect(self) -> Dict[str, Any]:
        """
        Perform self-reflection to improve system performance
        
        Returns:
            Results of self-reflection
        """
        # Get recent memories
        recent_memories = self.short_term_memory.get_recent(limit=20)
        
        # Perform reflection using API
        reflection_prompt = "Analyze recent system performance and identify areas for improvement"
        reflection = self.api_manager.get_reasoning(reflection_prompt, {"recent_memories": recent_memories})
        
        # Store reflection in memory
        self.short_term_memory.add("reflection", {
            "reflection": reflection,
            "timestamp": self.short_term_memory.get_timestamp()
        })
        
        # Store important reflections in long-term memory
        self.long_term_memory.add(
            "System Self-Reflection", 
            reflection.get("reasoning", ""), 
            metadata={"type": "reflection", "importance": 0.9}
        )
        
        return reflection