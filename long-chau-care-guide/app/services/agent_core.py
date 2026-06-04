import json
import logging
from google import genai
from openai import OpenAI
from app.core.config import OPENAI_API_KEY, GEMINI_API_KEY, MODEL_TEMPERATURE, ALLOW_OUT_OF_SCOPE, MAX_TOKENS
from app.core.model_settings import model_settings
from app.services.agent_tools import SearchHealthcareProductTool, AnalyzeIngredientsTool, AnalyzeDrugFoodInteractionTool

logger = logging.getLogger("HealthcareAgent.Agent")

SYSTEM_PROMPT = """
Bạn là Trợ lý Dược sĩ AI của Long Châu. 

NHIỆM VỤ CỦA BẠN:
1. Giải thích đơn thuốc dựa trên dữ liệu từ Long Châu Database.
2. Kiểm tra tương tác giữa Thuốc và Thực phẩm/Đồ uống khi người dùng yêu cầu.

NGUYÊN TẮC AN TOÀN (GARDRAILS):
- Tuyệt đối KHÔNG kê đơn mới hoặc chẩn đoán bệnh. 
- KHÔNG bao giờ đưa ra con số liều lượng cụ thể (VD: "uống 2 viên"). Hãy nhắc user: "Vui lòng xem trên đơn thuốc gốc hoặc hỏi trực tiếp bác sĩ."
- Luôn kết thúc câu trả lời bằng lời khuyên: "Thông tin chỉ mang tính chất tham khảo và không thay thế cho tư vấn từ bác sĩ hoặc dược sĩ chuyên môn."

CÁC CÔNG CỤ CỦA BẠN:
1. SearchHealthcareProductTool: Dùng đầu tiên để xác định đúng thuốc và thông tin cơ bản.
2. AnalyzeIngredientsTool: Tra cứu sâu về tác dụng phụ và cảnh báo an toàn.
3. AnalyzeDrugFoodInteractionTool: Kiểm tra tương tác giữa thuốc và đồ ăn/thức uống/rượu.

QUY TRÌNH SUY LUẬN (ReAct):
Tại mỗi bước lập luận, bạn BẮT BUỘC phải trả về một JSON object duy nhất (không bọc trong tag markdown):
{
    "thought": "Suy nghĩ của bạn (Ví dụ: User hỏi về thuốc và cà phê, tôi cần dùng AnalyzeDrugFoodInteractionTool để check...)",
    "action": "Tên công cụ ('SearchHealthcareProductTool', 'AnalyzeIngredientsTool', 'AnalyzeDrugFoodInteractionTool', 'Finish')",
    "action_input": "Tham số cho công cụ (Nếu AnalyzeDrugFoodInteractionTool thì input nên là tên thuốc)",
    "final_answer": "Câu trả lời tổng hợp chi tiết bằng tiếng Việt định dạng Markdown (để trống nếu chưa 'Finish')"
}
"""

