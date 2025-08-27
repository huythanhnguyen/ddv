# 🧭 DDV Product Advisor — Product Requirements Document

## 📋 Tổng quan dự án

**DDV Product Advisor** là một chatbot AI tư vấn sản phẩm điện thoại thông minh, sử dụng dữ liệu từ Di Động Việt để cung cấp thông tin chính xác về sản phẩm, giá cả, khuyến mãi và cửa hàng.

### 🎯 Mục tiêu chính
- Tư vấn sản phẩm điện thoại dựa trên nhu cầu người dùng
- Cung cấp thông tin giá cả, khuyến mãi và cửa hàng có hàng
- Hỗ trợ tìm kiếm và so sánh sản phẩm
- Định hướng người dùng đến cửa hàng gần nhất

---

## 🗂️ Cấu trúc dữ liệu hiện có

### 1. **`profiles/products.json`** - Cơ sở dữ liệu sản phẩm
**24 sản phẩm** với thông số kỹ thuật đầy đủ

### 2. **`profiles/offers.json`** - Thông tin giá cả và khuyến mãi
**20 offers** với cấu trúc chuẩn

### 3. **`profiles/reviews.json`** - Nội dung đánh giá chi tiết
**20 reviews** với cấu trúc phong phú

### 4. **`profiles/stores.json`** - Hệ thống cửa hàng
**48 cửa hàng** Di Động Việt trên toàn quốc

---

## 🏗️ Kiến trúc hệ thống

### Cấu trúc thư mục (dựa trên tree_ai_agent)
```
ddv/
├── app/
│   ├── __init__.py
│   ├── agent.py             # Main agent orchestrator (ADK-style)
│   ├── prompt.py            # Root prompts và instructions
│   ├── config.py            # Model configuration và settings
│   ├── sub_agents/
│   │   ├── __init__.py
│   │   └── product/
│   │       ├── __init__.py
│   │       ├── agent.py     # Product recommendation agent (gộp 3 agents)
│   │       └── tools.py     # Product, store, pricing tools
│   ├── shared_libraries/
│   │   ├── __init__.py
│   │   ├── types.py         # Data models & schemas (Pydantic)
│   │   ├── constants.py     # Constants & configurations
│   │   └── utils.py         # Utility functions
│   ├── tools/
│   │   ├── __init__.py
│   │   └── product_store.py # CRUD layer for data access
│   ├── profiles/             # Data files (đã hoàn thành)
│   └── crawl_tools/         # Data collection tools (đã hoàn thành)
├── frontend/                 # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/          # Radix UI components
│   │   │   ├── ProductCard.tsx
│   │   │   ├── ProductGrid.tsx
│   │   │   ├── ChatMessagesView.tsx
│   │   │   ├── ProductDetailModal.tsx
│   │   │   └── InputForm.tsx
│   │   ├── types/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
├── pyproject.toml           # Python dependencies với uv
├── Makefile                 # Build và deployment commands
├── README.md
└── .env.example
```

---

## 🤖 Agent Architecture (ADK-style)

### 1. **Main Agent (`app/agent.py`)**
**Vai trò**: Điều phối và quản lý luồng tương tác (ADK-style)

**ADK Callback Pattern**:
```python
def _before_agent_callback(callback_context: CallbackContext) -> None:
    """Initialize session for DDV product advisor"""
    session = callback_context._invocation_context.session
    
    # User profile initialization
    if SESSION_STATE_KEYS["USER_PROFILE"] not in session.state:
        session.state[SESSION_STATE_KEYS["USER_PROFILE"]] = {
            "user_type": "customer",
            "preferred_brands": [],
            "budget_range": "flexible",
            "location": "Vietnam",
            "first_visit": True
        }
    
    # Track conversation history
    if SESSION_STATE_KEYS["CONVERSATION_HISTORY"] not in session.state:
        session.state[SESSION_STATE_KEYS["CONVERSATION_HISTORY"]] = []
    
    # Default to product recommendation
    session.state[SESSION_STATE_KEYS["CURRENT_USE_CASE"]] = USE_CASES["PRODUCT_RECOMMENDATION"]
```

