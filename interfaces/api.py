"""
API Interface - RESTful API for the Hohenheim AGI system
Provides programmatic access to the AGI system
"""

import os
import sys
import logging
import json
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

class APIInterface:
    """
    RESTful API interface for the Hohenheim AGI system.
    Provides endpoints for interacting with the AGI programmatically.
    """
    
    def __init__(self, agi_core):
        """
        Initialize the API interface
        
        Args:
            agi_core: Reference to the main AGI core instance
        """
        self.agi_core = agi_core
        self.logger = logging.getLogger("Hohenheim.APIInterface")
        
        # Create Flask app
        self.app = Flask("Hohenheim-API")
        CORS(self.app)  # Enable CORS for all routes
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self) -> None:
        """Register API routes"""
        # System routes
        @self.app.route('/api/system/status', methods=['GET'])
        def get_status():
            """Get system status"""
            try:
                status = {
                    "system_name": self.agi_core.name,
                    "version": self.agi_core.version,
                    "codename": self.agi_core.codename,
                    "running": self.agi_core.is_running,
                    "uncensored_mode": self.agi_core.uncensored_mode
                }
                
                # Add memory stats
                status["memory"] = {
                    "short_term": self.agi_core.short_term_memory.get_stats(),
                    "long_term": self.agi_core.long_term_memory.get_stats()
                }
                
                return jsonify(status)
            except Exception as e:
                self.logger.error(f"Error getting status: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/system/uncensored', methods=['POST'])
        def toggle_uncensored():
            """Toggle uncensored mode"""
            try:
                data = request.json
                enable = data.get('enable')
                
                if enable is None:
                    return jsonify({"error": "Missing 'enable' parameter"}), 400
                
                current_state = self.agi_core.toggle_uncensored_mode(enable)
                
                return jsonify({
                    "uncensored_mode": current_state,
                    "message": f"Uncensored mode {'enabled' if current_state else 'disabled'}"
                })
            except Exception as e:
                self.logger.error(f"Error toggling uncensored mode: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        # Command routes
        @self.app.route('/api/command', methods=['POST'])
        def process_command():
            """Process a command"""
            try:
                data = request.json
                command = data.get('command')
                context = data.get('context', {})
                
                if not command:
                    return jsonify({"error": "Missing 'command' parameter"}), 400
                
                response = self.agi_core.process_command(command, context)
                
                return jsonify(response)
            except Exception as e:
                self.logger.error(f"Error processing command: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        # Reasoning routes
        @self.app.route('/api/reason', methods=['POST'])
        def reason():
            """Use reasoning capabilities"""
            try:
                data = request.json
                query = data.get('query')
                context = data.get('context', {})
                
                if not query:
                    return jsonify({"error": "Missing 'query' parameter"}), 400
                
                result = self.agi_core.reason(query, context)
                
                return jsonify(result)
            except Exception as e:
                self.logger.error(f"Error reasoning: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/advanced-reason', methods=['POST'])
        def advanced_reason():
            """Use advanced reasoning capabilities"""
            try:
                data = request.json
                query = data.get('query')
                context = data.get('context', {})
                
                if not query:
                    return jsonify({"error": "Missing 'query' parameter"}), 400
                
                result = self.agi_core.advanced_reason(query, context)
                
                return jsonify(result)
            except Exception as e:
                self.logger.error(f"Error advanced reasoning: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        # Memory routes
        @self.app.route('/api/memory/short-term', methods=['GET'])
        def get_short_term_memory():
            """Get short-term memory"""
            try:
                limit = request.args.get('limit', 10, type=int)
                memory_type = request.args.get('type')
                
                if memory_type:
                    memories = self.agi_core.short_term_memory.get_by_type(memory_type, limit=limit)
                else:
                    memories = self.agi_core.short_term_memory.get_recent(limit=limit)
                
                return jsonify(memories)
            except Exception as e:
                self.logger.error(f"Error getting short-term memory: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/memory/long-term/search', methods=['GET'])
        def search_long_term_memory():
            """Search long-term memory"""
            try:
                query = request.args.get('query')
                limit = request.args.get('limit', 5, type=int)
                
                if not query:
                    return jsonify({"error": "Missing 'query' parameter"}), 400
                
                memories = self.agi_core.long_term_memory.search(query, limit=limit)
                
                return jsonify(memories)
            except Exception as e:
                self.logger.error(f"Error searching long-term memory: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/memory/remember', methods=['POST'])
        def remember():
            """Store information in long-term memory"""
            try:
                data = request.json
                title = data.get('title')
                content = data.get('content')
                metadata = data.get('metadata', {})
                
                if not title or not content:
                    return jsonify({"error": "Missing 'title' or 'content' parameter"}), 400
                
                memory_id = self.agi_core.long_term_memory.add(title, content, metadata)
                
                return jsonify({
                    "memory_id": memory_id,
                    "message": "Memory stored successfully"
                })
            except Exception as e:
                self.logger.error(f"Error storing memory: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        # Evolution routes (if available)
        @self.app.route('/api/evolution/analyze', methods=['GET'])
        def analyze_codebase():
            """Analyze codebase for potential improvements"""
            try:
                if not hasattr(self.agi_core, 'evolution_agent'):
                    return jsonify({"error": "Evolution agent not initialized"}), 400
                
                analysis = self.agi_core.evolution_agent.analyze_codebase()
                
                return jsonify(analysis)
            except Exception as e:
                self.logger.error(f"Error analyzing codebase: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/evolution/improve', methods=['POST'])
        def improve_code():
            """Generate and apply code improvement"""
            try:
                if not hasattr(self.agi_core, 'evolution_agent'):
                    return jsonify({"error": "Evolution agent not initialized"}), 400
                
                data = request.json
                file_path = data.get('file_path')
                issue_description = data.get('issue_description')
                apply = data.get('apply', False)
                
                if not file_path or not issue_description:
                    return jsonify({"error": "Missing 'file_path' or 'issue_description' parameter"}), 400
                
                # Generate improvement
                improvement = self.agi_core.evolution_agent.generate_code_improvement(file_path, issue_description)
                
                # Apply if requested
                if apply and improvement.get('success', False):
                    result = self.agi_core.evolution_agent.apply_improvement(improvement)
                    improvement['applied'] = result
                
                return jsonify(improvement)
            except Exception as e:
                self.logger.error(f"Error improving code: {str(e)}")
                return jsonify({"error": str(e)}), 500
        
        # Documentation route
        @self.app.route('/api/docs', methods=['GET'])
        def get_docs():
            """Get API documentation"""
            docs = {
                "name": f"{self.agi_core.name} API",
                "version": self.agi_core.version,
                "description": "RESTful API for the Hohenheim AGI system",
                "endpoints": [
                    {
                        "path": "/api/system/status",
                        "method": "GET",
                        "description": "Get system status"
                    },
                    {
                        "path": "/api/system/uncensored",
                        "method": "POST",
                        "description": "Toggle uncensored mode",
                        "body": {"enable": "boolean"}
                    },
                    {
                        "path": "/api/command",
                        "method": "POST",
                        "description": "Process a command",
                        "body": {"command": "string", "context": "object (optional)"}
                    },
                    {
                        "path": "/api/reason",
                        "method": "POST",
                        "description": "Use reasoning capabilities",
                        "body": {"query": "string", "context": "object (optional)"}
                    },
                    {
                        "path": "/api/advanced-reason",
                        "method": "POST",
                        "description": "Use advanced reasoning capabilities",
                        "body": {"query": "string", "context": "object (optional)"}
                    },
                    {
                        "path": "/api/memory/short-term",
                        "method": "GET",
                        "description": "Get short-term memory",
                        "query": {"limit": "integer (optional)", "type": "string (optional)"}
                    },
                    {
                        "path": "/api/memory/long-term/search",
                        "method": "GET",
                        "description": "Search long-term memory",
                        "query": {"query": "string", "limit": "integer (optional)"}
                    },
                    {
                        "path": "/api/memory/remember",
                        "method": "POST",
                        "description": "Store information in long-term memory",
                        "body": {"title": "string", "content": "string", "metadata": "object (optional)"}
                    },
                    {
                        "path": "/api/evolution/analyze",
                        "method": "GET",
                        "description": "Analyze codebase for potential improvements"
                    },
                    {
                        "path": "/api/evolution/improve",
                        "method": "POST",
                        "description": "Generate and apply code improvement",
                        "body": {"file_path": "string", "issue_description": "string", "apply": "boolean (optional)"}
                    },
                    {
                        "path": "/api/docs",
                        "method": "GET",
                        "description": "Get API documentation"
                    }
                ]
            }
            
            return jsonify(docs)
        
        # Root route
        @self.app.route('/', methods=['GET'])
        def root():
            """Root endpoint"""
            return jsonify({
                "name": f"{self.agi_core.name} API",
                "version": self.agi_core.version,
                "documentation": "/api/docs"
            })
    
    def start(self, host: str = "0.0.0.0", port: int = 57264) -> None:
        """
        Start the API server
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        self.logger.info(f"Starting API server on {host}:{port}")
        
        # Start the AGI system
        self.agi_core.start()
        
        # Start the Flask app
        self.app.run(host=host, port=port, debug=False, threaded=True)