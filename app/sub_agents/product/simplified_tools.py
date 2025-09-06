"""
Simplified Tools for Product Agent - Focus on Search Functionality
"""

from typing import List, Dict, Any, Optional
from ...tools.enhanced_product_store import enhanced_data_store
from ...shared_libraries.utils import (
    extract_budget_from_text, extract_brands_from_text, extract_features_from_text,
    format_price_vnd, create_product_summary
)


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
    """Enhanced product search tool using Gemini AI search engine"""
    try:
        # Use natural language query directly with Gemini AI
        search_query = user_input.strip()
        
        # Extract requirements for additional filtering
        budget_min, budget_max = extract_budget_from_text(user_input)
        brands = extract_brands_from_text(user_input)
        
        # Build filters for post-processing
        filters = {}
        if brands:
            filters['brand'] = brands[0]  # Use first brand for now
        if budget_min is not None or budget_max is not None:
            filters['price_min'] = budget_min
            filters['price_max'] = budget_max
        
        # Search products using Gemini AI
        products = enhanced_data_store.search_products(
            query=search_query,
            filters=filters,
            limit=10
        )
        
        if not products:
            return {
                "success": False,
                "message": "Không tìm thấy sản phẩm phù hợp với yêu cầu của bạn.",
                "suggestions": [
                    "Thử mở rộng ngân sách",
                    "Bỏ bớt yêu cầu về tính năng",
                    "Chọn thương hiệu khác"
                ]
            }
        
        # Build UI payload compatible with mm_multi_agent product-display
        ui_products: List[Dict[str, Any]] = []
        for p in products:
            # Clean the product data first
            clean_p = clean_product_data(p)
            
            # Derive pricing
            current_price = clean_p.get('price', {}).get('current', 0)
            original_price = clean_p.get('price', {}).get('original', 0)
            discount_label = ""
            if current_price and original_price and original_price > current_price:
                try:
                    discount_pct = clean_p.get('price', {}).get('discount_percentage', 0)
                    discount_label = f"-{discount_pct}%" if discount_pct > 0 else ""
                except Exception:
                    discount_label = ""

            # Image and URL
            images = clean_p.get('images', [])
            image_url = images[0] if images else ''
            
            # Ensure all required fields are present and clean
            ui_product = {
                "id": clean_p.get('id', ''),
                "sku": clean_p.get('sku', ''),
                "name": clean_p.get('name', ''),
                "price": {
                    "current": current_price,
                    "original": original_price,
                    "currency": "VND",
                    "discount": discount_label
                },
                "image": {"url": image_url},
                "productUrl": clean_p.get('url', ''),
            }
            
            # Clean the UI product data as well
            ui_products.append(clean_product_data(ui_product))

        # Add AI analysis to product display
        ai_analysis = []
        for p in products:
            if 'ai_analysis' in p:
                ai_analysis.append({
                    'product_id': p.get('id', ''),
                    'relevance_score': p['ai_analysis'].get('relevance_score', 0),
                    'reasoning': p['ai_analysis'].get('reasoning', ''),
                    'matched_criteria': p['ai_analysis'].get('matched_criteria', [])
                })

        product_display = {
            "type": "product-display",
            "message": f"Tìm thấy {len(products)} sản phẩm phù hợp với yêu cầu của bạn",
            "products": ui_products,
            "ai_analysis": ai_analysis
        }

        return {
            "success": True,
            "products": products,
            "total_found": len(products),
            "product_display": product_display,
            "criteria": {
                "budget_min": budget_min,
                "budget_max": budget_max,
                "brands": brands,
                "search_query": search_query,
                "ai_enhanced": True
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Lỗi khi tìm kiếm sản phẩm: {str(e)}",
            "suggestions": ["Thử lại với từ khóa khác"]
        }


def simplified_product_compare_tool(product_ids: List[str]) -> Dict[str, Any]:
    """Simplified product comparison tool"""
    try:
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
        
        # Get products
        products = []
        for product_id in product_ids:
            product = enhanced_data_store.get_product_by_id(product_id)
            if product:
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
                "os": [p.get('specs', {}).get('os', '') for p in products]
            }
        }
        
        return {
            "success": True,
            "comparison": comparison,
            "message": f"Đã so sánh {len(products)} sản phẩm"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Lỗi khi so sánh sản phẩm: {str(e)}"
        }


def basic_price_analysis_tool(product_id: str) -> Dict[str, Any]:
    """Basic price analysis tool"""
    try:
        product = enhanced_data_store.get_product_by_id(product_id)
        if not product:
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
        
        return {
            "success": True,
            "analysis": analysis,
            "message": f"Phân tích giá cho {clean_product.get('name', '')}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Lỗi khi phân tích giá: {str(e)}"
        }


# Export tools
__all__ = [
    "enhanced_product_search_tool",
    "simplified_product_compare_tool", 
    "basic_price_analysis_tool"
]
