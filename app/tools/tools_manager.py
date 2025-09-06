"""
Centralized Tools Manager for DDV Product Advisor
Manages all tool instances and provides unified access
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .meilisearch_engine import MeilisearchEngine
from .enhanced_product_store import EnhancedProductStore

logger = logging.getLogger(__name__)

class ToolsManager:
    """Centralized manager for all tools and services"""
    
    def __init__(self):
        self._search_engine: Optional[MeilisearchEngine] = None
        self._product_store: Optional[EnhancedProductStore] = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize all tools and services"""
        try:
            logger.info("🔧 Initializing Tools Manager...")
            
            # Initialize product store (which includes search engine)
            self._product_store = EnhancedProductStore()
            self._search_engine = self._product_store.search_engine
            
            self._initialized = True
            logger.info("✅ Tools Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Tools Manager: {e}")
            self._initialized = False
            return False
    
    @property
    def is_initialized(self) -> bool:
        """Check if tools manager is initialized"""
        return self._initialized
    
    @property
    def product_store(self) -> Optional[EnhancedProductStore]:
        """Get product store instance"""
        return self._product_store
    
    @property
    def search_engine(self) -> Optional[MeilisearchEngine]:
        """Get search engine instance"""
        return self._search_engine
    
    def search_products(self, 
                       query: str = "",
                       filters: Optional[Dict[str, Any]] = None,
                       limit: int = 20,
                       sort: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search products using the configured search engine"""
        if not self._initialized or not self._product_store:
            logger.error("❌ Tools Manager not initialized")
            return []
        
        try:
            return self._product_store.search_products(
                query=query,
                filters=filters,
                limit=limit,
                sort=sort
            )
        except Exception as e:
            logger.error(f"❌ Error searching products: {e}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        if not self._initialized or not self._product_store:
            logger.error("❌ Tools Manager not initialized")
            return None
        
        try:
            return self._product_store.get_product_by_id(product_id)
        except Exception as e:
            logger.error(f"❌ Error getting product by ID: {e}")
            return None
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        if not self._initialized or not self._product_store:
            return {"error": "Tools Manager not initialized"}
        
        try:
            return self._product_store.get_search_stats()
        except Exception as e:
            logger.error(f"❌ Error getting search stats: {e}")
            return {"error": str(e)}
    
    def reindex_products(self) -> bool:
        """Reindex all products"""
        if not self._initialized or not self._product_store:
            logger.error("❌ Tools Manager not initialized")
            return False
        
        try:
            self._product_store.reindex_products()
            logger.info("✅ Products reindexed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error reindexing products: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on all tools"""
        health_status = {
            "tools_manager_initialized": self._initialized,
            "product_store_available": self._product_store is not None,
            "search_engine_available": self._search_engine is not None,
            "timestamp": None
        }
        
        if self._initialized and self._product_store:
            try:
                stats = self.get_search_stats()
                health_status.update({
                    "search_stats": stats,
                    "timestamp": stats.get("timestamp", "unknown")
                })
            except Exception as e:
                health_status["error"] = str(e)
        
        return health_status

# Global tools manager instance
tools_manager = ToolsManager()


