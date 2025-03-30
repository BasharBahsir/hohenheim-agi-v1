# Hohenheim AGI System

![Hohenheim AGI](https://img.shields.io/badge/Hohenheim-AGI%20System-blue)
![Version](https://img.shields.io/badge/version-0.1.0-green)
![Codename](https://img.shields.io/badge/codename-Neo%20Jarvis-orange)

An evolving, modular, memory-enabled AGI system that can self-reflect, self-rewrite, and expand autonomously.

## 🧪 Project Vision

Hohenheim is an autonomous AGI system designed to think, reason, evolve, and self-develop like a digital super-intelligence. It is proactive, adaptive, and continuously enhances itself via:

- Autonomous code editing
- Memory expansion
- Internal reasoning capabilities

OpenHands serves as its internal dev brain. Eventually, Hohenheim should be able to operate without human input.

## 🌌 Core Capabilities

- **Autonomous Evolution**: Self-improvement via OpenHands & reasoning loops
- **Multi-memory System**: Short-term (RAM-like) & persistent long-term vector DB
- **Uncensored Mode**: Via local Qwen-14B for unrestricted reasoning
- **Jarvis-like Personality**: Smart, sarcastic, loyal assistant
- **Multiple Interfaces**: Terminal / GUI / Voice (CLI implemented in Phase 1)
- **Modular Architecture**: Plugin-based system for extensibility
- **Advanced Reasoning**: Via DeepSeek-R1 + Sonnet-3.7 APIs

## 📂 System Architecture

```
Hohenheim_AGI_system/
├── core/               # AGI building blocks
│   ├── agi_core.py     # Main AGI class
│   ├── api_manager.py  # API integrations
│   └── command_router.py # Command processing
├── memory/             # Memory systems
│   ├── short_term.py   # RAM-like memory
│   └── long_term.py    # Vector DB (Chroma/FAISS)
├── agents/             # Autonomous micro-agents
│   └── uncensored_agent.py # Qwen-14B integration
├── interfaces/         # User interfaces
│   └── cli.py          # Terminal interface
├── config/             # Configuration
│   └── config_manager.py # Config system
├── main.py             # Entry point
├── requirements.txt    # Dependencies
└── .env.example        # Environment variables template
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/BasharBahsir/Hohenheim_AGI_system.git
   cd Hohenheim_AGI_system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

### Running Hohenheim

Start the AGI system with the CLI interface:

```bash
python main.py
```

Additional options:
```bash
# Use a specific config file
python main.py --config path/to/config.json

# Start in uncensored mode
python main.py --uncensored

# Set log level
python main.py --log-level DEBUG
```

## 💬 CLI Commands

Once Hohenheim is running, you can interact with it using these commands:

- `help` - Display available commands
- `status` - Show system status
- `remember <text>` - Store information in long-term memory
- `recall <query>` - Retrieve information from memory
- `think about <query>` - Use reasoning capabilities
- `enable uncensored mode` - Switch to uncensored reasoning
- `disable uncensored mode` - Return to standard reasoning
- `exit` - Stop the AGI system

## 🔄 Development Roadmap

### Phase 1 (Current)
- Basic AGI skeleton
- Memory systems
- API integrations
- Command routing
- Terminal interface

### Phase 2 (Upcoming)
- Autonomous self-rewrites
- Enhanced reasoning capabilities
- GUI interface
- Voice interface
- Plugin system

### Phase 3 (Future)
- Advanced autonomous evolution
- Multi-agent collaboration
- External tool integration
- Web browsing capabilities
- Advanced self-reflection

## 🔧 Configuration

Hohenheim supports configuration via:
- Environment variables
- .env file
- JSON/YAML config files

See `.env.example` for available configuration options.

## 📚 API Integrations

Hohenheim uses these external APIs for reasoning:
- DeepSeek-R1 - Complex reasoning tasks
- Sonnet-3.7 - General reasoning and conversation

For uncensored mode, it uses a local Qwen-14B model.

## 🧠 Memory Systems

### Short-Term Memory
- RAM-based storage
- Stores recent interactions and context
- Organized by memory type
- Chronological timeline

### Long-Term Memory
- Vector database (Chroma or FAISS)
- Semantic search capabilities
- Persistent storage
- Metadata and importance tracking

## 🔒 License

This project is proprietary and confidential.

## 🙏 Acknowledgments

- OpenHands - Internal development agent
- DeepSeek and Sonnet - API providers
- Qwen - Local model provider