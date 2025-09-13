"""
Simple Compare Tool - Inspired by personalized_shopping
Product comparison functionality
"""

from google.adk.tools import ToolContext
import logging
import json
from typing import List

logger = logging.getLogger(__name__)

async def compare_products(product_ids: List[str], tool_context: ToolContext) -> str:
    """Compare multiple products side by side.
    
    Args:
        product_ids (list): List of product IDs to compare
        tool_context (ToolContext): The function context
        
    Returns:
        str: Comparison results
    """
    try:
        logger.info(f"Comparing products: {product_ids}")
        
        if len(product_ids) < 2:
            return "Cần ít nhất 2 sản phẩm để so sánh"
        
        if len(product_ids) > 5:
            return "Chỉ có thể so sánh tối đa 5 sản phẩm cùng lúc"
        
        # Import Simple Meilisearch engine
        from app.tools.meilisearch_simple import SimpleMeilisearchEngine
        
        # Get singleton instance
        search_engine = SimpleMeilisearchEngine()
        
        # Get product details for each ID
        products = []
        for product_id in product_ids:
            search_results = search_engine.search(product_id, limit=1)
            if search_results:
                products.append(search_results[0])
        
        if len(products) < 2:
            return "Không tìm đủ sản phẩm để so sánh"
        
        # Convert to comprehensive product format for frontend
        minimal_products = []
        for product in products:
            # Get first image from images array
            images = product.get("images", [])
            first_image = images[0] if images else ""
            
            # Get brand and category
            brand = product.get("brand", "")
            category = product.get("category", "")
            
            # Get specs for comparison
            specs = product.get("specs", {})
            display = specs.get("display", {})
            camera_main = specs.get("camera_main", "")
            battery = specs.get("battery", {})
            ram = specs.get("ram", "")
            storage = specs.get("storage", "")
            
            # Get reviews for rating
            reviews = product.get("reviews", {})
            rating = reviews.get("average_rating", 0)
            rating_count = reviews.get("rating_count", 0)
            
            # Get availability
            availability = product.get("availability", "unknown")
            
            # Get colors and storage options
            colors = product.get("colors", [])
            storage_options = product.get("storage_options", [])
            
            # Get promotions
            promotions = product.get("promotions", {})
            free_gifts = promotions.get("free_gifts", [])
            special_discounts = promotions.get("special_discounts", [])
            
            minimal_products.append({
                "id": product.get("id", ""),
                "sku": product.get("sku", ""),
                "name": product.get("name", ""),
                "brand": brand,
                "category": category,
                "price": {
                    "current": product.get("price", {}).get("current", 0),
                    "original": product.get("price", {}).get("original"),
                    "currency": product.get("price", {}).get("currency", "VND"),
                    "discount": f"{product.get('price', {}).get('discount_percentage', 0)}%" if product.get('price', {}).get('discount_percentage', 0) > 0 else None
                },
                "image": {
                    "url": first_image
                },
                "description": product.get("description", ""),
                "productUrl": product.get("url", ""),
                "availability": availability,
                "rating": {
                    "average": rating,
                    "count": rating_count
                },
                "specs": {
                    "display": {
                        "size": display.get("size", ""),
                        "technology": display.get("technology", ""),
                        "resolution": display.get("resolution", "")
                    },
                    "camera": {
                        "main": camera_main,
                        "front": specs.get("camera_front", "")
                    },
                    "battery": {
                        "capacity": battery.get("capacity", ""),
                        "charging": battery.get("wired_charging", "")
                    },
                    "ram": ram,
                    "storage": storage,
                    "os": specs.get("os", ""),
                    "chipset": specs.get("chipset", "")
                },
                "colors": colors,
                "storage_options": storage_options,
                "promotions": {
                    "free_gifts": free_gifts[:3],  # Limit to first 3
                    "special_discounts": special_discounts[:2]  # Limit to first 2
                }
            })
        
        # Create comparison summary
        # Safe comparison with proper type handling
        def safe_float(value, default=0):
            """Safely convert value to float, handling dict and other types"""
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return default
            elif isinstance(value, dict):
                # If it's a dict, try to get a numeric value from common keys
                for key in ['value', 'amount', 'capacity', 'current', 'original']:
                    if key in value and isinstance(value[key], (int, float)):
                        return float(value[key])
                return default
            else:
                return default
        
        cheapest = min(products, key=lambda p: safe_float(p.get("price", {}).get("current", 0), float('inf')))
        highest_rated = max(products, key=lambda p: safe_float(p.get("reviews", {}).get("average_rating", 0)))
        best_battery = max(products, key=lambda p: safe_float(p.get("specs", {}).get("battery", {}), 0))
        
        comparison_summary = f"**So sánh {len(products)} sản phẩm:**\n"
        cheapest_price = safe_float(cheapest.get('price', {}).get('current', 0))
        highest_rating = safe_float(highest_rated.get('reviews', {}).get('average_rating', 0))
        best_battery_capacity = safe_float(best_battery.get('specs', {}).get('battery', {}))
        
        comparison_summary += f"- Giá rẻ nhất: {cheapest.get('name', 'N/A')} ({cheapest_price:,.0f} VND)\n"
        comparison_summary += f"- Đánh giá cao nhất: {highest_rated.get('name', 'N/A')} ({highest_rating}/5)\n"
        comparison_summary += f"- Pin tốt nhất: {best_battery.get('name', 'N/A')} ({best_battery_capacity}mAh)\n"
        
        # Create JSON response for frontend
        json_response = {
            "type": "product-display",
            "message": comparison_summary,
            "products": minimal_products
        }
        
        # Skip artifact saving to avoid import issues
        # The comparison results are already returned as JSON
        
        return json.dumps(json_response, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Compare products error: {e}")
        return f"Lỗi khi so sánh sản phẩm: {str(e)}"
