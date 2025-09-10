#!/usr/bin/env python3
"""
Simple web server for testing DDV Product Advisor
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ.setdefault("GEMINI_API_KEY", "AIzaSyBvQZvQZvQZvQZvQZvQZvQZvQZvQZvQZvQ")
os.environ.setdefault("MEILISEARCH_URL", "http://localhost:7700")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")

# Create FastAPI app
app = FastAPI(title="DDV Product Advisor", version="1.0.0")

@app.get("/")
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "DDV Product Advisor API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search": "/search?q=query",
            "products": "/products"
        }
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DDV Product Advisor"}

@app.get("/search")
async def search(q: str = "phone", limit: int = 10):
    """Search products endpoint"""
    try:
        import requests
        response = requests.post("http://localhost:7700/indexes/products/search", 
                               json={"q": q, "limit": limit})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Search failed: {response.status_code}"}
    except Exception as e:
        return {"error": f"Search error: {str(e)}"}

@app.get("/products")
async def products():
    """Get all products endpoint"""
    try:
        import requests
        response = requests.post("http://localhost:7700/indexes/products/search", 
                               json={"q": "", "limit": 50})
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get products: {response.status_code}"}
    except Exception as e:
        return {"error": f"Error getting products: {str(e)}"}

@app.get("/chat", response_class=HTMLResponse)
async def chat():
    """Simple chat interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DDV Product Advisor</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .search-box { width: 100%; padding: 10px; font-size: 16px; margin: 10px 0; }
            .search-btn { padding: 10px 20px; font-size: 16px; background: #007bff; color: white; border: none; cursor: pointer; }
            .result { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }
            .product { margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛍️ DDV Product Advisor</h1>
            <p>Tìm kiếm sản phẩm điện thoại tại Di Động Việt</p>
            
            <input type="text" id="searchInput" class="search-box" placeholder="Nhập tên sản phẩm cần tìm..." value="iPhone">
            <button onclick="searchProducts()" class="search-btn">🔍 Tìm kiếm</button>
            
            <div id="results"></div>
        </div>

        <script>
            async function searchProducts() {
                const query = document.getElementById('searchInput').value;
                const resultsDiv = document.getElementById('results');
                
                if (!query.trim()) {
                    resultsDiv.innerHTML = '<p>Vui lòng nhập từ khóa tìm kiếm</p>';
                    return;
                }
                
                resultsDiv.innerHTML = '<p>Đang tìm kiếm...</p>';
                
                try {
                    const response = await fetch(`/search?q=${encodeURIComponent(query)}&limit=10`);
                    const data = await response.json();
                    
                    if (data.error) {
                        resultsDiv.innerHTML = `<p>Lỗi: ${data.error}</p>`;
                        return;
                    }
                    
                    if (data.hits && data.hits.length > 0) {
                        let html = `<h3>Tìm thấy ${data.totalHits} sản phẩm:</h3>`;
                        data.hits.forEach(product => {
                            const price = product.price ? product.price.current : 0;
                            html += `
                                <div class="product">
                                    <h4>${product.name}</h4>
                                    <p><strong>Thương hiệu:</strong> ${product.brand}</p>
                                    <p><strong>Giá:</strong> ${price.toLocaleString('vi-VN')} VND</p>
                                    <p><strong>Danh mục:</strong> ${product.category}</p>
                                </div>
                            `;
                        });
                        resultsDiv.innerHTML = html;
                    } else {
                        resultsDiv.innerHTML = '<p>Không tìm thấy sản phẩm nào</p>';
                    }
                } catch (error) {
                    resultsDiv.innerHTML = `<p>Lỗi: ${error.message}</p>`;
                }
            }
            
            // Search on Enter key
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    searchProducts();
                }
            });
            
            // Load initial results
            searchProducts();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    print("🚀 Starting DDV Product Advisor Web Server...")
    print("=" * 50)
    print("🌐 Server will be available at:")
    print("   - Main API: http://localhost:8000")
    print("   - Chat Interface: http://localhost:8000/chat")
    print("   - Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
