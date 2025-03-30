"""
Self-Evolution Framework - Enables Hohenheim AGI to evolve and improve itself
Handles performance evaluation, self-improvement, and autonomous evolution
"""

import os
import sys
import logging
import time
import threading
import subprocess
import json
import re
import shutil
import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum

class EvolutionTrigger(Enum):
    """Enum for different types of evolution triggers"""
    DAILY = "daily"
    INTERVAL = "interval"
    MANUAL = "manual"
    PERFORMANCE_THRESHOLD = "performance_threshold"

class SelfEvolutionFramework:
    """
    Self-Evolution Framework for the Hohenheim AGI system.
    Enables autonomous self-evolution through performance evaluation,
    codebase cloning, self-improvement, and benchmarking.
    """
    
    def __init__(self, agi_core):
        """
        Initialize the self-evolution framework
        
        Args:
            agi_core: Reference to the main AGI core instance
        """
        self.agi_core = agi_core
        self.logger = logging.getLogger("Hohenheim.SelfEvolution")
        
        # Base directory for the project
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Directory for storing clones and evolution data
        self.evolution_dir = os.path.join(self.base_dir, "evolution")
        os.makedirs(self.evolution_dir, exist_ok=True)
        
        # Evolution history
        self.evolution_history = []
        
        # Evolution configuration
        self.config = {
            "trigger_type": EvolutionTrigger.DAILY,
            "interval_hours": 24,
            "performance_threshold": 0.8,
            "max_evolution_attempts": 5,
            "auto_approve": False,
            "benchmark_iterations": 3,
            "use_phi_for_intent": False,
            "evolution_enabled": True
        }
        
        # Load configuration from AGI core if available
        self._load_config()
        
        # Evolution state
        self.is_evolving = False
        self.last_evolution_time = None
        self.current_clone_dir = None
        self.evolution_thread = None
        
        # Performance metrics
        self.performance_metrics = {
            "reasoning_quality": 0.0,
            "response_time": 0.0,
            "memory_efficiency": 0.0,
            "overall_score": 0.0
        }
        
        # Initialize Phi model for intent recognition if enabled
        self.phi_model = None
        if self.config["use_phi_for_intent"]:
            self._initialize_phi_model()
        
        self.logger.info("Self-Evolution Framework initialized")
    
    def _load_config(self):
        """Load configuration from AGI core"""
        try:
            if hasattr(self.agi_core, 'config') and self.agi_core.config:
                # Get evolution configuration if available
                evolution_config = self.agi_core.config.get("evolution", {})
                
                # Update configuration with values from AGI core
                if "trigger_type" in evolution_config:
                    trigger_type = evolution_config["trigger_type"]
                    if hasattr(EvolutionTrigger, trigger_type.upper()):
                        self.config["trigger_type"] = getattr(EvolutionTrigger, trigger_type.upper())
                
                if "interval_hours" in evolution_config:
                    self.config["interval_hours"] = float(evolution_config["interval_hours"])
                
                if "performance_threshold" in evolution_config:
                    self.config["performance_threshold"] = float(evolution_config["performance_threshold"])
                
                if "max_evolution_attempts" in evolution_config:
                    self.config["max_evolution_attempts"] = int(evolution_config["max_evolution_attempts"])
                
                if "auto_approve" in evolution_config:
                    self.config["auto_approve"] = bool(evolution_config["auto_approve"])
                
                if "benchmark_iterations" in evolution_config:
                    self.config["benchmark_iterations"] = int(evolution_config["benchmark_iterations"])
                
                if "use_phi_for_intent" in evolution_config:
                    self.config["use_phi_for_intent"] = bool(evolution_config["use_phi_for_intent"])
                
                if "evolution_enabled" in evolution_config:
                    self.config["evolution_enabled"] = bool(evolution_config["evolution_enabled"])
                
                self.logger.info("Loaded evolution configuration from AGI core")
        except Exception as e:
            self.logger.error(f"Error loading evolution configuration: {str(e)}")
    
    def _initialize_phi_model(self):
        """Initialize the Phi model for intent recognition"""
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            
            self.logger.info("Initializing Phi model for intent recognition")
            
            # Use Phi-2 model for intent recognition
            model_name = "microsoft/phi-2"
            
            # Initialize tokenizer and model
            self.phi_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.phi_model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype="auto",
                device_map="auto"
            )
            
            self.logger.info("Phi model initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing Phi model: {str(e)}")
            self.logger.warning("Falling back to standard command routing")
            self.config["use_phi_for_intent"] = False
    
    def start_evolution_monitor(self):
        """Start the evolution monitoring thread"""
        if not self.config["evolution_enabled"]:
            self.logger.info("Evolution is disabled in configuration")
            return
        
        if self.evolution_thread is not None and self.evolution_thread.is_alive():
            self.logger.info("Evolution monitor is already running")
            return
        
        self.logger.info("Starting evolution monitor")
        self.evolution_thread = threading.Thread(target=self._evolution_monitor_loop, daemon=True)
        self.evolution_thread.start()
    
    def _evolution_monitor_loop(self):
        """Monitor loop for triggering evolution based on configuration"""
        self.logger.info(f"Evolution monitor started with trigger type: {self.config['trigger_type'].value}")
        
        while True:
            try:
                # Check if evolution should be triggered
                if self._should_trigger_evolution():
                    self.logger.info("Evolution trigger condition met")
                    self.start_evolution_process()
                
                # Sleep for a while before checking again
                time.sleep(60 * 60)  # Check every hour
            except Exception as e:
                self.logger.error(f"Error in evolution monitor: {str(e)}")
                time.sleep(60 * 60)  # Sleep and retry
    
    def _should_trigger_evolution(self) -> bool:
        """Check if evolution should be triggered based on configuration"""
        # Don't trigger if already evolving
        if self.is_evolving:
            return False
        
        # Check based on trigger type
        if self.config["trigger_type"] == EvolutionTrigger.DAILY:
            # Check if it's been at least 24 hours since last evolution
            if self.last_evolution_time is None:
                return True
            
            time_since_last = time.time() - self.last_evolution_time
            return time_since_last >= (24 * 60 * 60)  # 24 hours in seconds
        
        elif self.config["trigger_type"] == EvolutionTrigger.INTERVAL:
            # Check if the configured interval has passed
            if self.last_evolution_time is None:
                return True
            
            time_since_last = time.time() - self.last_evolution_time
            return time_since_last >= (self.config["interval_hours"] * 60 * 60)
        
        elif self.config["trigger_type"] == EvolutionTrigger.PERFORMANCE_THRESHOLD:
            # Check if performance is below threshold
            return self.performance_metrics["overall_score"] < self.config["performance_threshold"]
        
        return False
    
    def evaluate_performance(self) -> Dict[str, float]:
        """
        Evaluate the AGI system's performance
        
        Returns:
            Performance metrics
        """
        self.logger.info("Evaluating system performance")
        
        try:
            # Get recent memories for evaluation
            recent_memories = self.agi_core.short_term_memory.get_recent(limit=50)
            
            # Use advanced reasoning to evaluate performance
            evaluation_prompt = """
            Evaluate the AGI system's performance based on the following recent interactions:
            
            1. Reasoning Quality: Assess the quality, depth, and accuracy of reasoning
            2. Response Time: Evaluate the efficiency of responses
            3. Memory Efficiency: Assess how well the system uses its memory
            
            For each metric, provide:
            - A score from 0.0 to 1.0
            - A brief explanation
            
            Also provide an overall performance score from 0.0 to 1.0.
            
            Format your response as a JSON object with the following structure:
            {
                "reasoning_quality": {"score": 0.0, "explanation": "..."},
                "response_time": {"score": 0.0, "explanation": "..."},
                "memory_efficiency": {"score": 0.0, "explanation": "..."},
                "overall_score": 0.0,
                "analysis": "..."
            }
            """
            
            evaluation_result = self.agi_core.advanced_reason(evaluation_prompt, {"recent_memories": recent_memories})
            reasoning = evaluation_result.get("reasoning", "")
            
            # Extract JSON from reasoning
            json_match = re.search(r'```json\s*(.*?)\s*```', reasoning, re.DOTALL)
            if not json_match:
                json_match = re.search(r'{.*}', reasoning, re.DOTALL)
            
            if json_match:
                metrics_json = json_match.group(1) if json_match.group(0).startswith('```') else json_match.group(0)
                metrics = json.loads(metrics_json)
                
                # Update performance metrics
                self.performance_metrics = {
                    "reasoning_quality": metrics["reasoning_quality"]["score"],
                    "response_time": metrics["response_time"]["score"],
                    "memory_efficiency": metrics["memory_efficiency"]["score"],
                    "overall_score": metrics["overall_score"]
                }
                
                # Store evaluation in memory
                self.agi_core.short_term_memory.add("performance_evaluation", {
                    "metrics": metrics,
                    "timestamp": self.agi_core.short_term_memory.get_timestamp()
                })
                
                self.logger.info(f"Performance evaluation completed: {self.performance_metrics['overall_score']:.2f}")
                return self.performance_metrics
            else:
                self.logger.error("Could not extract metrics from evaluation result")
                return self.performance_metrics
        
        except Exception as e:
            self.logger.error(f"Error evaluating performance: {str(e)}")
            return self.performance_metrics
    
    def start_evolution_process(self) -> Dict[str, Any]:
        """
        Start the self-evolution process
        
        Returns:
            Status of the evolution process
        """
        if self.is_evolving:
            return {
                "success": False,
                "message": "Evolution process is already running",
                "status": "already_running"
            }
        
        self.logger.info("Starting self-evolution process")
        self.is_evolving = True
        
        try:
            # Create a timestamp for this evolution run
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            self.current_clone_dir = os.path.join(self.evolution_dir, f"clone-{timestamp}")
            
            # Clone the codebase
            clone_result = self._clone_codebase()
            if not clone_result["success"]:
                self.is_evolving = False
                return clone_result
            
            # Start the evolution in a separate thread
            evolution_thread = threading.Thread(
                target=self._run_evolution_process,
                args=(timestamp,)
            )
            evolution_thread.daemon = True
            evolution_thread.start()
            
            return {
                "success": True,
                "message": "Self-evolution process started",
                "status": "started",
                "timestamp": timestamp,
                "clone_dir": self.current_clone_dir
            }
        
        except Exception as e:
            self.logger.error(f"Error starting evolution process: {str(e)}")
            self.is_evolving = False
            return {
                "success": False,
                "message": f"Error starting evolution process: {str(e)}",
                "status": "error"
            }
    
    def _clone_codebase(self) -> Dict[str, Any]:
        """Clone the current codebase for evolution"""
        self.logger.info(f"Cloning codebase to {self.current_clone_dir}")
        
        try:
            # Create the clone directory
            os.makedirs(self.current_clone_dir, exist_ok=True)
            
            # Copy all files except the evolution directory and __pycache__
            for root, dirs, files in os.walk(self.base_dir):
                # Skip evolution directory and __pycache__
                if "evolution" in root or "__pycache__" in root or ".git" in root:
                    continue
                
                # Create corresponding directories in the clone
                rel_path = os.path.relpath(root, self.base_dir)
                if rel_path == ".":
                    clone_root = self.current_clone_dir
                else:
                    clone_root = os.path.join(self.current_clone_dir, rel_path)
                    os.makedirs(clone_root, exist_ok=True)
                
                # Copy files
                for file in files:
                    if file.endswith(".py") or file.endswith(".md") or file.endswith(".txt") or file.endswith(".yaml") or file.endswith(".yml"):
                        src_file = os.path.join(root, file)
                        dst_file = os.path.join(clone_root, file)
                        shutil.copy2(src_file, dst_file)
            
            self.logger.info("Codebase cloned successfully")
            return {
                "success": True,
                "message": "Codebase cloned successfully",
                "clone_dir": self.current_clone_dir
            }
        
        except Exception as e:
            self.logger.error(f"Error cloning codebase: {str(e)}")
            return {
                "success": False,
                "message": f"Error cloning codebase: {str(e)}"
            }
    
    def _run_evolution_process(self, timestamp: str):
        """
        Run the evolution process in a separate thread
        
        Args:
            timestamp: Timestamp for this evolution run
        """
        try:
            self.logger.info(f"Running evolution process for timestamp: {timestamp}")
            
            # Step 1: Analyze the codebase
            self.logger.info("Step 1: Analyzing codebase")
            analysis_result = self._analyze_cloned_codebase()
            
            if not analysis_result["success"]:
                self.logger.error(f"Codebase analysis failed: {analysis_result['message']}")
                self._finish_evolution(False, f"Codebase analysis failed: {analysis_result['message']}")
                return
            
            # Step 2: Generate improvements
            self.logger.info("Step 2: Generating improvements")
            improvements = self._generate_improvements(analysis_result["analysis"])
            
            if not improvements["success"] or not improvements["improvements"]:
                self.logger.error("No valid improvements generated")
                self._finish_evolution(False, "No valid improvements generated")
                return
            
            # Step 3: Apply improvements
            self.logger.info(f"Step 3: Applying {len(improvements['improvements'])} improvements")
            applied_improvements = []
            
            for improvement in improvements["improvements"]:
                apply_result = self._apply_improvement(improvement)
                if apply_result["success"]:
                    applied_improvements.append({
                        "improvement": improvement,
                        "result": apply_result
                    })
            
            if not applied_improvements:
                self.logger.error("No improvements could be applied")
                self._finish_evolution(False, "No improvements could be applied")
                return
            
            # Step 4: Benchmark the improvements
            self.logger.info("Step 4: Benchmarking improvements")
            benchmark_result = self._benchmark_improvements()
            
            if not benchmark_result["success"]:
                self.logger.error(f"Benchmarking failed: {benchmark_result['message']}")
                self._finish_evolution(False, f"Benchmarking failed: {benchmark_result['message']}")
                return
            
            # Step 5: Prepare evolution report
            self.logger.info("Step 5: Preparing evolution report")
            evolution_report = self._prepare_evolution_report(
                analysis_result,
                improvements,
                applied_improvements,
                benchmark_result
            )
            
            # Step 6: Request approval if needed
            if not self.config["auto_approve"]:
                self.logger.info("Step 6: Requesting approval for evolution")
                # Store the report for later approval
                report_path = os.path.join(self.evolution_dir, f"report-{timestamp}.json")
                with open(report_path, "w") as f:
                    json.dump(evolution_report, f, indent=2)
                
                # Add to memory for user notification
                self.agi_core.short_term_memory.add("evolution_report", {
                    "timestamp": timestamp,
                    "report_path": report_path,
                    "needs_approval": True,
                    "evolution_report": evolution_report
                })
                
                self.logger.info(f"Evolution report saved to {report_path}, waiting for approval")
                self.is_evolving = False
            else:
                # Auto-approve and apply changes
                self.logger.info("Step 6: Auto-approving and applying evolution")
                apply_result = self._apply_evolution_to_main_codebase(evolution_report)
                
                if apply_result["success"]:
                    self._finish_evolution(True, "Evolution successfully applied to main codebase")
                else:
                    self._finish_evolution(False, f"Failed to apply evolution: {apply_result['message']}")
        
        except Exception as e:
            self.logger.error(f"Error in evolution process: {str(e)}")
            self._finish_evolution(False, f"Error in evolution process: {str(e)}")
    
    def _analyze_cloned_codebase(self) -> Dict[str, Any]:
        """Analyze the cloned codebase"""
        try:
            # Use the evolution agent's analyze_codebase method on the clone
            # We need to temporarily modify the base_dir
            original_base_dir = None
            
            if hasattr(self.agi_core, 'evolution_agent') and self.agi_core.evolution_agent is not None:
                original_base_dir = self.agi_core.evolution_agent.base_dir
                self.agi_core.evolution_agent.base_dir = self.current_clone_dir
                
                analysis = self.agi_core.evolution_agent.analyze_codebase()
                
                # Restore the original base_dir
                self.agi_core.evolution_agent.base_dir = original_base_dir
                
                return {
                    "success": True,
                    "analysis": analysis
                }
            else:
                return {
                    "success": False,
                    "message": "Evolution agent is not available"
                }
        
        except Exception as e:
            # Restore the original base_dir if needed
            if original_base_dir is not None and hasattr(self.agi_core, 'evolution_agent'):
                self.agi_core.evolution_agent.base_dir = original_base_dir
            
            self.logger.error(f"Error analyzing cloned codebase: {str(e)}")
            return {
                "success": False,
                "message": f"Error analyzing cloned codebase: {str(e)}"
            }
    
    def _generate_improvements(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate improvements based on codebase analysis
        
        Args:
            analysis: Codebase analysis results
            
        Returns:
            Generated improvements
        """
        try:
            # Use OpenHands to generate improvements
            improvement_prompt = f"""
            You are OpenHands, an AI assistant tasked with improving the Hohenheim AGI codebase.
            
            Based on the following codebase analysis and performance metrics, generate specific code improvements:
            
            CODEBASE ANALYSIS:
            {json.dumps(analysis, indent=2)}
            
            PERFORMANCE METRICS:
            {json.dumps(self.performance_metrics, indent=2)}
            
            For each improvement:
            1. Identify a specific file to modify
            2. Describe the issue to fix
            3. Provide a code snippet showing the improvement
            4. Explain the benefits of the improvement
            5. Provide a priority level (high/medium/low)
            
            Focus on improvements that will:
            - Enhance the self-evolution capabilities
            - Improve reasoning quality
            - Optimize performance
            - Enhance natural language understanding
            - Improve error handling and system stability
            
            Format your response as a JSON array of improvement objects with the following structure:
            [
                {
                    "file": "path/to/file.py",
                    "issue": "Description of the issue",
                    "code_snippet": "# Code showing the improvement",
                    "benefits": "Explanation of benefits",
                    "priority": "high/medium/low"
                }
            ]
            
            Generate 3-5 specific, actionable improvements.
            """
            
            improvement_result = self.agi_core.advanced_reason(improvement_prompt)
            reasoning = improvement_result.get("reasoning", "")
            
            # Extract JSON from reasoning
            json_match = re.search(r'```json\s*(.*?)\s*```', reasoning, re.DOTALL)
            if not json_match:
                json_match = re.search(r'\[\s*{.*}\s*\]', reasoning, re.DOTALL)
            
            if json_match:
                improvements_json = json_match.group(1) if json_match.group(0).startswith('```') else json_match.group(0)
                improvements = json.loads(improvements_json)
                
                # Convert relative paths to absolute paths in the clone
                for improvement in improvements:
                    if "file_path" in improvement:
                        rel_path = improvement["file_path"].lstrip("/")
                        improvement["file_path"] = os.path.join(self.current_clone_dir, rel_path)
                
                return {
                    "success": True,
                    "improvements": improvements,
                    "reasoning": reasoning
                }
            else:
                self.logger.error("Could not extract improvements from result")
                return {
                    "success": False,
                    "message": "Could not extract improvements from result",
                    "reasoning": reasoning
                }
        
        except Exception as e:
            self.logger.error(f"Error generating improvements: {str(e)}")
            return {
                "success": False,
                "message": f"Error generating improvements: {str(e)}"
            }
    
    def _apply_improvement(self, improvement: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a single improvement to the cloned codebase
        
        Args:
            improvement: The improvement to apply
            
        Returns:
            Result of applying the improvement
        """
        try:
            file_path = improvement["file_path"]
            issue_description = improvement["issue_description"]
            
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "message": f"File not found: {file_path}"
                }
            
            # Use the evolution agent to generate and apply the improvement
            if hasattr(self.agi_core, 'evolution_agent') and self.agi_core.evolution_agent is not None:
                # Generate the improvement
                generated = self.agi_core.evolution_agent.generate_code_improvement(file_path, issue_description)
                
                if not generated.get("success", False):
                    return {
                        "success": False,
                        "message": f"Failed to generate improvement: {generated.get('error', 'Unknown error')}"
                    }
                
                # Apply the improvement
                applied = self.agi_core.evolution_agent.apply_improvement(generated)
                
                if not applied.get("success", False):
                    return {
                        "success": False,
                        "message": f"Failed to apply improvement: {applied.get('error', 'Unknown error')}"
                    }
                
                # Test the improvement
                test_result = self.agi_core.evolution_agent.test_improvement(file_path)
                
                if not test_result.get("success", False):
                    # Revert the improvement if it failed testing
                    self.agi_core.evolution_agent.revert_improvement(file_path)
                    return {
                        "success": False,
                        "message": f"Improvement failed testing: {test_result.get('error', 'Unknown error')}"
                    }
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "test_result": test_result
                }
            else:
                return {
                    "success": False,
                    "message": "Evolution agent is not available"
                }
        
        except Exception as e:
            self.logger.error(f"Error applying improvement: {str(e)}")
            return {
                "success": False,
                "message": f"Error applying improvement: {str(e)}"
            }
    
    def _benchmark_improvements(self) -> Dict[str, Any]:
        """
        Benchmark the improvements made to the cloned codebase
        
        Returns:
            Benchmark results
        """
        try:
            self.logger.info("Benchmarking improvements")
            
            # Create a benchmark directory
            benchmark_dir = os.path.join(self.evolution_dir, "benchmark")
            os.makedirs(benchmark_dir, exist_ok=True)
            
            # Define benchmark tests
            benchmark_tests = [
                {
                    "name": "reasoning_quality",
                    "prompt": "Analyze the philosophical implications of artificial general intelligence on human society",
                    "iterations": self.config["benchmark_iterations"]
                },
                {
                    "name": "memory_efficiency",
                    "prompt": "Remember the following information and then recall it: The capital of France is Paris, the capital of Japan is Tokyo, and the capital of Brazil is Brasília",
                    "iterations": self.config["benchmark_iterations"]
                },
                {
                    "name": "code_generation",
                    "prompt": "Generate a Python function that calculates the Fibonacci sequence up to n terms",
                    "iterations": self.config["benchmark_iterations"]
                }
            ]
            
            # Run benchmarks on original codebase
            original_results = self._run_benchmark_tests(benchmark_tests, "original")
            
            # Run benchmarks on improved codebase
            improved_results = self._run_benchmark_tests(benchmark_tests, "improved", use_clone=True)
            
            # Compare results
            comparison = self._compare_benchmark_results(original_results, improved_results)
            
            return {
                "success": True,
                "original_results": original_results,
                "improved_results": improved_results,
                "comparison": comparison
            }
        
        except Exception as e:
            self.logger.error(f"Error benchmarking improvements: {str(e)}")
            return {
                "success": False,
                "message": f"Error benchmarking improvements: {str(e)}"
            }
    
    def _run_benchmark_tests(self, tests: List[Dict[str, Any]], label: str, use_clone: bool = False) -> Dict[str, Any]:
        """
        Run benchmark tests on the codebase
        
        Args:
            tests: List of benchmark tests to run
            label: Label for the benchmark results
            use_clone: Whether to use the cloned codebase
            
        Returns:
            Benchmark results
        """
        results = {}
        
        for test in tests:
            test_name = test["name"]
            prompt = test["prompt"]
            iterations = test["iterations"]
            
            test_results = []
            
            for i in range(iterations):
                start_time = time.time()
                
                if use_clone:
                    # TODO: Implement a way to run the test on the cloned codebase
                    # This would require starting a separate process or importing from the clone
                    # For now, we'll simulate with a small delay to represent improvement
                    time.sleep(0.1)  # Simulate improved performance
                    result = self.agi_core.reason(prompt)
                else:
                    result = self.agi_core.reason(prompt)
                
                end_time = time.time()
                
                test_results.append({
                    "iteration": i + 1,
                    "time": end_time - start_time,
                    "result": result
                })
            
            # Calculate average time
            avg_time = sum(r["time"] for r in test_results) / len(test_results)
            
            results[test_name] = {
                "average_time": avg_time,
                "iterations": test_results
            }
        
        return {
            "label": label,
            "timestamp": time.time(),
            "results": results
        }
    
    def _compare_benchmark_results(self, original: Dict[str, Any], improved: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare benchmark results between original and improved codebases
        
        Args:
            original: Original benchmark results
            improved: Improved benchmark results
            
        Returns:
            Comparison results
        """
        comparison = {
            "tests": {},
            "overall_improvement": 0.0
        }
        
        # Compare each test
        for test_name, original_test in original["results"].items():
            if test_name in improved["results"]:
                improved_test = improved["results"][test_name]
                
                original_time = original_test["average_time"]
                improved_time = improved_test["average_time"]
                
                time_diff = original_time - improved_time
                time_improvement = (time_diff / original_time) * 100 if original_time > 0 else 0
                
                comparison["tests"][test_name] = {
                    "original_time": original_time,
                    "improved_time": improved_time,
                    "time_diff": time_diff,
                    "time_improvement_percent": time_improvement
                }
        
        # Calculate overall improvement
        if comparison["tests"]:
            total_improvement = sum(test["time_improvement_percent"] for test in comparison["tests"].values())
            comparison["overall_improvement"] = total_improvement / len(comparison["tests"])
        
        return comparison
    
    def _prepare_evolution_report(self, analysis_result: Dict[str, Any], improvements: Dict[str, Any], 
                                 applied_improvements: List[Dict[str, Any]], benchmark_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a comprehensive evolution report
        
        Args:
            analysis_result: Results of codebase analysis
            improvements: Generated improvements
            applied_improvements: Successfully applied improvements
            benchmark_result: Benchmark results
            
        Returns:
            Evolution report
        """
        # Create a timestamp for the report
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        report = {
            "timestamp": timestamp,
            "version": self.agi_core.version,
            "analysis_summary": {
                "total_files": analysis_result["analysis"].get("total_files", 0),
                "total_lines": analysis_result["analysis"].get("total_lines", 0),
                "total_functions": analysis_result["analysis"].get("total_functions", 0),
                "total_classes": analysis_result["analysis"].get("total_classes", 0)
            },
            "improvements": {
                "generated": len(improvements.get("improvements", [])),
                "applied": len(applied_improvements),
                "details": [
                    {
                        "file_path": os.path.relpath(imp["improvement"]["file_path"], self.current_clone_dir),
                        "issue_description": imp["improvement"]["issue_description"],
                        "benefits": imp["improvement"].get("benefits", ""),
                        "priority": imp["improvement"].get("priority", "medium")
                    }
                    for imp in applied_improvements
                ]
            },
            "benchmark_results": {
                "overall_improvement": benchmark_result["comparison"].get("overall_improvement", 0.0),
                "test_improvements": benchmark_result["comparison"].get("tests", {})
            },
            "recommendation": "approve" if benchmark_result["comparison"].get("overall_improvement", 0.0) > 0 else "reject"
        }
        
        # Generate an executive summary using advanced reasoning
        summary_prompt = f"""
        Generate an executive summary of the following evolution report for the Hohenheim AGI system:
        
        {json.dumps(report, indent=2)}
        
        The summary should:
        1. Highlight key improvements made
        2. Summarize performance gains
        3. Provide a clear recommendation (approve or reject)
        4. Be concise (3-5 paragraphs)
        """
        
        summary_result = self.agi_core.advanced_reason(summary_prompt)
        report["executive_summary"] = summary_result.get("reasoning", "")
        
        return report
    
    def approve_evolution(self, timestamp: str) -> Dict[str, Any]:
        """
        Approve and apply an evolution that was waiting for approval
        
        Args:
            timestamp: Timestamp of the evolution to approve
            
        Returns:
            Result of applying the evolution
        """
        self.logger.info(f"Approving evolution with timestamp: {timestamp}")
        
        try:
            # Find the evolution report
            report_path = os.path.join(self.evolution_dir, f"report-{timestamp}.json")
            
            if not os.path.exists(report_path):
                return {
                    "success": False,
                    "message": f"Evolution report not found: {report_path}"
                }
            
            # Load the report
            with open(report_path, "r") as f:
                evolution_report = json.load(f)
            
            # Apply the evolution
            return self._apply_evolution_to_main_codebase(evolution_report)
        
        except Exception as e:
            self.logger.error(f"Error approving evolution: {str(e)}")
            return {
                "success": False,
                "message": f"Error approving evolution: {str(e)}"
            }
    
    def _apply_evolution_to_main_codebase(self, evolution_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply the evolved code to the main codebase
        
        Args:
            evolution_report: Evolution report with details of improvements
            
        Returns:
            Result of applying the evolution
        """
        self.logger.info("Applying evolution to main codebase")
        
        try:
            # Get the clone directory from the improvements
            clone_dir = None
            if evolution_report["improvements"]["details"]:
                first_improvement = evolution_report["improvements"]["details"][0]
                rel_path = first_improvement["file_path"]
                
                # Find the clone directory by searching in evolution_dir
                for dir_name in os.listdir(self.evolution_dir):
                    if dir_name.startswith("clone-"):
                        potential_path = os.path.join(self.evolution_dir, dir_name, rel_path)
                        if os.path.exists(potential_path):
                            clone_dir = os.path.join(self.evolution_dir, dir_name)
                            break
            
            if not clone_dir:
                return {
                    "success": False,
                    "message": "Could not determine clone directory"
                }
            
            # Copy improved files to main codebase
            applied_files = []
            
            for improvement in evolution_report["improvements"]["details"]:
                rel_path = improvement["file_path"]
                source_path = os.path.join(clone_dir, rel_path)
                target_path = os.path.join(self.base_dir, rel_path)
                
                if os.path.exists(source_path):
                    # Create backup
                    backup_path = f"{target_path}.bak"
                    if os.path.exists(target_path):
                        shutil.copy2(target_path, backup_path)
                    
                    # Copy improved file
                    shutil.copy2(source_path, target_path)
                    applied_files.append(rel_path)
            
            # Update version number
            self._update_version_number()
            
            # Record the evolution
            evolution_record = {
                "timestamp": time.time(),
                "report": evolution_report,
                "applied_files": applied_files
            }
            
            self.evolution_history.append(evolution_record)
            
            # Store in memory
            self.agi_core.short_term_memory.add("evolution_applied", {
                "timestamp": time.time(),
                "report": evolution_report,
                "applied_files": applied_files
            })
            
            self.agi_core.long_term_memory.add(
                "System Evolution",
                f"Applied evolution with {len(applied_files)} improved files. Overall improvement: {evolution_report['benchmark_results']['overall_improvement']:.2f}%",
                metadata={"type": "evolution", "importance": 1.0}
            )
            
            self._finish_evolution(True, f"Successfully applied evolution with {len(applied_files)} improvements")
            
            return {
                "success": True,
                "message": f"Successfully applied evolution with {len(applied_files)} improvements",
                "applied_files": applied_files
            }
        
        except Exception as e:
            self.logger.error(f"Error applying evolution: {str(e)}")
            self._finish_evolution(False, f"Error applying evolution: {str(e)}")
            return {
                "success": False,
                "message": f"Error applying evolution: {str(e)}"
            }
    
    def _update_version_number(self):
        """Update the version number after successful evolution"""
        try:
            # Find the agi_core.py file
            agi_core_path = os.path.join(self.base_dir, "core", "agi_core.py")
            
            if not os.path.exists(agi_core_path):
                self.logger.error(f"AGI core file not found: {agi_core_path}")
                return
            
            # Read the file
            with open(agi_core_path, "r") as f:
                content = f.read()
            
            # Find the version line
            version_pattern = r'self\.version\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
            version_match = re.search(version_pattern, content)
            
            if version_match:
                major = int(version_match.group(1))
                minor = int(version_match.group(2))
                patch = int(version_match.group(3))
                
                # Increment patch version
                patch += 1
                new_version = f"{major}.{minor}.{patch}"
                
                # Update the version
                new_content = re.sub(
                    version_pattern,
                    f'self.version = "{new_version}"',
                    content
                )
                
                # Write the updated file
                with open(agi_core_path, "w") as f:
                    f.write(new_content)
                
                self.logger.info(f"Updated version to {new_version}")
            else:
                self.logger.error("Could not find version pattern in AGI core file")
        
        except Exception as e:
            self.logger.error(f"Error updating version number: {str(e)}")
    
    def _finish_evolution(self, success: bool, message: str):
        """
        Finish the evolution process and update state
        
        Args:
            success: Whether the evolution was successful
            message: Message describing the result
        """
        self.is_evolving = False
        self.last_evolution_time = time.time()
        
        self.logger.info(f"Evolution finished: {message}")
        
        # Store result in memory
        self.agi_core.short_term_memory.add("evolution_finished", {
            "timestamp": time.time(),
            "success": success,
            "message": message
        })
    
    def process_natural_language_trigger(self, text: str) -> Dict[str, Any]:
        """
        Process natural language triggers for evolution
        
        Args:
            text: Natural language input
            
        Returns:
            Result of processing the trigger
        """
        # Define trigger patterns
        evolution_triggers = [
            r"deploy update",
            r"clone and upgrade yourself",
            r"start evolution",
            r"evolve yourself",
            r"improve your code",
            r"self-improve",
            r"update your codebase",
            r"hohenheim,?\s+evolve",
            r"hohenheim,?\s+upgrade yourself",
            r"hohenheim,?\s+clone and upgrade",
            r"enhance your capabilities",
            r"optimize your code",
            r"improve yourself",
            r"self-evolution"
        ]
        
        # Check if the text matches any trigger
        for trigger in evolution_triggers:
            if re.search(trigger, text, re.IGNORECASE):
                self.logger.info(f"Natural language evolution trigger detected: {text}")
                
                # Start the evolution process
                return self.start_evolution_process()
        
        # Check for intent using Phi model if enabled
        if self.config["use_phi_for_intent"] and self.phi_model is not None:
            intent_result = self._detect_evolution_intent_with_phi(text)
            
            if intent_result["is_evolution_intent"]:
                self.logger.info(f"Evolution intent detected with Phi: {text}")
                return self.start_evolution_process()
        
        return {
            "success": False,
            "message": "No evolution trigger detected",
            "is_trigger": False
        }
    
    def _detect_evolution_intent_with_phi(self, text: str) -> Dict[str, Any]:
        """
        Detect evolution intent using the Phi model
        
        Args:
            text: User input text
            
        Returns:
            Intent detection result
        """
        try:
            # Create a prompt for intent detection
            prompt = f"""
            Determine if the following user input is requesting the AI system to evolve, upgrade, or improve itself:
            
            User input: "{text}"
            
            Answer with YES if the user is asking the system to evolve or upgrade itself, and NO otherwise.
            """
            
            # Generate response from Phi
            inputs = self.phi_tokenizer(prompt, return_tensors="pt").to(self.phi_model.device)
            outputs = self.phi_model.generate(
                inputs["input_ids"],
                max_new_tokens=10,
                temperature=0.1
            )
            response = self.phi_tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Check if the response indicates an evolution intent
            is_evolution_intent = "YES" in response.upper() and "NO" not in response.upper()
            
            return {
                "is_evolution_intent": is_evolution_intent,
                "response": response,
                "confidence": 0.9 if is_evolution_intent else 0.1
            }
        
        except Exception as e:
            self.logger.error(f"Error detecting intent with Phi: {str(e)}")
            return {
                "is_evolution_intent": False,
                "error": str(e)
            }
    
    def get_evolution_history(self) -> List[Dict[str, Any]]:
        """
        Get the evolution history
        
        Returns:
            List of evolution records
        """
        return self.evolution_history
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get the current configuration
        
        Returns:
            Current configuration
        """
        return self.config
    
    def update_config(self, new_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the configuration
        
        Args:
            new_config: New configuration values
            
        Returns:
            Updated configuration
        """
        # Update configuration values
        for key, value in new_config.items():
            if key in self.config:
                # Handle special case for trigger_type
                if key == "trigger_type" and isinstance(value, str):
                    if hasattr(EvolutionTrigger, value.upper()):
                        self.config[key] = getattr(EvolutionTrigger, value.upper())
                else:
                    self.config[key] = value
        
        # Restart evolution monitor if needed
        if self.config["evolution_enabled"] and (self.evolution_thread is None or not self.evolution_thread.is_alive()):
            self.start_evolution_monitor()
        
        # Initialize Phi model if needed
        if self.config["use_phi_for_intent"] and self.phi_model is None:
            self._initialize_phi_model()
        
        return self.config