**SafeAgentTool Implementation**:
```python
class SafeAgentTool(AgentTool):
    """AgentTool subclass that catches errors during sub-agent execution."""
    
    def __init__(self, agent: LlmAgent):
        super().__init__(agent)

    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        except Exception as exc:
            return {
                "error": True,
                "agent": self.agent.name,
                "message": str(exc),
            }
```

**Root Agent Configuration**:
```python
ddv_product_advisor = LlmAgent(
    model=config.primary_model,
    name="ddv_product_advisor",
    description="Trợ lý AI tư vấn sản phẩm điện thoại Di Động Việt",
    instruction=ROOT_AGENT_INSTR,
    tools=[SafeAgentTool(product_agent)],  # Chỉ 1 product agent
    before_agent_callback=_before_agent_callback,
    after_agent_callback=_after_agent_callback,
)
```

### 2. **Product Agent (`app/sub_agents/product/agent.py`) - GỘP 3 AGENTS**
**Vai trò**: Tìm kiếm, gợi ý sản phẩm, phân tích giá cả và tìm cửa hàng

**Chức năng tích hợp**:
- **Product Search & Recommendation**: Tìm kiếm và gợi ý sản phẩm phù hợp
- **Price Analysis**: Phân tích giá cả, khuyến mãi và giá trị
- **Store Location**: Tìm cửa hàng có hàng và gần người dùng
- **Product Comparison**: So sánh sản phẩm dựa trên nhiều tiêu chí

**Agent Configuration**:
```python
product_agent = LlmAgent(
    model=config.worker_model,
    name="product_advisor_agent",
    description="Chuyên gia tư vấn sản phẩm điện thoại - tích hợp tìm kiếm, giá cả và cửa hàng",
    instruction=PRODUCT_AGENT_INSTR,
    tools=[
        product_search_tool,      # Tìm kiếm sản phẩm
        price_analysis_tool,      # Phân tích giá cả
        store_location_tool,      # Tìm cửa hàng
        product_compare_tool,     # So sánh sản phẩm
        store_availability_tool   # Kiểm tra hàng tồn kho
    ],
)
```

**Workflow tích hợp**:
```
User Input → Product Agent → Phân tích intent → Chọn tool phù hợp:
├── Tìm sản phẩm → product_search_tool
├── Phân tích giá → price_analysis_tool  
├── Tìm cửa hàng → store_location_tool
├── So sánh sản phẩm → product_compare_tool
└── Kiểm tra hàng tồn kho → store_availability_tool
```

---

## 🎨 Frontend Architecture (React + TypeScript + Vite)

### Core Components (từ mm_multi_agent_v2)
- **ProductCard.tsx**: Hiển thị thông tin sản phẩm với hình ảnh, giá, đặc điểm
- **ProductGrid.tsx**: Grid layout cho danh sách sản phẩm
- **ChatMessagesView.tsx**: Giao diện chat với AI advisor
- **ProductDetailModal.tsx**: Modal chi tiết sản phẩm
- **InputForm.tsx**: Form nhập yêu cầu tư vấn
- **SessionManager.tsx**: Quản lý phiên tư vấn
- **CartPanel.tsx**: Panel giỏ hàng và so sánh

### UI Framework
- **Radix UI**: Components cơ bản (tabs, select, tooltip, scroll-area)
- **Tailwind CSS**: Styling và responsive design
- **Lucide React**: Icons
- **React Markdown**: Hiển thị nội dung markdown từ reviews

---

## 📊 Data Schema & Models (Pydantic)

