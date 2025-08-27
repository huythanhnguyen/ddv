"""Utility functions for DDV Product Advisor"""

import json
import re
from typing import List, Dict, Any, Optional, Tuple
from math import radians, cos, sin, asin, sqrt
from .types import Product, Store, Offer, Review
from .constants import BRAND_MAPPINGS, BUDGET_BUCKETS, FEATURE_CATEGORIES, PRICE_RANGES


def format_price_vnd(price: int) -> str:
    """Format price in VND with thousand separators"""
    if price is None:
        return "N/A"
    return f"{price:,}đ"


def parse_price_from_text(text: str) -> Optional[int]:
    """Parse price from text (e.g., '18.390.000 đ' -> 18390000)"""
    if not text:
        return None
    
    # Remove all non-digit characters except dots
    price_text = re.sub(r'[^\d.]', '', text)
    
    try:
        # Handle Vietnamese price format (18.390.000)
        if '.' in price_text:
            # Remove dots and convert to integer
            price = int(price_text.replace('.', ''))
        else:
            price = int(price_text)
        
        # Validate price range
        if PRICE_RANGES["min_vnd"] <= price <= PRICE_RANGES["max_vnd"]:
            return price
        return None
    except (ValueError, TypeError):
        return None


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula (in km)"""
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


def extract_location_from_text(text: str) -> Optional[str]:
    """Extract location information from text"""
    if not text:
        return None
    
    # Common location patterns
    location_patterns = [
        r'quận\s+(\d+)',
        r'quận\s+([A-Za-zÀ-ỹ\s]+)',
        r'([A-Za-zÀ-ỹ\s]+)\s*,\s*HCM',
        r'([A-Za-zÀ-ỹ\s]+)\s*,\s*Hà\s*Nội',
        r'([A-Za-zÀ-ỹ\s]+)\s*,\s*Đà\s*Nẵng',
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None


def extract_budget_from_text(text: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract budget range from text"""
    if not text:
        return None, None
    
    # Budget patterns
    budget_patterns = [
        r'dưới\s+(\d+)\s*(triệu|m|M)',
        r'(\d+)\s*(triệu|m|M)\s*trở\s*xuống',
        r'từ\s+(\d+)\s*đến\s+(\d+)\s*(triệu|m|M)',
        r'(\d+)\s*-\s*(\d+)\s*(triệu|m|M)',
        r'(\d+)\s*đến\s+(\d+)\s*(triệu|m|M)',
    ]
    
    for pattern in budget_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 1:
                # Single budget (e.g., "dưới 20 triệu")
                max_budget = int(match.group(1)) * 1000000
                return None, max_budget
            elif len(match.groups()) == 3:
                # Range budget (e.g., "từ 10 đến 20 triệu")
                min_budget = int(match.group(1)) * 1000000
                max_budget = int(match.group(2)) * 1000000
                return min_budget, max_budget
    
    return None, None


def extract_brands_from_text(text: str) -> List[str]:
    """Extract brand preferences from text"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_brands = []
    
    for brand, synonyms in BRAND_MAPPINGS.items():
        for synonym in synonyms:
            if synonym.lower() in text_lower:
                found_brands.append(brand)
                break
    
    return list(set(found_brands))


def extract_features_from_text(text: str) -> List[str]:
    """Extract feature requirements from text"""
    if not text:
        return []
    
    text_lower = text.lower()
    found_features = []
    
    for category, keywords in FEATURE_CATEGORIES.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                found_features.append(category)
                break
    
    return list(set(found_features))


def get_budget_bucket(budget: int) -> str:
    """Get budget bucket label for a given amount"""
    for bucket_key, bucket_info in BUDGET_BUCKETS.items():
        if bucket_info["min"] <= budget <= bucket_info["max"]:
            return bucket_info["label"]
    return "Không xác định"


def filter_products_by_criteria(
    products: List[Product],
    budget_min: Optional[int] = None,
    budget_max: Optional[int] = None,
    brands: Optional[List[str]] = None,
    features: Optional[List[str]] = None
) -> List[Product]:
    """Filter products by given criteria"""
    filtered_products = []
    
    for product in products:
        # Budget filter
        if budget_min is not None and product.price < budget_min:
            continue
        if budget_max is not None and product.price > budget_max:
            continue
        
        # Brand filter
        if brands and product.brand.lower() not in [b.lower() for b in brands]:
            continue
        
        # Feature filter (basic implementation)
        if features:
            product_features = ' '.join(product.features).lower()
            if not any(f.lower() in product_features for f in features):
                continue
        
        filtered_products.append(product)
    
    return filtered_products


def sort_products_by_relevance(
    products: List[Product],
    user_requirements: Dict[str, Any]
) -> List[Product]:
    """Sort products by relevance to user requirements"""
    def calculate_score(product: Product) -> float:
        score = 0.0
        
        # Budget score (closer to user's preferred range = higher score)
        if 'budget_max' in user_requirements and user_requirements['budget_max']:
            budget_diff = abs(product.price - user_requirements['budget_max'])
            score += max(0, 1000000 - budget_diff) / 1000000
        
        # Brand preference score
        if 'preferred_brands' in user_requirements and user_requirements['preferred_brands']:
            if product.brand.lower() in [b.lower() for b in user_requirements['preferred_brands']]:
                score += 10
        
        # Feature score (basic implementation)
        if 'features' in user_requirements and user_requirements['features']:
            product_features = ' '.join(product.features).lower()
            feature_matches = sum(1 for f in user_requirements['features'] if f.lower() in product_features)
            score += feature_matches * 5
        
        return score
    
    return sorted(products, key=calculate_score, reverse=True)


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON data from file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {file_path}: {e}")
        return []


def save_json_data(file_path: str, data: List[Dict[str, Any]]) -> bool:
    """Save JSON data to file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False


def validate_product_data(product: Dict[str, Any]) -> bool:
    """Validate product data structure"""
    required_fields = ['id', 'name', 'brand', 'category', 'price']
    
    for field in required_fields:
        if field not in product or not product[field]:
            return False
    
    # Validate price
    try:
        price = int(product['price'])
        if not (PRICE_RANGES["min_vnd"] <= price <= PRICE_RANGES["max_vnd"]):
            return False
    except (ValueError, TypeError):
        return False
    
    return True


def create_product_summary(product: Dict[str, Any]) -> str:
    """Create a summary description for a product"""
    summary_parts = [
        f"{product.get('brand', 'N/A')} {product.get('name', 'N/A')}",
        f"Màn hình: {product.get('screen', 'N/A')}",
        f"Camera: {product.get('camera_main', 'N/A')} + {product.get('camera_front', 'N/A')}",
        f"Pin: {product.get('battery', 'N/A')}",
        f"Giá: {format_price_vnd(product.get('price_vnd', 0))}"
    ]
    
    features = product.get('features', [])
    if features:
        summary_parts.append(f"Tính năng: {', '.join(features[:3])}")
    
    return " | ".join(summary_parts)


def create_store_summary(store: Dict[str, Any]) -> str:
    """Create a summary description for a store"""
    summary_parts = [
        store.get('name', 'N/A'),
        f"Địa chỉ: {store.get('address', 'N/A')}",
        f"Điện thoại: {store.get('phone', 'N/A')}",
        f"Trạng thái: {store.get('status', 'N/A')}"
    ]
    
    parking = store.get('parking')
    if parking:
        summary_parts.append(f"Đỗ xe: {parking}")
    
    return " | ".join(summary_parts)
