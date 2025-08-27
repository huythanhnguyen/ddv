import requests
import re

def test_crawl():
    print("Testing price crawling...")
    
    url = "https://didongviet.vn/dien-thoai/samsung-galaxy-s25-ultra-256gb.html"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html_content = response.text
        print(f"Got {len(html_content)} characters")
        
        # Look for prices
        price_pattern = r'(\d{1,3}(?:[.,]\d{3})*)'
        prices = re.findall(price_pattern, html_content)
        
        print(f"Found {len(prices)} potential price numbers")
        
        # Show first 10 unique prices
        unique_prices = list(set(prices))
        for i, price in enumerate(unique_prices[:10]):
            print(f"Price {i+1}: {price}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_crawl()
