# DDV Product Agent Search Flow

## Tổng quan
Khi người dùng search sản phẩm (ví dụ: "tìm điện thoại giá rẻ"), hệ thống sẽ hoạt động theo flow sau:

## 1. User Input
```
User: "tìm điện thoại giá rẻ"
```

## 2. Simplified Product Agent
**File**: `app/sub_agents/product/simplified_agent.py`

```python
simplified_product_agent = Agent(
    name="simplified_product_advisor_agent",
    model=config.worker_model,  # gemini-2.0-flash
    description=SIMPLIFIED_PRODUCT_AGENT_DESCRIPTION,
    instruction=SIMPLIFIED_PRODUCT_AGENT_INSTR,
    tools=[
        enhanced_product_search_tool  # Tool chính để search
    ],
    output_key="simplified_product_advisor_response",
)
```

**Chức năng**: 
- Nhận input từ user
- Gọi `enhanced_product_search_tool` để tìm kiếm
- Xử lý và format response

## 3. Enhanced Product Search Tool
**File**: `app/sub_agents/product/simplified_tools.py`

### 3.1 Input Processing
```python
def enhanced_product_search_tool(user_input: str) -> Dict[str, Any]:
    # Input: "tìm điện thoại giá rẻ"
    search_query = user_input.strip()  # "tìm điện thoại giá rẻ"
```

### 3.2 Extract Requirements
```python
    # Extract budget từ text
    budget_min, budget_max = extract_budget_from_text(user_input)
    # Result: budget_min=None, budget_max=None (vì "giá rẻ" không có số cụ thể)
    
    # Extract brands từ text  
    brands = extract_brands_from_text(user_input)
    # Result: brands=[] (không có brand cụ thể)
    
    # Extract features từ text
    features = extract_features_from_text(user_input)
    # Result: features=["điện thoại", "giá rẻ"]
```

### 3.3 Build Filters
```python
    filters = {}
    if brands:
        filters['brand'] = brands[0]
    if budget_min is not None or budget_max is not None:
        filters['price_min'] = budget_min
        filters['price_max'] = budget_max
    # Result: filters = {} (không có filter cụ thể)
```

### 3.4 Call Enhanced Data Store
```python
    products = enhanced_data_store.search_products(
        query=search_query,  # "tìm điện thoại giá rẻ"
        filters=filters,     # {}
        limit=10
    )
```

## 4. Enhanced Product Store
**File**: `app/tools/enhanced_product_store.py`

### 4.1 Search Products Method
```python
def search_products(self, query="", filters=None, limit=20, sort=None):
    if not self.search_engine:  # MeilisearchEngine
        return []
    
    results = self.search_engine.search_products(
        query=query,      # "tìm điện thoại giá rẻ"
        filters=filters,  # {}
        limit=limit,      # 10
        sort=sort
    )
    return results
```

## 5. Meilisearch Engine
**File**: `app/tools/meilisearch_engine.py`

### 5.1 Search Processing
```python
def search_products(self, query, filters=None, limit=20, sort=None):
    # Query: "tìm điện thoại giá rẻ"
    # Filters: {}
    # Limit: 10
```

### 5.2 Prepare Search Parameters
```python
    search_params = {
        'limit': 10,
        'attributesToRetrieve': ['*'],
        'attributesToHighlight': ['name', 'brand', 'category', '_searchable_text'],
        'highlightPreTag': '<mark>',
        'highlightPostTag': '</mark>'
    }
```

### 5.3 Execute Search
```python
    # Gọi Meilisearch API
    results = self.index.search("tìm điện thoại giá rẻ", search_params)
```

### 5.4 Meilisearch Index Search
**Meilisearch sẽ tìm kiếm trong các trường:**
- `name`: Tên sản phẩm
- `brand`: Thương hiệu  
- `category`: Danh mục
- `_searchable_text`: Tất cả dữ liệu đã flatten
- `specs.*`: Tất cả thông số kỹ thuật
- `promotions.*`: Tất cả khuyến mãi

**Kết quả tìm kiếm:**
- Tìm các sản phẩm có từ "điện thoại" trong name/category
- Tìm các sản phẩm có "giá rẻ" trong promotions hoặc price range thấp
- Sắp xếp theo relevance score

