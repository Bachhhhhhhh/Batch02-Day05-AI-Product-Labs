import os
import json
import logging
from app.core.config import API_TIMEOUT
from thefuzz import fuzz

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
    Search healthcare products based on symptoms or requirements using the local database with fuzzy matching.
    """
    logger.info(f"Executing SearchHealthcareProductTool: Searching for '{query}' in local DB")
    
    query_lower = query.lower()
    raw_results = []
    
    # Pass 1: Exact / Substring match
    for drug in LOCAL_DRUGS_DB:
        name = drug.get('drug_name', '').lower()
        uses = drug.get('uses', '').lower()
        ingredients = drug.get('ingredients', '').lower()
        
        if query_lower in name or query_lower in uses or query_lower in ingredients:
            raw_results.append(drug)
            if len(raw_results) >= 3:
                break
                
    # Pass 2: Fuzzy matching if not enough results
    if len(raw_results) < 3:
        for drug in LOCAL_DRUGS_DB:
            if drug in raw_results:
                continue
            name = drug.get('drug_name', '').lower()
            # token_set_ratio is good for subset/partial match ignoring order
            score = fuzz.token_set_ratio(query_lower, name)
            if score >= 70:
                raw_results.append(drug)
            if len(raw_results) >= 3:
                break

    if not raw_results:
        return {"error": "Không tìm thấy sản phẩm nào phù hợp trong cơ sở dữ liệu nội bộ."}
        
    formatted_results = []
    for drug in raw_results:
        formatted_results.append({
            "brand_name": drug.get("drug_name", "Unknown"),
            "active_ingredients": drug.get("ingredients", ""),
            "uses": drug.get("uses", "")[:200] + "..." if len(drug.get("uses", "")) > 200 else drug.get("uses", ""),
            "dosage": drug.get("dosage", "")[:200] + "..." if len(drug.get("dosage", "")) > 200 else drug.get("dosage", ""),
            "warnings": drug.get("warnings", "")[:200] + "..." if len(drug.get("warnings", "")) > 200 else drug.get("warnings", "")
        })

    return {
        "source": "Local Database",
        "products": formatted_results
    }

def AnalyzeIngredientsTool(ingredients: str) -> dict:
    """
    Analyzes product ingredients for potential side effects using the local database with fuzzy matching.
    """
    logger.info(f"Executing AnalyzeIngredientsTool: Analyzing '{ingredients}' in local DB")
    
    query_lower = ingredients.lower()
    match = None
    
    # Pass 1: Exact match
    for drug in LOCAL_DRUGS_DB:
        name = drug.get('drug_name', '').lower()
        ing = drug.get('ingredients', '').lower()
        
        if query_lower in name or query_lower in ing:
            match = drug
            break
            
    # Pass 2: Fuzzy matching
    if not match:
        best_score = 0
        best_drug = None
        for drug in LOCAL_DRUGS_DB:
            name = drug.get('drug_name', '').lower()
            ing = drug.get('ingredients', '').lower()
            
            score_name = fuzz.token_set_ratio(query_lower, name)
            score_ing = fuzz.token_set_ratio(query_lower, ing)
            max_score = max(score_name, score_ing)
            
            if max_score > best_score and max_score >= 70:
                best_score = max_score
                best_drug = drug
                
        match = best_drug
            
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
