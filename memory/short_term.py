"""
Short-Term Memory - RAM-like memory system for the AGI
Stores recent interactions, context, and temporary information
"""

import time
import logging
import json
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
import datetime

class ShortTermMemory:
    """
    Short-term memory system for the Hohenheim AGI.
    Stores recent interactions, context, and temporary information in a RAM-like structure.
    """
    
    def __init__(self, config_manager, max_size: int = 1000):
        """
        Initialize the short-term memory system
        
        Args:
            config_manager: The configuration manager instance
            max_size: Maximum number of memory items to store
        """
        self.config = config_manager
        self.logger = logging.getLogger("Hohenheim.ShortTermMemory")
        
        # Memory storage - organized by type
        self.memories = defaultdict(lambda: deque(maxlen=max_size))
        
        # Global memory queue for chronological access
        self.memory_timeline = deque(maxlen=max_size)
        
        # Memory statistics
        self.stats = {
            "total_items": 0,
            "items_by_type": defaultdict(int),
            "created_at": self.get_timestamp()
        }
        
        self.logger.info(f"Short-term memory initialized with max size: {max_size}")
    
    def add(self, memory_type: str, data: Dict[str, Any]) -> str:
        """
        Add an item to short-term memory
        
        Args:
            memory_type: Type of memory (e.g., "command", "response", "reasoning")
            data: Memory data to store
            
        Returns:
            Memory ID
        """
        # Generate a memory ID
        memory_id = f"{memory_type}_{int(time.time() * 1000)}"
        
        # Ensure timestamp exists
        if "timestamp" not in data:
            data["timestamp"] = self.get_timestamp()
        
        # Create memory item
        memory_item = {
            "id": memory_id,
            "type": memory_type,
            "data": data,
            "created_at": self.get_timestamp()
        }
        
        # Add to type-specific queue
        self.memories[memory_type].append(memory_item)
        
        # Add to timeline
        self.memory_timeline.append(memory_item)
        
        # Update statistics
        self.stats["total_items"] += 1
        self.stats["items_by_type"][memory_type] += 1
        
        self.logger.debug(f"Added memory item: {memory_id} of type {memory_type}")
        
        return memory_id
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory item by ID
        
        Args:
            memory_id: The memory ID to retrieve
            
        Returns:
            Memory item or None if not found
        """
        # Extract memory type from ID
        if "_" not in memory_id:
            self.logger.warning(f"Invalid memory ID format: {memory_id}")
            return None
            
        memory_type = memory_id.split("_")[0]
        
        # Search in the specific memory type queue
        for item in self.memories[memory_type]:
            if item["id"] == memory_id:
                return item
        
        self.logger.warning(f"Memory item not found: {memory_id}")
        return None
    
    def get_by_type(self, memory_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent memories of a specific type
        
        Args:
            memory_type: Type of memories to retrieve
            limit: Maximum number of items to return
            
        Returns:
            List of memory items
        """
        items = list(self.memories[memory_type])
        
        # Return most recent items first
        return items[-limit:][::-1]
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent memories regardless of type
        
        Args:
            limit: Maximum number of items to return
            
        Returns:
            List of recent memory items
        """
        items = list(self.memory_timeline)
        
        # Return most recent items first
        return items[-limit:][::-1]
    
    def search(self, query: str, memory_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for memories containing the query string
        
        Args:
            query: Search query
            memory_type: Optional type filter
            limit: Maximum number of results
            
        Returns:
            List of matching memory items
        """
        results = []
        query = query.lower()
        
        # Determine which memories to search
        if memory_type:
            memories_to_search = list(self.memories[memory_type])
        else:
            memories_to_search = list(self.memory_timeline)
        
        # Simple string matching search
        for item in memories_to_search:
            # Convert data to string for searching
            item_str = json.dumps(item["data"]).lower()
            
            if query in item_str:
                results.append(item)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def clear(self, memory_type: str = None) -> None:
        """
        Clear memories
        
        Args:
            memory_type: Type of memories to clear, or None for all
        """
        if memory_type:
            self.logger.info(f"Clearing memories of type: {memory_type}")
            self.memories[memory_type].clear()
            
            # Update timeline to remove cleared items
            self.memory_timeline = deque(
                [item for item in self.memory_timeline if item["type"] != memory_type],
                maxlen=self.memory_timeline.maxlen
            )
            
            # Update statistics
            self.stats["total_items"] -= self.stats["items_by_type"][memory_type]
            self.stats["items_by_type"][memory_type] = 0
        else:
            self.logger.info("Clearing all short-term memories")
            self.memories.clear()
            self.memory_timeline.clear()
            
            # Reset statistics
            self.stats["total_items"] = 0
            self.stats["items_by_type"] = defaultdict(int)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics
        
        Returns:
            Dictionary of memory statistics
        """
        # Update stats with current counts
        self.stats["total_items"] = len(self.memory_timeline)
        for memory_type in self.memories:
            self.stats["items_by_type"][memory_type] = len(self.memories[memory_type])
        
        return dict(self.stats)
    
    @staticmethod
    def get_timestamp() -> str:
        """
        Get current timestamp in ISO format
        
        Returns:
            ISO formatted timestamp
        """
        return datetime.datetime.now().isoformat()