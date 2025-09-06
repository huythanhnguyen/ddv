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
from .gemini_utils_tool import gemini_utils

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
        """Enhanced search using Meilisearch with AI-powered query optimization"""
        if not self.search_engine:
            return []
        
        try:
            # Use Gemini AI to optimize search query and extract filters
            optimized_query = query
            enhanced_filters = filters or {}
            
            if query:
                # Analyze search intent and optimize query
                search_intent = gemini_utils.analyze_search_intent(query)
                
                # Use optimized query if available
                if search_intent.get('search_query'):
                    optimized_query = search_intent['search_query']
                    print(f"🔍 AI optimized query: '{query}' → '{optimized_query}'")
                
                # Extract additional filters from natural language
                budget_min, budget_max = gemini_utils.extract_budget_from_text(query)
                if budget_min is not None or budget_max is not None:
                    enhanced_filters['price_min'] = budget_min
                    enhanced_filters['price_max'] = budget_max
                    print(f"💰 AI extracted budget: {budget_min}-{budget_max}")
                
                brands = gemini_utils.extract_brands_from_text(query)
                if brands:
                    enhanced_filters['brand'] = brands[0]  # Use first brand for filter
                    print(f"🏷️ AI extracted brand: {brands}")
            
            # Use Meilisearch engine with AI-enhanced parameters
            results = self.search_engine.search_products(
                query=optimized_query, 
                filters=enhanced_filters, 
                limit=limit,
                sort=sort
            )
            
            return results
            
        except Exception as e:
            print(f"❌ Error in enhanced search: {e}")
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
    
    def get_ai_recommendations(self, user_query: str, limit: int = 5) -> Dict[str, Any]:
        """Get AI-powered product recommendations based on user query"""
        try:
            # Search for products first
            products = self.search_products(query=user_query, limit=limit * 2)
            
            if not products:
                return {
                    "success": False,
                    "message": "Không tìm thấy sản phẩm phù hợp",
                    "recommendations": []
                }
            
            # Analyze user requirements using Gemini AI
            user_requirements = {
                "query": user_query,
                "budget_range": gemini_utils.extract_budget_from_text(user_query),
                "brands": gemini_utils.extract_brands_from_text(user_query),
                "features": gemini_utils.extract_features_from_text(user_query),
                "intent": gemini_utils.analyze_search_intent(user_query)
            }
            
            # Generate AI recommendations
            recommendation_text = gemini_utils.generate_product_recommendation(
                user_requirements, products[:limit]
            )
            
            return {
                "success": True,
                "message": recommendation_text,
                "recommendations": products[:limit],
                "user_requirements": user_requirements,
                "total_found": len(products)
            }
            
        except Exception as e:
            print(f"❌ Error generating AI recommendations: {e}")
            return {
                "success": False,
                "message": f"Lỗi khi tạo gợi ý: {str(e)}",
                "recommendations": []
            }


# Global instance
enhanced_data_store = EnhancedProductStore()
