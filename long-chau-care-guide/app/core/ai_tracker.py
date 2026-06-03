import time
import uuid
import json
import psutil
import threading
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Callable, Any, Optional

# ==============================================================================
# AI PLATFORM: LLM RESOURCE TRACKER MODULE
# ==============================================================================

# Đường dẫn file xuất audit log
LOG_FILE = Path("ai_resource_audit.jsonl")

# Bảng giá ước tính (USD) trên 1 triệu tokens (Cập nhật T6/2026)
PRICING_PER_MILLION = {
    "gpt-4o": {"input": 5.0, "output": 15.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet": {"input": 3.0, "output": 15.0},
    "gemini-1.5-pro": {"input": 3.5, "output": 10.5},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
}

def calculate_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Tính toán chi phí dựa trên bảng giá định trước."""
    rates = PRICING_PER_MILLION.get(model_name, {"input": 0.0, "output": 0.0})
    cost = (prompt_tokens * rates["input"] / 1_000_000) + (completion_tokens * rates["output"] / 1_000_000)
    return cost

def async_log_to_file(log_data: dict):
    """
    Hàm ghi file bất đồng bộ (Asynchronous logging) bằng Threading.
    Tránh chặn (block) luồng xử lý (event loop) chính của ứng dụng web (FastAPI/Uvicorn).
    """
    def _write_log():
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data) + "\n")
        except Exception as e:
            print(f"[AI Tracker] Lỗi ghi log: {e}")
            
    threading.Thread(target=_write_log, daemon=True).start()


class AIResourceTracker:
    """
    Context Manager chuyên dụng để bao bọc các lượt gọi API đến LLM.
    Đo lường thời gian (latency), tài nguyên hệ thống (CPU/RAM) và token.
    
    Sử dụng:
    with AIResourceTracker("gpt-4o-mini") as tracker:
        response = call_openai_api(...)
        tracker.set_tokens(prompt=100, completion=50)
    """
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.request_id = str(uuid.uuid4())
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.start_time: float = 0.0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        
        # Liên kết với tiến trình hiện tại để đo tài nguyên
        self.process = psutil.Process()
        
    def __enter__(self):
        # Lưu thời điểm bắt đầu
        self.start_time = time.perf_counter()
        
        # Mồi (prime) hàm cpu_percent() của psutil để đo lường chính xác khoảng thời gian giữa enter và exit
        self.process.cpu_percent(interval=None)
        return self
        
    def set_tokens(self, prompt: int, completion: int):
        """Cập nhật số token sau khi API phản hồi."""
        self.prompt_tokens = prompt
        self.completion_tokens = completion

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 1. Đo lường Latency
        latency_seconds = time.perf_counter() - self.start_time
        
        # 2. Đo lường System Resources (CPU/RAM của process hiện tại trong suốt thời gian gọi API)
        cpu_percent = self.process.cpu_percent(interval=None)
        ram_mb = self.process.memory_info().rss / (1024 * 1024)
        
        # 3. Xác định Status
        status = "SUCCESS"
        error_message = None
        if exc_type is not None:
            status = "FAILED"
            error_message = f"{exc_type.__name__}: {str(exc_val)}"
            
        # 4. Tính toán Metrics (Tokens & Cost)
        total_tokens = self.prompt_tokens + self.completion_tokens
        estimated_cost = calculate_cost(self.model_name, self.prompt_tokens, self.completion_tokens)
        
        # 5. Khởi tạo Payload
        log_data = {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "model_name": self.model_name,
            "latency_seconds": round(latency_seconds, 4),
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(estimated_cost, 6),
            "system_resources": {
                "cpu_percent": round(cpu_percent, 2),
                "ram_mb": round(ram_mb, 2)
            },
            "status": status
        }
        
        if error_message:
            log_data["error_message"] = error_message
            
        # 6. Đẩy log vào background thread
        async_log_to_file(log_data)
        
        # Trả về False để reraise exception nếu có (không nuốt lỗi của hệ thống)
        return False


def track_ai_resource(model_name: str):
    """
    Decorator cho các hàm gọi API đồng bộ hoặc bất đồng bộ.
    Yêu cầu: Hàm được wrap phải trả về tuple (kết_quả, prompt_tokens, completion_tokens)
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with AIResourceTracker(model_name) as tracker:
                # Hàm thực thi
                result, prompt_toks, comp_toks = func(*args, **kwargs)
                tracker.set_tokens(prompt=prompt_toks, completion=comp_toks)
                return result
        return wrapper
    return decorator
