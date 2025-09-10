"""
Product Tools for DDV Product Advisor
Refactored and optimized product search and comparison tools
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.tools.tools_manager import tools_manager
from app.tools.gemini_utils_tool import gemini_utils
from app.shared_libraries.utils import (
    format_price_vnd, 
    create_product_summary
)

logger = logging.getLogger(__name__)

class ProductToolsError(Exception):
    """Custom exception for product tools errors"""
    pass

def clean_product_data(product: Dict[str, Any]) -> Dict[str, Any]:
    """Clean product data to ensure JSON compatibility"""
    def clean_value(value):
        if value is None:
            return ""
        elif isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            return value.strip() if value else ""
        elif isinstance(value, list):
            return [clean_value(item) for item in value if item is not None]
        elif isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items() if v is not None}
        else:
            return str(value) if value else ""
    
    return clean_value(product)

def enhanced_product_search_tool(user_input: str) -> Dict[str, Any]:
    """
    Enhanced product search tool using Meilisearch engine
    
    Args:
        user_input: Natural language search query from user
        
    Returns:
        Dict containing search results and UI-ready product display
    """
    try:
        logger.info(f"🔍 Searching products for query: '{user_input}'")
        
        # Ensure tools manager is initialized
        if not tools_manager.is_initialized:
            tools_manager.initialize()
        
        if not tools_manager.is_initialized:
            raise ProductToolsError("Tools manager not initialized")
        
        # Extract requirements from natural language using Gemini AI
        search_query = user_input.strip()
        
        # Use Gemini AI for flexible extraction
        budget_min, budget_max = gemini_utils.extract_budget_from_text(user_input)
        brands = gemini_utils.extract_brands_from_text(user_input)
        features = gemini_utils.extract_features_from_text(user_input)
        
        # Fallback to traditional methods if Gemini fails
        if budget_min is None and budget_max is None:
            logger.info("🔄 Gemini budget extraction failed, using fallback")
            from app.shared_libraries.utils import extract_budget_from_text as fallback_extract_budget
            budget_min, budget_max = fallback_extract_budget(user_input)
        
        if not brands:
            logger.info("🔄 Gemini brand extraction failed, using fallback")
            from app.shared_libraries.utils import extract_brands_from_text as fallback_extract_brands
            brands = fallback_extract_brands(user_input)
        
        if not features:
            logger.info("🔄 Gemini feature extraction failed, using fallback")
            from app.shared_libraries.utils import extract_features_from_text as fallback_extract_features
            features = fallback_extract_features(user_input)
        
        logger.info(f"📋 Extracted requirements - Budget: {budget_min}-{budget_max}, Brands: {brands}, Features: {features}")
        logger.info(f"🔍 Original query: '{user_input}'")
        logger.info(f"🔍 Search query: '{search_query}'")
        
        # Build filters for search
        filters = {}
        if brands:
            filters['brand'] = brands[0]  # Use first brand for now
        if budget_min is not None or budget_max is not None:
            filters['price_min'] = budget_min
            filters['price_max'] = budget_max
        
        logger.info(f"🔍 Built filters: {filters}")
        
        # Analyze search intent using Gemini AI for better search optimization
        search_intent = gemini_utils.analyze_search_intent(user_input)
        logger.info(f"🧠 Search intent analysis: {search_intent}")
        
        # Optimize search query based on intent
        if search_intent.get('search_query'):
            search_query = search_intent['search_query']
            logger.info(f"🔍 Optimized search query: '{search_query}'")
        
        # Search products using Meilisearch
        products = tools_manager.search_products(
            query=search_query,
            filters=filters,
            limit=10
        )
        
        logger.info(f"✅ Found {len(products)} products")
        
        if not products:
            return {
                "success": False,
                "message": "Không tìm thấy sản phẩm phù hợp với yêu cầu của bạn.",
                "suggestions": [
                    "Thử mở rộng ngân sách",
                    "Bỏ bớt yêu cầu về tính năng", 
                    "Chọn thương hiệu khác",
                    "Sử dụng từ khóa khác"
                ],
                "search_metadata": {
                    "query": search_query,
                    "filters_applied": filters,
                    "total_found": 0
                }
            }
        
        # Build UI payload compatible with frontend
        ui_products = []
        for product in products:
            try:
                clean_product = clean_product_data(product)
                
                # Extract pricing information
                current_price = clean_product.get('price', {}).get('current', 0)
                original_price = clean_product.get('price', {}).get('original', 0)
                discount_percentage = clean_product.get('price', {}).get('discount_percentage', 0)
                
                # Create discount label
                discount_label = ""
                if current_price and original_price and original_price > current_price:
                    discount_label = f"-{discount_percentage}%" if discount_percentage > 0 else ""
                
                # Get image URL
                images = clean_product.get('images', [])
                image_url = images[0] if images else ''
                
                # Build UI product object
                ui_product = {
                    "id": clean_product.get('id', ''),
                    "sku": clean_product.get('sku', ''),
                    "name": clean_product.get('name', ''),
                    "price": {
                        "current": current_price,
                        "original": original_price,
                        "currency": "VND",
                        "discount": discount_label
                    },
                    "image": {"url": image_url},
                    "productUrl": clean_product.get('url', ''),
                }
                
                ui_products.append(clean_product_data(ui_product))
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing product {product.get('id', 'unknown')}: {e}")
                continue
        
        # Create product display for frontend
        product_display = {
            "type": "product-display",
            "message": f"Tìm thấy {len(ui_products)} sản phẩm phù hợp với yêu cầu của bạn",
            "products": ui_products
        }
        try:
            compact_payload = json.dumps(product_display, ensure_ascii=False, separators=(",", ":"))
            logger.info("[PAYLOAD] product_display_json_length=%d head=%s tail=%s",
                        len(compact_payload), compact_payload[:200], compact_payload[-200:])
        except Exception as e:
            logger.warning("[PAYLOAD] Failed to serialize product_display: %s", e)
            compact_payload = ""
        
        # Add search metadata
        search_metadata = {
            "query": search_query,
            "filters_applied": filters,
            "total_found": len(ui_products),
            "search_engine": "meilisearch",
            "processing_time_ms": 0  # Could be added from search engine
        }
        
        logger.info(f"✅ Successfully processed {len(ui_products)} products for display")
        
        # Generate intelligent recommendation using Gemini AI
        recommendation_text = ""
        if ui_products:
            user_requirements = {
                "budget_range": {"min": budget_min, "max": budget_max},
                "brands": brands,
                "features": features,
                "intent": search_intent.get('intent', 'product_search')
            }
            recommendation_text = gemini_utils.generate_product_recommendation(user_requirements, ui_products[:3])
            logger.info(f"💡 Generated recommendation: {recommendation_text[:100]}...")
        
        result_payload = {
            "success": True,
            "products": products,  # Raw product data
            "total_found": len(ui_products),
            "product_display": product_display,
            "product_display_json": compact_payload,
            "recommendation": recommendation_text,
            "search_metadata": search_metadata,
            "criteria": {
                "budget_min": budget_min,
                "budget_max": budget_max,
                "brands": brands,
                "features": features,
                "search_query": search_query,
                "ai_enhanced": True,
                "search_intent": search_intent
            }
        }
        logger.info("✅ Returning payload with total_found=%d compact_json_len=%d",
                    result_payload["total_found"], len(compact_payload))
        return result_payload
        
    except ProductToolsError as e:
        logger.error(f"❌ Product tools error: {e}")
        return {
            "success": False,
            "message": f"Lỗi trong quá trình tìm kiếm: {str(e)}",
            "suggestions": ["Thử lại với từ khóa khác", "Kiểm tra kết nối"]
        }
    except Exception as e:
        logger.error(f"❌ Unexpected error in product search: {e}")
        return {
            "success": False,
            "message": f"Lỗi không mong muốn: {str(e)}",
            "suggestions": ["Thử lại sau", "Liên hệ hỗ trợ"]
        }

def product_compare_tool(product_ids: List[str]) -> Dict[str, Any]:
    """
    Product comparison tool
    
    Args:
        product_ids: List of product IDs to compare
        
    Returns:
        Dict containing comparison results
    """
    try:
        logger.info(f"🔄 Comparing products: {product_ids}")
        
        if len(product_ids) < 2:
            return {
                "success": False,
                "message": "Cần ít nhất 2 sản phẩm để so sánh"
            }
        
        if len(product_ids) > 4:
            return {
                "success": False,
                "message": "Chỉ có thể so sánh tối đa 4 sản phẩm"
            }
        
        # Ensure tools manager is initialized
        if not tools_manager.is_initialized:
            tools_manager.initialize()
        
        # Get products
        products = []
        for product_id in product_ids:
            product = tools_manager.get_product_by_id(product_id)
            if product and isinstance(product, dict):
                products.append(clean_product_data(product))
        
        if len(products) < 2:
            return {
                "success": False,
                "message": "Không tìm thấy đủ sản phẩm để so sánh"
            }
        
        # Create comparison table
        comparison = {
            "products": products,
            "total_products": len(products),
            "comparison_table": {
                "names": [p.get('name', '') for p in products],
                "brands": [p.get('brand', '') for p in products],
                "prices": [p.get('price', {}).get('current', 0) for p in products],
                "discounts": [p.get('price', {}).get('discount_percentage', 0) for p in products],
                "screen_sizes": [p.get('specs', {}).get('screen_size', '') for p in products],
                "storage": [p.get('specs', {}).get('storage', '') for p in products],
                "os": [p.get('specs', {}).get('os', '') for p in products],
                "cameras": [p.get('specs', {}).get('camera_main', '') for p in products]
            }
        }
        
        logger.info(f"✅ Successfully compared {len(products)} products")
        
        return {
            "success": True,
            "comparison": comparison,
            "message": f"Đã so sánh {len(products)} sản phẩm"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in product comparison: {e}")
        return {
            "success": False,
            "message": f"Lỗi khi so sánh sản phẩm: {str(e)}"
        }

def product_price_analysis_tool(product_id: str) -> Dict[str, Any]:
    """
    Product price analysis tool
    
    Args:
        product_id: Product ID to analyze
        
    Returns:
        Dict containing price analysis
    """
    try:
        logger.info(f"💰 Analyzing price for product: {product_id}")
        
        # Ensure tools manager is initialized
        if not tools_manager.is_initialized:
            tools_manager.initialize()
        
        product = tools_manager.get_product_by_id(product_id)
        if not product or not isinstance(product, dict):
            return {
                "success": False,
                "message": "Không tìm thấy sản phẩm"
            }
        
        # Clean product data
        clean_product = clean_product_data(product)
        
        price_info = clean_product.get('price', {})
        current_price = price_info.get('current', 0)
        original_price = price_info.get('original', 0)
        discount_percentage = price_info.get('discount_percentage', 0)
        
        # Basic price analysis
        analysis = {
            "product_name": clean_product.get('name', ''),
            "current_price": current_price,
            "original_price": original_price,
            "discount_percentage": discount_percentage,
            "price_difference": original_price - current_price if original_price > current_price else 0,
            "is_on_sale": discount_percentage > 0,
            "price_range": "Cao cấp" if current_price > 30000000 else "Trung bình" if current_price > 15000000 else "Phổ thông"
        }
        
        # Add recommendations
        recommendations = []
        if discount_percentage > 20:
            recommendations.append("Đang có khuyến mãi lớn, nên mua ngay")
        elif discount_percentage > 10:
            recommendations.append("Có khuyến mãi tốt")
        else:
            recommendations.append("Giá ổn định")
        
        if current_price < 10000000:
            recommendations.append("Giá rất tốt cho phân khúc này")
        
        analysis["recommendations"] = recommendations
        
        logger.info(f"✅ Successfully analyzed price for {clean_product.get('name', '')}")
        
        return {
            "success": True,
            "analysis": analysis,
            "message": f"Phân tích giá cho {clean_product.get('name', '')}"
        }
        
    except Exception as e:
        logger.error(f"❌ Error in price analysis: {e}")
        return {
            "success": False,
            "message": f"Lỗi khi phân tích giá: {str(e)}"
        }

# Export tools for agent use
__all__ = [
    "enhanced_product_search_tool",
    "product_compare_tool", 
    "product_price_analysis_tool",
    "ProductToolsError"
]
