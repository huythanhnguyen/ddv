"""Data access layer for DDV Product Advisor"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "profiles"

# Data file paths
PRODUCTS_FILE = DATA_DIR / "products.json"
OFFERS_FILE = DATA_DIR / "offers.json"
REVIEWS_FILE = DATA_DIR / "reviews.json"
STORES_FILE = DATA_DIR / "stores.json"


class DataStore:
    """Data store for DDV Product Advisor"""
    
    def __init__(self):
        self.products = []
        self.offers = []
        self.reviews = []
        self.stores = []
        self._load_data()
    
    def _load_data(self):
        """Load all data from JSON files"""
        try:
            # Load products
            if PRODUCTS_FILE.exists():
                with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                print(f"✅ Loaded {len(self.products)} products")
            else:
                print(f"⚠️  Products file not found: {PRODUCTS_FILE}")
            
            # Load offers
            if OFFERS_FILE.exists():
                with open(OFFERS_FILE, 'r', encoding='utf-8') as f:
                    self.offers = json.load(f)
                print(f"✅ Loaded {len(self.offers)} offers")
            else:
                print(f"⚠️  Offers file not found: {OFFERS_FILE}")
            
            # Load reviews
            if REVIEWS_FILE.exists():
                with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
                    self.reviews = json.load(f)
                print(f"✅ Loaded {len(self.reviews)} reviews")
            else:
                print(f"⚠️  Reviews file not found: {REVIEWS_FILE}")
            
            # Load stores
            if STORES_FILE.exists():
                with open(STORES_FILE, 'r', encoding='utf-8') as f:
                    self.stores = json.load(f)
                print(f"✅ Loaded {len(self.stores)} stores")
            else:
                print(f"⚠️  Stores file not found: {STORES_FILE}")
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
    
    def reload_data(self):
        """Reload data from files"""
        self._load_data()
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        for product in self.products:
            if product.get('id') == product_id:
                return product
        return None
    
    def get_product_by_name(self, product_name: str) -> Optional[Dict[str, Any]]:
        """Get product by name (fuzzy search)"""
        product_name_lower = product_name.lower()
        for product in self.products:
            if product_name_lower in product.get('name', '').lower():
                return product
        return None
    
    def search_products(self, 
                       budget_min: Optional[int] = None,
                       budget_max: Optional[int] = None,
                       brands: Optional[List[str]] = None,
                       features: Optional[List[str]] = None,
                       limit: int = 10) -> List[Dict[str, Any]]:
        """Search products by criteria"""
        results = []
        
        for product in self.products:
            # Budget filter
            if budget_min is not None and product.get('price_vnd', 0) < budget_min:
                continue
            if budget_max is not None and product.get('price_vnd', 0) > budget_max:
                continue
            
            # Brand filter
            if brands:
                product_brand = product.get('brand', '').lower()
                if not any(brand.lower() in product_brand or product_brand in brand.lower() for brand in brands):
                    continue
            
            # Feature filter
            if features:
                # Combine all feature-related fields
                product_features = []
                product_features.extend(product.get('promotions', []))
                product_features.extend(product.get('camera_features', []))
                if product.get('screen_size'):
                    product_features.append(product.get('screen_size'))
                if product.get('camera_main'):
                    product_features.append(product.get('camera_main'))
                if product.get('storage'):
                    product_features.append(product.get('storage'))
                
                product_features_text = ' '.join(product_features).lower()
                if not any(feature.lower() in product_features_text for feature in features):
                    continue
            
            results.append(product)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_offer_by_product_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get offer by product ID"""
        for offer in self.offers:
            if offer.get('product_id') == product_id:
                return offer
        return None
    
    def get_review_by_product_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get review by product ID"""
        for review in self.reviews:
            if review.get('product_id') == product_id:
                return review
        return None
    
    def get_stores_by_location(self, location: str) -> List[Dict[str, Any]]:
        """Get stores by location"""
        location_lower = location.lower()
        results = []
        
        for store in self.stores:
            store_city = store.get('city', '').lower()
            store_region = store.get('region', '').lower()
            
            if (location_lower in store_city or 
                location_lower in store_region or
                store_city in location_lower or
                store_region in location_lower):
                results.append(store)
        
        return results
    
    def get_stores_with_product(self, product_id: str) -> List[Dict[str, Any]]:
        """Get stores that have a specific product"""
        offer = self.get_offer_by_product_id(product_id)
        if not offer:
            return []
        
        available_store_ids = offer.get('availability', {}).get('available_stores', [])
        results = []
        
        for store in self.stores:
            if store.get('id') in available_store_ids:
                results.append(store)
        
        return results
    
    def get_products_by_brand(self, brand: str) -> List[Dict[str, Any]]:
        """Get products by brand"""
        brand_lower = brand.lower()
        results = []
        
        for product in self.products:
            if brand_lower in product.get('brand', '').lower():
                results.append(product)
        
        return results
    
    def get_products_by_price_range(self, min_price: int, max_price: int) -> List[Dict[str, Any]]:
        """Get products by price range"""
        results = []
        
        for product in self.products:
            price = product.get('price_vnd', 0)
            if min_price <= price <= max_price:
                results.append(product)
        
        return results
    
    def get_top_discounted_products(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get products with highest discounts"""
        products_with_discounts = []
        
        for offer in self.offers:
            product = self.get_product_by_id(offer.get('product_id'))
            if not product:
                continue
            
            # Calculate discount percentage
            current_price = offer.get('pricing', {}).get('current_prices', [{}])[0].get('price_vnd', 0)
            original_price = offer.get('pricing', {}).get('current_prices', [{}])[0].get('original_price_vnd', 0)
            
            if current_price and original_price and original_price > current_price:
                discount_percent = ((original_price - current_price) / original_price) * 100
                products_with_discounts.append({
                    'product': product,
                    'offer': offer,
                    'discount_percent': discount_percent
                })
        
        # Sort by discount percentage (highest first)
        products_with_discounts.sort(key=lambda x: x['discount_percent'], reverse=True)
        
        return products_with_discounts[:limit]
    
    def compare_products(self, product_id_1: str, product_id_2: str) -> Dict[str, Any]:
        """Compare two products"""
        product_1 = self.get_product_by_id(product_id_1)
        product_2 = self.get_product_by_id(product_id_2)
        
        if not product_1 or not product_2:
            return {}
        
        offer_1 = self.get_offer_by_product_id(product_id_1)
        offer_2 = self.get_offer_by_product_id(product_id_2)
        
        review_1 = self.get_review_by_product_id(product_id_1)
        review_2 = self.get_review_by_product_id(product_id_2)
        
        return {
            'product_1': {
                'info': product_1,
                'offer': offer_1,
                'review': review_1
            },
            'product_2': {
                'info': product_2,
                'offer': offer_2,
                'review': review_2
            }
        }
    
    def get_store_info(self, store_id: str) -> Optional[Dict[str, Any]]:
        """Get store information by ID"""
        for store in self.stores:
            if store.get('id') == store_id:
                return store
        return None
    
    def search_stores(self, query: str) -> List[Dict[str, Any]]:
        """Search stores by query"""
        query_lower = query.lower()
        results = []
        
        for store in self.stores:
            store_name = store.get('name', '').lower()
            store_address = store.get('address', '').lower()
            store_city = store.get('city', '').lower()
            
            if (query_lower in store_name or 
                query_lower in store_address or 
                query_lower in store_city):
                results.append(store)
        
        return results
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get summary of all data"""
        return {
            'total_products': len(self.products),
            'total_offers': len(self.offers),
            'total_reviews': len(self.reviews),
            'total_stores': len(self.stores),
            'brands': list(set(product.get('brand') for product in self.products if product.get('brand'))),
            'categories': list(set(product.get('category') for product in self.products if product.get('category'))),
            'regions': list(set(store.get('region') for store in self.stores if store.get('region'))),
            'cities': list(set(store.get('city') for store in self.stores if store.get('city')))
        }


# Global data store instance
data_store = DataStore()
