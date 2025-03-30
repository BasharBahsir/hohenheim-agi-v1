# Hohenheim AGI System - Architecture Documentation

## System Overview

Hohenheim is an autonomous AGI system designed to think, reason, evolve, and self-develop. The system is built with a modular architecture that allows for extensibility and autonomous evolution.

## Core Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Hohenheim AGI Core                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │ API Manager │◄───┤ AGI Core    │───►│ Command Router  │  │
│  └─────────────┘    └─────────────┘    └─────────────────┘  │
│         ▲                  ▲ ▲                  ▲           │
│         │                  │ │                  │           │
│         ▼                  │ │                  ▼           │
│  ┌─────────────┐           │ │           ┌─────────────┐    │
│  │ Reasoning   │◄──────────┘ └──────────►│ Interfaces  │    │
│  │ Engines     │                         │ (CLI/GUI)   │    │
│  └─────────────┘                         └─────────────┘    │
│         ▲                                      ▲           │
│         │                                      │           │
│         ▼                                      ▼           │
│  ┌─────────────┐                        ┌─────────────┐    │
│  │ Memory      │◄──────────────────────►│ Agents      │    │
│  │ Systems     │                        │             │    │
│  └─────────────┘                        └─────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **AGI Core** (`core/agi_core.py`)
   - Central coordinator for all subsystems
   - Manages system state and lifecycle
   - Orchestrates memory, reasoning, and command processing

2. **API Manager** (`core/api_manager.py`)
   - Handles external API integrations
   - Manages DeepSeek-R1 and Sonnet-3.7 APIs
   - Handles authentication, rate limiting, and fallbacks

3. **Command Router** (`core/command_router.py`)
   - Parses and routes user commands
   - Maps command patterns to handler functions
   - Processes conversational inputs

4. **Memory Systems**
   - **Short-Term Memory** (`memory/short_term.py`)
     - RAM-like storage for recent interactions
     - Organized by memory type with chronological timeline
   - **Long-Term Memory** (`memory/long_term.py`)
     - Vector database for persistent storage
     - Semantic search capabilities
     - Supports Chroma or FAISS backends

5. **Agents**
   - **Uncensored Agent** (`agents/uncensored_agent.py`)
     - Provides unrestricted reasoning via local Qwen-14B
     - Handles model loading and inference

6. **Interfaces**
   - **Terminal Interface** (`interfaces/cli.py`)
     - Command-line interface for user interaction
     - Handles input/output formatting

7. **Configuration** (`config/config_manager.py`)
   - Manages system configuration
   - Supports .env, JSON, and YAML formats

## Data Flow

### Command Processing Flow

1. User enters command via interface
2. Interface passes command to AGI Core
3. AGI Core records command in short-term memory
4. Command Router identifies and routes the command
5. Appropriate handler processes the command
6. Result is returned to AGI Core
7. AGI Core records response in short-term memory
8. Interface displays the response to the user

### Memory Flow

1. **Short-Term Memory**
   - Recent interactions stored by type
   - Chronological timeline maintained
   - Limited capacity (configurable)
   - In-memory storage only

2. **Long-Term Memory**
   - Important information persisted
   - Vector embeddings for semantic search
   - Metadata and importance tracking
   - Persistent storage via vector database

### Reasoning Flow

1. User query received
2. Relevant memories retrieved from long-term memory
3. Context assembled from current state and memories
4. If uncensored mode:
   - Local Qwen-14B model used for reasoning
5. If standard mode:
   - DeepSeek-R1 or Sonnet-3.7 API used based on query complexity
6. Reasoning result returned
7. Important reasoning stored in memory

## Autonomous Evolution (Phase 2)

In Phase 2, Hohenheim will gain the ability to self-modify and evolve:

1. **Self-Reflection**
   - Periodically analyze own performance
   - Identify areas for improvement

2. **Code Generation**
   - Generate code modifications
   - Test changes in isolated environment

3. **Self-Modification**
   - Apply validated changes to own codebase
   - Track evolution history

4. **Learning Loop**
   - Continuous improvement cycle
   - Feedback-based optimization

## Extension Points

Hohenheim is designed to be extensible through these mechanisms:

1. **Command Registration**
   - New commands can be registered with the Command Router
   - Pattern matching for flexible command syntax

2. **Memory Backends**
   - Alternative vector database implementations
   - Custom memory organization strategies

3. **Reasoning Engines**
   - Additional API integrations
   - Local model alternatives

4. **Interface Plugins**
   - GUI interfaces
   - Voice interfaces
   - API/webhook interfaces

5. **Agent System**
   - Specialized micro-agents for specific tasks
   - Multi-agent collaboration framework

## Security Considerations

1. **API Keys**
   - Stored in .env file (not committed to repository)
   - Loaded at runtime via ConfigManager

2. **Uncensored Mode**
   - Requires explicit activation
   - Uses local model to avoid API restrictions

3. **Memory Isolation**
   - Short-term memory is ephemeral
   - Long-term memory is persistent but contained

## Performance Considerations

1. **Memory Efficiency**
   - Short-term memory uses fixed-size deques
   - Long-term memory uses efficient vector storage

2. **API Usage**
   - Fallback mechanisms between APIs
   - Caching for repeated queries

3. **Local Model Optimization**
   - Half-precision (FP16) for Qwen model
   - Automatic device mapping

## Future Architecture Extensions

1. **Distributed Memory**
   - Sharded vector database
   - Cloud-based persistence

2. **Multi-Agent System**
   - Specialized agents for different domains
   - Agent communication protocol

3. **External Tool Integration**
   - Web browsing capabilities
   - API client generation
   - File system access

4. **Advanced Interfaces**
   - 3D avatar representation
   - Multimodal interaction
   - AR/VR interfaces