"""Constants and configurations for DDV Product Advisor"""

# Session state keys
SESSION_STATE_KEYS = {
    "USER_PROFILE": "user_profile",
    "CONVERSATION_HISTORY": "conversation_history",
    "CURRENT_USE_CASE": "current_use_case",
    "SYSTEM_TIME": "system_time",
    "USER_INPUT": "user_input",
}

# Use cases
USE_CASES = {
    "PRODUCT_RECOMMENDATION": "product_recommendation",
    "PRICE_ANALYSIS": "price_analysis",
    "STORE_LOCATION": "store_location",
    "PRODUCT_COMPARISON": "product_comparison",
    "STORE_AVAILABILITY": "store_availability",
}

# Brand mappings and synonyms
BRAND_MAPPINGS = {
    "samsung": ["samsung", "galaxy", "ss"],
    "apple": ["apple", "iphone", "ip", "ios"],
    "xiaomi": ["xiaomi", "mi", "redmi", "poco"],
    "oppo": ["oppo", "oneplus", "realme"],
    "vivo": ["vivo", "iqoo"],
    "nokia": ["nokia"],
    "asus": ["asus", "rog"],
    "lenovo": ["lenovo", "motorola"],
}

# Budget buckets (in VND)
BUDGET_BUCKETS = {
    "under_5m": {"min": 0, "max": 5000000, "label": "Dưới 5 triệu"},
    "5m_to_8m": {"min": 5000000, "max": 8000000, "label": "5-8 triệu"},
    "8m_to_12m": {"min": 8000000, "max": 12000000, "label": "8-12 triệu"},
    "12m_to_18m": {"min": 12000000, "max": 18000000, "label": "12-18 triệu"},
    "18m_to_25m": {"min": 18000000, "max": 25000000, "label": "18-25 triệu"},
    "above_25m": {"min": 25000000, "max": float('inf'), "label": "Trên 25 triệu"},
}

# Feature categories
FEATURE_CATEGORIES = {
    "camera": ["camera", "chụp ảnh", "quay video", "zoom", "night mode", "portrait"],
    "gaming": ["gaming", "chơi game", "hiệu năng", "fps", "graphics", "ram"],
    "livestream": ["livestream", "stream", "tiktok", "youtube", "facebook"],
    "battery": ["pin", "battery", "sạc", "thời lượng", "fast charging"],
    "design": ["thiết kế", "design", "màu sắc", "kích thước", "trọng lượng"],
    "security": ["bảo mật", "security", "fingerprint", "face id", "mật khẩu"],
}

# Store regions and cities
STORE_REGIONS = {
    "Hồ Chí Minh": [
        "Quận 1", "Quận 3", "Quận 4", "Quận 6", "Quận 7", "Quận 8", 
        "Quận 10", "Quận 12", "Tân Bình", "Tân Phú", "Thủ Đức"
    ],
    "Hà Nội": ["Thái Hà", "Lê Thái Tổ"],
    "Đà Nẵng": ["Đà Nẵng"],
    "Miền Nam": [
        "Tiền Giang", "Bến Tre", "Cần Thơ", "An Giang", "Tây Ninh", 
        "Bà Rịa - Vũng Tàu", "Bình Thuận", "Đồng Nai", "Long An", "Bình Dương"
    ],
    "Miền Tây": ["Kiên Giang", "Phú Quốc", "Rạch Giá"],
}

# Product categories
PRODUCT_CATEGORIES = {
    "smartphone": ["điện thoại", "smartphone", "mobile", "phone"],
    "tablet": ["tablet", "máy tính bảng", "ipad"],
    "laptop": ["laptop", "máy tính xách tay", "notebook"],
    "accessory": ["phụ kiện", "accessory", "case", "sạc", "tai nghe"],
}

# Price ranges for validation
PRICE_RANGES = {
    "min_vnd": 1000000,  # 1 triệu VND
    "max_vnd": 100000000,  # 100 triệu VND
}

# Response templates
RESPONSE_TEMPLATES = {
    "greeting": "Xin chào! Tôi là trợ lý AI tư vấn sản phẩm điện thoại Di Động Việt. Tôi có thể giúp bạn tìm kiếm, so sánh sản phẩm và tìm cửa hàng gần nhất. Bạn cần tư vấn gì?",
    "no_results": "Xin lỗi, tôi không tìm thấy sản phẩm phù hợp với yêu cầu của bạn. Bạn có thể thử điều chỉnh tiêu chí tìm kiếm.",
    "error": "Xin lỗi, có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ hỗ trợ.",
    "store_not_found": "Xin lỗi, tôi không tìm thấy cửa hàng nào có sản phẩm này trong khu vực của bạn.",
}
