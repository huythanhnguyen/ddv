"""
Simple Meilisearch Engine for DDV Product Advisor
Inspired by personalized_shopping structure
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import meilisearch
    from meilisearch.errors import MeilisearchError
    MEILISEARCH_AVAILABLE = True
except ImportError:
    MEILISEARCH_AVAILABLE = False
    meilisearch = None
    MeilisearchError = Exception

from app.config_simple import MEILISEARCH_CONFIG, DATA_DIR, MERGED_PRODUCTS_FILE

logger = logging.getLogger(__name__)

class SimpleMeilisearchEngine:
    """Simple search engine using Meilisearch"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SimpleMeilisearchEngine, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if not self._initialized:
            self.client = None
            self.index = None
            self.products = []
            
            # Initialize Meilisearch client
            self._setup_client()
            
            # Load products data
            self._load_products()
            
            self._initialized = True
    
    def _setup_client(self):
        """Setup Meilisearch client"""
        if not MEILISEARCH_AVAILABLE:
            logger.warning("Meilisearch not available, using fallback")
            return
        
        try:
            if MEILISEARCH_CONFIG["api_key"]:
                self.client = meilisearch.Client(
                    url=MEILISEARCH_CONFIG["url"],
                    api_key=MEILISEARCH_CONFIG["api_key"],
                    timeout=MEILISEARCH_CONFIG["timeout"]
                )
            else:
                # No API key for development
                self.client = meilisearch.Client(
                    url=MEILISEARCH_CONFIG["url"],
                    timeout=MEILISEARCH_CONFIG["timeout"]
                )
            
            # Get or create index
            self.index = self.client.index(MEILISEARCH_CONFIG["index_name"])
            logger.info("✅ Meilisearch client initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Meilisearch: {e}")
            self.client = None
            self.index = None
    
    def _load_products(self):
        """Load products from JSON file"""
        try:
            if MERGED_PRODUCTS_FILE.exists():
                with open(MERGED_PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                logger.info(f"✅ Loaded {len(self.products)} products from file")
            else:
                logger.warning(f"Products file not found: {MERGED_PRODUCTS_FILE}")
                self.products = []
        except Exception as e:
            logger.error(f"❌ Failed to load products: {e}")
            self.products = []
    
    def search(self, query: str, limit: int = 20, enhanced_filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search products using Meilisearch or fallback"""
        
        # Try Meilisearch first
        if self.client and self.index:
            try:
                return self._meilisearch_search(query, limit, enhanced_filters)
            except Exception as e:
                logger.warning(f"Meilisearch failed: {e}, using fallback")
        
        # Fallback to simple text search
        return self._fallback_search(query, limit)
    
    def _meilisearch_search(self, query: str, limit: int, enhanced_filters: Optional[Dict]) -> List[Dict[str, Any]]:
        """Search using Meilisearch"""
        
        search_params = {
            "q": query,
            "limit": limit,
            "attributesToRetrieve": ["*"]
        }
        
        # Add filters
        if enhanced_filters:
            filter_conditions = []
            
            if enhanced_filters.get("price_max"):
                filter_conditions.append(f"price.current <= {enhanced_filters['price_max']}")
            if enhanced_filters.get("price_min"):
                filter_conditions.append(f"price.current >= {enhanced_filters['price_min']}")
            if enhanced_filters.get("brand"):
                filter_conditions.append(f"brand = '{enhanced_filters['brand']}'")
            if enhanced_filters.get("battery_min"):
                filter_conditions.append(f"specs.battery >= {enhanced_filters['battery_min']}")
            if enhanced_filters.get("camera_min"):
                filter_conditions.append(f"specs.camera >= {enhanced_filters['camera_min']}")
            if enhanced_filters.get("storage_min"):
                # Extract numeric value from storage string (e.g., "256GB" -> 256)
                storage_min = enhanced_filters["storage_min"]
                if isinstance(storage_min, str):
                    storage_min = int(storage_min.replace("GB", "").replace("gb", ""))
                filter_conditions.append(f"specs.storage >= {storage_min}")
            
            if filter_conditions:
                search_params["filter"] = " AND ".join(filter_conditions)
        
        # Execute search
        results = self.index.search(query, search_params)
        
        # Return hits
        return results.get("hits", [])
    
    def _fallback_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Simple text-based fallback search"""
        
        if not self.products:
            return []
        
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            score = 0
            name = product.get("name", "").lower()
            brand = product.get("brand", "").lower()
            
            # Score based on name and brand matches
            if query_lower in name:
                score += 10
            if query_lower in brand:
                score += 8
            
            # Check specs
            specs = product.get("specs", {})
            for spec_value in specs.values():
                if isinstance(spec_value, str) and query_lower in spec_value.lower():
                    score += 3
            
            if score > 0:
                product["_score"] = score
                results.append(product)
        
        # Sort by score and return top results
        results.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return results[:limit]
    
    def health_check(self) -> Dict[str, Any]:
        """Check Meilisearch health"""
        if not self.client:
            return {"status": "unavailable", "message": "Meilisearch client not initialized"}
        
        try:
            # Try to get index stats
            stats = self.index.get_stats()
            return {
                "status": "healthy",
                "message": "Meilisearch is running",
                "stats": stats
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Meilisearch error: {str(e)}"
            }
    
    @classmethod
    def reset_instance(cls):
        """Reset singleton instance (for testing)"""
        cls._instance = None
        cls._initialized = False
