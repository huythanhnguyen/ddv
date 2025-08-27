# 🧭 DDV Product Advisor

**AI chatbot tư vấn sản phẩm điện thoại thông minh** sử dụng dữ liệu từ Di Động Việt để cung cấp thông tin chính xác về sản phẩm, giá cả, khuyến mãi và cửa hàng.

## 🎯 Tính năng chính

- **Tư vấn sản phẩm**: Tìm kiếm và gợi ý điện thoại phù hợp với nhu cầu
- **Phân tích giá cả**: So sánh giá và khuyến mãi giữa các sản phẩm
- **Tìm cửa hàng**: Định vị cửa hàng gần nhất có hàng tồn kho
- **So sánh sản phẩm**: Đánh giá chi tiết và so sánh tính năng
- **Chatbot AI**: Tương tác tự nhiên bằng tiếng Việt

## 🗂️ Dữ liệu hiện có

- **24 sản phẩm** với thông số kỹ thuật đầy đủ
- **20 offers** với giá cả và khuyến mãi cập nhật
- **20 reviews** với nội dung đánh giá chi tiết
- **48 cửa hàng** Di Động Việt trên toàn quốc

## 🏗️ Kiến trúc hệ thống

### Backend (Python + Google ADK)
- **Main Agent**: Điều phối và quản lý luồng tương tác
- **Product Agent**: Tìm kiếm, gợi ý sản phẩm, phân tích giá cả và tìm cửa hàng (gộp 3 agents)

### Frontend (React + TypeScript + Vite)
- **ProductCard**: Hiển thị thông tin sản phẩm
- **ProductGrid**: Grid layout cho danh sách sản phẩm
- **ChatMessagesView**: Giao diện chat với AI advisor
- **ProductDetailModal**: Modal chi tiết sản phẩm
- **InputForm**: Form nhập yêu cầu tư vấn

## 🚀 Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.8+
- Node.js 18+
- uv (Python package manager)
- Make

### Cài đặt nhanh

```bash
# Clone repository
git clone https://github.com/ddv-team/ddv-product-advisor.git
cd ddv-product-advisor

# Cài đặt dependencies
make quickstart

# Hoặc cài đặt từng phần
make install          # Python dependencies
make install-dev      # Development dependencies
make install-frontend # Frontend dependencies
```

### Chạy ứng dụng

```bash
# Chạy ADK API server development server
make dev

# Chạy frontend development server
make frontend-dev

# Chạy cả backend và frontend
make dev-all
```

### Truy cập ứng dụng
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs

## 🔧 Các lệnh Makefile

### Setup & Installation
```bash
make install          # Cài đặt Python dependencies
make install-dev      # Cài đặt development dependencies
make install-frontend # Cài đặt frontend dependencies
make quickstart       # Cài đặt tất cả dependencies
```

### Development
```bash
make dev              # Chạy ADK API server development server
make frontend-dev     # Chạy frontend development server
make dev-all          # Chạy cả backend và frontend
```

### Building
```bash
make build            # Build Python package
make frontend-build   # Build frontend cho production
make build-all        # Build cả backend và frontend
```

### Testing & Quality
```bash
make test             # Chạy Python tests
make test-cov         # Chạy tests với coverage
make lint             # Kiểm tra code quality
make format           # Format code với black và isort
make type-check       # Kiểm tra type với mypy
```

### Cleanup
```bash
make clean            # Xóa build artifacts
make clean-all        # Xóa tất cả artifacts
```

### Data Management
```bash
make data-sync        # Đồng bộ dữ liệu từ external sources
make data-validate    # Kiểm tra tính toàn vẹn dữ liệu
```

## 📁 Cấu trúc thư mục

```
ddv/
├── app/                      # Backend application
│   ├── __init__.py
│   ├── agent.py             # Main agent orchestrator
│   ├── prompt.py            # Root prompts và instructions
    |---ddv.sqlite3          #sqlite db
│   ├── config.py            # Model configuration
│   ├── sub_agents/          # Sub-agents
│   │   └── product/         # Product recommendation agent (gộp 3 agents)
│   │       ├── __init__.py
│   │       ├── agent.py     # Product advisor agent tích hợp
│   │       └── tools.py     # Product, store, pricing tools
│   ├── shared_libraries/    # Shared utilities
│   │   ├── types.py         # Data models (Pydantic)
│   │   ├── constants.py     # Constants & configurations
│   │   └── utils.py         # Utility functions
│   └── tools/               # Data access layer
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── types/           # TypeScript types
│   │   ├── services/        # API services
│   │   └── utils/           # Utility functions
│   ├── package.json
│   └── vite.config.js
├── profiles/                 # Data files
│   ├── products.json        # 24 products
│   ├── offers.json          # 20 offers
│   ├── reviews.json         # 20 reviews
│   └── stores.json          # 48 stores
├── crawl_tools/              # Data collection tools
├── pyproject.toml           # Python dependencies
├── Makefile                 # Build commands
└── README.md
```

## 🤖 Sử dụng AI Agents

### Tư vấn sản phẩm tích hợp
```
User: "Tôi cần điện thoại chụp ảnh đẹp dưới 20 triệu, gần quận 1"
Agent: Phân tích yêu cầu → Tìm sản phẩm phù hợp → Phân tích giá cả → Tìm cửa hàng gần → Kết quả tích hợp
```

### So sánh sản phẩm với giá cả
```
User: "So sánh iPhone 16 Pro và Galaxy S25 Ultra về giá cả"
Agent: Lấy thông số → So sánh từng tiêu chí → Phân tích giá trị → Đưa ra kết luận
```

### Tìm cửa hàng có hàng
```
User: "Cửa hàng nào ở HCM có iPhone 16 Pro Max và gần quận 1?"
Agent: Xác định vị trí → Tìm cửa hàng gần → Kiểm tra hàng tồn kho
```

### Phân tích khuyến mãi tích hợp
```
User: "Sản phẩm nào đang giảm giá nhiều nhất và có cửa hàng gần quận 3?"
Agent: Tính % giảm giá → Sắp xếp → Phân tích giá trị → Tìm cửa hàng gần
```

## 🧪 Testing

### Chạy tests
```bash
# Chạy tất cả tests
make test

# Chạy tests với coverage
make test-cov

# Chạy specific test file
uv run pytest tests/test_product_agent.py

# Chạy tests với markers
uv run pytest -m "unit"
uv run pytest -m "integration"
```

### Code Quality
```bash
# Kiểm tra code quality
make lint

# Format code
make format

# Type checking
make type-check
```

## 📚 Documentation

### Build documentation
```bash
make docs
```

### Serve documentation locally
```bash
make docs-serve
```

## 🐳 Docker

### Build Docker image
```bash
make docker-build
```

### Run Docker container
```bash
make docker-run
```

## 🔑 Environment Variables

Tạo file `.env` từ `.env.example`:

```bash
make env-setup
```

Các biến môi trường cần thiết:
```env
# Google AI
GOOGLE_API_KEY=your_google_api_key
GOOGLE_GENAI_USE_VERTEXAI=False

# Server
PORT=8000
DEBUG=True
```

## 🤝 Đóng góp

### Quy trình đóng góp
1. Fork repository
2. Tạo feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Tạo Pull Request

### Code Style
- Python: Black + isort + mypy
- TypeScript: ESLint + Prettier
- Commit messages: Conventional Commits

## 🙏 Cảm ơn

- **Google ADK** cho agent framework
- **React + Vite** cho frontend
- **Di Động Việt** cho dữ liệu sản phẩm

---

**DDV Product Advisor** - Trợ lý AI thông minh cho việc mua sắm điện thoại! 🚀📱
