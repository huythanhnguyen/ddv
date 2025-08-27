# 🧭 DDV Product Advisor — Task Log

## 📋 Tổng quan dự án

**DDV Product Advisor** là chatbot AI tư vấn sản phẩm điện thoại thông minh, sử dụng dữ liệu từ Di Động Việt để cung cấp thông tin chính xác về sản phẩm, giá cả, khuyến mãi và cửa hàng.

**Trạng thái hiện tại**: Data collection đã hoàn thành, tập trung vào implementation của agents và prompts với architecture từ tree_ai_agent và frontend từ mm_multi_agent_v2.

---

## ✅ **Phase 0 — Data Collection & Setup (ĐÃ HOÀN THÀNH)**

### Data Infrastructure
- [x] **`profiles/products.json`** - 24 sản phẩm với thông số kỹ thuật đầy đủ
- [x] **`profiles/offers.json`** - 20 offers với giá cả và khuyến mãi cập nhật
- [x] **`profiles/reviews.json`** - 20 reviews với nội dung chi tiết
- [x] **`profiles/stores.json`** - 48 cửa hàng Di Động Việt trên toàn quốc

### Data Collection Tools (Đã hoàn thành)
- [x] Tạo `crawl_tools/complete_offer_update.py` để cập nhật giá cả chính xác và thông tin cửa hàng
- [x] Tạo `crawl_tools/final_price_cleanup.py` để chuẩn hóa cấu trúc dữ liệu giá
- [x] Tạo `crawl_tools/sync_offers.py` để đồng bộ offers cho tất cả sản phẩm
- [x] Tạo `crawl_tools/sync_reviews.py` để đồng bộ reviews cho tất cả sản phẩm
- [x] Tạo `crawl_tools/enrich_from_internal.py` để điền thông tin còn thiếu từ dữ liệu nội bộ
- [x] Tạo `crawl_tools/crawl_ddv.py` để crawl thông số kỹ thuật từ website Di Động Việt

### Data Quality & Validation
- [x] Cập nhật tất cả offers với dữ liệu giá thực tế (đã loại bỏ giá không hợp lý)
- [x] Chuẩn hóa cấu trúc dữ liệu giá với discount_percentage và price_note
- [x] Đảm bảo mỗi sản phẩm có entry trong offers.json với cấu trúc cơ bản
- [x] Đảm bảo mỗi sản phẩm có entry trong reviews.json với nội dung placeholder
- [x] Cập nhật `profiles/stores.json` với 48 cửa hàng Di Động Việt trên toàn quốc

---

## 🚀 **Phase 1 — Core Implementation (ĐANG THỰC HIỆN)**

### 1. **Project Setup với uv và Makefile**
- [ ] Tạo `pyproject.toml` với dependencies cần thiết
- [ ] Tạo `Makefile` với commands build, dev, test, clean
- [ ] Setup virtual environment với uv
- [ ] Install dependencies và verify setup

### 2. **Backend Architecture (dựa trên tree_ai_agent)**
- [ ] Tạo cấu trúc thư mục `app/` theo pattern tree_ai_agent
- [ ] Implement `app/__init__.py`
- [ ] Implement `app/config.py` với ModelConfiguration
- [ ] Implement `app/prompt.py` với ROOT_AGENT_INSTR
- [ ] Implement `app/agent.py` với ADK-style callback hooks

### 3. **Data Models & Schemas (Pydantic)**
- [ ] Tạo `app/shared_libraries/types.py` với các data models:
  - [ ] `Product` class với tất cả fields từ products.json
  - [ ] `Offer` class với pricing, promotions, availability
  - [ ] `Review` class với sections, pricing_table, comparisons, FAQs
  - [ ] `Store` class với location, contact, status
  - [ ] `ProductRequirement` class cho user input parsing
  - [ ] `ProductRecommendation` class cho output

### 4. **Constants & Configurations**
- [ ] Tạo `app/shared_libraries/constants.py`:
  - [ ] `SESSION_STATE_KEYS` cho session management
  - [ ] `USE_CASES` cho các use case chính
  - [ ] Brand mappings và synonyms
  - [ ] Budget buckets (dưới 5M, 5-8M, 8-12M, 12-18M, 18-25M, trên 25M)
  - [ ] Feature categories (camera, gaming, livestream, battery, design)

