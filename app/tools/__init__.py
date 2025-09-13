"""
Simple Tools module for DDV Product Advisor
Clean, simple tools for product search and exploration
"""

# Simple search engine
from .meilisearch_simple import SimpleMeilisearchEngine

# Simple tools
from .search import search_products
from .explore import explore_product
from .compare import compare_products

# Export all tools and classes
__all__ = [
    # Search engine
    "SimpleMeilisearchEngine",
    
    # Tools
    "search_products",
    "explore_product", 
    "compare_products",
]