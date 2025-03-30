"""
Long-Term Memory - Vector database for persistent memory storage
Uses Chroma or FAISS for efficient vector storage and retrieval
"""

import os
import time
import logging
import json
import uuid
from typing import Dict, List, Any, Optional, Union
import datetime

class LongTermMemory:
    """
    Long-term memory system for the Hohenheim AGI.
    Uses vector databases (Chroma or FAISS) for efficient storage and semantic retrieval.
    """
    
    def __init__(self, config_manager):
        """
        Initialize the long-term memory system
        
        Args:
            config_manager: The configuration manager instance
        """
        self.config = config_manager
        self.logger = logging.getLogger("Hohenheim.LongTermMemory")
        
        # Get configuration
        self.vector_db_type = self.config.get("VECTOR_DB_TYPE", "chroma")
        self.vector_db_path = self.config.get("VECTOR_DB_PATH", "./data/vector_db")
        self.embedding_model = self.config.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        
        # Statistics
        self.stats = {
            "total_items": 0,
            "created_at": self.get_timestamp(),
            "last_access": self.get_timestamp()
        }
        
        # Initialize the vector database
        self._initialize_vector_db()
    
    def _initialize_vector_db(self) -> None:
        """Initialize the vector database based on configuration"""
        try:
            if self.vector_db_type.lower() == "chroma":
                self._initialize_chroma()
            elif self.vector_db_type.lower() == "faiss":
                self._initialize_faiss()
            else:
                self.logger.error(f"Unsupported vector database type: {self.vector_db_type}")
                raise ValueError(f"Unsupported vector database type: {self.vector_db_type}")
        except ImportError as e:
            self.logger.error(f"Failed to import required packages for {self.vector_db_type}: {str(e)}")
            self.logger.info("Falling back to in-memory vector storage")
            self._initialize_in_memory()
    
    def _initialize_chroma(self) -> None:
        """Initialize Chroma vector database"""
        try:
            import chromadb
            from chromadb.utils import embedding_functions
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.vector_db_path), exist_ok=True)
            
            # Initialize client
            self.client = chromadb.PersistentClient(path=self.vector_db_path)
            
            # Set up embedding function
            self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model
            )
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="hohenheim_memories",
                embedding_function=self.embedding_function
            )
            
            # Update stats
            self.stats["total_items"] = self.collection.count()
            self.stats["db_type"] = "chroma"
            
            self.logger.info(f"Initialized Chroma vector database with {self.stats['total_items']} items")
            
        except ImportError:
            self.logger.error("Failed to import chromadb. Please install with: pip install chromadb sentence-transformers")
            raise
    
    def _initialize_faiss(self) -> None:
        """Initialize FAISS vector database"""
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            import numpy as np
            import pickle
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.vector_db_path), exist_ok=True)
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(self.embedding_model)
            
            # Path for index and metadata
            index_path = os.path.join(self.vector_db_path, "faiss_index.bin")
            metadata_path = os.path.join(self.vector_db_path, "faiss_metadata.pkl")
            
            # Check if existing index and metadata
            if os.path.exists(index_path) and os.path.exists(metadata_path):
                # Load existing index and metadata
                self.index = faiss.read_index(index_path)
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
            else:
                # Create new index and metadata
                dimension = self.embedding_model.get_sentence_embedding_dimension()
                self.index = faiss.IndexFlatL2(dimension)
                self.metadata = []
            
            # Update stats
            self.stats["total_items"] = self.index.ntotal
            self.stats["db_type"] = "faiss"
            
            self.logger.info(f"Initialized FAISS vector database with {self.stats['total_items']} items")
            
        except ImportError:
            self.logger.error("Failed to import faiss. Please install with: pip install faiss-cpu sentence-transformers")
            raise
    
    def _initialize_in_memory(self) -> None:
        """Initialize in-memory vector storage as fallback"""
        self.logger.warning("Using in-memory storage for long-term memory (not persistent)")
        
        # Simple in-memory storage
        self.memories = []
        
        # Update stats
        self.stats["total_items"] = 0
        self.stats["db_type"] = "in-memory"
    
    def add(self, title: str, content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Add an item to long-term memory
        
        Args:
            title: Title or summary of the memory
            content: Main content of the memory
            metadata: Additional metadata for the memory
            
        Returns:
            Memory ID
        """
        # Generate a memory ID
        memory_id = str(uuid.uuid4())
        
        # Ensure metadata exists
        if metadata is None:
            metadata = {}
        
        # Add timestamp if not present
        if "timestamp" not in metadata:
            metadata["timestamp"] = self.get_timestamp()
        
        try:
            if self.stats.get("db_type") == "chroma":
                self._add_to_chroma(memory_id, title, content, metadata)
            elif self.stats.get("db_type") == "faiss":
                self._add_to_faiss(memory_id, title, content, metadata)
            else:
                self._add_to_memory(memory_id, title, content, metadata)
            
            # Update statistics
            self.stats["total_items"] += 1
            self.stats["last_access"] = self.get_timestamp()
            
            self.logger.debug(f"Added memory to long-term storage: {memory_id}")
            
            return memory_id
            
        except Exception as e:
            self.logger.error(f"Error adding to long-term memory: {str(e)}")
            # Fallback to in-memory if vector DB fails
            if self.stats.get("db_type") not in ["in-memory"]:
                self.logger.info("Falling back to in-memory storage")
                self._initialize_in_memory()
                return self._add_to_memory(memory_id, title, content, metadata)
            raise
    
    def _add_to_chroma(self, memory_id: str, title: str, content: str, metadata: Dict[str, Any]) -> None:
        """Add memory to Chroma database"""
        # Combine title and content for document
        document = f"{title}\n\n{content}"
        
        # Add metadata fields
        metadata_dict = {
            "title": title,
            "timestamp": metadata.get("timestamp", self.get_timestamp()),
            **metadata
        }
        
        # Add to collection
        self.collection.add(
            ids=[memory_id],
            documents=[document],
            metadatas=[metadata_dict]
        )
    
    def _add_to_faiss(self, memory_id: str, title: str, content: str, metadata: Dict[str, Any]) -> None:
        """Add memory to FAISS database"""
        import numpy as np
        import pickle
        import faiss
        
        # Combine title and content for embedding
        document = f"{title}\n\n{content}"
        
        # Generate embedding
        embedding = self.embedding_model.encode([document])[0]
        embedding = np.array([embedding]).astype('float32')
        
        # Add to index
        self.index.add(embedding)
        
        # Add metadata
        metadata_dict = {
            "id": memory_id,
            "title": title,
            "content": content,
            "timestamp": metadata.get("timestamp", self.get_timestamp()),
            **metadata
        }
        self.metadata.append(metadata_dict)
        
        # Save index and metadata
        faiss.write_index(self.index, os.path.join(self.vector_db_path, "faiss_index.bin"))
        with open(os.path.join(self.vector_db_path, "faiss_metadata.pkl"), 'wb') as f:
            pickle.dump(self.metadata, f)
    
    def _add_to_memory(self, memory_id: str, title: str, content: str, metadata: Dict[str, Any]) -> str:
        """Add to in-memory storage"""
        memory_item = {
            "id": memory_id,
            "title": title,
            "content": content,
            "timestamp": metadata.get("timestamp", self.get_timestamp()),
            "metadata": metadata
        }
        
        self.memories.append(memory_item)
        return memory_id
    
    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memories semantically related to the query
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching memory items
        """
        try:
            self.stats["last_access"] = self.get_timestamp()
            
            if self.stats.get("db_type") == "chroma":
                return self._search_chroma(query, limit)
            elif self.stats.get("db_type") == "faiss":
                return self._search_faiss(query, limit)
            else:
                return self._search_memory(query, limit)
                
        except Exception as e:
            self.logger.error(f"Error searching long-term memory: {str(e)}")
            return []
    
    def _search_chroma(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search in Chroma database"""
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results.get("distances", [[0] * len(results["ids"][0])])[0][i]
            })
        
        return formatted_results
    
    def _search_faiss(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search in FAISS database"""
        import numpy as np
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Search index
        k = min(limit, self.index.ntotal)
        if k == 0:
            return []
            
        distances, indices = self.index.search(query_embedding, k)
        
        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                metadata = self.metadata[idx]
                results.append({
                    "id": metadata["id"],
                    "title": metadata["title"],
                    "content": metadata["content"],
                    "metadata": metadata,
                    "distance": float(distances[0][i])
                })
        
        return results
    
    def _search_memory(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Search in in-memory storage"""
        # Simple string matching for in-memory
        query = query.lower()
        results = []
        
        for item in self.memories:
            title = item["title"].lower()
            content = item["content"].lower()
            
            if query in title or query in content:
                results.append(item)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID
        
        Args:
            memory_id: ID of the memory to retrieve
            
        Returns:
            Memory item or None if not found
        """
        try:
            self.stats["last_access"] = self.get_timestamp()
            
            if self.stats.get("db_type") == "chroma":
                results = self.collection.get(ids=[memory_id])
                if results["ids"]:
                    return {
                        "id": results["ids"][0],
                        "content": results["documents"][0],
                        "metadata": results["metadatas"][0]
                    }
                return None
                
            elif self.stats.get("db_type") == "faiss":
                for item in self.metadata:
                    if item["id"] == memory_id:
                        return item
                return None
                
            else:
                for item in self.memories:
                    if item["id"] == memory_id:
                        return item
                return None
                
        except Exception as e:
            self.logger.error(f"Error retrieving memory {memory_id}: {str(e)}")
            return None
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a memory by ID
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.stats.get("db_type") == "chroma":
                self.collection.delete(ids=[memory_id])
                self.stats["total_items"] = self.collection.count()
                return True
                
            elif self.stats.get("db_type") == "faiss":
                # FAISS doesn't support direct deletion
                # We would need to rebuild the index, which is complex
                # For now, just mark as deleted in metadata
                for i, item in enumerate(self.metadata):
                    if item["id"] == memory_id:
                        self.metadata[i]["deleted"] = True
                        
                        # Save updated metadata
                        with open(os.path.join(self.vector_db_path, "faiss_metadata.pkl"), 'wb') as f:
                            import pickle
                            pickle.dump(self.metadata, f)
                        
                        return True
                return False
                
            else:
                self.memories = [item for item in self.memories if item["id"] != memory_id]
                self.stats["total_items"] = len(self.memories)
                return True
                
        except Exception as e:
            self.logger.error(f"Error deleting memory {memory_id}: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics
        
        Returns:
            Dictionary of memory statistics
        """
        # Update total items count
        if self.stats.get("db_type") == "chroma":
            self.stats["total_items"] = self.collection.count()
        elif self.stats.get("db_type") == "faiss":
            self.stats["total_items"] = self.index.ntotal
        else:
            self.stats["total_items"] = len(self.memories)
        
        return dict(self.stats)
    
    @staticmethod
    def get_timestamp() -> str:
        """
        Get current timestamp in ISO format
        
        Returns:
            ISO formatted timestamp
        """
        return datetime.datetime.now().isoformat()