### 5. **Utility Functions**
- [ ] Tạo `app/shared_libraries/utils.py`:
  - [ ] Price formatting functions
  - [ ] Distance calculation (Haversine)
  - [ ] Search và filter utilities
  - [ ] Data validation helpers

---

## 🤖 **Phase 2 — Agent Implementation (TIẾP THEO)**

### 1. **Main Agent (`app/agent.py`) - ADK-style**
- [ ] Implement main orchestrator agent với LlmAgent
- [ ] ADK callback hooks: `_before_agent_callback`, `_after_agent_callback`
- [ ] SafeAgentTool implementation cho error handling
- [ ] Intent classification và routing
- [ ] Context management và session handling
- [ ] Response formatting và output generation

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

## 🎨 **Phase 3 — Frontend Implementation (từ mm_multi_agent_v2)**

### 1. **Frontend Setup**
- [ ] Tạo `frontend/` directory với React + TypeScript + Vite
- [ ] Copy package.json và dependencies từ mm_multi_agent_v2
- [ ] Setup Tailwind CSS và Radix UI
- [ ] Configure Vite và TypeScript

### 2. **Core Components (từ mm_multi_agent_v2)**
- [ ] **ProductCard.tsx**: Hiển thị thông tin sản phẩm với hình ảnh, giá, đặc điểm
- [ ] **ProductGrid.tsx**: Grid layout cho danh sách sản phẩm
- [ ] **ChatMessagesView.tsx**: Giao diện chat với AI advisor
- [ ] **ProductDetailModal.tsx**: Modal chi tiết sản phẩm
- [ ] **InputForm.tsx**: Form nhập yêu cầu tư vấn
- [ ] **SessionManager.tsx**: Quản lý phiên tư vấn
- [ ] **CartPanel.tsx**: Panel giỏ hàng và so sánh

### 3. **UI Framework Integration**
- [ ] Radix UI components (tabs, select, tooltip, scroll-area)
- [ ] Tailwind CSS styling và responsive design
- [ ] Lucide React icons
- [ ] React Markdown cho nội dung từ reviews

### 4. **State Management & Routing**
- [ ] React hooks cho local state
- [ ] Context API cho global state (user preferences, cart)
- [ ] Local storage cho session persistence
- [ ] React Router cho navigation

---

## 🔄 **Phase 4 — Integration & Workflow**

### 1. **API Integration với ADK**
- [ ] ADK API server endpoints:
  - [ ] `/api/products` - Product search và recommendation
  - [ ] `/api/stores` - Store location và availability
  - [ ] `/api/pricing` - Price analysis và promotions
  - [ ] `/api/chat` - Chat interface với AI agents

### 2. **Core Workflows tích hợp**
- [ ] **Product Recommendation Flow tích hợp**:
  - [ ] User input parsing
  - [ ] Requirement extraction
  - [ ] Product search và filtering
  - [ ] Price analysis
  - [ ] Store location
  - [ ] Integrated response generation

- [ ] **Store Location Flow tích hợp**:
  - [ ] Location input processing
  - [ ] Product availability check
  - [ ] Store search và filtering
  - [ ] Distance calculation
  - [ ] Integrated store list generation

- [ ] **Price Analysis Flow tích hợp**:
  - [ ] Product identification
  - [ ] Price data retrieval
  - [ ] Promotion analysis
  - [ ] Store availability
  - [ ] Integrated recommendation generation

### 3. **Data Integration**
- [ ] Data loading từ 4 JSON files
- [ ] Agent communication và coordination
- [ ] Error handling và fallbacks
- [ ] Response formatting và output

---

## 🎯 **Phase 5 — Testing & Demo**

### 1. **Test Scenarios tích hợp**
- [ ] **"Tôi cần điện thoại chụp ảnh đẹp dưới 20 triệu, gần quận 1"**
  - [ ] Intent classification
  - [ ] Product search và filtering
  - [ ] Price analysis
  - [ ] Store location
  - [ ] Integrated response

- [ ] **"So sánh iPhone 16 Pro và Galaxy S25 Ultra về giá cả"**
  - [ ] Product identification
  - [ ] Feature comparison
  - [ ] Price analysis
  - [ ] Integrated comparison table

- [ ] **"Cửa hàng nào gần quận 1 có Galaxy S25 Ultra?"**
  - [ ] Location processing
  - [ ] Product availability check
  - [ ] Store search
  - [ ] Integrated store list

