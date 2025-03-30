"""
Hohenheim AGI System - Main Entry Point
Initializes and starts the AGI system
"""

import os
import sys
import argparse
import logging

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
        help="Interface to use (cli, gui, api)",
        choices=["cli", "gui", "api"],
        default="cli"
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
    
    return parser.parse_args()

def setup_logging(log_level):
    """Set up logging configuration"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/hohenheim.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

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
    
    # Start the appropriate interface
    if args.interface == "cli":
        interface = TerminalInterface(agi)
        interface.start()
    elif args.interface == "gui":
        # GUI interface not implemented yet
        logging.error("GUI interface not implemented yet")
        print("GUI interface not implemented yet. Use --interface=cli instead.")
        sys.exit(1)
    elif args.interface == "api":
        # API interface not implemented yet
        logging.error("API interface not implemented yet")
        print("API interface not implemented yet. Use --interface=cli instead.")
        sys.exit(1)
    else:
        logging.error(f"Unknown interface: {args.interface}")
        print(f"Unknown interface: {args.interface}")
        sys.exit(1)

if __name__ == "__main__":
    main()