import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.chunking import RecursiveChunker
from src.embeddings import LocalEmbedder
from src.store import EmbeddingStore
from src.models import Document
from src.agent import KnowledgeBaseAgent

def main():
    from dotenv import load_dotenv
    load_dotenv()

    # 1. Read document
    doc_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'khao_thi_quy_che.md')
    with open(doc_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # 2. Chunking
    chunker = RecursiveChunker(chunk_size=800, overlap=100)
    chunks = chunker.chunk(text)
    
    # Create documents with metadata
    docs = []
    for i, chunk in enumerate(chunks):
        meta = {"topic": "khao_thi", "source": "khao_thi_quy_che.md"}
        lower_chunk = chunk.lower()
        if "thực hành" in lower_chunk or "lâm sàng" in lower_chunk or "đồ án" in lower_chunk:
            meta["loai_mon"] = "thuc_hanh_lam_sang"
        else:
            meta["loai_mon"] = "ly_thuyet"
        docs.append(Document(id=f"khao_thi_{i}", content=chunk, metadata=meta))

    # 3. Store
    store = EmbeddingStore(collection_name="benchmark5", embedding_fn=LocalEmbedder())
    store.add_documents(docs)

    # 4. Query with metadata filter
    query = "Quy định vắng mặt đối với môn thực hành lâm sàng và đồ án tốt nghiệp là gì? Trường hợp nào giảng viên được quyền từ chối?"
    print(f"Query: {query}")
    print(f"Total chunks: {len(chunks)}")

    # Test filtering by loai_mon
    filter_dict = {"loai_mon": "thuc_hanh_lam_sang"}
    results = store.search_with_filter(query, metadata_filter=filter_dict, top_k=3)
    
    print(f"\nResults with filter {filter_dict}:")
    for i, res in enumerate(results, 1):
        content_preview = res["content"][:100].replace('\n', ' ')
        print(f"Rank {i} | Score: {res['score']:.4f}")
        print(f"Preview: {content_preview}...")

if __name__ == '__main__':
    main()
