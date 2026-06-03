import re
import json
import os
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional

# Import mock catalog
from products_db import PRODUCT_CATALOG, get_products_by_category

app = FastAPI(title="Long Chau OTC Finder API")

# Setup static directory
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# Define request schemas
class ChatRequest(BaseModel):
    message: str
    api_key: Optional[str] = None
    provider: Optional[str] = "mock"  # "mock", "gemini", "openai"
    chat_history: Optional[List[dict]] = None

# Hard-coded safety triggers (Red Flags)
EMERGENCY_KEYWORDS = [
    r"khó thở", r"nghẹt thở", r"không thở được", r"thở dốc",
    r"đau ngực", r"tức ngực", r"nhói ngực", r"đau tim",
    r"co giật", r"động kinh", r"sùi bọt mép",
    r"ngất", r"hôn mê", r"mất ý thức", r"xỉu", r"bất tỉnh",
    r"liệt", r"yếu nửa người", r"không cử động được nửa người",
    r"chảy máu không cầm", r"mất máu nhiều", r"băng huyết",
    r"sốt rất cao ở trẻ", r"trẻ sốt cao co giật", r"em bé sốt cao",
    r"vã mồ hôi", r"vã mồ hôi lạnh", r"vã mồ hôi hột"
]

def check_emergency_rules(text: str) -> bool:
    text_lower = text.lower()
    for pattern in EMERGENCY_KEYWORDS:
        if re.search(pattern, text_lower):
            return True
    return False

# Rule-based fallback/mock processor
def process_mock_ai(message: str) -> dict:
    message_lower = message.lower()
    
    # 1. Emergency Case
    if check_emergency_rules(message_lower):
        return {
            "symptoms": ["Khó thở", "Đau ngực", "Dấu hiệu nguy kịch"],
            "confidence": "emergency",
            "message": "Chú ý! Triệu chứng bạn mô tả có thể là dấu hiệu khẩn cấp nguy hiểm đến tính mạng. Chúng tôi KHÔNG THỂ đề xuất các sản phẩm tự điều trị (OTC) lúc này.",
            "categories": [],
            "recommendations": [
                "Ngừng hoạt động thể lực ngay lập tức, ngồi hoặc nằm ở tư thế dễ thở.",
                "Mở thông thoáng cửa sổ, nới lỏng quần áo.",
                "Vui lòng di chuyển đến bệnh viện/phòng khám gần nhất ngay lập tức."
            ],
            "warnings": [
                "GỌI CẤP CỨU 115 HOẶC LIÊN HỆ NGƯỜI THÂN NGAY LẬP TỨC."
            ],
            "is_emergency": True,
            "clarifying_questions": []
        }
    
    # 2. Low Confidence / General Symptoms
    low_confidence_triggers = [
        "mệt", "người mệt", "không ổn", "không khỏe", "thấy mỏi", "khó chịu", "ốm", "bị ốm"
    ]
    is_low_conf = any(trigger in message_lower for trigger in low_confidence_triggers) and len(message_lower.split()) < 6
    
    if is_low_conf:
        return {
            "symptoms": ["Mệt mỏi chưa rõ nguyên nhân"],
            "confidence": "low",
            "message": "Triệu chứng bạn nhập còn khá chung chung, chưa đủ thông tin để định hướng nhóm sản phẩm OTC.",
            "categories": [],
            "recommendations": ["Nghỉ ngơi tại chỗ", "Uống nước ấm"],
            "warnings": ["Theo dõi thân nhiệt thường xuyên"],
            "is_emergency": False,
            "clarifying_questions": [
                "Bạn có bị sốt hoặc đau nhức mình mẩy không?",
                "Bạn có ho, sổ mũi hay nghẹt mũi không?",
                "Bạn có đau mỏi ở vị trí nào cụ thể không?",
                "Triệu chứng này đã kéo dài bao nhiêu lâu rồi?"
            ]
        }
    
    # 3. Happy Path (Cough + Sore throat)
    is_cough = "ho" in message_lower or "siro" in message_lower or "khan" in message_lower
    is_sore_throat = "đau họng" in message_lower or "rát họng" in message_lower or "ngậm" in message_lower
    is_flu = "cảm" in message_lower or "sổ mũi" in message_lower or "nghẹt mũi" in message_lower or "xịt mũi" in message_lower or "ngạt" in message_lower
    is_fever = "sốt" in message_lower or "nóng" in message_lower or "đau đầu" in message_lower or "nhức đầu" in message_lower
    is_allergy = "nổi mẩn" in message_lower or "dị ứng" in message_lower or "ngứa" in message_lower or "nổi đỏ" in message_lower or "nổi mụn" in message_lower
    
    symptoms = []
    categories = []
    recommendations = ["Uống nhiều nước ấm", "Súc họng nước muối ấm", "Tránh thức ăn cay nóng hoặc quá lạnh"]
    warnings = ["Cần đi khám nếu sốt cao trên 38.5 độ, ho kéo dài hơn 7 ngày, hoặc triệu chứng nặng lên."]
    
    if is_cough:
        symptoms.append("Ho khan / Ho có đờm")
        categories.append("siro ho")
    if is_sore_throat:
        symptoms.append("Đau họng / Rát họng")
        categories.append("viên ngậm giảm đau họng")
    if is_flu:
        symptoms.append("Sổ mũi / Nghẹt mũi / Cảm cúm")
        categories.append("thuốc cảm cúm & sổ mũi")
        categories.append("thuốc xịt mũi")
    if is_fever:
        symptoms.append("Sốt nhẹ / Đau nhức đầu")
        categories.append("thuốc giảm đau & hạ sốt")
    if is_allergy:
        symptoms.append("Nổi mẩn đỏ / Dị ứng da")
        categories.append("thuốc dị ứng & nổi mẩn")
        recommendations.append("Hạn chế tiếp xúc với tác nhân nghi gây dị ứng (bụi, lông thú, thực phẩm lạ)")
        warnings.append("Cần đi cấp cứu ngay nếu phát ban kèm theo khó thở hoặc sưng phù mặt/môi.")
        
    if not symptoms:
        symptoms = ["Triệu chứng chung"]
        categories = ["thuốc cảm cúm & sổ mũi", "thuốc giảm đau & hạ sốt"]
        
    return {
        "symptoms": symptoms,
        "confidence": "high",
        "message": f"Dựa trên các triệu chứng bạn mô tả ({', '.join(symptoms).lower()}), chúng tôi gợi ý các nhóm sản phẩm hỗ trợ sau:",
        "categories": categories,
        "recommendations": recommendations,
        "warnings": warnings,
        "is_emergency": False,
        "clarifying_questions": []
    }

