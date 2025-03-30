"""
Command Line Interface - Terminal interface for the AGI system
Provides a simple CLI for interacting with the Hohenheim AGI
"""

import os
import sys
import logging
import readline
import json
from typing import Dict, List, Any, Optional

class TerminalInterface:
    """
    Terminal interface for the Hohenheim AGI system.
    Provides a command-line interface for interacting with the AGI.
    """
    
    def __init__(self, agi_core):
        """
        Initialize the terminal interface
        
        Args:
            agi_core: Reference to the main AGI core instance
        """
        self.agi_core = agi_core
        self.logger = logging.getLogger("Hohenheim.TerminalInterface")
        
        # Get configuration
        self.prompt = self.agi_core.config.get("CLI_PROMPT", "Hohenheim> ")
        self.history_file = os.path.expanduser("~/.hohenheim_history")
        
        # Set up command history
        self._setup_history()
        
        # Running flag
        self.running = False
    
    def _setup_history(self) -> None:
        """Set up command history"""
        try:
            # Set up readline history
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)
            
            # Set history length
            readline.set_history_length(1000)
            
        except Exception as e:
            self.logger.warning(f"Could not set up command history: {str(e)}")
    
    def _save_history(self) -> None:
        """Save command history"""
        try:
            readline.write_history_file(self.history_file)
        except Exception as e:
            self.logger.warning(f"Could not save command history: {str(e)}")
    
    def start(self) -> None:
        """Start the terminal interface"""
        self.running = True
        self.agi_core.start()
        
        self.logger.info("Terminal interface started")
        
        # Print welcome message
        self._print_welcome()
        
        # Main loop
        while self.running:
            try:
                # Get user input
                user_input = input(self.prompt)
                
                # Skip empty input
                if not user_input.strip():
                    continue
                
                # Process the command
                response = self.agi_core.process_command(user_input)
                
                # Display the response
                self._display_response(response)
                
                # Check if we should exit
                if user_input.lower() in ["exit", "quit", "stop"]:
                    self.running = False
                
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except EOFError:
                print("\nExiting...")
                self.running = False
            except Exception as e:
                self.logger.error(f"Error in terminal interface: {str(e)}")
                print(f"Error: {str(e)}")
        
        # Save history and clean up
        self._save_history()
        self.agi_core.stop()
        self.logger.info("Terminal interface stopped")
    
    def _print_welcome(self) -> None:
        """Print welcome message"""
        print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██╗  ██╗ ██████╗ ██╗  ██╗███████╗███╗   ██╗██╗  ██╗███████╗ ║
║   ██║  ██║██╔═══██╗██║  ██║██╔════╝████╗  ██║██║  ██║██╔════╝ ║
║   ███████║██║   ██║███████║█████╗  ██╔██╗ ██║███████║█████╗   ║
║   ██╔══██║██║   ██║██╔══██║██╔══╝  ██║╚██╗██║██╔══██║██╔══╝   ║
║   ██║  ██║╚██████╔╝██║  ██║███████╗██║ ╚████║██║  ██║███████╗ ║
║   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝ ║
║                                                               ║
╠═══════════════════════════════════════════════════════════════╣
║  {self.agi_core.name} AGI System v{self.agi_core.version}                                ║
║  Codename: {self.agi_core.codename}                                      ║
║                                                               ║
║  Type 'help' for available commands                           ║
║  Type 'exit' to quit                                          ║
╚═══════════════════════════════════════════════════════════════╝
""")
    
    def _display_response(self, response: Dict[str, Any]) -> None:
        """
        Display a response from the AGI
        
        Args:
            response: Response dictionary from the AGI
        """
        if "error" in response:
            print(f"Error: {response['error']}")
            return
        
        if "message" in response:
            print(f"\n{response['message']}")
        
        # Display commands list
        if "commands" in response:
            print("\nAvailable commands:")
            for cmd in response["commands"]:
                print(f"  {cmd['command']:<30} - {cmd['description']}")
        
        # Display memories
        if "memories" in response:
            print("\nMemories:")
            for i, memory in enumerate(response["memories"], 1):
                if isinstance(memory, dict):
                    if "content" in memory:
                        print(f"\n{i}. {memory['content']}")
                    elif "data" in memory:
                        print(f"\n{i}. {json.dumps(memory['data'], indent=2)}")
                else:
                    print(f"\n{i}. {memory}")
        
        # Display reasoning
        if "reasoning" in response:
            print(f"\nReasoning:\n{response['reasoning']}")
            if "source" in response:
                print(f"\nSource: {response['source']}")
        
        print()  # Add a blank line for readability