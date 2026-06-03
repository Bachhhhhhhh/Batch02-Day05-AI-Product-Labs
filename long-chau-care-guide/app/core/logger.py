import os
import logging
from logging.handlers import RotatingFileHandler
from app.core.config import LOG_LEVEL

def setup_logger(name: str = "LongChauApp") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Avoid adding handlers multiple times in dev reload mode
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # 1. Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 2. File Handler (Rotating)
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, "app.log")
        # Giới hạn file log 5MB, giữ lại tối đa 5 file cũ
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger

# Create a global instance
system_logger = setup_logger()
