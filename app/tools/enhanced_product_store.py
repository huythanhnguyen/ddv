"""
Enhanced Data Store for DDV Product Advisor with Meilisearch Engine
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Meilisearch Engine import
from .meilisearch_engine import MeilisearchEngine

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "profiles"

# Data file paths
MERGED_PRODUCTS_FILE = DATA_DIR / "merged_products.json"


class EnhancedProductStore:
    """Enhanced data store with Meilisearch engine"""
    
    def __init__(self):
        self.products = []
        self.search_engine = None
        self._load_data()
        self._setup_search_engine()
    
    def _load_data(self):
        """Load merged products data"""
        try:
            if MERGED_PRODUCTS_FILE.exists():
                with open(MERGED_PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                print(f"✅ Loaded {len(self.products)} merged products")
            else:
                print(f"⚠️  Merged products file not found: {MERGED_PRODUCTS_FILE}")
                self.products = []
        except Exception as e:
            print(f"❌ Error loading merged products: {e}")
            self.products = []
    
    def _setup_search_engine(self):
        """Setup Meilisearch engine"""
        try:
            self.search_engine = MeilisearchEngine()
            print(f"✅ Meilisearch engine initialized")
        except Exception as e:
            print(f"❌ Error setting up search engine: {e}")
            self.search_engine = None
    

    
    def search_products(self, 
                       query: str = "",
                       filters: Optional[Dict[str, Any]] = None,
                       limit: int = 20,
                       sort: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Enhanced search using Meilisearch"""
        if not self.search_engine:
            return []
        
        try:
            # Use Meilisearch engine with built-in filtering
            results = self.search_engine.search_products(
                query=query, 
                filters=filters, 
                limit=limit,
                sort=sort
            )
            
            return results
            
        except Exception as e:
            print(f"❌ Error in Meilisearch: {e}")
            return []
    
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID using Meilisearch"""
        if self.search_engine:
            return self.search_engine.get_product_by_id(product_id)
        
        # Fallback to direct lookup
        for product in self.products:
            if product.get('id') == product_id:
                return product
        return None
    
    def get_products_by_brand(self, brand: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by brand using Meilisearch"""
        if self.search_engine:
            return self.search_engine.get_products_by_brand(brand, limit)
        return self.search_products(filters={'brand': brand}, limit=limit)
    
    def get_products_by_category(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by category using Meilisearch"""
        if self.search_engine:
            return self.search_engine.get_products_by_category(category, limit)
        return self.search_products(filters={'category': category}, limit=limit)
    
    def get_products_by_price_range(self, min_price: int, max_price: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by price range using Meilisearch"""
        if self.search_engine:
            return self.search_engine.get_products_by_price_range(min_price, max_price, limit)
        return self.search_products(filters={'price_min': min_price, 'price_max': max_price}, limit=limit)
    
    def get_products_with_discount(self, min_discount: int = 10, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products with minimum discount percentage using Meilisearch"""
        if self.search_engine:
            return self.search_engine.get_products_with_discount(min_discount, limit)
        return self.search_products(filters={'min_discount': min_discount}, limit=limit)
    
    def reload_data(self):
        """Reload data and reinitialize search engine"""
        self._load_data()
        self._setup_search_engine()
        # Reindex products in Meilisearch
        if self.search_engine:
            self.search_engine.reindex_products()
    
    def reindex_products(self):
        """Reindex all products in Meilisearch"""
        if self.search_engine:
            self.search_engine.reindex_products()
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        if not self.search_engine:
            return {}
        
        try:
            return self.search_engine.get_search_stats()
        except Exception as e:
            print(f"❌ Error getting search stats: {e}")
            return {}


# Global instance
enhanced_data_store = EnhancedProductStore()
