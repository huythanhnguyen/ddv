"""Tools for Product Agent - tích hợp tìm kiếm, giá cả và cửa hàng"""

from typing import List, Dict, Any, Optional
from ...tools.product_store import data_store
from ...shared_libraries.utils import (
    extract_budget_from_text, extract_brands_from_text, extract_features_from_text,
    extract_location_from_text, format_price_vnd, create_product_summary,
    create_store_summary
)


def product_search_tool(user_input: str) -> Dict[str, Any]:
    """Tìm kiếm sản phẩm theo yêu cầu của người dùng"""
    try:
        # Extract requirements from user input
        budget_min, budget_max = extract_budget_from_text(user_input)
        brands = extract_brands_from_text(user_input)
        features = extract_features_from_text(user_input)
        location = extract_location_from_text(user_input)
        
        # Search products
        products = data_store.search_products(
            budget_min=budget_min,
            budget_max=budget_max,
            brands=brands,
            features=features,
            limit=5
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
        
        # Get offers and reviews for each product
        enriched_products = []
        for product in products:
            offer = data_store.get_offer_by_product_id(product['id'])
            review = data_store.get_review_by_product_id(product['id'])
            
            enriched_product = {
                **product,
                'offer': offer,
                'review': review,
                'summary': create_product_summary(product)
            }
            enriched_products.append(enriched_product)
        
        # Build UI payload compatible with mm_multi_agent product-display
        ui_products: List[Dict[str, Any]] = []
        for p in enriched_products:
            # Derive pricing
            current_price = p.get('price_vnd')
            original_price = p.get('price_listed_vnd')
            discount_label = ""
            if isinstance(current_price, (int, float)) and isinstance(original_price, (int, float)) and original_price and original_price > current_price:
                try:
                    discount_pct = round((original_price - current_price) / original_price * 100)
                    discount_label = f"-{discount_pct}%"
                except Exception:
                    discount_label = ""

            # Image and URL
            images = p.get('images') or []
            image_url = images[0] if images else ''
            ui_products.append({
                "id": p.get('id', ''),
                "sku": p.get('sku'),
                "name": p.get('name', ''),
                "price": {
                    "current": current_price if current_price is not None else 0,
                    "original": original_price if isinstance(original_price, (int, float)) else 0,
                    "currency": "VND",
                    "discount": discount_label or ""
                },
                "image": {"url": image_url},
                "productUrl": p.get('url', ''),
            })

        product_display = {
            "type": "product-display",
            "message": "Các lựa chọn phù hợp theo yêu cầu của bạn",
            "products": ui_products,
        }

        return {
            "success": True,
            "products": enriched_products,
            "total_found": len(enriched_products),
            "product_display": product_display,
            "criteria": {
                "budget_min": budget_min,
                "budget_max": budget_max,
                "brands": brands,
                "features": features,
                "location": location
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Có lỗi xảy ra khi tìm kiếm sản phẩm."
        }


def price_analysis_tool(product_id: str) -> Dict[str, Any]:
    """Phân tích giá cả và khuyến mãi cho sản phẩm"""
    try:
        product = data_store.get_product_by_id(product_id)
        if not product:
            return {
                "success": False,
                "message": "Không tìm thấy sản phẩm."
            }
        
        offer = data_store.get_offer_by_product_id(product_id)
        if not offer:
            return {
                "success": False,
                "message": "Không có thông tin giá cả cho sản phẩm này."
            }
        
        # Extract pricing information
        pricing = offer.get('pricing', {})
        current_prices = pricing.get('current_prices', [])
        
        if not current_prices:
            return {
                "success": False,
                "message": "Không có thông tin giá hiện tại."
            }
        
        price_info = current_prices[0]
        current_price = price_info.get('price_vnd', 0)
        original_price = price_info.get('original_price_vnd', 0)
        discount_percentage = price_info.get('discount_percentage', 0)
        
        # Calculate additional metrics
        price_difference = original_price - current_price if original_price > current_price else 0
        value_score = (current_price / original_price * 100) if original_price > 0 else 100
        
        # Get promotions
        promotions = offer.get('promotions', {})
        free_gifts = promotions.get('free_gifts', [])
        special_discounts = promotions.get('special_discounts', [])
        bundle_offers = promotions.get('bundle_offers', [])
        
        return {
            "success": True,
            "product": {
                "id": product['id'],
                "name": product['name'],
                "brand": product['brand']
            },
            "pricing": {
                "current_price": current_price,
                "original_price": original_price,
                "price_difference": price_difference,
                "discount_percentage": discount_percentage,
                "value_score": round(value_score, 1),
                "formatted_current": format_price_vnd(current_price),
                "formatted_original": format_price_vnd(original_price)
            },
            "promotions": {
                "free_gifts": free_gifts,
                "special_discounts": special_discounts,
                "bundle_offers": bundle_offers
            },
            "analysis": {
                "is_discounted": discount_percentage > 0,
                "discount_level": "Cao" if discount_percentage > 20 else "Trung bình" if discount_percentage > 10 else "Thấp",
                "value_recommendation": "Tốt" if value_score > 80 else "Khá" if value_score > 60 else "Cần cân nhắc"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Có lỗi xảy ra khi phân tích giá cả."
        }


def store_location_tool(product_id: str, location: Optional[str] = None) -> Dict[str, Any]:
    """Tìm cửa hàng có sản phẩm và gần vị trí"""
    try:
        product = data_store.get_product_by_id(product_id)
        if not product:
            return {
                "success": False,
                "message": "Không tìm thấy sản phẩm."
            }
        
        # Get stores with the product
        stores_with_product = data_store.get_stores_with_product(product_id)
        
        if not stores_with_product:
            return {
                "success": False,
                "message": "Không có cửa hàng nào có sản phẩm này trong kho.",
                "product_name": product['name']
            }
        
        # Filter stores by location if specified
        if location:
            location_stores = []
            for store in stores_with_product:
                store_city = store.get('city', '').lower()
                store_region = store.get('region', '').lower()
                location_lower = location.lower()
                
                if (location_lower in store_city or 
                    location_lower in store_region or
                    store_city in location_lower or
                    store_region in location_lower):
                    location_stores.append(store)
            
            stores_with_product = location_stores
        
        if not stores_with_product:
            return {
                "success": False,
                "message": f"Không có cửa hàng nào có {product['name']} ở {location}.",
                "suggestions": [
                    "Thử tìm ở khu vực khác",
                    "Liên hệ cửa hàng để đặt hàng",
                    "Kiểm tra cửa hàng online"
                ]
            }
        
        # Create store summaries
        store_summaries = []
        for store in stores_with_product:
            store_summary = create_store_summary(store)
            store_summaries.append({
                **store,
                'summary': store_summary
            })
        
        return {
            "success": True,
            "product": {
                "id": product['id'],
                "name": product['name'],
                "brand": product['brand']
            },
            "stores": store_summaries,
            "total_stores": len(store_summaries),
            "location_filter": location,
            "recommendations": [
                "Gọi điện trước khi đến để kiểm tra hàng tồn kho",
                "Hỏi về chính sách bảo hành và đổi trả",
                "Tìm hiểu về các khuyến mãi hiện tại"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Có lỗi xảy ra khi tìm cửa hàng."
        }


def product_compare_tool(product_id_1: str, product_id_2: str) -> Dict[str, Any]:
    """So sánh hai sản phẩm"""
    try:
        comparison = data_store.compare_products(product_id_1, product_id_2)
        
        if not comparison:
            return {
                "success": False,
                "message": "Không thể so sánh hai sản phẩm này."
            }
        
        product_1 = comparison['product_1']['info']
        product_2 = comparison['product_2']['info']
        offer_1 = comparison['product_1']['offer']
        offer_2 = comparison['product_2']['offer']
        
        # Extract key comparison points
        comparison_points = {
            "price": {
                "product_1": product_1.get('price', 0),
                "product_2": product_2.get('price', 0),
                "difference": abs(product_1.get('price', 0) - product_2.get('price', 0)),
                "cheaper": product_1['name'] if product_1.get('price', 0) < product_2.get('price', 0) else product_2['name']
            },
            "brand": {
                "product_1": product_1.get('brand', ''),
                "product_2": product_2.get('brand', ''),
                "same_brand": product_1.get('brand', '') == product_2.get('brand', '')
            },
            "screen": {
                "product_1": product_1.get('screen', ''),
                "product_2": product_2.get('screen', '')
            },
            "camera": {
                "product_1": product_1.get('camera_main', ''),
                "product_2": product_2.get('camera_main', '')
            },
            "battery": {
                "product_1": product_1.get('battery', ''),
                "product_2": product_2.get('battery', '')
            }
        }
        
        # Get pricing analysis
        price_analysis_1 = price_analysis_tool(product_id_1) if offer_1 else None
        price_analysis_2 = price_analysis_tool(product_id_2) if offer_2 else None
        
        return {
            "success": True,
            "products": {
                "product_1": {
                    "id": product_1['id'],
                    "name": product_1['name'],
                    "brand": product_1['brand'],
                    "price_analysis": price_analysis_1
                },
                "product_2": {
                    "id": product_2['id'],
                    "name": product_2['name'],
                    "brand": product_2['brand'],
                    "price_analysis": price_analysis_2
                }
            },
            "comparison": comparison_points,
            "summary": {
                "price_winner": comparison_points["price"]["cheaper"],
                "brand_diversity": "Đa dạng" if not comparison_points["brand"]["same_brand"] else "Cùng thương hiệu",
                "recommendation": f"Nếu ưu tiên giá: {comparison_points['price']['cheaper']}"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Có lỗi xảy ra khi so sánh sản phẩm."
        }


def store_availability_tool(product_id: str) -> Dict[str, Any]:
    """Kiểm tra hàng tồn kho tại các cửa hàng"""
    try:
        product = data_store.get_product_by_id(product_id)
        if not product:
            return {
                "success": False,
                "message": "Không tìm thấy sản phẩm."
            }
        
        offer = data_store.get_offer_by_product_id(product_id)
        if not offer:
            return {
                "success": False,
                "message": "Không có thông tin hàng tồn kho cho sản phẩm này."
            }
        
        # Get availability information
        availability = offer.get('availability', {})
        status = availability.get('status', 'Không xác định')
        available_stores = availability.get('available_stores', [])
        
        # Get store details
        stores_info = []
        for store_id in available_stores:
            store = data_store.get_store_info(store_id)
            if store:
                stores_info.append({
                    **store,
                    'summary': create_store_summary(store)
                })
        
        return {
            "success": True,
            "product": {
                "id": product['id'],
                "name": product['name'],
                "brand": product['brand']
            },
            "availability": {
                "status": status,
                "total_stores": len(available_stores),
                "stores": stores_info
            },
            "recommendations": [
                "Gọi điện trước khi đến để xác nhận hàng tồn kho",
                "Hỏi về thời gian giao hàng nếu cần ship",
                "Tìm hiểu về chính sách đặt cọc"
            ]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Có lỗi xảy ra khi kiểm tra hàng tồn kho."
        }


def integrated_recommendation_tool(user_input: str) -> Dict[str, Any]:
    """Tư vấn tích hợp: sản phẩm + giá cả + cửa hàng"""
    try:
        # Step 1: Product search
        search_result = product_search_tool(user_input)
        if not search_result.get('success'):
            return search_result
        
        products = search_result['products']
        if not products:
            return {
                "success": False,
                "message": "Không tìm thấy sản phẩm phù hợp."
            }
        
        # Step 2: Enrich with pricing and store information
        enriched_recommendations = []
        
        for product in products[:3]:  # Top 3 products
            product_id = product['id']
            
            # Get price analysis
            price_analysis = price_analysis_tool(product_id)
            
            # Get store locations
            location = search_result['criteria'].get('location')
            store_locations = store_location_tool(product_id, location)
            
            # Get availability
            availability = store_availability_tool(product_id)
            
            enriched_recommendation = {
                **product,
                'price_analysis': price_analysis,
                'store_locations': store_locations,
                'availability': availability
            }
            
            enriched_recommendations.append(enriched_recommendation)
        
        # Build UI payload for recommendations as product cards
        ui_products: List[Dict[str, Any]] = []
        for p in enriched_recommendations:
            current_price = p.get('price_vnd')
            original_price = p.get('price_listed_vnd')
            discount_label = ""
            if isinstance(current_price, (int, float)) and isinstance(original_price, (int, float)) and original_price and original_price > current_price:
                try:
                    discount_pct = round((original_price - current_price) / original_price * 100)
                    discount_label = f"-{discount_pct}%"
                except Exception:
                    discount_label = ""

            images = p.get('images') or []
            image_url = images[0] if images else ''
            ui_products.append({
                "id": p.get('id', ''),
                "sku": p.get('sku'),
                "name": p.get('name', ''),
                "price": {
                    "current": current_price if current_price is not None else 0,
                    "original": original_price if isinstance(original_price, (int, float)) else 0,
                    "currency": "VND",
                    "discount": discount_label or ""
                },
                "image": {"url": image_url},
                "productUrl": p.get('url', ''),
            })

        product_display = {
            "type": "product-display",
            "message": "Gợi ý hàng đầu kèm giá và cửa hàng",
            "products": ui_products,
        }

        return {
            "success": True,
            "recommendations": enriched_recommendations,
            "total_recommendations": len(enriched_recommendations),
            "criteria": search_result['criteria'],
            "summary": f"Đã tìm thấy {len(enriched_recommendations)} sản phẩm phù hợp với yêu cầu của bạn, kèm theo phân tích giá cả và thông tin cửa hàng.",
            "product_display": product_display,
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Có lỗi xảy ra khi tạo tư vấn tích hợp."
        }
