# Tasklog: Đơn Giản Hóa Product Agent - Tập Trung Vào Search Functionality

## Tổng Quan
**Mục tiêu**: Đơn giản hóa product agent để chỉ chuyên tìm thông tin sản phẩm theo yêu cầu khách hàng, với khả năng search mạnh mẽ theo tên, brand, giá, khuyến mãi và các attribute khác.

**Thời gian dự kiến**: 2-3 tuần
**Độ ưu tiên**: Cao
**Người thực hiện**: Development Team

## Phân Tích Hiện Trạng

### 1. Cấu Trúc Dữ Liệu Hiện Tại
- **products.json**: Thông tin cơ bản sản phẩm (tên, brand, giá, specs)
- **offers.json**: Thông tin khuyến mãi, giá cả, cửa hàng
- **reviews.json**: Đánh giá sản phẩm
- **stores.json**: Thông tin cửa hàng

### 2. Vấn Đề Hiện Tại
- Dữ liệu bị tách rời giữa products và offers
- Search functionality còn đơn giản, chưa có full-text search
- Không có indexing cho search performance
- Product agent có quá nhiều tool không cần thiết

## Research Tools Search Engine

### 1. Python Open Source Search Solutions

#### A. Whoosh (Recommended)
- **Ưu điểm**: Pure Python, lightweight, dễ tích hợp, hỗ trợ full-text search
- **Tính năng**: Fuzzy search, faceted search, ranking, stemming
- **Phù hợp**: Dữ liệu vừa và nhỏ (< 1M documents)
- **Install**: `pip install whoosh`

#### B. Elasticsearch
- **Ưu điểm**: Enterprise-grade, distributed, real-time search
- **Nhược điểm**: Overkill cho use case này, cần setup phức tạp
- **Phù hợp**: Dữ liệu lớn, cần distributed search

#### C. Haystack
- **Ưu điểm**: High-level interface, multiple backends
- **Nhược điểm**: Phức tạp hơn Whoosh
- **Phù hợp**: Cần flexibility trong backend

### 2. Lựa Chọn: Whoosh
- **Lý do**: Phù hợp với scale hiện tại, dễ implement, performance tốt
- **Features cần dùng**: Full-text search, faceted search, fuzzy matching

## Task Breakdown

### Phase 1: Data Consolidation & Schema Design (Week 1)

#### Task 1.1: Merge Products & Offers Data
- [ ] **Analyze data structure** của products.json và offers.json
- [ ] **Design unified schema** cho merged data
- [ ] **Create data migration script** để merge 2 file
- [ ] **Validate merged data** và fix inconsistencies
- [ ] **Update data_store.py** để load merged data

**Schema mới**:
```json
{
  "id": "string",
  "name": "string", 
  "brand": "string",
  "category": "string",
  "price": {
    "current": "number",
    "original": "number",
    "currency": "string",
    "discount_percentage": "number"
  },
  "promotions": {
    "free_gifts": ["string"],
    "vouchers": ["string"],
    "special_discounts": ["string"],
    "bundle_offers": ["string"]
  },
  "specs": {
    "screen_size": "string",
    "camera": "string",
    "storage": "string",
    "ram": "string"
  },
  "availability": "string",
  "url": "string",
  "images": ["string"],
  "last_updated": "datetime"
}
```

#### Task 1.2: Data Cleaning & Validation
- [ ] **Remove duplicates** và merge duplicate products
- [ ] **Standardize brand names** (Apple, Samsung, etc.)
- [ ] **Normalize price data** và fix invalid prices
- [ ] **Clean promotion text** và standardize format
- [ ] **Validate URLs** và fix broken links

### Phase 2: Search Engine Implementation (Week 2)

#### Task 2.1: Install & Setup Whoosh
- [ ] **Add Whoosh dependency** vào pyproject.toml
- [ ] **Create search index structure** với proper schema
- [ ] **Implement index builder** cho merged data
- [ ] **Add search index to DataStore class**

#### Task 2.2: Core Search Functionality
- [ ] **Implement full-text search** theo tên sản phẩm
- [ ] **Add brand-based search** với exact và fuzzy matching
- [ ] **Implement price range search** (min-max)
- [ ] **Add promotion-based search** (khuyến mãi, quà tặng)
- [ ] **Implement attribute search** (screen size, camera, storage)

#### Task 2.3: Advanced Search Features
- [ ] **Add fuzzy search** cho tên sản phẩm
- [ ] **Implement faceted search** (brand, category, price range)
- [ ] **Add search ranking** dựa trên relevance
- [ ] **Implement search suggestions** và autocomplete

### Phase 3: Simplified Product Agent (Week 3)

#### Task 3.1: Streamline Agent Tools
- [ ] **Remove unnecessary tools** (store_location, store_availability)
- [ ] **Keep essential tools**:
  - `product_search_tool` (enhanced)
  - `product_compare_tool` (simplified)
  - `price_analysis_tool` (basic)
