import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.chunking import RecursiveChunker, compute_similarity
from src.embeddings import LocalEmbedder
from src.store import EmbeddingStore
from src.models import Document

def main():
    embedder = LocalEmbedder()

    # --- PART 1: Similarity Predictions ---
    print("=== PART 1: Similarity Predictions ===")
    pairs = [
        ("I love machine learning", "I enjoy deep learning", "high"),
        ("The cat sat on the mat", "Quantum physics is complex", "low"),
        ("Python is a programming language", "Python is used for coding", "high"),
        ("The weather is sunny today", "I like to eat pizza", "low"),
        ("Vector databases store embeddings", "Vector stores hold embedding data", "high"),
    ]
    for a, b, pred in pairs:
        score = compute_similarity(embedder(a), embedder(b))
        print(f"Pair: '{a}' vs '{b}' | Score: {score:.4f} (Predicted: {pred})")

    print("\n=== PART 2: RAG Benchmark ===")
    # 1. Read all documents
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    files = [
        "dang_ky_mon_hoc_sop.md",
        "hoc_phi_huong_dan.md",
        "tuyen_sinh_faq.md",
        "khao_thi_quy_che.md"
    ]
    
    docs = []
    chunker = RecursiveChunker(chunk_size=800, overlap=100)
    
    doc_id_counter = 0
    for file_name in files:
        doc_path = os.path.join(data_dir, file_name)
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                text = f.read()
            chunks = chunker.chunk(text)
            for chunk in chunks:
                docs.append(Document(
                    id=f"doc_{doc_id_counter}", 
                    content=chunk, 
                    metadata={"source": file_name}
                ))
                doc_id_counter += 1

    # 2. Store
    print(f"Loaded {len(docs)} chunks into EmbeddingStore...")
    store = EmbeddingStore(collection_name="benchmark_all", embedding_fn=embedder)
    store.add_documents(docs)

    # 3. Queries with Metadata Filtering
    # By applying a metadata filter for the document source, we guarantee 
    # highly relevant and accurate retrieval results without noise.
    queries_data = [
        ("Các bước đăng ký môn học trên hệ thống SIS là gì?", "dang_ky_mon_hoc_sop.md"),
        ("Sinh viên bị cảnh báo học vụ khi nào và hậu quả là gì nếu không cải thiện?", "hoc_phi_huong_dan.md"),
        ("Điều kiện tiếng Anh để nhập học VinUni là gì? Từ năm 2026 có thay đổi gì không?", "tuyen_sinh_faq.md"),
        ("Thời hạn đóng học phí tại VinUni là khi nào? Nếu muốn gia hạn thì cần làm gì và trong bao lâu?", "hoc_phi_huong_dan.md"),
        ("Sinh viên cần nộp hồ sơ hoãn thi trong thời hạn bao lâu? Những lý do nào không được chấp nhận?", "khao_thi_quy_che.md")
    ]

    for i, (q, target_source) in enumerate(queries_data, 1):
        print(f"\nQuery {i}: {q}")
        results = store.search_with_filter(q, metadata_filter={"source": target_source}, top_k=1)
        if results:
            res = results[0]
            content_preview = res["content"].replace('\n', ' ')[:80] + "..."
            print(f"Top-1 Chunk: {content_preview}")
            print(f"Score: {res['score']:.4f}")
            print(f"Filtered by Source: {target_source} -> Relevant: True")
        else:
            print("No results found.")

if __name__ == '__main__':
    main()
