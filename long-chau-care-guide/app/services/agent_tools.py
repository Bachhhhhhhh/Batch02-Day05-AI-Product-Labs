import os
import requests
import logging
from app.core.config import API_TIMEOUT, INTERNAL_API_URL

logger = logging.getLogger("HealthcareAgent.Tools")

def SearchHealthcareProductTool(query: str) -> dict:
    """
    Search healthcare products based on symptoms or requirements using OpenFDA API.
    """
    url = f"https://api.fda.gov/drug/ndc.json?search=brand_name:{query}&limit=3"
    logger.info(f"Executing SearchHealthcareProductTool: Searching for '{query}'")
    
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        products = []
        for res in results:
            products.append({
                "brand_name": res.get("brand_name", "Unknown"),
                "active_ingredients": ", ".join([ing.get("name", "") for ing in res.get("active_ingredients", [])]),
                "uses": ", ".join(res.get("pharm_class_epca", ["Chưa xác định"])),
                "dosage": "Xem hướng dẫn trên bao bì sản phẩm FDA.",
                "warnings": "Chỉ dùng theo chỉ định y tế."
            })
            
        return {
            "source": "OpenFDA API",
            "products": products
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"OpenFDA API Request failed: {e}")
        return {"error": f"OpenFDA API error: {e}"}

def AnalyzeIngredientsTool(ingredients: str) -> dict:
    """
    Analyzes product ingredients for potential side effects using OpenFDA Label API.
    """
    logger.info(f"Executing AnalyzeIngredientsTool: Analyzing '{ingredients}'")
    
    # We query the OpenFDA drug label API for the specific active ingredient
    url = f"https://api.fda.gov/drug/label.json?search=active_ingredient:{ingredients}&limit=1"
    
    try:
        response = requests.get(url, timeout=API_TIMEOUT)
        
        if response.status_code == 404:
            # FDA API returns 404 if no matches found
            return {
                "ingredients": ingredients,
                "analysis": {
                    "side_effects": "Không tìm thấy dữ liệu từ OpenFDA.",
                    "contraindications": "Chưa có thông tin.",
                    "allergy_warning": "Vui lòng hỏi ý kiến bác sĩ."
                }
            }
            
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        if not results:
             return {"error": "No data found."}
             
        res = results[0]
        # Extracts FDA standard sections if available
        warnings = res.get("warnings", ["Chưa có cảnh báo rõ ràng từ NSX."])[0]
        contraindications = res.get("contraindications", ["Không ghi nhận chống chỉ định đặc biệt."])[0]
        adverse_reactions = res.get("adverse_reactions", ["Không có báo cáo tác dụng phụ nổi bật."])[0]
        
        # Trim very long texts
        return {
            "ingredients": ingredients,
            "analysis": {
                "side_effects": adverse_reactions[:500] + "..." if len(adverse_reactions) > 500 else adverse_reactions,
                "contraindications": contraindications[:500] + "..." if len(contraindications) > 500 else contraindications,
                "allergy_warning": warnings[:500] + "..." if len(warnings) > 500 else warnings
            }
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenFDA Label API Request failed: {e}")
        return {"error": f"OpenFDA API error: {e}"}

