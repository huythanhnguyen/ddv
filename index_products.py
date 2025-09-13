#!/usr/bin/env python3
"""
Script to index products from merged_products.json into Meilisearch
"""

import json
import meilisearch
import os
from typing import List, Dict, Any

# Meilisearch configuration
MEILISEARCH_URL = "http://127.0.0.1:7700"
INDEX_NAME = "products"

def load_products(file_path: str) -> List[Dict[str, Any]]:
    """Load products from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        print(f"✅ Loaded {len(products)} products from {file_path}")
        return products
    except Exception as e:
        print(f"❌ Error loading products: {e}")
        return []

def setup_meilisearch_client():
    """Setup Meilisearch client"""
    try:
        client = meilisearch.Client(MEILISEARCH_URL)
        print(f"✅ Connected to Meilisearch at {MEILISEARCH_URL}")
        return client
    except Exception as e:
        print(f"❌ Error connecting to Meilisearch: {e}")
        return None

def create_index(client: meilisearch.Client, index_name: str):
    """Create or get index"""
    try:
        # Try to get existing index
        index = client.index(index_name)
        print(f"✅ Using existing index: {index_name}")
        return index
    except Exception as e:
        try:
            # Create new index
            index = client.create_index(index_name)
            print(f"✅ Created new index: {index_name}")
            return index
        except Exception as e2:
            print(f"❌ Error creating index: {e2}")
            return None

def configure_index(index):
    """Configure index settings"""
    try:
        # Set searchable attributes
        searchable_attributes = [
            "name", "brand", "description", "category", 
            "specs.processor", "specs.os", "specs.colors"
        ]
        index.update_searchable_attributes(searchable_attributes)
        print(f"✅ Set searchable attributes: {searchable_attributes}")
        
        # Set filterable attributes
        filterable_attributes = [
            "brand", "category", "price.current", "price.original",
            "specs.ram", "specs.storage", "specs.camera", "specs.battery",
            "specs.screen_size", "reviews.average_rating", "promotions_count"
        ]
        index.update_filterable_attributes(filterable_attributes)
        print(f"✅ Set filterable attributes: {filterable_attributes}")
        
        # Set sortable attributes
        sortable_attributes = [
            "price.current", "price.original", "reviews.average_rating",
            "specs.ram", "specs.storage", "specs.camera", "specs.battery"
        ]
        index.update_sortable_attributes(sortable_attributes)
        print(f"✅ Set sortable attributes: {sortable_attributes}")
        
        return True
    except Exception as e:
        print(f"❌ Error configuring index: {e}")
        return False

def index_products(index, products: List[Dict[str, Any]]):
    """Index products into Meilisearch"""
    try:
        # Clear existing documents
        index.delete_all_documents()
        print("🗑️ Cleared existing documents")
        
        # Add new documents
        task = index.add_documents(products)
        print(f"📝 Added {len(products)} products to index")
        print(f"⏳ Task ID: {task.task_uid}")
        
        # Wait for indexing to complete
        print("⏳ Waiting for indexing to complete...")
        index.wait_for_task(task.task_uid)
        print("✅ Indexing completed successfully!")
        
        return True
    except Exception as e:
        print(f"❌ Error indexing products: {e}")
        return False

def verify_indexing(index):
    """Verify that products were indexed correctly"""
    try:
        # Get index stats
        stats = index.get_stats()
        print(f"📊 Index stats: {stats.number_of_documents} documents")
        
        # Test search
        results = index.search("iPhone", {"limit": 3})
        print(f"🔍 Test search 'iPhone': {len(results['hits'])} results")
        
        # Test filter
        filter_results = index.search("", {
            "filter": "price.current < 20000000",
            "limit": 5
        })
        print(f"🔍 Test filter (price < 20M): {len(filter_results['hits'])} results")
        
        return True
    except Exception as e:
        print(f"❌ Error verifying indexing: {e}")
        return False

def main():
    """Main function"""
    print("🚀 Starting product indexing process...")
    
    # Load products
    products_file = "profiles/merged_products.json"
    if not os.path.exists(products_file):
        print(f"❌ Products file not found: {products_file}")
        return
    
    products = load_products(products_file)
    if not products:
        return
    
    # Setup Meilisearch
    client = setup_meilisearch_client()
    if not client:
        return
    
    # Create/get index
    index = create_index(client, INDEX_NAME)
    if not index:
        return
    
    # Configure index
    if not configure_index(index):
        return
    
    # Index products
    if not index_products(index, products):
        return
    
    # Verify indexing
    verify_indexing(index)
    
    print("🎉 Product indexing completed successfully!")
    print(f"🌐 You can now test at: http://127.0.0.1:7700/")

if __name__ == "__main__":
    main()
