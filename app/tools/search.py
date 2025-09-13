"""
Simple Search Tool - Inspired by personalized_shopping
Basic product search functionality
"""

from google.adk.tools import ToolContext
from google.genai import types
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)

async def search_products(keywords: str, tool_context: ToolContext, filters: Optional[dict] = None) -> str:
    """Search for smartphones based on keywords and filters.
    
    Args:
        keywords (str): Search keywords (e.g., "iPhone 16 Pro", "Samsung Galaxy")
        filters (dict, optional): Search filters (e.g., {"price_max": 20000000, "brand": "Apple"})
        tool_context (ToolContext): The function context
        
    Returns:
        str: Search results with product information
    """
    try:
        logger.info(f"Searching for: {keywords} with filters: {filters}")
        
        # Import Simple Meilisearch engine
        from app.tools.meilisearch_simple import SimpleMeilisearchEngine
        
        # Get singleton instance
        search_engine = SimpleMeilisearchEngine()
        
        # Convert filters to MeilisearchEngine format
        enhanced_filters = {}
        if filters:
            if "price_max" in filters:
                enhanced_filters["price_max"] = filters["price_max"]
            if "price_min" in filters:
                enhanced_filters["price_min"] = filters["price_min"]
            if "brand" in filters:
                enhanced_filters["brand"] = filters["brand"]
            if "battery_min" in filters:
                enhanced_filters["battery_min"] = filters["battery_min"]
            if "camera_min" in filters:
                enhanced_filters["camera_min"] = filters["camera_min"]
            if "storage_min" in filters:
                enhanced_filters["storage_min"] = filters["storage_min"]
        
        # Execute search using MeilisearchEngine
        products = search_engine.search(keywords, limit=20, enhanced_filters=enhanced_filters)
        
        # Format results for display
        if not products:
            return "Không tìm thấy sản phẩm phù hợp với yêu cầu của bạn. Hãy thử từ khóa khác hoặc điều chỉnh bộ lọc."
        
        # Convert to comprehensive product format for frontend
        minimal_products = []
        for product in products[:10]:  # Limit to top 10
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
        
        # Create JSON response for frontend
        json_response = {
            "type": "product-display",
            "message": f"Tìm thấy {len(products)} sản phẩm phù hợp với '{keywords}'",
            "products": minimal_products
        }
        
        # Skip artifact saving to avoid import issues
        # The search results are already returned as JSON
        
        return json.dumps(json_response, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return f"Lỗi khi tìm kiếm sản phẩm: {str(e)}"
