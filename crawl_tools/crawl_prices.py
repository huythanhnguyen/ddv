import json
import os
import re
import requests
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin
import time


def load_json(path: str) -> Any:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_prices_from_html(html_content: str) -> List[Dict[str, Any]]:
    """
    Extract prices from HTML content based on actual structure found.
    Returns list of price dictionaries.
    """
    prices = []
    
    # Pattern 1: Look for "Giá bán" followed by price in the same context
    # Example: "Giá bán</p><div class="...">25.590.000
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
    
    # Pattern 2: Look for price table with "Giá bán hiện tại" and "Giá bán khởi điểm"
    # This captures the discount pricing structure
    table_pattern = r'Giá bán hiện tại[^>]*>.*?(\d{1,3}(?:[.,]\d{3})*).*?Giá bán khởi điểm[^>]*>.*?(\d{1,3}(?:[.,]\d{3})*)'
    table_matches = re.findall(table_pattern, html_content, re.DOTALL)
    
    for match in table_matches:
        try:
            current_price = int(match[0].replace('.', '').replace(',', ''))
            original_price = int(match[1].replace('.', '').replace(',', ''))
            
            # Calculate discount percentage
            discount_percentage = int(((original_price - current_price) / original_price) * 100) if original_price > current_price else 0
            
            prices.append({
                "variant": "Giá khuyến mãi",
                "price_vnd": current_price,
                "original_price_vnd": original_price,
                "discount_percentage": discount_percentage,
                "currency": "VND"
            })
        except (ValueError, IndexError):
            continue
    
    # Pattern 3: Look for VNĐ prices in tables
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
    
    # Pattern 4: Look for prices in meta tags (structured data)
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
    
    # Remove duplicates and sort by price
    unique_prices = []
    seen_prices = set()
    
    for price in prices:
        price_key = (price["price_vnd"], price["original_price_vnd"])
        if price_key not in seen_prices:
            unique_prices.append(price)
            seen_prices.add(price_key)
    
    # Sort by current price
    unique_prices.sort(key=lambda x: x["price_vnd"])
    
    return unique_prices


def crawl_product_prices(url: str) -> List[Dict[str, Any]]:
    """
    Crawl a product page to extract pricing information.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html_content = response.text
        
        # Extract prices
        price_data = extract_prices_from_html(html_content)
        
        return price_data
        
    except Exception as e:
        print(f"Error crawling {url}: {e}")
        return []


def update_offers_with_prices(offers: List[Dict[str, Any]], products: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], int]:
    """
    Update offers with real pricing data from crawled pages.
    """
    updated_count = 0
    
    for offer in offers:
        product_id = offer.get("product_id")
        source_url = offer.get("source_url")
        
        if not source_url:
            continue
            
        # Find corresponding product to get storage info
        product = next((p for p in products if p.get("id") == product_id), None)
        if not product:
            continue
        
        print(f"Crawling prices for {product_id}...")
        
        # Crawl prices
        current_prices = crawl_product_prices(source_url)
        
        if current_prices:
            # Update the offer with real prices
            offer["pricing"]["current_prices"] = current_prices
            
            # Update price note
            if any(price.get("discount_percentage", 0) > 0 for price in current_prices):
                offer["pricing"]["price_note"] = "Giá khuyến mãi có thể thay đổi"
            else:
                offer["pricing"]["price_note"] = "Giá hiện tại"
            
            # Update timestamp
            offer["last_updated_at"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            
            print(f"  Found {len(current_prices)} prices: {[f'{p.get('price_vnd', 0):,}đ' for p in current_prices]}")
            updated_count += 1
            
            # Add delay to be respectful to the server
            time.sleep(1)
        
        else:
            print(f"  No prices found for {product_id}")
    
    return offers, updated_count


def main() -> None:
    print("Starting price crawling...")
    
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    products_path = os.path.join(repo_root, "profiles", "products.json")
    offers_path = os.path.join(repo_root, "profiles", "offers.json")
    
    print("Loading existing data...")
    products = load_json(products_path) or []
    offers = load_json(offers_path) or []
    
    if not offers:
        print("No offers found. Please run sync_offers.py first.")
        return
    
    print(f"Found {len(offers)} offers to update with pricing data...")
    
    # Update offers with real prices
    updated_offers, updated_count = update_offers_with_prices(offers, products)
    
    # Save updated offers
    save_json(offers_path, updated_offers)
    
    print(f"Successfully updated {updated_count} offers with real pricing data → {offers_path}")
    print("Note: Some products may not have pricing information available on their pages.")


if __name__ == "__main__":
    main()
