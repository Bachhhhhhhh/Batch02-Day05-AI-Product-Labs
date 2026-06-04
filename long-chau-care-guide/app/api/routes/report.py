from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os
from datetime import datetime
from app.core.logger import system_logger

router = APIRouter()

# Path to the reports file
REPORTS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "reports.json")

class ReportRequest(BaseModel):
    user_feedback: str
    message: str

@router.post("")
async def submit_report(request: ReportRequest):
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(REPORTS_FILE), exist_ok=True)
        
        # Load existing reports
        reports = []
        if os.path.exists(REPORTS_FILE):
            try:
                with open(REPORTS_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        reports = json.loads(content)
            except json.JSONDecodeError:
                system_logger.warning(f"Could not parse existing reports file. Starting fresh.")
                reports = []
        
        # Create new report entry
        new_report = {
            "timestamp": datetime.now().isoformat(),
            "user_feedback": request.user_feedback,
            "ai_message": request.message
        }
        
        reports.append(new_report)
        
        # Save back to file
        with open(REPORTS_FILE, "w", encoding="utf-8") as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
            
        system_logger.info(f"Report saved successfully.")
        return {"status": "success", "message": "Báo cáo của bạn đã được ghi nhận."}
        
    except Exception as e:
        system_logger.error(f"Error saving report: {str(e)}")
        raise HTTPException(status_code=500, detail="Không thể lưu báo cáo.")
