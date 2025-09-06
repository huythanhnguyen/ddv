"""
Gemini AI Search Engine for DDV Product Advisor
Replaces Whoosh with intelligent semantic search using Google Gemini AI
"""

import json
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.config import gemini_search_config

# Setup logging
logger = logging.getLogger(__name__)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "profiles"
MERGED_PRODUCTS_FILE = DATA_DIR / "merged_products.json"


class GeminiSearchEngine:
    """Intelligent search engine using Google Gemini AI for semantic understanding"""
    
    def __init__(self):
        self.products = []
        self.client = None
        self.model = None
        self._cache = {}
        self._cache_timestamps = {}
        
        # Initialize Gemini client
        self._setup_gemini_client()
        
        # Load products data
        self._load_products()
        
        # Setup safety settings
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    
    def _setup_gemini_client(self):
        """Setup Gemini client with API key"""
        try:
            api_key = gemini_search_config.api_key
            if not api_key:
                logger.warning("No Gemini API key found. Please set GEMINI_API_KEY environment variable.")
                return
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name=gemini_search_config.model,
                safety_settings=self.safety_settings,
                generation_config=genai.types.GenerationConfig(
                    temperature=gemini_search_config.temperature,
                    max_output_tokens=gemini_search_config.max_tokens,
                )
            )
            logger.info(f"✅ Gemini client initialized with model: {gemini_search_config.model}")
            
        except Exception as e:
            logger.error(f"❌ Failed to setup Gemini client: {e}")
            self.model = None
    
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
    
    def search_products(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Main search function using Gemini AI for intelligent product matching
        
        Args:
            query: Natural language search query (Vietnamese/English)
            max_results: Maximum number of results to return
            
        Returns:
            List of matching products with AI analysis
        """
        if not query or not query.strip():
            return []
        
        if not self.model:
            logger.warning("Gemini model not available, using fallback search")
            return self._fallback_search(query, max_results)
        
        max_results = max_results or gemini_search_config.max_results
        
        # Check cache first
        cache_key = f"{query}_{max_results}"
        if gemini_search_config.cache_enabled and self._is_cache_valid(cache_key):
            logger.info(f"📋 Returning cached results for: {query}")
            return self._cache[cache_key]
        
        try:
            start_time = time.time()
            
            # Simplify products for AI processing
            simplified_products = self._simplify_products_for_ai()
            
            # Create intelligent search prompt
            prompt = self._create_search_prompt(query, simplified_products, max_results)
            
            # Get AI response
            response = self.model.generate_content(prompt)
            
            # Parse AI response
            results = self._parse_ai_response(response.text, query)
            
            # Reconstruct full product data
            full_results = self._reconstruct_full_products(results, max_results)
            
            # Cache results
            if gemini_search_config.cache_enabled:
                self._cache[cache_key] = full_results
                self._cache_timestamps[cache_key] = datetime.now()
            
            search_time = time.time() - start_time
            logger.info(f"🔍 AI search completed in {search_time:.2f}s for query: {query}")
            
            return full_results
            
        except Exception as e:
            logger.error(f"❌ AI search failed for query '{query}': {e}")
            logger.info("🔄 Falling back to simple text search")
            return self._fallback_search(query, max_results)
    
    def _simplify_products_for_ai(self) -> List[Dict[str, Any]]:
        """Simplify product data to reduce token usage for AI processing"""
        simplified = []
        
        for product in self.products:
            simplified_product = {
                'id': product.get('id', ''),
                'name': product.get('name', ''),
                'brand': product.get('brand', ''),
                'category': product.get('category', ''),
                'price_current': product.get('price', {}).get('current', 0),
                'price_original': product.get('price', {}).get('original', 0),
                'price_currency': product.get('price', {}).get('currency', 'VND'),
                'discount_percentage': product.get('price', {}).get('discount_percentage', 0),
                'specs': {
                    'screen_size': product.get('specs', {}).get('screen_size', ''),
                    'camera_main': product.get('specs', {}).get('camera_main', ''),
                    'storage': product.get('specs', {}).get('storage', ''),
                    'ram': product.get('specs', {}).get('ram', ''),
                    'os': product.get('specs', {}).get('os', ''),
                    'chipset': product.get('specs', {}).get('chipset', ''),
                },
                'promotions': product.get('promotions', {}),
                'availability': product.get('availability', ''),
                'url': product.get('url', ''),
            }
            simplified.append(simplified_product)
        
        return simplified
    
    def _create_search_prompt(self, query: str, products: List[Dict], max_results: int) -> str:
        """Create intelligent search prompt for Gemini AI"""
        
        prompt = f"""
Bạn là trợ lý AI chuyên gia tư vấn điện thoại Di Động Việt. Nhiệm vụ của bạn là tìm kiếm sản phẩm phù hợp nhất với yêu cầu của khách hàng.

**Yêu cầu tìm kiếm:** {query}

**Danh sách sản phẩm có sẵn:**
{json.dumps(products, ensure_ascii=False, indent=2)}

**Hướng dẫn tìm kiếm:**
1. Phân tích yêu cầu khách hàng (ngân sách, tính năng, thương hiệu, v.v.)
2. Tìm các sản phẩm phù hợp nhất dựa trên:
   - Tên sản phẩm và thương hiệu
   - Khoảng giá (current_price)
   - Tính năng kỹ thuật (specs)
   - Khuyến mãi hiện tại
   - Tình trạng có sẵn
3. Sắp xếp kết quả theo mức độ phù hợp (phù hợp nhất trước)
4. Trả về tối đa {max_results} sản phẩm

**Yêu cầu trả về:**
Trả về JSON array với format:
```json
[
  {{
    "id": "product_id",
    "relevance_score": 0.95,
    "reasoning": "Lý do sản phẩm này phù hợp",
    "matched_criteria": ["giá rẻ", "chụp ảnh tốt", "pin trâu"]
  }}
]
```

**Lưu ý:**
- Sử dụng tiếng Việt trong reasoning
- Chỉ trả về JSON, không có text khác
- relevance_score từ 0.0 đến 1.0 (1.0 = phù hợp nhất)
- matched_criteria là danh sách các tiêu chí khớp
"""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str, query: str) -> List[Dict[str, Any]]:
        """Parse AI response and extract product IDs with analysis"""
        try:
            # Clean response text
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            # Parse JSON
            ai_results = json.loads(response_text)
            
            # Validate structure
            if not isinstance(ai_results, list):
                logger.warning("AI response is not a list, treating as single result")
                ai_results = [ai_results]
            
            # Extract and validate results
            parsed_results = []
            for result in ai_results:
                if isinstance(result, dict) and 'id' in result:
                    parsed_results.append({
                        'id': result.get('id', ''),
                        'relevance_score': result.get('relevance_score', 0.5),
                        'reasoning': result.get('reasoning', ''),
                        'matched_criteria': result.get('matched_criteria', [])
                    })
            
            logger.info(f"✅ Parsed {len(parsed_results)} AI results for query: {query}")
            return parsed_results
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing AI response: {e}")
            return []
    
    def _reconstruct_full_products(self, ai_results: List[Dict], max_results: int) -> List[Dict[str, Any]]:
        """Reconstruct full product data from AI results"""
        full_results = []
        
        # Create product lookup
        product_lookup = {p['id']: p for p in self.products}
        
        for ai_result in ai_results[:max_results]:
            product_id = ai_result.get('id', '')
            if product_id in product_lookup:
                product = product_lookup[product_id].copy()
                
                # Add AI analysis
                product['ai_analysis'] = {
                    'relevance_score': ai_result.get('relevance_score', 0.5),
                    'reasoning': ai_result.get('reasoning', ''),
                    'matched_criteria': ai_result.get('matched_criteria', [])
                }
                
                full_results.append(product)
        
        return full_results
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Simple text-based fallback search when AI fails"""
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
                product_copy['ai_analysis'] = {
                    'relevance_score': min(score / 20, 1.0),  # Normalize to 0-1
                    'reasoning': f'Kết quả tìm kiếm đơn giản cho "{query}"',
                    'matched_criteria': ['text_match']
                }
                results.append(product_copy)
        
        # Sort by score and limit results
        results.sort(key=lambda x: x['ai_analysis']['relevance_score'], reverse=True)
        return results[:max_results]
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_time = self._cache_timestamps[cache_key]
        cache_age = datetime.now() - cache_time
        
        return cache_age.total_seconds() < gemini_search_config.cache_ttl
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        return {
            'total_products': len(self.products),
            'cache_size': len(self._cache),
            'gemini_model': gemini_search_config.model,
            'cache_enabled': gemini_search_config.cache_enabled,
            'cache_ttl': gemini_search_config.cache_ttl,
            'max_results': gemini_search_config.max_results
        }
    
    def clear_cache(self):
        """Clear search cache"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("🗑️ Search cache cleared")
