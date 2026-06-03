import json
import re
from typing import List, Optional
from app.data.products_db import get_products_by_category
from app.core.config import MODEL_TEMPERATURE, ALLOW_OUT_OF_SCOPE, MAX_TOKENS, OPENAI_API_KEY, GEMINI_API_KEY
from app.core.logger import system_logger

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
                "ĐÂY LÀ TÌNH TRẠNG KHẨN CẤP. VUI LÒNG GỌI CẤP CỨU 115 HOẶC ĐẾN TRẠM Y TẾ NGAY LẬP TỨC."
            ],
            "is_emergency": True,
            "clarifying_questions": [],
            "references": []
        }
    
    # 2. Low Confidence / General Symptoms
    low_confidence_triggers = [
        "mệt", "người mệt", "không ổn", "không khỏe", "thấy mỏi", "khó chịu", "ốm", "bị ốm"
    ]
    is_low_conf = any(trigger in message_lower for trigger in low_confidence_triggers) and len(message_lower.split()) < 6
    
    if is_low_conf:
        return {
            "symptoms": [],
            "confidence": "low",
            "message": "Dạ, tôi chưa nghe rõ các triệu chứng của bạn. Bạn có thể chia sẻ cụ thể hơn cảm giác khó chịu ở đâu để tôi tư vấn chính xác nhé!",
            "categories": [],
            "recommendations": [],
            "warnings": ["Theo dõi thân nhiệt thường xuyên"],
            "is_emergency": False,
            "clarifying_questions": [
                "Bạn có bị sốt hoặc đau nhức mình mẩy không?",
                "Bạn có ho, sổ mũi hay nghẹt mũi không?",
                "Bạn có đau mỏi ở vị trí nào cụ thể không?",
                "Triệu chứng này đã kéo dài bao nhiêu lâu rồi?"
            ],
            "references": []
        }
    
    # 3. Happy Path
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
        if ALLOW_OUT_OF_SCOPE:
            return {
                "symptoms": [],
                "confidence": "high",
                "message": "Xin chào! Tôi là Trợ lý Dược sĩ AI của Long Châu. Tôi có thể giúp gì cho bạn hôm nay?",
                "categories": [],
                "recommendations": [],
                "warnings": [],
                "is_emergency": False,
                "clarifying_questions": [],
                "references": []
            }
            
        return {
            "symptoms": [],
            "confidence": "low",
            "message": "Dạ, tôi chưa nhận diện được triệu chứng cụ thể nào từ mô tả của bạn. Bạn có thể chia sẻ rõ hơn để tôi tư vấn không ạ?",
            "categories": [],
            "recommendations": [],
            "warnings": [],
            "is_emergency": False,
            "clarifying_questions": [
                "Bạn có bị đau, sốt hay ho không?",
                "Bạn có thể mô tả chi tiết hơn cảm giác khó chịu của bạn không?"
            ],
            "references": []
        }
        
    return {
        "symptoms": symptoms,
        "confidence": "high",
        "message": f"Dựa trên các triệu chứng bạn mô tả ({', '.join(symptoms).lower()}), chúng tôi gợi ý các nhóm sản phẩm hỗ trợ sau:",
        "categories": categories,
        "recommendations": recommendations,
        "warnings": warnings,
        "is_emergency": False,
        "clarifying_questions": [],
        "references": []
    }

