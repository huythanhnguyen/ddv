"""
Meilisearch Engine for DDV Product Advisor
Replaces Gemini AI search with fast, relevant full-text and hybrid search using Meilisearch
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

import meilisearch
from meilisearch.errors import MeilisearchError

from app.config import meilisearch_config

# Setup logging
logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "profiles"
MERGED_PRODUCTS_FILE = DATA_DIR / "merged_products.json"


class MeilisearchEngine:
    """Fast search engine using Meilisearch for full-text and hybrid search"""
    
    def __init__(self):
        self.products = []
        self.client = None
        self.index = None
        self.index_name = "ddv_products"
        
        # Initialize Meilisearch client
        self._setup_meilisearch_client()
        
        # Load products data
        self._load_products()
        
        # Setup index and add documents
        self._setup_index()
    
    def _setup_meilisearch_client(self):
        """Setup Meilisearch client"""
        try:
            self.client = meilisearch.Client(
                url=meilisearch_config.url,
                api_key=meilisearch_config.api_key
            )
            
            # Test connection
            health = self.client.health()
            logger.info(f"✅ Meilisearch client connected: {health}")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Meilisearch client: {e}")
            self.client = None
    
    def _load_products(self):
        """Load products data from JSON file"""
        try:
            if MERGED_PRODUCTS_FILE.exists():
                with open(MERGED_PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                    self.products = json.load(f)
                logger.info(f"✅ Loaded {len(self.products)} products for search")
            else:
                logger.warning(f"⚠️ Products file not found: {MERGED_PRODUCTS_FILE}")
                self.products = []
        except Exception as e:
            logger.error(f"❌ Error loading products: {e}")
            self.products = []
    
    def _setup_index(self):
        """Setup Meilisearch index with proper configuration"""
        if not self.client:
            logger.error("❌ Meilisearch client not available")
            return
        
        try:
            # Get or create index
            try:
                self.index = self.client.index(self.index_name)
                logger.info(f"✅ Using existing index: {self.index_name}")
            except MeilisearchError:
                # Create new index
                self.index = self.client.create_index(self.index_name, {'primaryKey': 'id'})
                logger.info(f"✅ Created new index: {self.index_name}")
            
            # Configure index settings for optimal search
            self._configure_index_settings()
            
            # Add documents to index
            self._index_products()
            
        except Exception as e:
            logger.error(f"❌ Error setting up index: {e}")
            self.index = None
    
    def _configure_index_settings(self):
        """Configure Meilisearch index settings for optimal product search"""
        try:
            # Configure searchable attributes (what can be searched)
            # Include ALL fields for comprehensive search
            searchable_attributes = [
                'name',
                'brand', 
                'category',
                'availability',
                'url',
                # All specs fields
                'specs.screen_size',
                'specs.screen_tech',
                'specs.resolution',
                'specs.camera_main',
                'specs.camera_front',
                'specs.camera_features',
                'specs.os',
                'specs.chipset',
                'specs.cpu_cores',
                'specs.gpu',
                'specs.ram',
                'specs.storage',
                'specs.network',
                'specs.sim',
                'specs.bluetooth',
                'specs.usb',
                'specs.wifi',
                'specs.gps',
                'specs.battery',
                'specs.weight',
                'specs.dimensions',
                'specs.colors',
                'specs.materials',
                'specs.water_resistance',
                'specs.biometric',
                'specs.sensors',
                'specs.audio',
                'specs.charging',
                'specs.connectivity',
                # All promotions fields
                'promotions.free_gifts',
                'promotions.vouchers',
                'promotions.special_discounts',
                'promotions.bundle_offers',
                'promotions.description',
                'promotions.terms',
                # Price fields
                'price.currency',
                # Images (for future use)
                'images',
                # Combined searchable text (contains all flattened data)
                '_searchable_text'
            ]
            
            # Configure filterable attributes (what can be filtered)
            filterable_attributes = [
                'brand',
                'category',
                'price.current',
                'price.original',
                'price.discount_percentage',
                'specs.screen_size',
                'specs.storage',
                'specs.ram',
                'availability'
            ]
            
            # Configure sortable attributes
            sortable_attributes = [
                'price.current',
                'price.original',
                'price.discount_percentage',
                'name',
                'brand'
            ]
            
            # Configure ranking rules (how results are ranked)
            ranking_rules = [
                'words',
                'typo',
                'proximity',
                'attribute',
                'sort',
                'exactness'
            ]
            
            # Configure synonyms for better Vietnamese search
            synonyms = {
                'điện thoại': ['phone', 'smartphone', 'mobile'],
                'iphone': ['apple'],
                'samsung': ['galaxy'],
                'xiaomi': ['mi'],
                'oppo': ['oneplus'],
                'vivo': ['iqoo'],
                'realme': ['real me'],
                'pin': ['battery'],
                'camera': ['chụp ảnh', 'chụp hình'],
                'màn hình': ['screen', 'display'],
                'bộ nhớ': ['storage', 'memory'],
                'ram': ['memory'],
                'chip': ['processor', 'cpu'],
                'hệ điều hành': ['os', 'operating system']
            }
            
            # Apply settings
            settings = {
                'searchableAttributes': searchable_attributes,
                'filterableAttributes': filterable_attributes,
                'sortableAttributes': sortable_attributes,
                'rankingRules': ranking_rules,
                'synonyms': synonyms,
                'stopWords': ['và', 'của', 'cho', 'với', 'từ', 'đến', 'trong', 'ngoài'],
                'typoTolerance': {
                    'enabled': True,
                    'minWordSizeForTypos': {
                        'oneTypo': 4,
                        'twoTypos': 8
                    }
                }
            }
            
            self.index.update_settings(settings)
            logger.info("✅ Meilisearch index settings configured")
            
        except Exception as e:
            logger.error(f"❌ Error configuring index settings: {e}")
    
    def _index_products(self):
        """Index all products in Meilisearch"""
        if not self.index or not self.products:
            return
        
        try:
            # Prepare documents for indexing
            documents = []
            for product in self.products:
                # Flatten nested structures for better search
                doc = {
                    'id': product.get('id', ''),
                    'name': product.get('name', ''),
                    'brand': product.get('brand', ''),
                    'category': product.get('category', ''),
                    'availability': product.get('availability', ''),
                    'url': product.get('url', ''),
                    'images': product.get('images', []),
                    'last_updated': product.get('last_updated', ''),
                    'created_at': datetime.now().isoformat()
                }
                
                # Add price information
                price = product.get('price', {})
                doc['price'] = price
                
                # Add specs (flatten for better search)
                specs = product.get('specs', {})
                doc['specs'] = specs
                
                # Add promotions (flatten for better search)
                promotions = product.get('promotions', {})
                doc['promotions'] = promotions
                
                # Create searchable text fields by flattening arrays
                searchable_text = []
                
                # Add name and brand
                searchable_text.append(doc['name'])
                searchable_text.append(doc['brand'])
                searchable_text.append(doc['category'])
                
                # Add all specs values
                for spec_key, spec_value in specs.items():
                    if isinstance(spec_value, str):
                        searchable_text.append(spec_value)
                    elif isinstance(spec_value, list):
                        searchable_text.extend([str(item) for item in spec_value])
                    else:
                        searchable_text.append(str(spec_value))
                
                # Add all promotions values
                for promo_key, promo_value in promotions.items():
                    if isinstance(promo_value, list):
                        searchable_text.extend([str(item) for item in promo_value])
                    elif isinstance(promo_value, str):
                        searchable_text.append(promo_value)
                
                # Add combined searchable text
                doc['_searchable_text'] = ' '.join(searchable_text)
                
                documents.append(doc)
            
            # Add documents to index
            task = self.index.add_documents(documents)
            logger.info(f"✅ Indexed {len(documents)} products. Task ID: {task.task_uid}")
            
        except Exception as e:
            logger.error(f"❌ Error indexing products: {e}")
    
    def search_products(self, 
                       query: str, 
                       filters: Optional[Dict[str, Any]] = None,
                       limit: int = 20,
                       sort: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search products using Meilisearch
        
        Args:
            query: Search query (Vietnamese/English)
            filters: Optional filters to apply
            limit: Maximum number of results
            sort: Optional sorting criteria
            
        Returns:
            List of matching products
        """
        if not self.index:
            logger.warning("Meilisearch index not available, using fallback search")
            return self._fallback_search(query, limit)
        
        if not query or not query.strip():
            return []
        
        try:
            start_time = time.time()
            
            # Prepare search parameters
            search_params = {
                'limit': limit,
                'attributesToRetrieve': ['*'],
                'attributesToHighlight': ['name', 'brand', 'category', '_searchable_text'],
                'highlightPreTag': '<mark>',
                'highlightPostTag': '</mark>'
            }
            
            # Add filters if provided
            if filters:
                filter_conditions = []
                
                if filters.get('brand'):
                    filter_conditions.append(f"brand = '{filters['brand']}'")
                
                if filters.get('category'):
                    filter_conditions.append(f"category = '{filters['category']}'")
                
                if filters.get('price_min') is not None:
                    filter_conditions.append(f"price.current >= {filters['price_min']}")
                
                if filters.get('price_max') is not None:
                    filter_conditions.append(f"price.current <= {filters['price_max']}")
                
                if filters.get('min_discount'):
                    filter_conditions.append(f"price.discount_percentage >= {filters['min_discount']}")
                
                if filter_conditions:
                    search_params['filter'] = ' AND '.join(filter_conditions)
            
            # Add sorting if provided
            if sort:
                search_params['sort'] = sort
            
            # Perform search
            results = self.index.search(query, search_params)
            
            # Process results
            products = []
            for hit in results.get('hits', []):
                product = hit.copy()
                
                # Add search metadata
                product['search_metadata'] = {
                    'relevance_score': hit.get('_rankingScore', 0.0),
                    'formatted': hit.get('_formatted', {}),
                    'matched_terms': hit.get('_matchesInfo', {})
                }
                
                products.append(product)
            
            search_time = time.time() - start_time
            logger.info(f"🔍 Meilisearch completed in {search_time:.3f}s for query: {query}")
            logger.info(f"📊 Found {len(products)} results")
            
            return products
            
        except Exception as e:
            logger.error(f"❌ Meilisearch failed for query '{query}': {e}")
            logger.info("🔄 Falling back to simple text search")
            return self._fallback_search(query, limit)
    
    def _fallback_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Simple text-based fallback search when Meilisearch fails"""
        if not query or not self.products:
            return []
        
        query_lower = query.lower()
        results = []
        
        for product in self.products:
            score = 0
            
            # Check name
            name = product.get('name', '').lower()
            if query_lower in name:
                score += 10
            
            # Check brand
            brand = product.get('brand', '').lower()
            if query_lower in brand:
                score += 8
            
            # Check category
            category = product.get('category', '').lower()
            if query_lower in category:
                score += 5
            
            # Check specs
            specs = product.get('specs', {})
            for spec_value in specs.values():
                if isinstance(spec_value, str) and query_lower in spec_value.lower():
                    score += 3
            
            if score > 0:
                product_copy = product.copy()
                product_copy['search_metadata'] = {
                    'relevance_score': min(score / 20, 1.0),
                    'formatted': {},
                    'matched_terms': {}
                }
                results.append(product_copy)
        
        # Sort by score and limit results
        results.sort(key=lambda x: x['search_metadata']['relevance_score'], reverse=True)
        return results[:limit]
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID using Meilisearch"""
        if not self.index:
            # Fallback to direct lookup
            for product in self.products:
                if product.get('id') == product_id:
                    return product
            return None
        
        try:
            result = self.index.get_document(product_id)
            return result
        except MeilisearchError:
            return None
    
    def get_products_by_brand(self, brand: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by brand using Meilisearch filter"""
        return self.search_products("", filters={'brand': brand}, limit=limit)
    
    def get_products_by_category(self, category: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by category using Meilisearch filter"""
        return self.search_products("", filters={'category': category}, limit=limit)
    
    def get_products_by_price_range(self, min_price: int, max_price: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by price range using Meilisearch filter"""
        return self.search_products("", filters={'price_min': min_price, 'price_max': max_price}, limit=limit)
    
    def get_products_with_discount(self, min_discount: int = 10, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products with minimum discount using Meilisearch filter"""
        return self.search_products("", filters={'min_discount': min_discount}, limit=limit)
    
    def reindex_products(self):
        """Reindex all products (useful when data changes)"""
        if not self.index:
            logger.error("❌ Meilisearch index not available")
            return
        
        try:
            # Clear existing documents
            self.index.delete_all_documents()
            
            # Reindex all products
            self._index_products()
            logger.info("✅ Products reindexed successfully")
            
        except Exception as e:
            logger.error(f"❌ Error reindexing products: {e}")
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        stats = {
            'total_products': len(self.products),
            'meilisearch_url': meilisearch_config.url,
            'index_name': self.index_name,
            'client_connected': self.client is not None,
            'index_available': self.index is not None
        }
        
        if self.index:
            try:
                index_stats = self.index.get_stats()
                stats.update({
                    'indexed_documents': getattr(index_stats, 'number_of_documents', 0),
                    'index_size': getattr(index_stats, 'database_size', 0),
                    'last_update': getattr(index_stats, 'last_update', '')
                })
            except Exception as e:
                logger.error(f"❌ Error getting index stats: {e}")
        
        return stats
    
    def clear_index(self):
        """Clear all documents from the index"""
        if not self.index:
            logger.error("❌ Meilisearch index not available")
            return
        
        try:
            task = self.index.delete_all_documents()
            logger.info(f"🗑️ Index cleared. Task ID: {task.task_uid}")
        except Exception as e:
            logger.error(f"❌ Error clearing index: {e}")

