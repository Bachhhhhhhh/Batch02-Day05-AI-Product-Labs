import os
import json
import logging
from app.core.config import API_TIMEOUT

logger = logging.getLogger("HealthcareAgent.Tools")

# Load internal database once
DRUGS_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'drugs_clean.json')
try:
    with open(DRUGS_DB_PATH, 'r', encoding='utf-8') as f:
        LOCAL_DRUGS_DB = json.load(f)
except Exception as e:
    logger.error(f"Failed to load local drugs DB: {e}")
    LOCAL_DRUGS_DB = []

def SearchHealthcareProductTool(query: str) -> dict:
    """
    Search healthcare products based on symptoms or requirements using the local database.
    """
    logger.info(f"Executing SearchHealthcareProductTool: Searching for '{query}' in local DB")
    
    query_lower = query.lower()
    results = []
    
    for drug in LOCAL_DRUGS_DB:
        name = drug.get('drug_name', '').lower()
        uses = drug.get('uses', '').lower()
        ingredients = drug.get('ingredients', '').lower()
        
        if query_lower in name or query_lower in uses or query_lower in ingredients:
            results.append({
                "brand_name": drug.get("drug_name", "Unknown"),
                "active_ingredients": drug.get("ingredients", ""),
                "uses": drug.get("uses", "")[:200] + "..." if len(drug.get("uses", "")) > 200 else drug.get("uses", ""),
                "dosage": drug.get("dosage", "")[:200] + "..." if len(drug.get("dosage", "")) > 200 else drug.get("dosage", ""),
                "warnings": drug.get("warnings", "")[:200] + "..." if len(drug.get("warnings", "")) > 200 else drug.get("warnings", "")
            })
            if len(results) >= 3:
                break
                
    if not results:
        return {"error": "Không tìm thấy sản phẩm nào phù hợp trong cơ sở dữ liệu nội bộ."}
        
    return {
        "source": "Local Database",
        "products": results
    }

def AnalyzeIngredientsTool(ingredients: str) -> dict:
    """
    Analyzes product ingredients for potential side effects using the local database.
    """
    logger.info(f"Executing AnalyzeIngredientsTool: Analyzing '{ingredients}' in local DB")
    
    query_lower = ingredients.lower()
    match = None
    
    for drug in LOCAL_DRUGS_DB:
        name = drug.get('drug_name', '').lower()
        ing = drug.get('ingredients', '').lower()
        
        if query_lower in name or query_lower in ing:
            match = drug
            break
            
    if not match:
        return {
            "ingredients": ingredients,
            "analysis": {
                "side_effects": "Không tìm thấy dữ liệu tác dụng phụ trong hệ thống nội bộ.",
                "contraindications": "Chưa có thông tin chống chỉ định.",
                "allergy_warning": "Vui lòng hỏi ý kiến bác sĩ."
            }
        }
        
    side_effects = match.get("side_effects", "Không có báo cáo tác dụng phụ nổi bật.")
    contraindications = match.get("contraindications", "Không ghi nhận chống chỉ định đặc biệt.")
    warnings = match.get("warnings", "Chưa có cảnh báo rõ ràng từ NSX.")
    
    return {
        "ingredients": ingredients,
        "analysis": {
            "side_effects": side_effects[:500] + "..." if len(side_effects) > 500 else side_effects,
            "contraindications": contraindications[:500] + "..." if len(contraindications) > 500 else contraindications,
            "allergy_warning": warnings[:500] + "..." if len(warnings) > 500 else warnings
        }
    }