- [ ] **Update tool implementations** để dùng search engine mới

#### Task 3.2: Enhanced Search Tool
- [ ] **Rewrite product_search_tool** để dùng Whoosh
- [ ] **Add search parameters**:
  - Text query (tên, brand, features)
  - Price range (min, max)
  - Brand filter
  - Category filter
  - Promotion filter
- [ ] **Implement result ranking** và pagination
- [ ] **Add search result highlighting**

#### Task 3.3: Update Agent Prompts
- [ ] **Simplify PRODUCT_AGENT_INSTR** để focus vào search
- [ ] **Update tool descriptions** cho phù hợp
- [ ] **Add search examples** trong prompt

### Phase 4: Testing & Optimization (Week 3)

#### Task 4.1: Performance Testing
- [ ] **Test search performance** với dataset hiện tại
- [ ] **Optimize index size** và search speed
- [ ] **Add search result caching** nếu cần
- [ ] **Test with different query types**

#### Task 4.2: Quality Assurance
- [ ] **Test search accuracy** với various queries
- [ ] **Validate search results** với expected outcomes
- [ ] **Test edge cases** (empty queries, invalid filters)
- [ ] **Performance benchmarking** vs old implementation

## Implementation Details

### 1. Whoosh Integration
```python
from whoosh.fields import Schema, TEXT, NUMERIC, DATETIME, ID
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import scoring

# Schema definition
schema = Schema(
    id=ID(stored=True),
    name=TEXT(stored=True),
    brand=TEXT(stored=True),
    category=TEXT(stored=True),
    price_current=NUMERIC(stored=True),
    price_original=NUMERIC(stored=True),
    promotions=TEXT(stored=True),
    specs=TEXT(stored=True),
    availability=TEXT(stored=True)
)
```

### 2. Search Implementation
```python
def search_products(self, query: str, filters: dict = None) -> List[Dict]:
    """Enhanced search using Whoosh"""
    with self.ix.searcher() as searcher:
        # Build query
        qp = MultifieldParser(['name', 'brand', 'specs', 'promotions'], self.ix.schema)
        q = qp.parse(query)
        
        # Apply filters
        if filters:
            # Price range, brand, category filters
            pass
            
        # Execute search
        results = searcher.search(q, limit=20)
        return [dict(r) for r in results]
```

### 3. Data Migration Script
```python
def merge_products_offers():
    """Merge products.json and offers.json into unified format"""
    products = load_json('profiles/products.json')
    offers = load_json('profiles/offers.json')
    
    merged = []
    for product in products:
        offer = find_offer_by_id(product['id'], offers)
        merged_product = merge_product_offer(product, offer)
        merged.append(merged_product)
    
    save_json('profiles/merged_products.json', merged)
```

## Dependencies & Requirements

### New Dependencies
```toml
dependencies = [
    # Existing dependencies...
    "whoosh>=2.7.4",  # Full-text search engine
]
```

### System Requirements
- Python 3.9+
- Memory: 2GB+ cho search index
- Storage: 100MB+ cho merged data

## Success Metrics

### Performance
- **Search speed**: < 100ms cho queries đơn giản
- **Index size**: < 50MB cho 10K products
- **Memory usage**: < 200MB cho search operations

### Quality
- **Search accuracy**: > 95% relevant results
- **Query coverage**: Support 90%+ user query types
- **Result ranking**: Most relevant products appear first

### User Experience
- **Response time**: < 2s cho complex queries
- **Result relevance**: Users find desired products quickly
- **Search suggestions**: Helpful autocomplete và suggestions

## Risk Assessment

### High Risk
- **Data migration**: Có thể mất data trong quá trình merge
- **Search performance**: Whoosh có thể chậm với dataset lớn

### Medium Risk
- **Schema changes**: Cần update frontend để handle new data format
- **Tool compatibility**: Existing tools có thể break với new structure

### Mitigation
- **Backup data** trước khi migration
- **Test thoroughly** với subset data trước
- **Gradual rollout** với feature flags

## Future Enhancements

### Phase 5: Advanced Features (Future)
- [ ] **Semantic search** với embeddings
- [ ] **Search analytics** và query optimization
- [ ] **Personalized search** dựa trên user history
- [ ] **Search API** cho external integrations
- [ ] **Real-time search** với live data updates

## Conclusion

Việc đơn giản hóa product agent với focus vào search functionality sẽ:
1. **Cải thiện user experience** với search mạnh mẽ
2. **Giảm complexity** của agent system
3. **Tăng performance** với proper indexing
4. **Dễ maintain** và extend trong tương lai

Whoosh là lựa chọn tối ưu cho use case này, cung cấp balance tốt giữa performance và simplicity.