- [ ] **"Sản phẩm nào đang giảm giá nhiều nhất và có cửa hàng gần quận 3?"**
  - [ ] Price analysis
  - [ ] Discount calculation
  - [ ] Store location
  - [ ] Integrated top deals output

### 2. **Performance Testing**
- [ ] Response time measurement
- [ ] Accuracy validation
- [ ] Error rate monitoring
- [ ] User experience testing

---

## 📊 **Success Metrics & Validation**

### Technical Metrics
- [ ] Response time < 3 seconds
- [ ] Accuracy > 95% cho product recommendations
- [ ] Coverage 100% cho 24 sản phẩm hiện có
- [ ] Error rate < 5%

### User Experience Metrics
- [ ] User satisfaction > 4.5/5
- [ ] Successful product matches > 90%
- [ ] Store location accuracy > 95%
- [ ] Response relevance > 90%

### Business Metrics
- [ ] Product discovery rate > 80%
- [ ] Store visit conversion > 60%
- [ ] User engagement time > 5 minutes
- [ ] Recommendation acceptance > 70%

---

## 🔧 **Technical Requirements & Dependencies**

### Backend Dependencies (uv)
- [ ] Python 3.8+
- [ ] Google ADK cho agent framework (không cần FastAPI)
- [ ] Pydantic cho data validation
- [ ] ADK API server cho backend

### Frontend Dependencies
- [ ] React 19+
- [ ] TypeScript 5.7+
- [ ] Vite cho build tool
- [ ] Tailwind CSS cho styling
- [ ] Radix UI cho components

### Performance Requirements
- [ ] Handle 100+ concurrent users
- [ ] Cache frequently accessed data
- [ ] Optimize search algorithms
- [ ] Implement rate limiting

### Security Requirements
- [ ] Input validation và sanitization
- [ ] Rate limiting cho API calls
- [ ] Secure data handling
- [ ] Privacy compliance

---

## 📝 **Notes & Assumptions**

### Data Assumptions
- ✅ Tất cả dữ liệu trong 4 files JSON là chính xác và cập nhật
- ✅ Không cần crawl thêm data từ website
- ✅ Focus vào việc sử dụng data có sẵn một cách hiệu quả

### Technical Assumptions
- [ ] LLM có thể xử lý JSON data một cách hiệu quả
- [ ] Response time chấp nhận được với data cục bộ
- [ ] Không cần real-time data updates
- [ ] Google ADK framework hoạt động tốt với Gemini models
- [ ] ADK API server cung cấp đủ functionality không cần FastAPI

### User Assumptions
- [ ] Người dùng chủ yếu tìm kiếm sản phẩm theo budget và features
- [ ] Store location là feature quan trọng
- [ ] Price comparison và promotion analysis có giá trị cao
- [ ] Người dùng muốn thông tin tích hợp (sản phẩm + giá + cửa hàng)

---

## 🎯 **Next Steps & Priorities**

### **Week 1 (Priority 1)**
1. Setup project với uv và Makefile
2. Implement data models và schemas với Pydantic
3. Build main agent với ADK-style callback hooks
4. Basic ADK API server setup

### **Week 2 (Priority 2)**
1. Complete main agent với prompt templates
2. Implement product agent tích hợp (gộp 3 agents)
3. Add integrated tools (search, pricing, store)
4. Basic integration testing

### **Week 3 (Priority 3)**
1. Implement advanced features (comparison, analysis)
2. Frontend integration với React components
3. End-to-end testing với ADK backend

---

## 📚 **References & Resources**

### Data Sources
- **Products**: `profiles/products.json` (24 sản phẩm)
- **Offers**: `profiles/offers.json` (20 offers)
- **Reviews**: `profiles/reviews.json` (20 reviews)
- **Stores**: `profiles/stores.json` (48 cửa hàng)

### Technical References
- **Tree AI Agent**: Backend architecture patterns
- **MM Multi Agent V2**: Frontend component patterns
- **Google ADK**: Agent framework và callback patterns
- **ADK API Server**: Backend server functionality
- **uv**: Python package management

---

*Task log này phản ánh tình trạng hiện tại của dự án với data đã hoàn thành, architecture từ tree_ai_agent, frontend elements từ mm_multi_agent_v2, và focus vào implementation với ADK API server trực tiếp và 1 Product Agent tích hợp.*