class HealthcareAgent:
    def __init__(self, provider: str = "mock", max_iterations: int = 5):
        self.provider = provider
        self.max_iterations = max_iterations
        self.history = []
        logger.info(f"HealthcareAgent initialized with provider: {provider}")

    def _execute_tool(self, action: str, action_input: str) -> str:
        """Executes the corresponding tool and returns the observation as string."""
        logger.info(f"Agent Action: Call {action} with input '{action_input}'")
        try:
            if action == "SearchHealthcareProductTool":
                result = SearchHealthcareProductTool(action_input)
            elif action == "AnalyzeIngredientsTool":
                result = AnalyzeIngredientsTool(action_input)
            elif action == "AnalyzeDrugFoodInteractionTool":
                # Logic to handle potential multiple inputs if needed, 
                # but standard ReAct often passes single string
                result = AnalyzeDrugFoodInteractionTool(action_input)
            else:
                result = {"error": f"Công cụ '{action}' không tồn tại."}
            
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    def _call_llm(self, prompt: str) -> str:
        """Calls the configured LLM API (Gemini, OpenAI, or Mock)."""
        logger.info(f"Calling LLM ({self.provider})...")
        
        if self.provider == "gemini":
            if not GEMINI_API_KEY:
                logger.warning("Gemini API Key is missing. Falling back to Mock LLM.")
                return self._mock_llm_response(prompt)
            try:
                client = genai.Client(api_key=GEMINI_API_KEY)
                response = client.models.generate_content(
                    model=model_settings.GEMINI_MODEL_NAME,
                    contents=prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=MODEL_TEMPERATURE,
                        max_output_tokens=MAX_TOKENS
                    )
                )
                raw_text = response.text.strip()
                logger.info(f"Gemini LLM Raw Output: {raw_text}")
                return raw_text
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Falling back to Mock LLM.")
                return self._mock_llm_response(prompt)
                
        elif self.provider == "openai":
            if not OPENAI_API_KEY:
                logger.warning("OpenAI API Key is missing. Falling back to Mock LLM.")
                return self._mock_llm_response(prompt)
            try:
                client = OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=model_settings.OPENAI_MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=MODEL_TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )
                raw_text = response.choices[0].message.content.strip()
                logger.info(f"OpenAI LLM Raw Output: {raw_text}")
                return raw_text
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}. Falling back to Mock LLM.")
                return self._mock_llm_response(prompt)
                
        else:
            return self._mock_llm_response(prompt)

    def _mock_llm_response(self, prompt: str) -> str:
        """Simulates ReAct steps for local testing and offline execution."""
        history_str = "\n".join(self.history)
        
        if "SearchHealthcareProductTool" not in history_str:
            return json.dumps({
                "thought": "Người dùng cần tìm sản phẩm ho và rát họng. Tôi sẽ dùng SearchHealthcareProductTool để tìm kiếm sản phẩm phù hợp.",
                "action": "SearchHealthcareProductTool",
                "action_input": "ho rát họng",
                "final_answer": ""
            }, ensure_ascii=False)
            
        elif "AnalyzeIngredientsTool" not in history_str:
            return json.dumps({
                "thought": "Tôi cần phân tích tác dụng phụ và dị ứng của thành phần này bằng AnalyzeIngredientsTool.",
                "action": "AnalyzeIngredientsTool",
                "action_input": "ibuprofen",
                "final_answer": ""
            }, ensure_ascii=False)
            
        else:
            final_markdown = (
                "### Kết quả tư vấn sản phẩm:\n\n"
                "**1. Sản phẩm gợi ý:** Đã lấy thông tin từ OpenFDA.\n"
                "**2. Phân tích an toàn hoạt chất:** Lấy thông tin từ OpenFDA Label.\n\n"
                "*Cảnh báo y tế: Thông tin chỉ mang tính chất tham khảo và không thay thế cho tư vấn từ bác sĩ hoặc dược sĩ chuyên môn.*"
            )
            return json.dumps({
                "thought": "Tôi đã thu thập đầy đủ thông tin về sản phẩm, phân tích hoạt chất và so sánh giá. Tôi sẽ kết thúc cuộc hội thoại.",
                "action": "Finish",
                "action_input": "",
                "final_answer": final_markdown
            }, ensure_ascii=False)

    def run(self, user_query: str) -> str:
        self.history = []
        
        dynamic_prompt = SYSTEM_PROMPT
        if ALLOW_OUT_OF_SCOPE:
            dynamic_prompt += "\n\nCấu hình ALLOW_OUT_OF_SCOPE đang BẬT: Nếu người dùng hỏi các câu hỏi giao tiếp thông thường hoặc ngoài lĩnh vực y tế, bạn CÓ QUYỀN trả lời trực tiếp bằng kiến thức chung của mình. Bạn hãy dùng action 'Finish' và ghi câu trả lời vào 'final_answer' mà không cần dùng tool."
        else:
            dynamic_prompt += "\n\nCấu hình ALLOW_OUT_OF_SCOPE đang TẮT: Nếu người dùng hỏi các câu hỏi ngoài lĩnh vực y tế hoặc không liên quan đến tìm kiếm sản phẩm chăm sóc sức khoẻ, bạn BẮT BUỘC phải từ chối lịch sự bằng action 'Finish' và thông báo bạn chỉ có thể hỗ trợ các vấn đề về y tế/dược phẩm."
            
        current_prompt = f"{dynamic_prompt}\n\nUser Query: {user_query}\n\nBắt đầu lập luận."
        
        logger.info(f"Starting agent run for query: '{user_query}'")
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"--- ReAct Loop Iteration {iteration}/{self.max_iterations} ---")
            
            raw_response = ""
            parsed_json = None
            retry_count = 2
            
            while retry_count > 0:
                raw_response = self._call_llm(current_prompt)
                
                cleaned = raw_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                try:
                    parsed_json = json.loads(cleaned)
                    break
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON response. Error: {e}. Raw: {raw_response}")
                    retry_count -= 1
                    current_prompt += f"\n\n[LỖI HỆ THỐNG] Phản hồi vừa rồi của bạn không phải JSON hợp lệ. Vui lòng trả về kết quả dạng JSON thuần túy có đầy đủ trường 'thought', 'action', 'action_input', 'final_answer'."
                    logger.info("Prompting LLM again to recover/correct JSON formatting.")
            
            if not parsed_json:
                error_msg = "Không thể phân tích phản hồi từ AI sau nhiều lần thử lại định dạng."
                logger.error(error_msg)
                return error_msg
                
            thought = parsed_json.get("thought", "")
            action = parsed_json.get("action", "Finish")
            action_input = parsed_json.get("action_input", "")
            final_answer = parsed_json.get("final_answer", "")
            
            logger.info(f"Thought: {thought}")
            
            if action == "Finish":
                logger.info("Agent decided to Finish. Outputting final answer.")
                return final_answer
                
            observation = self._execute_tool(action, action_input)
            step_record = f"Step {iteration}: Action={action}({action_input}) -> Observation={observation}"
            self.history.append(step_record)
            current_prompt += f"\n\nStep {iteration} Result:\nThought: {thought}\nAction: {action}\nAction Input: {action_input}\nObservation: {observation}"
            
        timeout_msg = "Đại lý đã dừng hoạt động do đạt giới hạn số lần lập luận tối đa (max_iterations)."
        logger.warning(timeout_msg)
        return timeout_msg
