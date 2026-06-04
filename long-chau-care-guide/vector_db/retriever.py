import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

DB_PATH = str(Path(__file__).resolve().parent / "chroma_db")

def search_drugs(query: str, top_k: int = 5) -> list[dict]:
    """
    Hàm search tuân thủ Contract 2 của nhóm.
    Return:
    [
      {
        "drug_name": "...",
        "section": "uses/warnings/side_effects/dosage",
        "content": "...",
        "source_url": "..."
      }
    ]
    """
    try:
        client = chromadb.PersistentClient(path=DB_PATH)
        emb_fn = embedding_functions.DefaultEmbeddingFunction()
        collection = client.get_collection(name="longchau_drugs", embedding_function=emb_fn)
        
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        formatted_results = []
        # results['documents'][0] chứa list các text tìm được
        # results['metadatas'][0] chứa list các metadata tương ứng
        if results['documents']:
            for i in range(len(results['documents'][0])):
                doc = results['documents'][0][i]
                meta = results['metadatas'][0][i]
                
                formatted_results.append({
                    "drug_name": meta.get("drug_name"),
                    "section": meta.get("section"),
                    "content": doc,
                    "source_url": meta.get("source_url")
                })
        
        return formatted_results
        
    except Exception as e:
        print(f"Lỗi khi truy vấn Vector DB: {e}")
        # Trả về list rỗng nếu có lỗi hoặc DB chưa được khởi tạo
        return []

if __name__ == "__main__":
    import sys
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    # Test thử hàm search
    test_query = "Paracetamol dùng như thế nào?"
    res = search_drugs(test_query)
    print(f"Kết quả tìm kiếm cho: '{test_query}'")
    for r in res:
        print(f"- {r['drug_name']} ({r['section']}): {r['content'][:100]}...")