# Gemini API Caller
def process_gemini_ai(message: str, api_key: str) -> dict:
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        system_instruction = f"""
        Bạn là Trợ lý Dược sĩ AI của FPT Long Châu. Nhiệm vụ của bạn là nhận triệu chứng của người dùng bằng ngôn ngữ tự nhiên, trích xuất triệu chứng, và đề xuất nhóm sản phẩm OTC (Không kê đơn) phù hợp.
        
        Các nhóm sản phẩm OTC có sẵn trong hệ thống:
        - "viên ngậm giảm đau họng" (dành cho đau rát họng, ho nhẹ)
        - "siro ho" (dành cho ho khan, ho có đờm)
        - "thuốc cảm cúm & sổ mũi" (dành cho nghẹt mũi, sổ mũi, nhức đầu)
        - "thuốc xịt mũi" (dành cho thông mũi, viêm mũi dị ứng)
        - "thuốc giảm đau & hạ sốt" (dành cho sốt, đau đầu, đau mình mẩy)
        - "thuốc dị ứng & nổi mẩn" (dành cho nổi mề đay, mẩn đỏ, dị ứng da)
        
        Quy tắc an toàn (MANDATORY):
        Nếu người dùng có triệu chứng nguy hiểm: đau ngực, khó thở, co giật, mất ý thức, yếu/liệt nửa người, chảy máu không cầm, sốt rất cao ở trẻ nhỏ, vã mồ hôi.
        -> Đặt 'is_emergency' thành true, 'confidence' thành 'emergency', và 'categories' thành mảng rỗng []. Đề xuất họ đi cấp cứu 115 ngay lập tức.
        
        Quy tắc độ tin cậy thấp (Low Confidence):
        Nếu mô tả của người dùng quá ngắn, mơ hồ (ví dụ: "tôi thấy mệt", "người không ổn") mà không có triệu chứng cụ thể nào.
        -> Đặt 'confidence' thành 'low', 'categories' thành [], và đặt các câu hỏi làm rõ trong 'clarifying_questions' (như: Có sốt không? Ho không? Đau ở đâu?).
        
        Định dạng đầu ra PHẢI LÀ JSON duy nhất, không có markdown trích dẫn (không có ```json ... ```), khớp chính xác với cấu trúc sau:
        {{
            "symptoms": ["mảng các triệu chứng đã trích xuất, ví dụ: Ho khan, Đau họng"],
            "confidence": "high" | "low" | "emergency",
            "message": "Lời giải thích ngắn gọn, tự nhiên cho người bệnh",
            "categories": ["tên nhóm sản phẩm khớp chính xác với danh sách có sẵn ở trên, ví dụ: 'siro ho', 'viên ngậm giảm đau họng'"],
            "recommendations": ["Lời khuyên chăm sóc sức khỏe 1", "Lời khuyên 2"],
            "warnings": ["Cảnh báo cần đi khám y tế nếu có dấu hiệu..."],
            "is_emergency": true | false,
            "clarifying_questions": ["câu hỏi 1", "câu hỏi 2"]
        }}
        """
        
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"response_mime_type": "application/json"},
            system_instruction=system_instruction
        )
        
        response = model.generate_content(message)
        data = json.loads(response.text.strip())
        return data
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        fallback = process_mock_ai(message)
        fallback["message"] = f"(Lỗi Gemini API, chuyển sang Mock Engine) " + fallback["message"]
        return fallback

