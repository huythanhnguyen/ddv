"""
Enhanced Data Store for DDV Product Advisor with Whoosh Search Engine
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Whoosh imports
from whoosh.fields import Schema, TEXT, NUMERIC, DATETIME, ID, STORED
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import scoring
from whoosh.analysis import StandardAnalyzer

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "profiles"
INDEX_DIR = PROJECT_ROOT / "search_index"

# Data file paths
MERGED_PRODUCTS_FILE = DATA_DIR / "merged_products.json"


class EnhancedProductStore:
    """Enhanced data store with Whoosh search engine"""
    
    def __init__(self):
        self.products = []
        self.ix = None
        self._load_data()
        self._build_search_index()
    
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
    
    def _build_search_index(self):
        """Build Whoosh search index"""
        try:
            # Create index directory if not exists
            INDEX_DIR.mkdir(exist_ok=True)
            
            # Define schema
            schema = Schema(
                id=ID(stored=True),
                name=TEXT(stored=True, analyzer=StandardAnalyzer()),
                brand=TEXT(stored=True, analyzer=StandardAnalyzer()),
                category=TEXT(stored=True, analyzer=StandardAnalyzer()),
                price_current=NUMERIC(stored=True, numtype=int),
                price_original=NUMERIC(stored=True, numtype=int),
                price_currency=STORED,
                discount_percentage=NUMERIC(stored=True, numtype=int),
                promotions_free_gifts=TEXT(stored=True, analyzer=StandardAnalyzer()),
                promotions_vouchers=TEXT(stored=True, analyzer=StandardAnalyzer()),
                promotions_special_discounts=TEXT(stored=True, analyzer=StandardAnalyzer()),
                promotions_bundle_offers=TEXT(stored=True, analyzer=StandardAnalyzer()),
                specs_screen_size=TEXT(stored=True, analyzer=StandardAnalyzer()),
                specs_camera_main=TEXT(stored=True, analyzer=StandardAnalyzer()),
                specs_storage=TEXT(stored=True, analyzer=StandardAnalyzer()),
                specs_ram=TEXT(stored=True, analyzer=StandardAnalyzer()),
                specs_os=TEXT(stored=True, analyzer=StandardAnalyzer()),
                specs_chipset=TEXT(stored=True, analyzer=StandardAnalyzer()),
                availability=STORED,
                url=STORED,
                images=STORED,
                last_updated=STORED
            )
            
            # Create or open index
            if INDEX_DIR.exists() and any(INDEX_DIR.iterdir()):
                self.ix = open_dir(INDEX_DIR)
                print(f"✅ Opened existing search index")
            else:
                self.ix = create_in(INDEX_DIR, schema)
                print(f"✅ Created new search index")
            
            # Index all products
            self._index_products()
            
        except Exception as e:
            print(f"❌ Error building search index: {e}")
            self.ix = None
    
    def _index_products(self):
        """Index all products in search engine"""
        if not self.ix:
            return
        
        try:
            writer = self.ix.writer()
            
            for product in self.products:
                # Prepare document for indexing
                doc = {
                    'id': product.get('id', ''),
                    'name': product.get('name', ''),
                    'brand': product.get('brand', ''),
                    'category': product.get('category', ''),
                    'price_current': product.get('price', {}).get('current', 0),
                    'price_original': product.get('price', {}).get('original', 0),
                    'price_currency': product.get('price', {}).get('currency', 'VND'),
                    'discount_percentage': product.get('price', {}).get('discount_percentage', 0),
                    'promotions_free_gifts': ' '.join(filter(None, product.get('promotions', {}).get('free_gifts', []))),
                    'promotions_vouchers': ' '.join(filter(None, product.get('promotions', {}).get('vouchers', []))),
                    'promotions_special_discounts': ' '.join(filter(None, product.get('promotions', {}).get('special_discounts', []))),
                    'promotions_bundle_offers': ' '.join(filter(None, product.get('promotions', {}).get('bundle_offers', []))),
                    'specs_screen_size': product.get('specs', {}).get('screen_size', '') or '',
                    'specs_camera_main': product.get('specs', {}).get('camera_main', '') or '',
                    'specs_storage': product.get('specs', {}).get('storage', '') or '',
                    'specs_ram': product.get('specs', {}).get('ram', '') or '',
                    'specs_os': product.get('specs', {}).get('os', '') or '',
                    'specs_chipset': product.get('specs', {}).get('chipset', '') or '',
                    'availability': product.get('availability', ''),
                    'url': product.get('url', ''),
                    'images': json.dumps(product.get('images', [])),
                    'last_updated': product.get('last_updated', '')
                }
                
                writer.add_document(**doc)
            
            writer.commit()
            print(f"✅ Indexed {len(self.products)} products")
            
        except Exception as e:
            print(f"❌ Error indexing products: {e}")
            import traceback
            traceback.print_exc()
    
    def search_products(self, 
                       query: str = "",
                       filters: Optional[Dict[str, Any]] = None,
                       limit: int = 20) -> List[Dict[str, Any]]:
        """Enhanced search using Whoosh"""
        if not self.ix:
            return []
        
        try:
            with self.ix.searcher() as searcher:
                # Build query
                if query.strip():
                    # Multi-field text search
                    qp = MultifieldParser([
                        'name', 'brand', 'specs_screen_size', 'specs_camera_main',
                        'specs_storage', 'specs_ram', 'specs_os', 'specs_chipset',
                        'promotions_free_gifts', 'promotions_vouchers', 
                        'promotions_special_discounts', 'promotions_bundle_offers'
                    ], self.ix.schema)
                    q = qp.parse(query)
                else:
                    # Match all if no query
                    q = None
                
                # Apply filters
                filter_queries = []
                if filters:
                    # Brand filter
                    if filters.get('brand'):
                        brand_qp = QueryParser('brand', self.ix.schema)
                        brand_q = brand_qp.parse(f'brand:{filters["brand"]}')
                        filter_queries.append(brand_q)
                    
                    # Category filter
                    if filters.get('category'):
                        category_qp = QueryParser('category', self.ix.schema)
                        category_q = category_qp.parse(f'category:{filters["category"]}')
                        filter_queries.append(category_q)
                    
                    # Price range filter
                    if filters.get('price_min') is not None or filters.get('price_max') is not None:
                        price_min = filters.get('price_min', 0)
                        price_max = filters.get('price_max', float('inf'))
                        price_qp = QueryParser('price_current', self.ix.schema)
                        price_q = price_qp.parse(f'price_current:[{price_min} TO {price_max}]')
                        filter_queries.append(price_q)
                    
                    # Discount filter
                    if filters.get('min_discount'):
                        discount_qp = QueryParser('discount_percentage', self.ix.schema)
                        discount_q = discount_qp.parse(f'discount_percentage:[{filters["min_discount"]} TO]')
                        filter_queries.append(discount_q)
                
                # Combine queries
                if filter_queries:
                    if q:
                        # Combine text query with filters
                        from whoosh.query import And
                        q = And([q] + filter_queries)
                    else:
                        # Only filters
                        from whoosh.query import And
                        q = And(filter_queries)
                
                # Execute search
                if q:
                    results = searcher.search(q, limit=limit, sortedby='price_current')
                else:
                    # No query, return all with sorting
                    results = searcher.search(q, limit=limit, sortedby='price_current')
                
                # Convert results to product format
                products = []
                for result in results:
                    product = {
                        'id': result['id'],
                        'name': result['name'],
                        'brand': result['brand'],
                        'category': result['category'],
                        'price': {
                            'current': result['price_current'],
                            'original': result['price_original'],
                            'currency': result['price_currency'],
                            'discount_percentage': result['discount_percentage']
                        },
                        'promotions': {
                            'free_gifts': result['promotions_free_gifts'].split() if result['promotions_free_gifts'] else [],
                            'vouchers': result['promotions_vouchers'].split() if result['promotions_vouchers'] else [],
                            'special_discounts': result['promotions_special_discounts'].split() if result['promotions_special_discounts'] else [],
                            'bundle_offers': result['promotions_bundle_offers'].split() if result['promotions_bundle_offers'] else []
                        },
                        'specs': {
                            'screen_size': result['specs_screen_size'] or '',
                            'camera_main': result['specs_camera_main'] or '',
                            'storage': result['specs_storage'] or '',
                            'ram': result['specs_ram'] or '',
                            'os': result['specs_os'] or '',
                            'chipset': result['specs_chipset'] or ''
                        },
                        'availability': result['availability'] or '',
                        'url': result['url'] or '',
                        'images': json.loads(result['images']) if result['images'] else [],
                        'last_updated': result['last_updated'] or '',
                        'score': result.score,
                        'sku': ''  # Add empty sku field for compatibility
                    }
                    products.append(product)
                
                return products
                
        except Exception as e:
            print(f"❌ Error searching products: {e}")
            return []
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID"""
        for product in self.products:
            if product.get('id') == product_id:
                return product
        return None
    
    def get_products_by_brand(self, brand: str) -> List[Dict[str, Any]]:
        """Get products by brand"""
        return self.search_products(filters={'brand': brand})
    
    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get products by category"""
        return self.search_products(filters={'category': category})
    
    def get_products_by_price_range(self, min_price: int, max_price: int) -> List[Dict[str, Any]]:
        """Get products by price range"""
        return self.search_products(filters={'price_min': min_price, 'price_max': max_price})
    
    def get_products_with_discount(self, min_discount: int = 10) -> List[Dict[str, Any]]:
        """Get products with minimum discount percentage"""
        return self.search_products(filters={'min_discount': min_discount})
    
    def reload_data(self):
        """Reload data and rebuild index"""
        self._load_data()
        self._build_search_index()
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        if not self.ix:
            return {}
        
        try:
            with self.ix.searcher() as searcher:
                return {
                    'total_products': len(self.products),
                    'indexed_products': searcher.doc_count(),
                    'index_size_mb': sum(f.stat().st_size for f in INDEX_DIR.rglob('*') if f.is_file()) / (1024 * 1024)
                }
        except Exception as e:
            print(f"❌ Error getting search stats: {e}")
            return {}


# Global instance
enhanced_data_store = EnhancedProductStore()
