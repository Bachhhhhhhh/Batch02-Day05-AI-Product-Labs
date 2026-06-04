import os
import json
import logging
import requests
from app.core.config import API_TIMEOUT
from thefuzz import fuzz

logger = logging.getLogger("HealthcareAgent.Tools")

# Load internal database once
DRUGS_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'drugs_clean.json')
FOOD_DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'food_interactions.json')

try:
    with open(DRUGS_DB_PATH, 'r', encoding='utf-8') as f:
        LOCAL_DRUGS_DB = json.load(f)
except Exception as e:
    logger.error(f"Failed to load local drugs DB: {e}")
    LOCAL_DRUGS_DB = []

try:
    with open(FOOD_DB_PATH, 'r', encoding='utf-8') as f:
        FOOD_INTERACTIONS_DB = json.load(f)
except Exception as e:
    logger.error(f"Failed to load food interactions DB: {e}")
    FOOD_INTERACTIONS_DB = []

def SearchHealthcareProductTool(query: str) -> dict:
    """
    Dùng để tìm kiếm thông tin cơ bản của thuốc (tên, thành phần, công dụng).
    Input: Tên thuốc hoặc hoạt chất.
    """
    logger.info(f"Executing SearchHealthcareProductTool: Searching for '{query}'")
    
    query_lower = query.lower()
    raw_results = []
    
    # Pass 1: Exact / Substring match
    for drug in LOCAL_DRUGS_DB:
        name = drug.get('drug_name', '').lower()
        if query_lower in name:
            raw_results.append(drug)
            if len(raw_results) >= 3:
                break
                
    # Pass 2: Fuzzy matching if not enough results
    if len(raw_results) < 3:
        for drug in LOCAL_DRUGS_DB:
            if drug in raw_results:
                continue
            name = drug.get('drug_name', '').lower()
            score = fuzz.token_set_ratio(query_lower, name)
            if score >= 80:
                raw_results.append(drug)
            if len(raw_results) >= 3:
                break

    if not raw_results:
        return {"error": "Không tìm thấy thông tin thuốc này trong hệ thống nội bộ."}
        
    formatted_results = []
    for drug in raw_results:
        formatted_results.append({
            "brand_name": drug.get("drug_name", "Unknown"),
            "active_ingredients": drug.get("ingredients", ""),
            "uses": drug.get("uses", "")[:300] + "..." if len(drug.get("uses", "")) > 300 else drug.get("uses", ""),
            "dosage_guide": drug.get("dosage", "")[:300] + "..." if len(drug.get("dosage", "")) > 300 else drug.get("dosage", "")
        })

    return {
        "source": "Long Châu Database",
        "products": formatted_results
    }

def AnalyzeIngredientsTool(ingredients: str) -> dict:
    """
    Dùng để tra cứu chuyên sâu về tác dụng phụ, chống chỉ định và cảnh báo an toàn.
    Chỉ sử dụng sau khi đã xác định rõ tên thuốc hoặc hoạt chất.
    """
    logger.info(f"Executing AnalyzeIngredientsTool: Analyzing '{ingredients}'")
    
    query_lower = ingredients.lower()
    match = None
    
    for drug in LOCAL_DRUGS_DB:
        name = drug.get('drug_name', '').lower()
        if query_lower in name:
            match = drug
            break
            
    if not match:
        best_score = 0
        for drug in LOCAL_DRUGS_DB:
            name = drug.get('drug_name', '').lower()
            score = fuzz.token_set_ratio(query_lower, name)
            if score > best_score and score >= 80:
                best_score = score
                match = drug
            
    if not match:
        return {"error": "Không tìm thấy dữ liệu an toàn cho thành phần này."}
        
    return {
        "analysis": {
            "side_effects": match.get("side_effects", "Không có dữ liệu."),
            "contraindications": match.get("contraindications", "Không có dữ liệu."),
            "warnings": match.get("warnings", "Không có dữ liệu.")
        }
    }

def AnalyzeDrugFoodInteractionTool(drug_name: str, food_item: str = "") -> dict:
    """
    Tra cứu tương tác giữa thuốc và thực phẩm/đồ uống.
    Input: Tên thuốc (bắt buộc) và tên thực phẩm (tùy chọn).
    """
    logger.info(f"Executing AnalyzeDrugFoodInteractionTool: Drug='{drug_name}', Food='{food_item}'")
    
    # 1. Search in local Food Interaction DB
    drug_lower = drug_name.lower()
    local_match = None
    
    for entry in FOOD_INTERACTIONS_DB:
        if fuzz.token_set_ratio(drug_lower, entry['drug_name'].lower()) >= 85:
            local_match = entry
            break
            
    if local_match:
        if food_item:
            # Filter specifically for the food item
            food_lower = food_item.lower()
            specific_interactions = [i for i in local_match['interactions'] if fuzz.token_set_ratio(food_lower, i['object'].lower()) >= 70]
            if specific_interactions:
                return {"source": "Local Expert DB", "interactions": specific_interactions}
        
        return {"source": "Local Expert DB", "interactions": local_match['interactions']}

    # 2. Fallback to OpenFDA API (Public)
    try:
        fda_url = f"https://api.fda.gov/drug/label.json?search=openfda.brand_name:{drug_name}&limit=1"
        response = requests.get(fda_url, timeout=API_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            if results:
                label_info = results[0]
                # Look for food/alcohol interactions in labels
                drug_int = label_info.get('drug_interactions', [""])[0]
                precautions = label_info.get('precautions', [""])[0]
                
                return {
                    "source": "OpenFDA (US Government)",
                    "raw_info": {
                        "drug_interactions": drug_int[:1000] + "..." if len(drug_int) > 1000 else drug_int,
                        "precautions": precautions[:1000] + "..." if len(precautions) > 1000 else precautions
                    },
                    "note": "Thông tin từ FDA Mỹ, cần dịch sang tiếng Việt để trả lời user."
                }
    except Exception as e:
        logger.error(f"OpenFDA call failed: {e}")

    return {"error": "Hiện chưa có dữ liệu cụ thể về tương tác thực phẩm cho thuốc này trong hệ thống demo."}
