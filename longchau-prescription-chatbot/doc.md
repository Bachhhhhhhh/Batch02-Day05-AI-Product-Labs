# Project: Long Châu Prescription Chatbot

## 1. Overview
Hệ thống hỗ trợ đọc và giải thích đơn thuốc dựa trên dữ liệu từ nhà thuốc Long Châu.

## 2. Team Strategy: Contract-First Approach
Nhóm làm việc song song dựa trên các giao diện (contracts) đã thống nhất:
- **Contract 1 (Data):** `data/drugs_clean.json` (Schema: name, ingredients, uses, dosage, side_effects, warnings, contraindications, storage, source_url).
- **Contract 2 (Vector DB):** `search_drugs(query, top_k) -> list[dict]`.
- **Contract 3 (Chatbot):** `answer_prescription(user_input) -> dict`.

## 3. Owner Plan & Status

| Owner | Task | Status | Deliverable |
|---|---|---|---|
| Member 1 | Crawl dữ liệu thuốc Long Châu | In Progress | `drugs_clean.json` |
| **Member 2 (Kiên)** | **Vector DB & Infrastructure** | **Ready (Mock)** | `build_vector_db.py`, `retriever.py`, `Dockerfile` |
| Member 3 | RAG chatbot logic | Pending | `answer_prescription()` |
| Member 4 | Safety + test cases | Pending | `test_cases.md` |
| Member 5 | UI Streamlit | Pending | `streamlit_app.py` |

## 4. Vector DB Documentation (Member 2)

### Setup & Build
1. Cài đặt dependencies: `pip install -r vector_db/requirements.txt`
2. Build database từ dữ liệu mẫu: `python vector_db/build_vector_db.py`
   - Dữ liệu sẽ được lưu tại `vector_db/chroma_db/`.
   - Mặc định dùng `sentence-transformers` (all-MiniLM-L6-v2) để nhúng dữ liệu.

### Integration for Chatbot Owner
Để sử dụng hàm tìm kiếm, chỉ cần import:
```python
from vector_db.retriever import search_drugs

results = search_drugs("Cách dùng Paracetamol?")
# Trả về list các dict chứa: drug_name, section, content, source_url
```

### Docker
Build image cho module Vector DB:
```bash
docker build -t longchau-vector-db -f vector_db/Dockerfile .
```
