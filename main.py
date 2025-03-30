"""
Hohenheim AGI System - Main Entry Point
Initializes and starts the AGI system
"""

import os
import sys
import argparse
import logging
import time

from core.agi_core import HohenheimAGI
from interfaces.cli import TerminalInterface

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Hohenheim AGI System")
    
    parser.add_argument(
        "--config", "-c",
        help="Path to configuration file",
        default=None
    )
    
    parser.add_argument(
        "--interface", "-i",
        help="Interface to use (cli, web, api, telegram)",
        choices=["cli", "web", "api", "telegram"],
        default="cli"
    )
    
    parser.add_argument(
        "--port", "-p",
        help="Port for web or API interface",
        type=int,
        default=57264
    )
    
    parser.add_argument(
        "--log-level", "-l",
        help="Logging level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO"
    )
    
    parser.add_argument(
        "--uncensored", "-u",
        help="Start in uncensored mode",
        action="store_true"
    )
    
    parser.add_argument(
        "--evolution", "-e",
        help="Enable autonomous evolution",
        action="store_true"
    )
    
    return parser.parse_args()

def setup_logging(log_level):
    """Set up logging configuration"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    log_file = f"logs/hohenheim-{timestamp}.log"
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create a symlink to the latest log
    latest_log = "logs/latest.log"
    try:
        if os.path.exists(latest_log):
            os.remove(latest_log)
        os.symlink(log_file, latest_log)
    except Exception as e:
        logging.warning(f"Could not create symlink to latest log: {str(e)}")

def main():
    """Main entry point"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set up logging
    setup_logging(args.log_level)
    
    # Create AGI instance
    agi = HohenheimAGI(config_path=args.config)
    
    # Set uncensored mode if requested
    if args.uncensored:
        agi.toggle_uncensored_mode(True)
    
    # Initialize evolution agent if requested
    if args.evolution:
        try:
            from agents.evolution_agent import EvolutionAgent
            agi.evolution_agent = EvolutionAgent(agi)
            logging.info("Evolution agent initialized")
        except Exception as e:
            logging.error(f"Error initializing evolution agent: {str(e)}")
    
    # Start the appropriate interface
    if args.interface == "cli":
        interface = TerminalInterface(agi)
        interface.start()
    elif args.interface == "voice":
        try:
            from interfaces.voice_assistant import VoiceAssistant
            interface = VoiceAssistant()
            interface.run_cycle()
        except Exception as e:
            logging.error(f"Error starting voice interface: {str(e)}")
            sys.exit(1)
    elif args.interface == "web":
        try:
            from interfaces.web_gui import WebGUI
            web_gui = WebGUI(agi)
            web_gui.start(server_port=args.port)
        except ImportError as e:
            logging.error(f"Web interface dependencies missing: {str(e)}")
            print("Install required packages with: pip install gradio plotly pandas pillow")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error starting web interface: {str(e)}")
            sys.exit(1)
    elif args.interface == "api":
        try:
            from interfaces.api import APIInterface
            api = APIInterface(agi)
            api.start(port=args.port)
        except ImportError as e:
            logging.error(f"API dependencies not installed: {str(e)}")
            print(f"API dependencies not installed: {str(e)}")
            print("Install required packages with: pip install flask flask-cors")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error starting API interface: {str(e)}")
            print(f"Error starting API interface: {str(e)}")
            sys.exit(1)
    else:
        logging.error(f"Unknown interface: {args.interface}")
        print(f"Unknown interface: {args.interface}")
        sys.exit(1)

if __name__ == "__main__":
    main()