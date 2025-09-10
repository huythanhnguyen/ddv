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
import re

import meilisearch
from meilisearch.errors import MeilisearchError

from app.config import meilisearch_config
from .gemini_utils_tool import gemini_utils

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
        # Use the canonical index name created in runtime scripts
        self.index_name = "products"
        
        # Initialize Meilisearch client
        self._setup_meilisearch_client()
        
        # Load products data
        self._load_products()
        
        # Setup index and add documents
        self._setup_index()

    # ------------------------- Heuristics -------------------------
    def _heuristic_brand_from_query(self, text: str) -> Optional[str]:
        """Simple deterministic brand detection to complement AI extraction.
        If the user explicitly mentions a brand family (e.g., 'iphone', 'galaxy'),
        enforce that as a brand filter to avoid cross-brand results.
        """
        if not text:
            return None
        t = text.lower()
        # map tokens → canonical brand
        brand_map = {
            r"\biphone\b": "Apple",
            r"\bipad\b": "Apple",
            r"\bmac\b": "Apple",
            r"\bgalaxy\b": "Samsung",
            r"\bsamsung\b": "Samsung",
            r"\bxiaomi\b|\bmi\b": "Xiaomi",
            r"\boppo\b": "OPPO",
            r"\bvivo\b": "Vivo",
            r"\brealme\b": "Realme",
        }
        for pattern, brand in brand_map.items():
            if re.search(pattern, t):
                return brand
        return None

    def _normalize_model_phrase(self, text: str) -> Optional[str]:
        """Extract a concise model phrase to boost relevance (e.g., 'iphone 16 pro')."""
        if not text:
            return None
        t = text.lower().strip()
        # common phones: iphone <number> [pro|max|plus]
        m = re.search(r"iphone\s+([0-9]{1,2})(?:\s+(pro\s*max|pro|plus))?", t)
        if m:
            parts = ["iPhone", m.group(1)]
            if m.group(2):
                parts.append(m.group(2).title().replace(" ", " "))
            return " ".join(parts)
        return None

    def _tokens_from_phrase(self, phrase: str) -> List[str]:
        return [w for w in re.split(r"[^a-z0-9]+", phrase.lower()) if w]

    # ------------------------- Client/Index ------------------------
    def _setup_meilisearch_client(self):
        """Setup Meilisearch client"""
        try:
            # Create client without API key for local development
            if meilisearch_config.api_key:
                self.client = meilisearch.Client(
                    url=meilisearch_config.url,
                    api_key=meilisearch_config.api_key
                )
            else:
                self.client = meilisearch.Client(meilisearch_config.url)
            
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
                # Touch the index to verify it exists; if not, create it
                _ = self.index.get_stats()
                logger.info(f"✅ Using index: {self.index_name}")
            except Exception:
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
            # Configure searchable attributes to include ALL fields
            searchable_attributes = ['*']
            
            # Configure filterable attributes (what can be filtered)
            filterable_attributes = [
                'brand',
                'category',
                'availability',
                'price.current',
                'price.original',
                'price.discount_percentage',
                'promotions_count',
            ]
            
            # Configure sortable attributes
            sortable_attributes = [
                'last_updated',
                'price.current',
                'price.original',
                'price.discount_percentage',
                'promotions_count',
                'reviews.average_rating',
                'reviews.rating_count',
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
                'iphone': ['apple', 'ip'],
                'samsung': ['galaxy', 'ss'],
                'khuyến mãi': ['giảm giá', 'ưu đãi', 'promotion', 'deal', 'discount'],
                'giam gia': ['khuyến mãi', 'promotion', 'discount'],
                'uu dai': ['khuyến mãi', 'promotion'],
                'màu': ['color', 'mau'],
                'bộ nhớ': ['storage', 'memory'],
            }
            
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
    
    def _count_promotions(self, promotions: Dict[str, Any]) -> int:
        """Count total number of promotions across promo categories"""
        if not promotions:
            return 0
        total = 0
        for key in ['free_gifts', 'vouchers', 'special_discounts', 'bundle_offers']:
            val = promotions.get(key)
            if isinstance(val, list):
                total += len(val)
        return total
    
    def _index_products(self):
        """Index all products in Meilisearch"""
        if not self.index or not self.products:
            return
        
        try:
            documents = []
            for product in self.products:
                # Base doc
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
                
                # Price
                price_obj = product.get('price', {})
                price_vnd = price_obj.get('current', 0)
                price_listed_vnd = price_obj.get('original', price_vnd)
                if price_vnd == 0:
                    price_vnd = product.get('price_vnd', 0)
                if price_listed_vnd == 0:
                    price_listed_vnd = product.get('price_listed_vnd', price_vnd)
                discount_pct = price_obj.get('discount_percentage', 0)
                if not discount_pct and price_listed_vnd and price_listed_vnd > price_vnd:
                    discount_pct = round(((price_listed_vnd - price_vnd) / price_listed_vnd) * 100, 2)
                doc['price'] = {
                    'current': price_vnd,
                    'original': price_listed_vnd,
                    'currency': price_obj.get('currency', 'VND'),
                    'discount_percentage': discount_pct or 0
                }
                
                # Specs and promotions
                specs = product.get('specs', {})
                promotions = product.get('promotions', {})
                doc['specs'] = specs
                doc['promotions'] = promotions
                doc['promotions_count'] = self._count_promotions(promotions)
                
                # Flatten to searchable text
                searchable_text = [doc['name'], doc['brand'], doc['category']]
                for spec_value in specs.values():
                    if isinstance(spec_value, str):
                        searchable_text.append(spec_value)
                    elif isinstance(spec_value, list):
                        searchable_text.extend([str(item) for item in spec_value])
                    else:
                        searchable_text.append(str(spec_value))
                for promo_value in promotions.values():
                    if isinstance(promo_value, list):
                        searchable_text.extend([str(item) for item in promo_value])
                    elif isinstance(promo_value, str):
                        searchable_text.append(promo_value)
                doc['_searchable_text'] = ' '.join([s for s in searchable_text if s])
                
                documents.append(doc)
            
            task = self.index.add_documents(documents)
            logger.info(f"✅ Indexed {len(documents)} products. Task ID: {task.task_uid}")
            
        except Exception as e:
            logger.error(f"❌ Error indexing products: {e}")
    
    def _detect_promotion_intent(self, text: str) -> bool:
        if not text:
            return False
        t = text.lower()
        keywords = [
            'khuyến mãi', 'khuyen mai', 'giảm giá', 'giam gia', 'ưu đãi', 'uu dai',
            'promotion', 'discount', 'deal'
        ]
        return any(k in t for k in keywords)
    
    def search_products(self, 
                       query: str, 
                       filters: Optional[Dict[str, Any]] = None,
                       limit: int = 20,
                       sort: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search products using Meilisearch with AI-powered query enhancement
        """
        if not self.index:
            logger.warning("Meilisearch index not available, using fallback search")
            return self._fallback_search(query, limit)
        
        if not query or not query.strip():
            return []
        
        try:
            start_time = time.time()
            
            enhanced_query = query
            enhanced_filters = filters or {}
            
            # AI intent enhancement
            search_intent = gemini_utils.analyze_search_intent(query)
            if search_intent.get('search_query'):
                enhanced_query = search_intent['search_query']
                logger.info(f"🧠 AI enhanced query: '{query}' → '{enhanced_query}'")
            
            # Heuristic brand extraction (deterministic) to prevent cross-brand noise
            detected_brand = self._heuristic_brand_from_query(query)
            if detected_brand and not enhanced_filters.get('brand'):
                enhanced_filters['brand'] = detected_brand
                logger.info(f"🏷️ Heuristic brand filter: {detected_brand}")
            
            # Budget filters
            if not enhanced_filters.get('price_min') and not enhanced_filters.get('price_max'):
                budget_min, budget_max = gemini_utils.extract_budget_from_text(query)
                if budget_min is not None or budget_max is not None:
                    enhanced_filters['price_min'] = budget_min
                    enhanced_filters['price_max'] = budget_max
                    logger.info(f"💰 AI extracted budget filters: {budget_min}-{budget_max}")
            
            # AI brand extraction as a fallback if heuristic not found
            if not enhanced_filters.get('brand'):
                brands = gemini_utils.extract_brands_from_text(query)
                if brands:
                    enhanced_filters['brand'] = brands[0]
                    logger.info(f"🏷️ AI extracted brand filter: {brands[0]}")
            
            # Build search params
            search_params: Dict[str, Any] = {
                'limit': limit,
                'attributesToRetrieve': ['*'],
                'attributesToHighlight': ['name', 'brand', 'category', '_searchable_text', 'promotions'],
                'highlightPreTag': '<mark>',
                'highlightPostTag': '</mark>'
            }
            
            filter_conditions = []
            if enhanced_filters:
                if enhanced_filters.get('brand'):
                    filter_conditions.append(f"brand = '{enhanced_filters['brand']}'")
                if enhanced_filters.get('category'):
                    filter_conditions.append(f"category = '{enhanced_filters['category']}'")
                if enhanced_filters.get('price_min') is not None:
                    filter_conditions.append(f"price.current >= {enhanced_filters['price_min']}")
                if enhanced_filters.get('price_max') is not None:
                    filter_conditions.append(f"price.current <= {enhanced_filters['price_max']}")
                if enhanced_filters.get('min_discount') is not None:
                    filter_conditions.append(f"price.discount_percentage >= {enhanced_filters['min_discount']}")
            
            # Promotion intent
            promo_intent = self._detect_promotion_intent(query)
            if promo_intent:
                filter_conditions.append("promotions_count >= 1 OR price.discount_percentage > 0")
                if not sort:
                    sort = ["promotions_count:desc", "price.discount_percentage:desc"]
            
            if filter_conditions:
                search_params['filter'] = ' AND '.join(filter_conditions)
                logger.info(f"🔍 Applied filters: {search_params['filter']}")
            
            # Boost model phrase if present by appending to query
            model_phrase = self._normalize_model_phrase(query)
            if model_phrase and model_phrase.lower() not in enhanced_query.lower():
                enhanced_query = f"{enhanced_query} {model_phrase}"
                logger.info(f"🔎 Model phrase boost: '{model_phrase}'")
            
            if sort:
                search_params['sort'] = sort
            
            results = self.index.search(enhanced_query, search_params)
            
            products = []
            for hit in results.get('hits', []):
                product = hit.copy()
                product['search_metadata'] = {
                    'relevance_score': hit.get('_rankingScore', 0.0),
                    'formatted': hit.get('_formatted', {}),
                    'matched_terms': hit.get('_matchesInfo', {})
                }
                products.append(product)

            # If user asked a specific model, keep only exact-like matches on name
            if model_phrase:
                tokens = self._tokens_from_phrase(model_phrase)
                narrowed = []
                for p in products:
                    name = (p.get('name') or '').lower()
                    if all(tok in name for tok in tokens):
                        narrowed.append(p)
                if narrowed:
                    products = narrowed
            
            search_time = time.time() - start_time
            logger.info(f"🔍 AI-enhanced Meilisearch completed in {search_time:.3f}s for query: '{query}' → '{enhanced_query}'")
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
            name = product.get('name', '').lower()
            if query_lower in name:
                score += 10
            brand = product.get('brand', '').lower()
            if query_lower in brand:
                score += 8
            category = product.get('category', '').lower()
            if query_lower in category:
                score += 5
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
        results.sort(key=lambda x: x['search_metadata']['relevance_score'], reverse=True)
        return results[:limit]
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Get product by ID using Meilisearch"""
        if not self.index:
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
            self.index.delete_all_documents()
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
    
    def analyze_product_with_ai(self, product_id: str) -> Dict[str, Any]:
        """Analyze a specific product using AI to provide insights"""
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                return {
                    "success": False,
                    "message": "Không tìm thấy sản phẩm",
                    "analysis": {}
                }
            
            product_summary = {
                "name": product.get('name', ''),
                "brand": product.get('brand', ''),
                "price": product.get('price', {}),
                "specs": product.get('specs', {}),
                "promotions": product.get('promotions', {})
            }
            
            analysis_prompt = f"""
            Phân tích sản phẩm điện thoại sau và đưa ra đánh giá:
            
            Tên: {product_summary['name']}
            Thương hiệu: {product_summary['brand']}
            Giá: {product_summary['price']}
            Thông số: {product_summary['specs']}
            Khuyến mãi: {product_summary['promotions']}
            
            Đưa ra đánh giá về:
            1. Điểm mạnh của sản phẩm
            2. Điểm yếu cần lưu ý
            3. Đối tượng phù hợp
            4. So sánh với thị trường
            5. Khuyến nghị mua hàng
            """
            
            analysis_result = gemini_utils._call_gemini(
                analysis_prompt,
                "Bạn là chuyên gia đánh giá điện thoại. Hãy phân tích khách quan và đưa ra lời khuyên hữu ích."
            )
            
            return {
                "success": True,
                "product": product_summary,
                "analysis": analysis_result or "Không thể phân tích sản phẩm tại thời điểm này",
                "ai_enhanced": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error analyzing product {product_id}: {e}")
            return {
                "success": False,
                "message": f"Lỗi khi phân tích sản phẩm: {str(e)}",
                "analysis": {}
            }

    def search(self, query: str, limit: int = 20, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search products using Meilisearch - simplified interface"""
        return self.search_products(query, filters, limit)

