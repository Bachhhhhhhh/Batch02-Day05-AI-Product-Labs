import os
from dotenv import load_dotenv
from pathlib import Path

# Tải cấu hình từ file .env
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

class ModelSettings:
    """Cấu hình tập trung cho các mô hình AI được sử dụng trong dự án"""
    GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash-lite")
    OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")

# Khởi tạo instance duy nhất để import
model_settings = ModelSettings()
