# DDV Product Advisor - Simple Version

## 📋 Tổng quan
Phiên bản đơn giản của DDV Product Advisor, được thiết kế theo cấu trúc của `personalized_shopping` sample để dễ hiểu và maintain.

## 🏗️ Cấu trúc

```
ddv/
├── app/
│   ├── agent_simple.py          # Agent chính (đơn giản)
│   ├── prompt_simple.py         # Instructions cho agent
│   ├── config_simple.py         # Cấu hình đơn giản
│   └── tools/                   # Tools chuyên biệt
│       ├── search.py            # Tìm kiếm sản phẩm
│       ├── explore.py           # Khám phá sản phẩm
│       ├── compare.py           # So sánh sản phẩm
│       └── meilisearch_simple.py # Search engine đơn giản
└── test_simple_agent.py         # Test script
```

## 🚀 Cách sử dụng

### 1. Khởi động Meilisearch
```bash
# Chạy Meilisearch server
./meilisearch --http-addr 127.0.0.1:7700
```

### 2. Chạy Agent
```python
from app.agent_simple import ddv_simple_agent

# Sử dụng agent
response = await ddv_simple_agent.run("Tìm iPhone 16 Pro")
```

### 3. Test Agent
```bash
python test_simple_agent.py
```

## 🛠️ Tools

### search_products(keywords, filters=None)
- Tìm kiếm sản phẩm theo từ khóa
- Hỗ trợ filters: price_max, price_min, brand, battery_min, camera_min

### explore_product(product_id)
- Lấy thông tin chi tiết sản phẩm
- Hiển thị specs, giá, đánh giá

### compare_products(product_ids)
- So sánh nhiều sản phẩm
- Tạo bảng so sánh chi tiết

## ⚙️ Cấu hình

### Meilisearch
```python
MEILISEARCH_CONFIG = {
    "url": "http://localhost:7700",
    "api_key": "",
    "index_name": "products",
    "timeout": 30
}
```

### Model
```python
MODEL_CONFIG = {
    "primary_model": "gemini-2.5-flash",
    "worker_model": "gemini-2.5-flash"
}
```

## 🔄 So sánh với phiên bản cũ

| Tính năng | Phiên bản cũ | Phiên bản đơn giản |
|-----------|--------------|-------------------|
| Agent | Phức tạp, nhiều sub-agents | Đơn giản, 1 agent chính |
| Tools | Monolithic | Chuyên biệt |
| Config | Phức tạp | Đơn giản |
| Maintain | Khó | Dễ |
| Performance | Chậm | Nhanh |

## 🎯 Lợi ích

1. **Đơn giản**: Dễ hiểu và maintain
2. **Nhanh**: Ít overhead, response time tốt
3. **Linh hoạt**: Dễ mở rộng và customize
4. **Ổn định**: Ít lỗi, dễ debug
5. **Tương thích**: Hoạt động tốt với ADK framework

## 🚧 Cần cải thiện

- [ ] Thêm error handling tốt hơn
- [ ] Cải thiện UI integration
- [ ] Thêm caching
- [ ] Tối ưu performance
- [ ] Thêm unit tests

## 📝 Ghi chú

- Phiên bản này tập trung vào simplicity và usability
- Tương thích với cấu trúc của `personalized_shopping` sample
- Dễ dàng migrate từ phiên bản cũ
- Phù hợp cho development và production
