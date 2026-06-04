# Mock database for Long Chau OTC Products

PRODUCT_CATALOG = {
   "thuốc xịt mũi": [
    {
        "id": "xisat-blue",
        "name": "Xisat Nước Biển Sâu",
        "price": "32000",
        "description": "Làm sạch khoang mũi, giảm nghẹt mũi.",
        "usage": "3-5 lần/ngày."
    },
    {
        "id": "otrivin-01",
        "name": "Otrivin 0.1%",
        "price": "56000",
        "description": "Giảm nghẹt mũi nhanh.",
        "usage": "Không quá 3 lần/ngày."
    },
    {
        "id": "sterimar",
        "name": "Sterimar Baby",
        "price": "95000",
        "description": "Nước biển sâu vệ sinh mũi.",
        "usage": "2-6 lần/ngày."
    }
],

"thuốc giảm đau & hạ sốt": [
    {
        "id": "panadol-extra",
        "name": "Panadol Extra",
        "price": "42000",
        "description": "Giảm đau đầu, đau cơ, hạ sốt.",
        "usage": "1-2 viên/lần."
    },
    {
        "id": "efferalgan-500",
        "name": "Efferalgan 500mg",
        "price": "50000",
        "description": "Viên sủi hạ sốt.",
        "usage": "1 viên/lần."
    },
    {
        "id": "hapacol-500",
        "name": "Hapacol 500mg",
        "price": "18000",
        "description": "Paracetamol giảm đau hạ sốt.",
        "usage": "1 viên mỗi 4-6 giờ."
    }
],

"thuốc dị ứng & nổi mẩn": [
    {
        "id": "telfast-180",
        "name": "Telfast 180mg",
        "price": "95000",
        "description": "Điều trị viêm mũi dị ứng.",
        "usage": "1 viên/ngày."
    },
    {
        "id": "loratadine-10",
        "name": "Loratadine 10mg",
        "price": "22000",
        "description": "Giảm ngứa, nổi mẩn.",
        "usage": "1 viên/ngày."
    },
    {
        "id": "cetirizine-10",
        "name": "Cetirizine 10mg",
        "price": "18000",
        "description": "Kháng histamine điều trị dị ứng.",
        "usage": "1 viên/ngày."
    }
],

"men vi sinh & tiêu hóa": [
    {
        "id": "enterogermina",
        "name": "Enterogermina",
        "price": "85000",
        "description": "Bổ sung lợi khuẩn đường ruột.",
        "usage": "1-2 ống/ngày."
    },
    {
        "id": "bioflora",
        "name": "Bioflora",
        "price": "95000",
        "description": "Cân bằng hệ vi sinh đường ruột.",
        "usage": "Theo chỉ định."
    },
    {
        "id": "lactomin-plus",
        "name": "Lactomin Plus",
        "price": "120000",
        "description": "Hỗ trợ hệ tiêu hóa khỏe mạnh.",
        "usage": "1 gói/ngày."
    }
],

"thuốc dạ dày": [
    {
        "id": "phosphalugel",
        "name": "Phosphalugel",
        "price": "85000",
        "description": "Giảm đau dạ dày, ợ nóng.",
        "usage": "1-2 gói/lần."
    },
    {
        "id": "gastropulgite",
        "name": "Gastropulgite",
        "price": "60000",
        "description": "Giảm triệu chứng viêm dạ dày.",
        "usage": "1 gói/lần."
    },
    {
        "id": "yumangel",
        "name": "Yumangel",
        "price": "78000",
        "description": "Trung hòa acid dạ dày.",
        "usage": "1 gói/lần."
    }
],

"thuốc tiêu chảy": [
    {
        "id": "smecta",
        "name": "Smecta",
        "price": "35000",
        "description": "Điều trị tiêu chảy cấp.",
        "usage": "1 gói/lần."
    },
    {
        "id": "berberin",
        "name": "Berberin OPC",
        "price": "15000",
        "description": "Hỗ trợ điều trị tiêu chảy.",
        "usage": "2 viên/lần."
    },
    {
        "id": "hidrasec",
        "name": "Hidrasec",
        "price": "110000",
        "description": "Điều trị tiêu chảy cấp ở trẻ em và người lớn.",
        "usage": "Theo hướng dẫn."
    }
],

"vitamin & khoáng chất": [
    {
        "id": "redoxon",
        "name": "Redoxon Vitamin C",
        "price": "120000",
        "description": "Tăng cường đề kháng.",
        "usage": "1 viên/ngày."
    },
    {
        "id": "vitamin-c-500",
        "name": "Vitamin C 500mg DHG",
        "price": "45000",
        "description": "Bổ sung vitamin C.",
        "usage": "1 viên/ngày."
    },
    {
        "id": "centrum",
        "name": "Centrum Adults",
        "price": "320000",
        "description": "Bổ sung đa vitamin.",
        "usage": "1 viên/ngày."
    }
],

"thực phẩm bổ sung": [
    {
        "id": "omega3",
        "name": "Omega 3 Fish Oil",
        "price": "280000",
        "description": "Bổ sung DHA và EPA.",
        "usage": "1-2 viên/ngày."
    },
    {
        "id": "d3k2",
        "name": "Vitamin D3 K2",
        "price": "250000",
        "description": "Hỗ trợ hấp thu canxi.",
        "usage": "1 viên/ngày."
    },
    {
        "id": "calcium-corbiere",
        "name": "Calcium Corbiere",
        "price": "135000",
        "description": "Bổ sung canxi cho xương.",
        "usage": "1 ống/ngày."
    }
]
}

def get_products_by_category(category_name):
    category_name_lower = category_name.lower()
    for cat_key in PRODUCT_CATALOG.keys():
        if cat_key in category_name_lower or category_name_lower in cat_key:
            return PRODUCT_CATALOG[cat_key]
    return []
