"""
Evolution Agent - Enables autonomous self-evolution of the AGI system
Analyzes code, generates improvements, and applies changes
"""

import os
import sys
import logging
import inspect
import importlib
import ast
import re
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union
import black
import autopep8

class EvolutionAgent:
    """
    Evolution agent for the Hohenheim AGI system.
    Enables autonomous self-evolution through code analysis and modification.
    """
    
    def __init__(self, agi_core):
        """
        Initialize the evolution agent
        
        Args:
            agi_core: Reference to the main AGI core instance
        """
        self.agi_core = agi_core
        self.logger = logging.getLogger("Hohenheim.EvolutionAgent")
        
        # Base directory for the project
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Evolution history
        self.evolution_history = []
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """
        Analyze the codebase to identify potential improvements
        
        Returns:
            Analysis results
        """
        self.logger.info("Analyzing codebase for potential improvements")
        
        # Get all Python files in the project
        python_files = self._get_python_files()
        
        # Collect code metrics
        metrics = {
            "total_files": len(python_files),
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "complexity_scores": {},
            "potential_improvements": []
        }
        
        # Analyze each file
        for file_path in python_files:
            file_metrics = self._analyze_file(file_path)
            
            metrics["total_lines"] += file_metrics["lines"]
            metrics["total_functions"] += file_metrics["functions"]
            metrics["total_classes"] += file_metrics["classes"]
            metrics["complexity_scores"][file_path] = file_metrics["complexity"]
            
            # Add potential improvements
            if file_metrics["potential_improvements"]:
                metrics["potential_improvements"].extend(file_metrics["potential_improvements"])
        
        # Sort improvements by priority
        metrics["potential_improvements"].sort(key=lambda x: x["priority"], reverse=True)
        
        # Use advanced reasoning to generate improvement suggestions
        improvement_prompt = f"""
        Analyze the following codebase metrics and suggest improvements:
        
        Total files: {metrics['total_files']}
        Total lines of code: {metrics['total_lines']}
        Total functions: {metrics['total_functions']}
        Total classes: {metrics['total_classes']}
        
        Files with highest complexity:
        {self._format_complexity_scores(metrics['complexity_scores'])}
        
        Potential issues identified:
        {self._format_potential_improvements(metrics['potential_improvements'])}
        
        Based on this analysis, suggest 3-5 specific improvements that would enhance the system's:
        1. Performance
        2. Maintainability
        3. Extensibility
        4. Robustness
        
        For each suggestion, provide:
        - A clear description of the improvement
        - The specific files/components to modify
        - The expected benefits
        - A priority level (high/medium/low)
        """
        
        improvement_suggestions = self.agi_core.advanced_reason(improvement_prompt)
        metrics["improvement_suggestions"] = improvement_suggestions.get("reasoning", "")
        
        return metrics
    
    def _get_python_files(self) -> List[str]:
        """Get all Python files in the project"""
        python_files = []
        
        for root, dirs, files in os.walk(self.base_dir):
            # Skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        return python_files
    
    def _analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            File metrics
        """
        metrics = {
            "lines": 0,
            "functions": 0,
            "classes": 0,
            "complexity": 0,
            "potential_improvements": []
        }
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Count lines
            metrics["lines"] = len(content.split('\n'))
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Count functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
                    
                    # Check function complexity
                    func_complexity = self._calculate_complexity(node)
                    if func_complexity > 10:
                        metrics["potential_improvements"].append({
                            "type": "high_complexity",
                            "location": f"{file_path}:{node.lineno}",
                            "description": f"Function '{node.name}' has high complexity ({func_complexity})",
                            "priority": func_complexity / 10
                        })
                
                elif isinstance(node, ast.ClassDef):
                    metrics["classes"] += 1
            
            # Calculate overall complexity
            metrics["complexity"] = self._calculate_file_complexity(tree)
            
            # Check for long lines
            for i, line in enumerate(content.split('\n')):
                if len(line) > 100:
                    metrics["potential_improvements"].append({
                        "type": "long_line",
                        "location": f"{file_path}:{i+1}",
                        "description": f"Line {i+1} is too long ({len(line)} characters)",
                        "priority": 0.5
                    })
            
            # Check for TODO comments
            todo_pattern = re.compile(r'#\s*TODO', re.IGNORECASE)
            for i, line in enumerate(content.split('\n')):
                if todo_pattern.search(line):
                    metrics["potential_improvements"].append({
                        "type": "todo",
                        "location": f"{file_path}:{i+1}",
                        "description": f"TODO comment found: {line.strip()}",
                        "priority": 0.3
                    })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error analyzing file {file_path}: {str(e)}")
            return metrics
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Start with 1
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.comprehension)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            elif isinstance(child, ast.Try):
                complexity += len(child.handlers)
        
        return complexity
    
    def _calculate_file_complexity(self, tree: ast.AST) -> float:
        """Calculate overall complexity of a file"""
        total_complexity = 0
        function_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_complexity += self._calculate_complexity(node)
                function_count += 1
        
        return total_complexity / max(function_count, 1)
    
    def _format_complexity_scores(self, complexity_scores: Dict[str, float]) -> str:
        """Format complexity scores for display"""
        # Sort by complexity
        sorted_scores = sorted(complexity_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Format the top 5
        result = ""
        for i, (file_path, score) in enumerate(sorted_scores[:5], 1):
            rel_path = os.path.relpath(file_path, self.base_dir)
            result += f"{i}. {rel_path}: {score:.2f}\n"
        
        return result
    
    def _format_potential_improvements(self, improvements: List[Dict[str, Any]]) -> str:
        """Format potential improvements for display"""
        if not improvements:
            return "No issues identified."
        
        result = ""
        for i, improvement in enumerate(improvements[:10], 1):
            result += f"{i}. {improvement['description']} ({improvement['location']})\n"
        
        if len(improvements) > 10:
            result += f"... and {len(improvements) - 10} more issues.\n"
        
        return result
    
    def generate_code_improvement(self, file_path: str, issue_description: str) -> Dict[str, Any]:
        """
        Generate code improvement for a specific issue
        
        Args:
            file_path: Path to the file to improve
            issue_description: Description of the issue to fix
            
        Returns:
            Generated improvement
        """
        self.logger.info(f"Generating improvement for {file_path}: {issue_description}")
        
        try:
            # Read the file content
            with open(file_path, 'r') as f:
                original_content = f.read()
            
            # Get relative path for better context
            rel_path = os.path.relpath(file_path, self.base_dir)
            
            # Generate improvement using advanced reasoning
            improvement_prompt = f"""
            I need to improve the following Python file: {rel_path}
            
            Issue to fix: {issue_description}
            
            Here's the current code:
            ```python
            {original_content}
            ```
            
            Please generate an improved version of this code that addresses the issue.
            Focus on making the code more efficient, maintainable, and robust.
            
            Provide your response in the following format:
            1. Analysis of the issue
            2. Proposed changes
            3. Complete improved code (the entire file)
            4. Explanation of benefits
            """
            
            improvement_result = self.agi_core.advanced_reason(improvement_prompt)
            reasoning = improvement_result.get("reasoning", "")
            
            # Extract the improved code
            improved_code = self._extract_code_from_reasoning(reasoning)
            
            if not improved_code:
                return {
                    "success": False,
                    "error": "Could not extract improved code from reasoning",
                    "reasoning": reasoning
                }
            
            # Format the code with Black
            try:
                improved_code = black.format_str(improved_code, mode=black.Mode())
            except Exception as e:
                self.logger.warning(f"Error formatting code with Black: {str(e)}")
                # Try with autopep8 as fallback
                try:
                    improved_code = autopep8.fix_code(improved_code)
                except Exception as e2:
                    self.logger.warning(f"Error formatting code with autopep8: {str(e2)}")
            
            return {
                "success": True,
                "original_content": original_content,
                "improved_content": improved_code,
                "reasoning": reasoning,
                "file_path": file_path
            }
            
        except Exception as e:
            self.logger.error(f"Error generating improvement: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_code_from_reasoning(self, reasoning: str) -> str:
        """Extract code blocks from reasoning text"""
        # Look for code blocks with ```python ... ``` format
        code_blocks = re.findall(r'```python\s*(.*?)\s*```', reasoning, re.DOTALL)
        
        if code_blocks:
            # Return the largest code block (assuming it's the complete file)
            return max(code_blocks, key=len)
        
        # Try alternative format: ```\n...\n```
        code_blocks = re.findall(r'```\s*(.*?)\s*```', reasoning, re.DOTALL)
        
        if code_blocks:
            return max(code_blocks, key=len)
        
        return ""
    
    def apply_improvement(self, improvement: Dict[str, Any], backup: bool = True) -> Dict[str, Any]:
        """
        Apply a generated code improvement
        
        Args:
            improvement: The improvement to apply
            backup: Whether to create a backup of the original file
            
        Returns:
            Result of the operation
        """
        if not improvement.get("success", False):
            return {
                "success": False,
                "error": "Cannot apply an unsuccessful improvement"
            }
        
        file_path = improvement["file_path"]
        improved_content = improvement["improved_content"]
        
        try:
            # Create backup if requested
            if backup:
                backup_path = f"{file_path}.bak"
                with open(backup_path, 'w') as f:
                    f.write(improvement["original_content"])
                self.logger.info(f"Created backup at {backup_path}")
            
            # Write the improved content
            with open(file_path, 'w') as f:
                f.write(improved_content)
            
            # Record the evolution
            evolution_record = {
                "timestamp": self.agi_core.short_term_memory.get_timestamp(),
                "file_path": file_path,
                "description": "Applied code improvement",
                "reasoning": improvement["reasoning"]
            }
            
            self.evolution_history.append(evolution_record)
            
            # Store in memory
            self.agi_core.short_term_memory.add("evolution", {
                "file_path": file_path,
                "action": "improve_code",
                "timestamp": self.agi_core.short_term_memory.get_timestamp()
            })
            
            self.agi_core.long_term_memory.add(
                "Code Evolution", 
                f"Improved {file_path}:\n{improvement['reasoning'][:500]}...", 
                metadata={"type": "evolution", "importance": 0.8}
            )
            
            return {
                "success": True,
                "file_path": file_path,
                "backup_path": backup_path if backup else None,
                "evolution_record": evolution_record
            }
            
        except Exception as e:
            self.logger.error(f"Error applying improvement: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_improvement(self, file_path: str) -> Dict[str, Any]:
        """
        Test if an improvement breaks functionality
        
        Args:
            file_path: Path to the improved file
            
        Returns:
            Test results
        """
        self.logger.info(f"Testing improvement for {file_path}")
        
        try:
            # Get the module name from the file path
            rel_path = os.path.relpath(file_path, self.base_dir)
            module_path = rel_path.replace('/', '.').replace('\\', '.').replace('.py', '')
            
            # Try to import the module
            try:
                # Clear the module from sys.modules if it's already imported
                if module_path in sys.modules:
                    del sys.modules[module_path]
                
                # Import the module
                module = importlib.import_module(module_path)
                
                # Reload to ensure we have the latest version
                importlib.reload(module)
                
                self.logger.info(f"Successfully imported {module_path}")
                import_success = True
            except Exception as e:
                self.logger.error(f"Error importing {module_path}: {str(e)}")
                import_success = False
                import_error = str(e)
            
            # Run pylint on the file
            try:
                pylint_output = subprocess.check_output(
                    ["pylint", "--output-format=json", file_path],
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                pylint_success = True
            except subprocess.CalledProcessError as e:
                pylint_output = e.output
                pylint_success = False
            except Exception as e:
                pylint_output = str(e)
                pylint_success = False
            
            return {
                "success": import_success and pylint_success,
                "import_success": import_success,
                "import_error": import_error if not import_success else None,
                "pylint_success": pylint_success,
                "pylint_output": pylint_output
            }
            
        except Exception as e:
            self.logger.error(f"Error testing improvement: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def revert_improvement(self, file_path: str) -> Dict[str, Any]:
        """
        Revert an improvement using the backup file
        
        Args:
            file_path: Path to the file to revert
            
        Returns:
            Result of the operation
        """
        backup_path = f"{file_path}.bak"
        
        if not os.path.exists(backup_path):
            return {
                "success": False,
                "error": f"Backup file not found: {backup_path}"
            }
        
        try:
            # Read the backup content
            with open(backup_path, 'r') as f:
                original_content = f.read()
            
            # Restore the original content
            with open(file_path, 'w') as f:
                f.write(original_content)
            
            # Record the reversion
            reversion_record = {
                "timestamp": self.agi_core.short_term_memory.get_timestamp(),
                "file_path": file_path,
                "description": "Reverted code improvement"
            }
            
            self.evolution_history.append(reversion_record)
            
            # Store in memory
            self.agi_core.short_term_memory.add("evolution", {
                "file_path": file_path,
                "action": "revert_improvement",
                "timestamp": self.agi_core.short_term_memory.get_timestamp()
            })
            
            return {
                "success": True,
                "file_path": file_path,
                "reversion_record": reversion_record
            }
            
        except Exception as e:
            self.logger.error(f"Error reverting improvement: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_new_component(self, component_type: str, component_name: str, description: str) -> Dict[str, Any]:
        """
        Generate a new component for the system
        
        Args:
            component_type: Type of component (e.g., 'agent', 'interface', 'memory')
            component_name: Name of the component
            description: Description of the component's functionality
            
        Returns:
            Generated component
        """
        self.logger.info(f"Generating new {component_type} component: {component_name}")
        
        # Determine the appropriate directory and file path
        if component_type == 'agent':
            directory = os.path.join(self.base_dir, 'agents')
            file_name = f"{component_name.lower()}_agent.py"
        elif component_type == 'interface':
            directory = os.path.join(self.base_dir, 'interfaces')
            file_name = f"{component_name.lower()}.py"
        elif component_type == 'memory':
            directory = os.path.join(self.base_dir, 'memory')
            file_name = f"{component_name.lower()}.py"
        elif component_type == 'core':
            directory = os.path.join(self.base_dir, 'core')
            file_name = f"{component_name.lower()}.py"
        else:
            return {
                "success": False,
                "error": f"Unknown component type: {component_type}"
            }
        
        file_path = os.path.join(directory, file_name)
        
        # Check if the file already exists
        if os.path.exists(file_path):
            return {
                "success": False,
                "error": f"Component already exists: {file_path}"
            }
        
        # Generate the component using advanced reasoning
        component_prompt = f"""
        Generate a new {component_type} component for the Hohenheim AGI system.
        
        Component name: {component_name}
        Description: {description}
        
        The component should:
        1. Follow the existing architecture and coding style
        2. Integrate with the AGI core
        3. Include proper documentation
        4. Implement the functionality described
        
        Please generate the complete Python file for this component.
        """
        
        component_result = self.agi_core.advanced_reason(component_prompt)
        reasoning = component_result.get("reasoning", "")
        
        # Extract the code
        component_code = self._extract_code_from_reasoning(reasoning)
        
        if not component_code:
            return {
                "success": False,
                "error": "Could not extract component code from reasoning",
                "reasoning": reasoning
            }
        
        # Format the code
        try:
            component_code = black.format_str(component_code, mode=black.Mode())
        except Exception as e:
            self.logger.warning(f"Error formatting code with Black: {str(e)}")
            try:
                component_code = autopep8.fix_code(component_code)
            except Exception as e2:
                self.logger.warning(f"Error formatting code with autopep8: {str(e2)}")
        
        try:
            # Create the file
            with open(file_path, 'w') as f:
                f.write(component_code)
            
            # Record the creation
            creation_record = {
                "timestamp": self.agi_core.short_term_memory.get_timestamp(),
                "file_path": file_path,
                "description": f"Created new {component_type} component: {component_name}"
            }
            
            self.evolution_history.append(creation_record)
            
            # Store in memory
            self.agi_core.short_term_memory.add("evolution", {
                "file_path": file_path,
                "action": "create_component",
                "component_type": component_type,
                "component_name": component_name,
                "timestamp": self.agi_core.short_term_memory.get_timestamp()
            })
            
            self.agi_core.long_term_memory.add(
                "Component Creation", 
                f"Created new {component_type} component: {component_name}\n{description}", 
                metadata={"type": "evolution", "importance": 0.9}
            )
            
            return {
                "success": True,
                "file_path": file_path,
                "component_code": component_code,
                "creation_record": creation_record
            }
            
        except Exception as e:
            self.logger.error(f"Error creating component: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """
        Get the evolution history
        
        Returns:
            List of evolution records
        """
        return self.evolution_history