#!/usr/bin/env python3
"""
Test script for Meilisearch search functionality
"""

import requests
import json

def test_search():
    """Test search functionality"""
    base_url = "http://localhost:7700"
    
    # Test health
    print("🔍 Testing Meilisearch server...")
    try:
        r = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test search for iPhone
    print("\n📱 Searching for 'iPhone'...")
    try:
        r = requests.post(f"{base_url}/indexes/products/search", json={'q': 'iPhone', 'limit': 5})
        result = r.json()
        print(f"✅ Search status: {r.status_code}")
        print(f"📊 Total hits: {result['totalHits']}")
        print(f"📄 Results found: {len(result['hits'])}")
        
        if result['hits']:
            print("\n📋 First 3 results:")
            for i, hit in enumerate(result['hits'][:3], 1):
                price = hit.get('price', {}).get('current', 0)
                print(f"{i}. {hit['name']} - {hit['brand']} - {price:,} VND")
        else:
            print("❌ No results found")
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    # Test search for Samsung
    print("\n📱 Searching for 'Samsung'...")
    try:
        r = requests.post(f"{base_url}/indexes/products/search", json={'q': 'Samsung', 'limit': 3})
        result = r.json()
        print(f"✅ Search status: {r.status_code}")
        print(f"📊 Total hits: {result['totalHits']}")
        
        if result['hits']:
            print("\n📋 Samsung products:")
            for i, hit in enumerate(result['hits'], 1):
                price = hit.get('price', {}).get('current', 0)
                print(f"{i}. {hit['name']} - {price:,} VND")
        else:
            print("❌ No Samsung products found")
            
    except Exception as e:
        print(f"❌ Samsung search failed: {e}")
    
    # Test search for specific price range
    print("\n💰 Searching for products under 20,000,000 VND...")
    try:
        r = requests.post(f"{base_url}/indexes/products/search", json={'q': 'phone', 'limit': 10})
        result = r.json()
        print(f"✅ Search status: {r.status_code}")
        
        affordable_products = []
        for hit in result['hits']:
            price = hit.get('price', {}).get('current', 0)
            if price > 0 and price < 20000000:
                affordable_products.append((hit['name'], price))
        
        if affordable_products:
            print(f"\n📋 Affordable products (under 20M VND):")
            for i, (name, price) in enumerate(affordable_products[:5], 1):
                print(f"{i}. {name} - {price:,} VND")
        else:
            print("❌ No affordable products found")
            
    except Exception as e:
        print(f"❌ Price search failed: {e}")

if __name__ == "__main__":
    test_search()
