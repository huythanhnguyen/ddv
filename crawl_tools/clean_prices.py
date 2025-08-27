#!/usr/bin/env python3
import json
import re

def clean_prices():
    print("Cleaning price data...")
    
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
        
        # Filter out unrealistic prices (less than 1 million VND)
        valid_prices = []
        for price in current_prices:
            price_vnd = price.get("price_vnd", 0)
            if price_vnd >= 1000000:  # Only keep prices >= 1 million VND
                valid_prices.append(price)
        
        # Update the offer with cleaned prices
        if len(valid_prices) != len(current_prices):
            offer["pricing"]["current_prices"] = valid_prices
            cleaned_count += 1
            print(f"Cleaned {product_id}: {len(current_prices)} -> {len(valid_prices)} prices")
    
    # Save cleaned offers
    try:
        with open('profiles/offers.json', 'w', encoding='utf-8') as f:
            json.dump(offers, f, ensure_ascii=False, indent=2)
        
        print(f"\nSuccessfully cleaned {cleaned_count} offers!")
        print("Removed unrealistic prices (less than 1 million VND)")
        
    except Exception as e:
        print(f"Error saving cleaned offers: {e}")

if __name__ == "__main__":
    clean_prices()
