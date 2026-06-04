from fastapi import APIRouter, HTTPException, Body
from app.models.schemas import ChatRequest
from app.services.chat_service import (
    check_emergency_rules,
    process_mock_ai,
    process_gemini_ai,
    process_openai_ai
)

router = APIRouter()

@router.post("")
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
        provider = request.provider
        
        if provider == "gemini":
            result = process_gemini_ai(user_msg, request.chat_history)
        elif provider == "openai":
            result = process_openai_ai(user_msg, request.chat_history)
        else:
            result = process_mock_ai(user_msg, request.chat_history)
            
    result["products"] = []
    result["symptoms"] = []
    result["categories"] = []
    return result
