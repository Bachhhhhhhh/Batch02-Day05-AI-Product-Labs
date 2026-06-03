import json
import os
import sys
import chromadb
from chromadb.utils import embedding_functions

# Fix Windows console unicode print error
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Cấu hình đường dẫn
DATA_PATH = "data/sample_drugs.json" # Có thể thay bằng drugs_clean.json khi có data thật
DB_PATH = "vector_db/chroma_db"

def build_vector_db(json_file):
    # Khởi tạo Chroma Client với chế độ lưu trữ local
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # Sử dụng model embedding mặc định của Chroma (sentence-transformers/all-MiniLM-L6-v2)
    # Hoặc có thể đổi sang OpenAI nếu nhóm yêu cầu
    emb_fn = embedding_functions.DefaultEmbeddingFunction()
    
    # Tạo hoặc lấy collection
    collection = client.get_or_create_collection(name="longchau_drugs", embedding_function=emb_fn)
    
    with open(json_file, 'r', encoding='utf-8') as f:
        drugs = json.load(f)
    
    documents = []
    metadatas = []
    ids = []
    
    # Các trường thông tin muốn index để search
    sections = ["uses", "dosage", "side_effects", "warnings", "contraindications"]
    
    for drug in drugs:
        drug_name = drug.get("drug_name")
        source_url = drug.get("source_url")
        
        for section in sections:
            content = drug.get(section)
            if content and content.strip():
                # Tạo một document cho mỗi section của mỗi loại thuốc
                documents.append(content)
                metadatas.append({
                    "drug_name": drug_name,
                    "section": section,
                    "source_url": source_url
                })
                # ID dạng: TênThuốc_Section
                ids.append(f"{drug_name}_{section}".replace(" ", "_"))
    
    # Thêm dữ liệu vào collection
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Đã index {len(ids)} đoạn thông tin từ {len(drugs)} loại thuốc.")

if __name__ == "__main__":
    if os.path.exists(DATA_PATH):
        build_vector_db(DATA_PATH)
    else:
        print(f"Không tìm thấy file {DATA_PATH}")