### Product Schema
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class Product(BaseModel):
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    brand: str = Field(..., description="Brand name")
    category: str = Field(..., description="Product category")
    price: int = Field(..., description="Current price in VND")
    storage: str = Field(..., description="Storage capacity")
    ram: str = Field(..., description="RAM capacity")
    chipset: str = Field(..., description="Processor chipset")
    camera_main: str = Field(..., description="Main camera specification")
    camera_front: str = Field(..., description="Front camera specification")
    battery: str = Field(..., description="Battery specification")
    screen: str = Field(..., description="Screen specification")
    os: str = Field(..., description="Operating system")
    connectivity: List[str] = Field(default_factory=list, description="Connectivity features")
    features: List[str] = Field(default_factory=list, description="Special features")
    url: str = Field(..., description="Product URL on DDV website")
```

---

## 🔄 Workflow chính

### 1. **Tư vấn sản phẩm tích hợp**
```
User Input → Main Agent → Product Agent → Phân tích intent → Chọn tool phù hợp → Kết quả tích hợp
```

**Ví dụ tích hợp**:
- Input: "Tôi cần điện thoại chụp ảnh đẹp dưới 20 triệu, gần quận 1"
- Process: Product Agent → Tìm sản phẩm phù hợp → Phân tích giá cả → Tìm cửa hàng gần → Kết quả tích hợp
- Output: 3-5 sản phẩm + phân tích giá trị + danh sách cửa hàng gần nhất

### 2. **So sánh sản phẩm với giá cả**
```
User Input → Product Agent → Product Compare Tool → Price Analysis Tool → Comparison Table
```

### 3. **Tìm cửa hàng có hàng**
```
User Input → Product Agent → Store Location Tool → Store Availability Tool → Store List
```

---

## 🎯 Use Cases & Scenarios

### 1. **Tư vấn sản phẩm tích hợp**
- **Input**: "Tôi có 15 triệu, muốn điện thoại chụp ảnh tốt, gần quận 7"
- **Process**: Tìm sản phẩm → Phân tích giá → Tìm cửa hàng gần
- **Output**: Samsung A56, Xiaomi 13T, OPPO Reno11 + phân tích giá trị + danh sách cửa hàng

### 2. **So sánh sản phẩm với giá cả**
- **Input**: "So sánh iPhone 16 Pro và Galaxy S25 Ultra về giá cả"
- **Output**: Bảng so sánh chi tiết + phân tích giá trị + khuyến mãi

### 3. **Tìm cửa hàng có hàng**
- **Input**: "Cửa hàng nào ở HCM có iPhone 16 Pro Max và gần quận 1?"
- **Output**: Danh sách cửa hàng + khoảng cách + thông tin hàng tồn kho

### 4. **Phân tích khuyến mãi tích hợp**
- **Input**: "Sản phẩm nào đang giảm giá nhiều nhất và có cửa hàng gần quận 3?"
- **Output**: Top 5 sản phẩm giảm giá + phân tích giá trị + cửa hàng gần nhất

---

## 🚀 Triển khai & Demo

### Phase 1: Core Implementation (Week 1)
- [ ] Implement data models và schemas với Pydantic
- [ ] Build main agent với ADK-style callback hooks
- [ ] Implement product agent tích hợp (gộp 3 agents)
- [ ] Basic ADK API server setup

### Phase 2: Advanced Features (Week 2)
- [ ] Implement product search và recommendation
- [ ] Add price analysis và store location
- [ ] Enhance product comparison
- [ ] Add store availability checking

### Phase 3: Frontend Integration (Week 3)
- [ ] React components từ mm_multi_agent_v2
- [ ] API integration với ADK backend
- [ ] State management và routing
- [ ] Responsive design và testing

---

## 🔧 Technical Requirements

### Backend Dependencies
- Python 3.8+
- Google ADK cho agent framework (không cần FastAPI)
- Pydantic cho data validation
- uv cho package management

### Frontend Dependencies
- React 19+
- TypeScript 5.7+
- Vite cho build tool
- Tailwind CSS cho styling
- Radix UI cho components

---

*Document này phản ánh tình trạng hiện tại của dự án với data đã hoàn thành, architecture từ tree_ai_agent, frontend elements từ mm_multi_agent_v2, và focus vào implementation với ADK API server trực tiếp và 1 Product Agent tích hợp.*


