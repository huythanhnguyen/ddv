#!/usr/bin/env python3
import json
import requests
import re
from datetime import datetime

def crawl_accurate_prices():
    print("Starting accurate price crawling...")
    
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
            
            # Pattern to find the exact structure:
            # <div><p>Giá bán</p><div class="flex flex-row items-end gap-4">
            # <div class="text-24 font-bold text-red-500 ">18.390.000 đ</div>
            # <span><p class=" line-through">19.990.000<!-- --> đ</p></span>
            # </div></div>
            
            price_pattern = r'<div><p>Giá bán</p><div[^>]*><div[^>]*>([^<]+)\s*đ</div><span><p[^>]*line-through[^>]*>([^<]+)<!--[^>]*>\s*đ</p></span></div></div>'
            
            matches = re.findall(price_pattern, html_content, re.DOTALL)
            
            if matches:
                # Take the first match (should be the main price)
                current_price_str, original_price_str = matches[0]
                
                try:
                    # Clean and convert prices
                    current_price = int(current_price_str.replace('.', '').replace(',', '').strip())
                    original_price = int(original_price_str.replace('.', '').replace(',', '').strip())
                    
                    # Calculate discount percentage
                    discount_percentage = int(((original_price - current_price) / original_price) * 100)
                    
                    # Create clean price structure
                    clean_prices = [
                        {
                            "variant": "Giá hiện tại",
                            "price_vnd": current_price,
                            "original_price_vnd": original_price,
                            "discount_percentage": discount_percentage,
                            "currency": "VND"
                        }
                    ]
                    
                    # Update the offer
                    offer["pricing"]["current_prices"] = clean_prices
                    offer["pricing"]["price_note"] = f"Giá khuyến mãi: giảm {discount_percentage}% từ {original_price:,}đ"
                    offer["last_updated_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                    
                    print(f"  Found: {current_price:,}đ (giảm từ {original_price:,}đ - {discount_percentage}%)")
                    updated_count += 1
                    
                except ValueError as e:
                    print(f"  Error parsing prices: {e}")
                    print(f"  Raw: current='{current_price_str}', original='{original_price_str}'")
                    
            else:
                # Fallback: look for simpler patterns
                print(f"  No exact price structure found, trying fallback patterns...")
                
                # Look for any price with line-through
                fallback_pattern = r'<p[^>]*line-through[^>]*>([^<]+)\s*đ</p>'
                fallback_matches = re.findall(fallback_pattern, html_content)
                
                if fallback_matches:
                    try:
                        original_price = int(fallback_matches[0].replace('.', '').replace(',', '').strip())
                        
                        # Look for current price (usually nearby, without line-through)
                        current_pattern = r'<div[^>]*text-red-500[^>]*>([^<]+)\s*đ</div>'
                        current_matches = re.findall(current_pattern, html_content)
                        
                        if current_matches:
                            current_price = int(current_matches[0].replace('.', '').replace(',', '').strip())
                            discount_percentage = int(((original_price - current_price) / original_price) * 100)
                            
                            clean_prices = [
                                {
                                    "variant": "Giá hiện tại",
                                    "price_vnd": current_price,
                                    "original_price_vnd": original_price,
                                    "discount_percentage": discount_percentage,
                                    "currency": "VND"
                                }
                            ]
                            
                            offer["pricing"]["current_prices"] = clean_prices
                            offer["pricing"]["price_note"] = f"Giá khuyến mãi: giảm {discount_percentage}% từ {original_price:,}đ"
                            offer["last_updated_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                            
                            print(f"  Found (fallback): {current_price:,}đ (giảm từ {original_price:,}đ - {discount_percentage}%)")
                            updated_count += 1
                        else:
                            print(f"  No current price found in fallback")
                    except ValueError as e:
                        print(f"  Error parsing fallback prices: {e}")
                else:
                    print(f"  No prices found with any pattern")
            
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
        
        print(f"\nSuccessfully updated {updated_count} offers with accurate pricing data!")
        print("Updated offers.json with current price and original price structure")
        
    except Exception as e:
        print(f"Error saving offers: {e}")

if __name__ == "__main__":
    crawl_accurate_prices()
