"""
Simple Configuration for DDV Product Advisor
Inspired by personalized_shopping structure
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "profiles"
MERGED_PRODUCTS_FILE = DATA_DIR / "merged_products.json"

# Meilisearch configuration
MEILISEARCH_CONFIG = {
    "url": os.getenv("MEILISEARCH_URL", "http://localhost:7700"),
    "api_key": None,  # No API key for development
    "index_name": "products",
    "timeout": 30
}

# Model configuration
MODEL_CONFIG = {
    "primary_model": "gemini-2.0-flash",
    "worker_model": "gemini-2.0-flash"
}

# Search configuration
SEARCH_CONFIG = {
    "default_limit": 20,
    "max_limit": 100,
    "default_filters": {},
    "sort_options": [
        "price.current:asc",
        "price.current:desc", 
        "reviews.average_rating:desc",
        "name:asc"
    ]
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}
