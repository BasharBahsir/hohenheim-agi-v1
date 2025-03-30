# Changelog

## v0.2.0 - Phase 2 Release

### Added
- Modern Web GUI Interface
  - Multi-tab interface with chat, memory, system, and settings
  - Interactive visualizations for memory and system status
  - Aesthetic design with custom styling
  - Real-time updates and responsive layout

- RESTful API Interface
  - Comprehensive endpoints for all system functions
  - JSON-based communication
  - API documentation endpoint
  - CORS support for cross-origin requests

- Autonomous Evolution System
  - Code analysis and improvement capabilities
  - Component generation functionality
  - Self-modification with safety checks
  - Evolution history tracking

- Enhanced Reasoning
  - Tiered reasoning system (basic vs. advanced)
  - Claude 3.7 Sonnet integration for complex reasoning
  - Local LM Studio server integration for uncensored mode
  - Improved context handling

- System Improvements
  - Updated command router with evolution commands
  - Enhanced logging with timestamped files
  - Capability detection and tracking
  - Improved error handling and fallbacks

### Changed
- Updated API Manager to use DeepSeek Chat and Claude APIs
- Replaced Qwen-14B with local LM Studio server for uncensored mode
- Improved command routing system with context handling
- Enhanced memory systems with better search capabilities
- Updated documentation for Phase 2 features

### Technical Details
- Added new dependencies for GUI and evolution
- Improved code organization and modularity
- Enhanced error handling and recovery
- Added capability detection system
- Implemented advanced command context handling

## v0.1.0 - Initial Release (Phase 1)

### Added
- Core AGI system architecture
  - Central AGI Core class
  - API Manager for DeepSeek-R1 and Sonnet-3.7 integration
  - Command Router for processing user commands
  
- Memory systems
  - Short-term memory (RAM-like)
  - Long-term memory with vector database support (Chroma/FAISS)
  
- Uncensored mode
  - Local Qwen-14B integration
  - Toggle functionality
  
- Configuration system
  - Environment variables support
  - JSON/YAML config files
  - Default configuration
  
- Terminal interface
  - Command-line interaction
  - Command history
  - Formatted output
  
- Documentation
  - README with system overview
  - Architecture documentation
  - Code documentation

### Technical Details
- Modular folder structure
- Comprehensive logging system
- Error handling and fallbacks
- Memory statistics tracking
- Command pattern matching