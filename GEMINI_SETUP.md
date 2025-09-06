# Gemini AI Setup Guide

## 🚀 Cách Bật Tính Năng AI-Powered

### 1. Lấy Gemini API Key

1. Truy cập [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Đăng nhập bằng Google account
3. Tạo API key mới
4. Copy API key

### 2. Cấu Hình Environment

#### Cách 1: Tạo file `.env`
```bash
# Copy file mẫu
cp env.example .env

# Chỉnh sửa file .env
nano .env
```

Thêm API key vào file `.env`:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

#### Cách 2: Set Environment Variable
```bash
# Linux/Mac
export GEMINI_API_KEY="your_actual_api_key_here"

# Windows
set GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Kiểm Tra Setup

```bash
python -c "
from app.tools.gemini_utils_tool import gemini_utils
print('Gemini available:', gemini_utils.is_available())
"
```

Nếu thấy `Gemini available: True` thì đã setup thành công!

## 🎯 Tính Năng AI-Powered

Khi có Gemini API key, hệ thống sẽ có:

### ✅ **Enhanced Search**
- Tự động tối ưu query từ người dùng
- Extract budget, brand, features từ natural language
- Phân tích search intent thông minh

### ✅ **Smart Recommendations**
- Tạo gợi ý sản phẩm thông minh
- Phân tích yêu cầu người dùng
- Đưa ra lời khuyên phù hợp

### ✅ **Product Analysis**
- Phân tích sản phẩm chi tiết với AI
- Đánh giá điểm mạnh/yếu
- So sánh với thị trường

## 🔧 Fallback Mode

Nếu không có Gemini API key, hệ thống vẫn hoạt động bình thường với:
- Traditional regex-based text processing
- Meilisearch full-text search
- Basic product recommendations

## 🐛 Troubleshooting

### Lỗi: "Gemini client not initialized"
- Kiểm tra `GEMINI_API_KEY` đã được set chưa
- Kiểm tra API key có hợp lệ không
- Xem logs để biết chi tiết lỗi

### Lỗi: "API quota exceeded"
- Kiểm tra quota trong Google AI Studio
- Có thể cần upgrade plan

### Lỗi: "Invalid API key"
- Tạo lại API key mới
- Đảm bảo copy đúng API key

## 📊 Monitoring

Xem logs để monitor:
```bash
# Xem logs real-time
tail -f logs/app.log

# Filter Gemini logs
grep "Gemini" logs/app.log
```

## 🔒 Security

- **KHÔNG** commit API key vào Git
- Sử dụng `.env` file và thêm vào `.gitignore`
- Rotate API key định kỳ
- Monitor usage trong Google AI Studio