# OpenAI API Caller
def process_openai_ai(message: str, api_key: str) -> dict:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        prompt = f"""
        Bạn là Trợ lý Dược sĩ AI của FPT Long Châu.
        Hãy phân tích triệu chứng sau: "{message}"
        
        Các nhóm sản phẩm OTC có sẵn:
        - viên ngậm giảm đau họng
        - siro ho
        - thuốc cảm cúm & sổ mũi
        - thuốc xịt mũi
        - thuốc giảm đau & hạ sốt
        - thuốc dị ứng & nổi mẩn
        
        Trả về kết quả ở dạng JSON chứa cấu trúc:
        {{
            "symptoms": ["danh sách triệu chứng"],
            "confidence": "high" | "low" | "emergency",
            "message": "Lời nhắn giải thích",
            "categories": ["tên nhóm sản phẩm trùng khớp với danh sách ở trên"],
            "recommendations": ["lời khuyên"],
            "warnings": ["cảnh báo"],
            "is_emergency": true | false,
            "clarifying_questions": ["câu hỏi nếu confidence là low"]
        }}
        
        Nhớ tuân thủ các quy tắc an toàn cấp cứu (đau ngực, khó thở, co giật -> emergency) và thông tin mơ hồ -> low confidence.
        """
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content.strip())
        return data
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        fallback = process_mock_ai(message)
        fallback["message"] = f"(Lỗi OpenAI API, chuyển sang Mock Engine) " + fallback["message"]
        return fallback

# API endpoint
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest = Body(...)):
    user_msg = request.message.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Tin nhắn không được để trống")
    
    # 1. Hard-coded Safety Guardrail Interceptor (MANDATORY)
    if check_emergency_rules(user_msg):
        result = {
            "symptoms": ["Khó thở / Đau ngực / Dấu hiệu nguy cấp"],
            "confidence": "emergency",
            "message": "CẢNH BÁO NGUY HIỂM: Phát hiện dấu hiệu cấp cứu khẩn cấp từ tin nhắn của bạn. Vui lòng KHÔNG tự mua thuốc điều trị.",
            "categories": [],
            "recommendations": [
                "Ngồi thẳng lưng, cố gắng duy trì nhịp thở ổn định.",
                "Gần bệnh viện hoặc cơ sở y tế gần nhất là ưu tiên số một."
            ],
            "warnings": [
                "ĐÂY LÀ TÌNH TRẠNG KHẨN CẤP. VUI LÒNG GỌI CẤP CỨU 115 HOẶC ĐẾN TRẠM Y TẾ NGAY LẬP TỨC."
            ],
            "is_emergency": True,
            "clarifying_questions": []
        }
    else:
        # 2. Call AI engines
        if request.provider == "gemini" and request.api_key:
            result = process_gemini_ai(user_msg, request.api_key)
        elif request.provider == "openai" and request.api_key:
            result = process_openai_ai(user_msg, request.api_key)
        else:
            result = process_mock_ai(user_msg)
            
    # 3. Retrieve mock products
    products = []
    if not result.get("is_emergency") and result.get("confidence") == "high":
        for cat in result.get("categories", []):
            products.extend(get_products_by_category(cat))
            
    result["products"] = products
    return result

# Serve static files
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