### 5.5 Process Results
```python
    products = []
    for hit in results.get('hits', []):
        product = hit.copy()
        
        # Thêm search metadata
        product['search_metadata'] = {
            'relevance_score': hit.get('_rankingScore', 0.0),
            'formatted': hit.get('_formatted', {}),
            'matched_terms': hit.get('_matchesInfo', {})
        }
        
        products.append(product)
    
    return products
```

## 6. Back to Enhanced Product Search Tool

### 6.1 Process Results
```python
    if not products:
        return {
            "success": False,
            "message": "Không tìm thấy sản phẩm phù hợp",
            "suggestions": [...]
        }
```

### 6.2 Build UI Payload
```python
    ui_products = []
    for p in products:
        # Clean product data
        clean_p = clean_product_data(p)
        
        # Extract pricing info
        current_price = clean_p.get('price', {}).get('current', 0)
        original_price = clean_p.get('price', {}).get('original', 0)
        
        # Build UI product object
        ui_product = {
            "id": clean_p.get('id', ''),
            "name": clean_p.get('name', ''),
            "price": {
                "current": current_price,
                "original": original_price,
                "currency": "VND",
                "discount": discount_label
            },
            "image": {"url": image_url},
            "productUrl": clean_p.get('url', ''),
        }
        
        ui_products.append(ui_product)
```

### 6.3 Add AI Analysis
```python
    ai_analysis = []
    for p in products:
        if 'search_metadata' in p:  # Từ Meilisearch
            ai_analysis.append({
                'product_id': p.get('id', ''),
                'relevance_score': p['search_metadata'].get('relevance_score', 0),
                'matched_terms': p['search_metadata'].get('matched_terms', {})
            })
```

### 6.4 Create Product Display
```python
    product_display = {
        "type": "product-display",
        "message": f"Tìm thấy {len(products)} sản phẩm phù hợp",
        "products": ui_products,
        "ai_analysis": ai_analysis
    }
```

### 6.5 Return Final Response
```python
    return {
        "success": True,
        "products": products,           # Raw product data
        "total_found": len(products),
        "product_display": product_display,  # UI-ready data
        "criteria": {
            "budget_min": budget_min,
            "budget_max": budget_max,
            "brands": brands,
            "search_query": search_query,
            "ai_enhanced": True
        }
    }
```

## 7. Back to Simplified Product Agent

### 7.1 Process Tool Response
```python
# Agent nhận response từ enhanced_product_search_tool
# Format và gửi về user
```

### 7.2 Final Output
```json
{
    "type": "product-display",
    "message": "Tìm thấy 5 sản phẩm phù hợp với yêu cầu của bạn",
    "products": [
        {
            "id": "samsung-galaxy-a56",
            "name": "Samsung Galaxy A56 5G",
            "price": {
                "current": 8500000,
                "original": 9500000,
                "currency": "VND",
                "discount": "-10%"
            },
            "image": {"url": "https://..."},
            "productUrl": "https://didongviet.vn/..."
        }
    ],
    "ai_analysis": [
        {
            "product_id": "samsung-galaxy-a56",
            "relevance_score": 0.85,
            "matched_terms": {
                "name": ["điện thoại"],
                "category": ["phone"],
                "promotions": ["giá rẻ"]
            }
        }
    ]
}
```

## Tóm tắt Flow

1. **User Input** → "tìm điện thoại giá rẻ"
2. **Simplified Product Agent** → Gọi enhanced_product_search_tool
3. **Enhanced Product Search Tool** → Extract requirements, build filters
4. **Enhanced Product Store** → Gọi Meilisearch engine
5. **Meilisearch Engine** → Search trong index với query "tìm điện thoại giá rẻ"
6. **Meilisearch Index** → Tìm kiếm trong tất cả fields (name, specs, promotions, etc.)
7. **Results Processing** → Format data, add metadata
8. **UI Payload Creation** → Tạo product display object
9. **Response** → Trả về danh sách sản phẩm với AI analysis

## Điểm mạnh của hệ thống

- **Tìm kiếm toàn diện**: Meilisearch tìm trong tất cả fields
- **AI Analysis**: Relevance score và matched terms
- **Flexible Filtering**: Brand, price range, features
- **UI Ready**: Data đã được format sẵn cho frontend
- **Fast Response**: <50ms search time
- **Vietnamese Support**: Hỗ trợ tìm kiếm tiếng Việt


