import requests
import re

def debug_page_structure(url: str):
    """Debug the HTML structure of a product page to understand price formatting."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html_content = response.text
        
        print(f"=== Debugging page: {url} ===")
        print(f"Content length: {len(html_content)} characters")
        
        # Look for price-related text
        price_keywords = ['Giá bán', 'giá', 'đồng', 'VND', 'VNĐ', 'đ']
        
        for keyword in price_keywords:
            # Find all occurrences of the keyword
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)
            matches = pattern.finditer(html_content)
            
            print(f"\n--- Searching for '{keyword}' ---")
            count = 0
            for match in matches:
                if count >= 5:  # Limit to first 5 matches
                    break
                    
                start = max(0, match.start() - 100)
                end = min(len(html_content), match.end() + 100)
                context = html_content[start:end]
                
                print(f"Match {count + 1} at position {match.start()}:")
                print(f"Context: ...{context}...")
                print("-" * 50)
                count += 1
        
        # Look for number patterns that might be prices
        price_pattern = r'(\d{1,3}(?:[.,]\d{3})*)\s*(?:đ|VNĐ|VND|đồng)'
        price_matches = re.findall(price_pattern, html_content, re.IGNORECASE)
        
        print(f"\n--- Potential price numbers found ---")
        unique_prices = list(set(price_matches))
        for price in unique_prices[:10]:  # Show first 10 unique prices
            print(f"Price: {price}")
        
        # Look for specific price sections
        print(f"\n--- Looking for price sections ---")
        price_sections = re.findall(r'<[^>]*class[^>]*price[^>]*>.*?</[^>]*>', html_content, re.IGNORECASE | re.DOTALL)
        for i, section in enumerate(price_sections[:3]):
            print(f"Price section {i + 1}: {section[:200]}...")
        
        # Look for divs with price-related classes
        price_divs = re.findall(r'<div[^>]*class="[^"]*price[^"]*"[^>]*>.*?</div>', html_content, re.IGNORECASE | re.DOTALL)
        for i, div in enumerate(price_divs[:3]):
            print(f"Price div {i + 1}: {div[:200]}...")
            
    except Exception as e:
        print(f"Error debugging {url}: {e}")

if __name__ == "__main__":
    # Test with a few product URLs
    test_urls = [
        "https://didongviet.vn/dien-thoai/samsung-galaxy-s25-ultra-256gb.html",
        "https://didongviet.vn/dien-thoai/iphone-16-pro-max.html"
    ]
    
    for url in test_urls:
        debug_page_structure(url)
        print("\n" + "="*80 + "\n")
