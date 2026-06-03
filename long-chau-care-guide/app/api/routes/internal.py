from fastapi import APIRouter
from typing import Optional

router = APIRouter()

MOCK_PRICE_DATABASE = {
    "paracetamol": {
        "Long Châu": "1.000đ / viên",
        "Pharmacity": "1.200đ / viên",
        "An Khang": "1.100đ / viên"
    },
    "ibuprofen": {
        "Long Châu": "3.500đ / viên",
        "Pharmacity": "3.200đ / viên",
        "An Khang": "3.400đ / viên"
    },
    "loratadine": {
        "Long Châu": "2.200đ / viên",
        "Pharmacity": "2.500đ / viên",
        "An Khang": "2.300đ / viên"
    },
    "prospan": {
        "Long Châu": "82.000đ / chai 100ml",
        "Pharmacity": "85.000đ / chai 100ml",
        "An Khang": "83.000đ / chai 100ml"
    }
}

@router.get("/price")
async def get_price(product: str):
    """
    Internal Mock API endpoint for querying product prices.
    This replaces the local dictionary lookup in the ComparePriceTool.
    """
    prod_lower = product.lower()
    
    prices = {
        "Long Châu": "Liên hệ nhà thuốc",
        "Pharmacity": "Liên hệ nhà thuốc",
        "An Khang": "Liên hệ nhà thuốc"
    }
    
    for key, price_dict in MOCK_PRICE_DATABASE.items():
        if key in prod_lower:
            prices = price_dict
            break
            
    return {
        "product_name": product,
        "prices": prices,
        "source": "Internal Mock API"
    }
