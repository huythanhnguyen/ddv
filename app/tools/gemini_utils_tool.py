"""
Gemini-based Utility Tool for DDV Product Advisor
Uses Gemini AI to parse and extract information from natural language
"""

import os
import json
import logging
from typing import Optional, Tuple, List, Dict, Any
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiUtilsTool:
    """Utility tool using Gemini AI for flexible text processing"""
    
    def __init__(self):
        self.client = None
        self.model = "gemini-2.0-flash-lite"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Gemini client"""
        try:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logger.error("❌ GEMINI_API_KEY not found in environment variables")
                return
            
            self.client = genai.Client(api_key=api_key)
            logger.info("✅ Gemini Utils Tool initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini client: {e}")
    
    def _call_gemini(self, prompt: str, system_instruction: str) -> Optional[str]:
        """Call Gemini API with given prompt and system instruction"""
        if not self.client:
            logger.error("❌ Gemini client not initialized")
            return None
        
        try:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                ),
            ]
            
            generate_content_config = types.GenerateContentConfig(
                system_instruction=[types.Part.from_text(text=system_instruction)],
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=contents,
                config=generate_content_config,
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"❌ Gemini API call failed: {e}")
            return None
    
    def parse_price_from_text(self, text: str) -> Optional[int]:
        """Parse price from text using Gemini AI"""
        if not text:
            return None
        
        system_instruction = """
        Trích xuất giá từ đoạn văn bản sau và trả về dưới dạng một số nguyên.
        Loại bỏ tất cả các ký tự không phải là số và các dấu phân cách hàng nghìn.
        Nếu không tìm thấy giá trị số hợp lệ, hãy trả về null.
        Chỉ trả về số nguyên, không có text khác.
        """
        
        prompt = f"Trích xuất giá từ: '{text}'"
        result = self._call_gemini(prompt, system_instruction)
        
        if result and result.lower() != "null":
            try:
                return int(result)
            except ValueError:
                logger.warning(f"⚠️ Could not parse price result: {result}")
                return None
        
        return None
    
    def extract_budget_from_text(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract budget range from text using Gemini AI"""
        if not text:
            return None, None
        
        system_instruction = """
        Phân tích yêu cầu ngân sách từ đoạn văn bản và trả về khoảng giá trị.
        
        Quy tắc định nghĩa:
        - "giá rẻ" = dưới 5 triệu VND
        - "tầm trung" = 5-15 triệu VND  
        - "cao cấp" = trên 15 triệu VND
        - "dưới X triệu" = dưới X triệu VND
        - "từ X đến Y triệu" = X-Y triệu VND
        
        Trả về JSON format: {"min": số_nguyên_hoặc_null, "max": số_nguyên_hoặc_null}
        Ví dụ: {"min": null, "max": 5000000} cho "giá rẻ"
        """
        
        prompt = f"Phân tích ngân sách từ: '{text}'"
        result = self._call_gemini(prompt, system_instruction)
        
        if result:
            try:
                budget_data = json.loads(result)
                min_budget = budget_data.get("min")
                max_budget = budget_data.get("max")
                return min_budget, max_budget
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Could not parse budget result: {result}")
        
        return None, None
    
    def extract_brands_from_text(self, text: str) -> List[str]:
        """Extract brand preferences from text using Gemini AI"""
        if not text:
            return []
        
        system_instruction = """
        Trích xuất các thương hiệu điện thoại từ đoạn văn bản.
        
        Các thương hiệu phổ biến: Apple, Samsung, Xiaomi, Oppo, Vivo, Realme, OnePlus, Huawei, Nokia, Motorola
        
        Trả về JSON array: ["brand1", "brand2", ...]
        Nếu không tìm thấy thương hiệu nào, trả về []
        """
        
        prompt = f"Trích xuất thương hiệu từ: '{text}'"
        result = self._call_gemini(prompt, system_instruction)
        
        if result:
            try:
                brands = json.loads(result)
                if isinstance(brands, list):
                    return brands
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Could not parse brands result: {result}")
        
        return []
    
    def extract_features_from_text(self, text: str) -> List[str]:
        """Extract feature requirements from text using Gemini AI"""
        if not text:
            return []
        
        system_instruction = """
        Trích xuất các tính năng điện thoại từ đoạn văn bản.
        
        Các tính năng phổ biến: camera, pin, màn hình, chip, ram, bộ nhớ, hệ điều hành, wifi, bluetooth, gps
        
        Trả về JSON array: ["feature1", "feature2", ...]
        Nếu không tìm thấy tính năng nào, trả về []
        """
        
        prompt = f"Trích xuất tính năng từ: '{text}'"
        result = self._call_gemini(prompt, system_instruction)
        
        if result:
            try:
                features = json.loads(result)
                if isinstance(features, list):
                    return features
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Could not parse features result: {result}")
        
        return []
    
    def extract_location_from_text(self, text: str) -> Optional[str]:
        """Extract location information from text using Gemini AI"""
        if not text:
            return None
        
        system_instruction = """
        Trích xuất thông tin địa điểm từ đoạn văn bản.
        
        Tìm các địa điểm như: quận, huyện, thành phố, tỉnh
        Trả về địa điểm chính xác nhất tìm được.
        Nếu không tìm thấy địa điểm nào, trả về null.
        """
        
        prompt = f"Trích xuất địa điểm từ: '{text}'"
        result = self._call_gemini(prompt, system_instruction)
        
        if result and result.lower() != "null":
            return result.strip()
        
        return None
    
    def analyze_search_intent(self, text: str) -> Dict[str, Any]:
        """Analyze search intent from user input using Gemini AI"""
        if not text:
            return {}
        
        system_instruction = """
        Phân tích ý định tìm kiếm từ yêu cầu của người dùng và trả về thông tin chi tiết.
        
        Trả về JSON với các trường:
        {
            "intent": "product_search|price_check|comparison|general_info",
            "product_type": "phone|accessory|service",
            "budget_range": {"min": số_nguyên_hoặc_null, "max": số_nguyên_hoặc_null},
            "brands": ["brand1", "brand2"],
            "features": ["feature1", "feature2"],
            "location": "địa_điểm_hoặc_null",
            "urgency": "high|medium|low",
            "search_query": "từ_khóa_tìm_kiếm_tối_ưu"
        }
        """
        
        prompt = f"Phân tích ý định tìm kiếm từ: '{text}'"
        result = self._call_gemini(prompt, system_instruction)
        
        if result:
            try:
                intent_data = json.loads(result)
                return intent_data
            except json.JSONDecodeError:
                logger.warning(f"⚠️ Could not parse intent result: {result}")
        
        return {}
    
    def generate_product_recommendation(self, user_requirements: Dict[str, Any], available_products: List[Dict[str, Any]]) -> str:
        """Generate product recommendation using Gemini AI"""
        if not user_requirements or not available_products:
            return "Không có thông tin đủ để đưa ra gợi ý."
        
        system_instruction = """
        Dựa trên yêu cầu của người dùng và danh sách sản phẩm có sẵn, đưa ra gợi ý sản phẩm phù hợp nhất.
        
        Phân tích:
        1. So sánh yêu cầu với đặc điểm sản phẩm
        2. Đánh giá mức độ phù hợp
        3. Đưa ra lý do cụ thể
        4. Gợi ý sản phẩm tốt nhất
        
        Trả về văn bản tư vấn ngắn gọn, dễ hiểu.
        """
        
        prompt = f"""
        Yêu cầu người dùng: {json.dumps(user_requirements, ensure_ascii=False)}
        
        Sản phẩm có sẵn: {json.dumps(available_products[:5], ensure_ascii=False)}
        
        Đưa ra gợi ý sản phẩm phù hợp nhất.
        """
        
        result = self._call_gemini(prompt, system_instruction)
        return result or "Không thể đưa ra gợi ý tại thời điểm này."

# Global instance
gemini_utils = GeminiUtilsTool()