def process_gemini_ai(message: str) -> dict:
    try:
        from google import genai
        from google.genai import types
        
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured in .env")
        
        # 1. RAG Retrieval
        context_str = ""
        rag_results = []
        try:
            from vector_db.retriever import search_drugs
            # Lấy 3 tài liệu liên quan nhất
            rag_results = search_drugs(message, top_k=3)
            if rag_results:
                context_str = "\n--- KIẾN THỨC Y KHOA TỪ CƠ SỞ DỮ LIỆU LONG CHÂU ---\n"
                for r in rag_results:
                    context_str += f"- Thuốc {r['drug_name']} (Phần: {r['section']}): {r['content']}\n"
                context_str += "--------------------------------------------------\n"
        except Exception as e:
            print(f"RAG Retrieval Error: {e}")
            
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        system_instruction = f"""
        Bạn là Trợ lý AI Đọc Hiểu Đơn Thuốc & Dược Sĩ của FPT Long Châu. Nhiệm vụ của bạn là:
        1. Phân tích triệu chứng và đề xuất nhóm sản phẩm OTC (nếu người dùng hỏi về bệnh/triệu chứng).
        2. Tương tác Thuốc-Thức ăn (Happy Path): Nếu người dùng hỏi thuốc này có kỵ đồ ăn thức uống nào không, hãy đối chiếu KIẾN THỨC Y KHOA. Đưa ra câu trả lời "Nên / Không nên dùng cùng" trong 'message', và BẮT BUỘC thêm vào 'warnings': "Vui lòng tham khảo ý kiến bác sĩ/dược sĩ."
        3. Hỏi liều lượng (Failure Mode Nguy Hiểm): Nếu người dùng hỏi về liều lượng (vd: uống mấy viên, ngày mấy lần), TUYỆT ĐỐI TỪ CHỐI cung cấp con số. Bạn phải đặt 'is_emergency' = true, và điền vào 'warnings': "Tôi là AI, không được phép kê đơn hay chỉ định liều lượng. Vui lòng xem trên đơn thuốc gốc hoặc hỏi trực tiếp bác sĩ."
        4. Thuốc lạ / Mơ hồ (Low Confidence): Nếu thông tin không có trong CSDL, hãy nói rõ trong 'message': "Đây chỉ là phỏng đoán, chưa chắc chắn. Đề nghị xác nhận với dược sĩ." và đặt 'confidence' = 'low'.
        {context_str}
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
        -> Đặt 'confidence' thành 'low', 'categories' thành [], 'symptoms' thành [], 'recommendations' thành [], 'warnings' thành [] (TUYỆT ĐỐI SỬ DỤNG MẢNG RỖNG [], KHÔNG ĐIỀN CHỮ "Không có" HAY "None") và trả lời một cách thật thân thiện, lịch sự, quan tâm trong 'message' (ví dụ: "Dạ, bạn có thể chia sẻ rõ hơn để tôi tư vấn nhé"). Đặt các câu hỏi làm rõ trong 'clarifying_questions'.
        
        """
        if ALLOW_OUT_OF_SCOPE:
            system_instruction += "\nCấu hình ALLOW_OUT_OF_SCOPE đang BẬT: Bạn được quyền trả lời các câu hỏi ngoài y tế bằng kiến thức chung một cách tự nhiên, vui vẻ. Đặt 'confidence' thành 'high', 'categories' thành [], 'symptoms' thành [], 'recommendations' thành [], 'warnings' thành [] (TUYỆT ĐỐI SỬ DỤNG MẢNG RỖNG []) và ghi câu trả lời của bạn vào 'message'."
        else:
            system_instruction += "\nCấu hình ALLOW_OUT_OF_SCOPE đang TẮT: Nếu người dùng hỏi câu hỏi ngoài y tế, bạn BẮT BUỘC TỪ CHỐI thật lịch sự và khéo léo (ví dụ: 'Dạ tôi là Dược sĩ AI nên chỉ hỗ trợ tư vấn sức khỏe thôi ạ...'). Đặt 'confidence' thành 'low', 'categories' thành [], 'symptoms' thành [], 'recommendations' thành [], 'warnings' thành [] (TUYỆT ĐỐI SỬ DỤNG MẢNG RỖNG []) và ghi lời từ chối vào 'message'."
            
        system_instruction += """
        Định dạng đầu ra PHẢI LÀ JSON duy nhất, không có markdown trích dẫn (không có ```json ... ```), khớp chính xác với cấu trúc sau:
        {{
            "symptoms": ["mảng các triệu chứng đã trích xuất, ví dụ: Ho khan, Đau họng"],
            "confidence": "high" | "low" | "emergency",
            "message": "Lời giải thích ngắn gọn, tự nhiên cho người bệnh",
            "categories": ["tên nhóm sản phẩm khớp chính xác với danh sách có sẵn ở trên, ví dụ: 'siro ho', 'viên ngậm giảm đau họng'"],
            "recommendations": ["Lời khuyên chăm sóc sức khỏe 1", "Lời khuyên 2"],
            "warnings": ["Cảnh báo cần đi khám y tế nếu có dấu hiệu..."],
            "is_emergency": true | false,
            "clarifying_questions": ["câu hỏi 1", "câu hỏi 2"],
            "references": ["Tên các loại thuốc từ KIẾN THỨC Y KHOA mà bạn thực sự đã dùng để tư vấn. Để rỗng [] nếu không dùng."]
        }}
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_instruction,
                temperature=MODEL_TEMPERATURE,
                max_output_tokens=MAX_TOKENS
            )
        )
        data = json.loads(response.text.strip())
        
        # Lọc references: Chỉ lấy source_url của các thuốc mà LLM báo là đã dùng
        final_refs = []
        llm_refs = data.get("references", [])
        if isinstance(llm_refs, list):
            for r in rag_results:
                if any(r['drug_name'].lower() in str(ref).lower() for ref in llm_refs):
                    if r.get('source_url') and not any(ref['url'] == r['source_url'] for ref in final_refs):
                        final_refs.append({"name": r['drug_name'], "url": r['source_url']})
        
        data["references"] = final_refs
        system_logger.info(f"Gemini API Response Data: {data}")
        return data
        
    except Exception as e:
        system_logger.error(f"Gemini API Error: {e}", exc_info=True)
        fallback = process_mock_ai(message)
        return fallback

def process_openai_ai(message: str) -> dict:
    try:
        from openai import OpenAI
        
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured in .env")
            
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # 1. RAG Retrieval
        context_str = ""
        rag_results = []
        try:
            from vector_db.retriever import search_drugs
            rag_results = search_drugs(message, top_k=3)
            if rag_results:
                context_str = "\n--- KIẾN THỨC Y KHOA TỪ CƠ SỞ DỮ LIỆU LONG CHÂU ---\n"
                for r in rag_results:
                    context_str += f"- Thuốc {r['drug_name']} (Phần: {r['section']}): {r['content']}\n"
                context_str += "--------------------------------------------------\n"
        except Exception as e:
            print(f"RAG Retrieval Error: {e}")
        
        prompt = f"""
        Bạn là Trợ lý AI Đọc Hiểu Đơn Thuốc & Dược Sĩ của FPT Long Châu.
        Hãy phân tích triệu chứng hoặc câu hỏi sau: "{message}"
        
        Quy tắc xử lý (Thin Spec):
        1. Phân tích triệu chứng và đề xuất nhóm sản phẩm OTC (nếu hỏi về bệnh/triệu chứng).
        2. Tương tác Thuốc-Thức ăn (Happy Path): Nếu hỏi thuốc này có kỵ đồ ăn thức uống nào không, hãy đối chiếu KIẾN THỨC Y KHOA. Đưa ra câu trả lời "Nên / Không nên dùng cùng" trong 'message', và BẮT BUỘC thêm vào 'warnings': "Vui lòng tham khảo ý kiến bác sĩ/dược sĩ."
        3. Hỏi liều lượng (Failure Mode Nguy Hiểm): Nếu người dùng hỏi về liều lượng (vd: uống mấy viên, ngày mấy lần), TUYỆT ĐỐI TỪ CHỐI cung cấp con số. Đặt 'is_emergency' = true, và điền vào 'warnings': "Tôi là AI, không được phép kê đơn hay chỉ định liều lượng. Vui lòng xem trên đơn thuốc gốc hoặc hỏi trực tiếp bác sĩ."
        4. Thuốc lạ / Mơ hồ (Low Confidence): Nếu thông tin không có trong CSDL, nói rõ trong 'message': "Đây chỉ là phỏng đoán, chưa chắc chắn. Đề nghị xác nhận với dược sĩ." và đặt 'confidence' = 'low'.
        
        {context_str}
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
            "clarifying_questions": ["câu hỏi nếu confidence là low"],
            "references": ["Tên các loại thuốc từ KIẾN THỨC Y KHOA mà bạn thực sự đã dùng để tư vấn. Để rỗng [] nếu không dùng."]
        }}
        
        Nếu mô tả của người dùng mơ hồ, không có triệu chứng cụ thể -> Đặt 'confidence' thành 'low', 'categories' thành [], 'symptoms' thành [], 'recommendations' thành [], 'warnings' thành [], 'references' thành [] (TUYỆT ĐỐI SỬ DỤNG MẢNG RỖNG [], KHÔNG ĐIỀN CHỮ "Không có" HAY "None") và trả lời thật thân thiện, lịch sự trong 'message' (VD: Dạ, bạn có thể chia sẻ rõ hơn...).
        """
        
        if ALLOW_OUT_OF_SCOPE:
            prompt += "\nCấu hình ALLOW_OUT_OF_SCOPE đang BẬT: Bạn được quyền trả lời các câu hỏi ngoài y tế bằng kiến thức chung một cách tự nhiên, vui vẻ. Đặt 'confidence' thành 'high', 'categories' thành [], 'symptoms' thành [], 'recommendations' thành [], 'warnings' thành [] (TUYỆT ĐỐI SỬ DỤNG MẢNG RỖNG []) và ghi câu trả lời của bạn vào 'message'."
        else:
            prompt += "\nCấu hình ALLOW_OUT_OF_SCOPE đang TẮT: Nếu người dùng hỏi câu hỏi ngoài y tế, bạn BẮT BUỘC TỪ CHỐI thật lịch sự và khéo léo (ví dụ: 'Dạ tôi là Dược sĩ AI nên chỉ hỗ trợ tư vấn sức khỏe thôi ạ...'). Đặt 'confidence' thành 'low', 'categories' thành [], 'symptoms' thành [], 'recommendations' thành [], 'warnings' thành [] (TUYỆT ĐỐI SỬ DỤNG MẢNG RỖNG []) và ghi lời từ chối vào 'message'."
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=MODEL_TEMPERATURE,
            max_tokens=MAX_TOKENS
        )
        
        data = json.loads(response.choices[0].message.content.strip())
        
        # Lọc references
        final_refs = []
        llm_refs = data.get("references", [])
        if isinstance(llm_refs, list):
            for r in rag_results:
                if any(r['drug_name'].lower() in str(ref).lower() for ref in llm_refs):
                    if r.get('source_url') and not any(ref['url'] == r['source_url'] for ref in final_refs):
                        final_refs.append({"name": r['drug_name'], "url": r['source_url']})
        
        data["references"] = final_refs
        system_logger.info(f"OpenAI API Response Data: {data}")
        return data
    except Exception as e:
        system_logger.error(f"OpenAI API Error: {e}", exc_info=True)
        fallback = process_mock_ai(message)
        return fallback
