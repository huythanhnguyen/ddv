#!/usr/bin/env python3
import json
import requests
import re
from datetime import datetime

def crawl_and_update_prices():
    print("Starting price crawling...")
    
    # Load existing data
    try:
        with open('profiles/products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        with open('profiles/offers.json', 'r', encoding='utf-8') as f:
            offers = json.load(f)
            
        print(f"Loaded {len(products)} products and {len(offers)} offers")
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    updated_count = 0
    
    for offer in offers:
        product_id = offer.get("product_id")
        source_url = offer.get("source_url")
        
        if not source_url:
            continue
            
        print(f"Crawling prices for {product_id}...")
        
        try:
            # Fetch page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(source_url, headers=headers, timeout=10)
            response.raise_for_status()
            html_content = response.text
            
            # Extract prices using multiple patterns
            prices = []
            
            # Pattern 1: Look for prices near "Giá bán"
            price_pattern1 = r'Giá bán[^>]*>.*?(\d{1,3}(?:[.,]\d{3})*)'
            matches1 = re.findall(price_pattern1, html_content, re.DOTALL)
            
            for match in matches1:
                try:
                    price = int(match.replace('.', '').replace(',', ''))
                    prices.append({
                        "variant": "Giá bán",
                        "price_vnd": price,
                        "original_price_vnd": price,
                        "discount_percentage": 0,
                        "currency": "VND"
                    })
                except ValueError:
                    continue
            
            # Pattern 2: Look for VNĐ prices
            vnd_pattern = r'(\d{1,3}(?:[.,]\d{3})*)\s*VNĐ'
            vnd_matches = re.findall(vnd_pattern, html_content)
            
            for i, match in enumerate(vnd_matches):
                try:
                    price = int(match.replace('.', '').replace(',', ''))
                    if i % 2 == 0:  # Even indices are usually current prices
                        prices.append({
                            "variant": "Giá hiện tại",
                            "price_vnd": price,
                            "original_price_vnd": price,
                            "discount_percentage": 0,
                            "currency": "VND"
                        })
                except ValueError:
                    continue
            
            # Pattern 3: Look for meta tag prices
            meta_pattern = r'"price":"(\d+)"'
            meta_matches = re.findall(meta_pattern, html_content)
            
            for match in meta_matches:
                try:
                    price = int(match)
                    prices.append({
                        "variant": "Giá từ meta",
                        "price_vnd": price,
                        "original_price_vnd": price,
                        "discount_percentage": 0,
                        "currency": "VND"
                    })
                except ValueError:
                    continue
            
            # Remove duplicates
            unique_prices = []
            seen_prices = set()
            
            for price in prices:
                price_key = (price["price_vnd"], price["original_price_vnd"])
                if price_key not in seen_prices:
                    unique_prices.append(price)
                    seen_prices.add(price_key)
            
            # Sort by price
            unique_prices.sort(key=lambda x: x["price_vnd"])
            
            if unique_prices:
                # Update the offer
                offer["pricing"]["current_prices"] = unique_prices
                
                if any(price.get("discount_percentage", 0) > 0 for price in unique_prices):
                    offer["pricing"]["price_note"] = "Giá khuyến mãi có thể thay đổi"
                else:
                    offer["pricing"]["price_note"] = "Giá hiện tại"
                
                offer["last_updated_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                
                price_list = [f"{p.get('price_vnd', 0):,}đ" for p in unique_prices]
                print(f"  Found {len(unique_prices)} prices: {price_list}")
                updated_count += 1
            else:
                print(f"  No prices found")
            
            # Small delay
            import time
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Error crawling {product_id}: {e}")
            continue
    
    # Save updated offers
    try:
        with open('profiles/offers.json', 'w', encoding='utf-8') as f:
            json.dump(offers, f, ensure_ascii=False, indent=2)
        
        print(f"\nSuccessfully updated {updated_count} offers with real pricing data!")
        print("Updated offers.json")
        
    except Exception as e:
        print(f"Error saving offers: {e}")

if __name__ == "__main__":
    crawl_and_update_prices()
