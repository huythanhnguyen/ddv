import requests
from bs4 import BeautifulSoup

# Test technical specs extraction
url = "https://didongviet.vn/dien-thoai/iphone-16-pro-max-256gb.html"
resp = requests.get(url)
soup = BeautifulSoup(resp.text, 'html.parser')

print("=== Testing Technical Specs Extraction ===")
print(f"URL: {url}")

# Look for technical specs section
tech_section = soup.find(string=lambda x: x and "Thông số kỹ thuật" in x)
if tech_section:
    print(f"Found tech section: {tech_section}")
    parent = tech_section.parent
    print(f"Parent tag: {parent.name}")
    
    # Find all text nodes that might contain specs
    spec_texts = []
    for node in parent.find_all_next(string=True):
        if node.parent and node.parent.name in ['p', 'div', 'span', 'li']:
            text = node.strip()
            if text and len(text) > 5:
                spec_texts.append(text)
        if len(spec_texts) > 20:  # Limit to avoid going too far
            break
    
    print(f"\nFound {len(spec_texts)} potential spec texts:")
    for i, text in enumerate(spec_texts[:10]):
        print(f"{i+1}. {text}")
else:
    print("No technical specs section found")
    
    # Try alternative selectors
    print("\nTrying alternative selectors...")
    for selector in ['.specs', '.technical', '.product-specs', '[class*="spec"]']:
        nodes = soup.select(selector)
        if nodes:
            print(f"Found {len(nodes)} nodes with selector '{selector}'")
            for node in nodes[:3]:
                print(f"  - {node.get_text()[:100]}")
