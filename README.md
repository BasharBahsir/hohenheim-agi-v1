# Hohenheim AGI System

![Hohenheim AGI](https://img.shields.io/badge/Hohenheim-AGI%20System-blue)
![Version](https://img.shields.io/badge/version-0.2.0-green)
![Codename](https://img.shields.io/badge/codename-Neo%20Jarvis-orange)
![Phase](https://img.shields.io/badge/phase-2-purple)

An evolving, modular, memory-enabled AGI system that can self-reflect, self-rewrite, and expand autonomously through OpenHands as its dev core.

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
   git clone https://github.com/BasharBahsir/hohenheim-agi-v1.git
   cd hohenheim-agi-v1
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

#### Terminal Interface

Start the AGI system with the CLI interface:

```bash
python main.py
```

#### Web Interface (New in Phase 2)

Start the AGI system with the modern web GUI:

```bash
python main.py --interface web
```

This will launch a beautiful, multi-functional web interface on port 57264. Access it at:
http://localhost:57264

#### API Interface (New in Phase 2)

Start the AGI system with the RESTful API:

```bash
python main.py --interface api
```

This will launch an API server on port 57264. Documentation available at:
http://localhost:57264/api/docs

### Additional Options

```bash
# Use a specific config file
python main.py --config path/to/config.json

# Start in uncensored mode
python main.py --uncensored

# Enable autonomous evolution capabilities
python main.py --evolution

# Set log level
python main.py --log-level DEBUG

# Specify port for web or API interface
python main.py --interface web --port 8080
```

## 💬 Commands

Once Hohenheim is running, you can interact with it using these commands:

### Basic Commands
- `help` - Display available commands
- `status` - Show system status
- `exit` - Stop the AGI system

### Memory Commands
- `remember <text>` - Store information in long-term memory
- `recall <query>` - Retrieve information from memory

### Reasoning Commands
- `think about <query>` - Use basic reasoning capabilities (DeepSeek)
- `analyze about <query>` - Use advanced reasoning capabilities (Claude)
- `reflect` or `self-reflect` - Perform system self-reflection

### Mode Commands
- `enable uncensored mode` - Switch to uncensored reasoning (local LM Studio)
- `disable uncensored mode` - Return to standard reasoning

### Evolution Commands (Phase 2)
- `analyze codebase` - Analyze the codebase for potential improvements
- `improve code <issue description>` - Generate code improvement for a specific issue
- `create component <type> <name> <description>` - Create a new component

## 🔄 Development Roadmap

### Phase 1 (Completed)
- Basic AGI skeleton
- Memory systems
- API integrations
- Command routing
- Terminal interface

### Phase 2 (Current)
- Autonomous self-evolution
- Enhanced reasoning capabilities
- Modern web GUI interface
- RESTful API interface
- Code analysis and improvement

### Phase 3 (Upcoming)
- Advanced autonomous evolution
- Multi-agent collaboration
- External tool integration
- Web browsing capabilities
- Voice interface integration

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