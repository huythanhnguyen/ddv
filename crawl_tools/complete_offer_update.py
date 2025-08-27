#!/usr/bin/env python3
import json
import requests
import re
from datetime import datetime

def update_offers_with_prices_and_stores():
    print("Starting comprehensive offer update (prices + store availability)...")
    
    # Load existing data
    try:
        with open('profiles/products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        with open('profiles/offers.json', 'r', encoding='utf-8') as f:
            offers = json.load(f)
            
        with open('profiles/stores.json', 'r', encoding='utf-8') as f:
            stores = json.load(f)
            
        print(f"Loaded {len(products)} products, {len(offers)} offers, and {len(stores)} stores")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    updated_count = 0
    
    for offer in offers:
        product_id = offer.get("product_id")
        source_url = offer.get("source_url")
        
        if not source_url:
            continue
            
        print(f"Updating {product_id}...")
        
        try:
            # Fetch page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(source_url, headers=headers, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # 1. Extract accurate pricing
            prices = []
            
            # Pattern for exact price structure with line-through
            price_pattern = r'<div><p>Giá bán</p><div[^>]*><div[^>]*>([^<]+)\s*đ</div><span><p[^>]*line-through[^>]*>([^<]+)<!--[^>]*>\s*đ</p></span></div></div>'
            matches = re.findall(price_pattern, html_content, re.DOTALL)
            
            if matches:
                current_price_str, original_price_str = matches[0]
                try:
                    current_price = int(current_price_str.replace('.', '').replace(',', '').strip())
                    original_price = int(original_price_str.replace('.', '').replace(',', '').strip())
                    discount_percentage = int(((original_price - current_price) / original_price) * 100)
                    
                    prices.append({
                        "variant": "Giá hiện tại",
                        "price_vnd": current_price,
                        "original_price_vnd": original_price,
                        "discount_percentage": discount_percentage,
                        "currency": "VND"
                    })
                    
                    print(f"  Found price: {current_price:,}đ (giảm từ {original_price:,}đ - {discount_percentage}%)")
                except ValueError as e:
                    print(f"  Error parsing prices: {e}")
            
            # 2. Extract store availability information
            available_stores = []
            
            # Look for store information in the page
            store_patterns = [
                r'Cửa hàng Di Động Việt ([^<]+)',
                r'Cửa hàng Vertu ([^<]+)'
            ]
            
            for pattern in store_patterns:
                store_matches = re.findall(pattern, html_content)
                for store_name in store_matches:
                    store_name = store_name.strip()
                    if store_name:
                        # Find corresponding store in stores.json
                        store_id = None
                        for store in stores:
                            if store_name in store.get("name", ""):
                                store_id = store.get("id")
                                break
                        
                        if store_id:
                            available_stores.append({
                                "store_id": store_id,
                                "store_name": store_name,
                                "status": "Có hàng"
                            })
            
            # Remove duplicates
            unique_stores = []
            seen_store_ids = set()
            for store in available_stores:
                if store["store_id"] not in seen_store_ids:
                    unique_stores.append(store)
                    seen_store_ids.add(store["store_id"])
            
            if unique_stores:
                print(f"  Found {len(unique_stores)} stores with stock")
                for store in unique_stores:
                    print(f"    - {store['store_name']}")
            
            # 3. Update the offer
            if prices:
                offer["pricing"]["current_prices"] = prices
                if any(price.get("discount_percentage", 0) > 0 for price in prices):
                    offer["pricing"]["price_note"] = f"Giá khuyến mãi: giảm {prices[0].get('discount_percentage', 0)}%"
                else:
                    offer["pricing"]["price_note"] = "Giá hiện tại"
            
            if unique_stores:
                offer["availability"]["available_stores"] = unique_stores
                offer["availability"]["status"] = "in_stock"
            
            offer["last_updated_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            if prices or unique_stores:
                updated_count += 1
            
            # Small delay
            import time
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Error updating {product_id}: {e}")
            continue
    
    # Save updated offers
    try:
        with open('profiles/offers.json', 'w', encoding='utf-8') as f:
            json.dump(offers, f, ensure_ascii=False, indent=2)
        
        print(f"\nSuccessfully updated {updated_count} offers!")
        print("Updated offers.json with accurate pricing and store availability")
        
    except Exception as e:
        print(f"Error saving offers: {e}")

if __name__ == "__main__":
    update_offers_with_prices_and_stores()
