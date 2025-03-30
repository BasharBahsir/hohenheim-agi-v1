# Changelog

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