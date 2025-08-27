#!/usr/bin/env python3
import json
from datetime import datetime

def cleanup_pricing_data():
    print("Cleaning up pricing data...")
    
    # Load offers
    try:
        with open('profiles/offers.json', 'r', encoding='utf-8') as f:
            offers = json.load(f)
    except Exception as e:
        print(f"Error loading offers: {e}")
        return
    
    cleaned_count = 0
    
    for offer in offers:
        product_id = offer.get("product_id")
        current_prices = offer.get("pricing", {}).get("current_prices", [])
        
        if not current_prices:
            continue
        
        # Filter out unrealistic prices and keep only the best price
        valid_prices = []
        for price in current_prices:
            price_vnd = price.get("price_vnd", 0)
            original_price_vnd = price.get("original_price_vnd", 0)
            
            # Only keep prices >= 1 million VND and <= 100 million VND
            if 1000000 <= price_vnd <= 100000000:
                # Calculate discount if original price is valid
                if original_price_vnd > price_vnd:
                    discount = int(((original_price_vnd - price_vnd) / original_price_vnd) * 100)
                    price["discount_percentage"] = discount
                else:
                    price["discount_percentage"] = 0
                    price["original_price_vnd"] = price_vnd
                
                valid_prices.append(price)
        
        # Sort by price (lowest first) and take the best one
        if valid_prices:
            valid_prices.sort(key=lambda x: x["price_vnd"])
            best_price = valid_prices[0]
            
            # Update the offer with clean pricing
            offer["pricing"]["current_prices"] = [best_price]
            
            # Update price note
            if best_price.get("discount_percentage", 0) > 0:
                offer["pricing"]["price_note"] = f"Giá khuyến mãi: giảm {best_price['discount_percentage']}% từ {best_price['original_price_vnd']:,}đ"
            else:
                offer["pricing"]["price_note"] = f"Giá hiện tại: {best_price['price_vnd']:,}đ"
            
            # Update timestamp
            offer["last_updated_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            print(f"Cleaned {product_id}: {best_price['price_vnd']:,}đ (giảm {best_price['discount_percentage']}%)")
            cleaned_count += 1
        
        else:
            # No valid prices found, set default
            offer["pricing"]["current_prices"] = []
            offer["pricing"]["price_note"] = "Giá đang cập nhật"
            print(f"No valid prices for {product_id}")
    
    # Save cleaned offers
    try:
        with open('profiles/offers.json', 'w', encoding='utf-8') as f:
            json.dump(offers, f, ensure_ascii=False, indent=2)
        
        print(f"\nSuccessfully cleaned {cleaned_count} offers!")
        print("Removed unrealistic prices and standardized structure")
        
    except Exception as e:
        print(f"Error saving cleaned offers: {e}")

if __name__ == "__main__":
    cleanup_pricing_data()
