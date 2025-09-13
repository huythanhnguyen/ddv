"""
Simple Explore Tool - Inspired by personalized_shopping
Product exploration and detailed information
"""

from google.adk.tools import ToolContext
from google.genai import types
import logging
import json

logger = logging.getLogger(__name__)

async def explore_product(product_id: str, tool_context: ToolContext) -> str:
    """Get detailed information about a specific product.
    
    Args:
        product_id (str): Product ID or SKU to explore
        tool_context (ToolContext): The function context
        
    Returns:
        str: Detailed product information
    """
    try:
        logger.info(f"Exploring product: {product_id}")
        
        # Import Simple Meilisearch engine
        from app.tools.meilisearch_simple import SimpleMeilisearchEngine
        
        # Get singleton instance
        search_engine = SimpleMeilisearchEngine()
        
        # Search for specific product
        products = search_engine.search(product_id, limit=1)
        
        if not products:
            return f"Không tìm thấy sản phẩm với ID: {product_id}"
        
        product = products[0]
        
        # Convert to comprehensive product format for frontend
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
        
        minimal_product = {
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
        }
        
        # Create JSON response for frontend
        json_response = {
            "type": "product-display",
            "message": f"Chi tiết sản phẩm: {product.get('name', 'N/A')}",
            "products": [minimal_product]
        }
        
        # Skip artifact saving to avoid import issues
        # The product details are already returned as JSON
        
        return json.dumps(json_response, ensure_ascii=False)
        
    except Exception as e:
        logger.error(f"Explore product error: {e}")
        return f"Lỗi khi lấy thông tin sản phẩm: {str(e)}"
