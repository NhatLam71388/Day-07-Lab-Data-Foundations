import os
import re
from pathlib import Path

from src.models import Document
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker
from src.store import EmbeddingStore

class MarkdownHeaderChunker:
    """Custom Chunking Strategy cho Thành viên 1: Cắt theo header Markdown"""
    def chunk(self, text: str) -> list[str]:
        parts = re.split(r'(^#+\s+.*)', text, flags=re.MULTILINE)
        chunks = []
        current = ""
        for p in parts:
            if re.match(r'^#+\s+.*', p):
                if current.strip():
                    chunks.append(current.strip())
                current = p + "\n"
            else:
                current += p
        if current.strip():
            chunks.append(current.strip())
        return chunks

def load_file(path: str) -> str:
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def main():
    data_dir = Path("data")
    
    # 1. Định nghĩa file, chiến lược chunking và load data
    configs = [
        {
            "id": "doc1_canh_bao",
            "file": "canh_bao_hoc_vu_quy_che.md",
            "chunker": MarkdownHeaderChunker(),
            "strategy_name": "Custom (Markdown Headers)"
        },
        {
            "id": "doc2_dang_ky",
            "file": "dang_ky_mon_hoc_sop.md",
            "chunker": SentenceChunker(max_sentences_per_chunk=5),
            "strategy_name": "Sentence (max=5)"
        },
        {
            "id": "doc3_tuyen_sinh",
            "file": "tuyen_sinh_faq.md",
            "chunker": SentenceChunker(max_sentences_per_chunk=2),
            "strategy_name": "Sentence (max=2)"
        },
        {
            "id": "doc4_hoc_phi",
            "file": "hoc_phi_huong_dan.md",
            "chunker": RecursiveChunker(chunk_size=300),
            "strategy_name": "Recursive (size=300)"
        },
        {
            "id": "doc5_khao_thi",
            "file": "khao_thi_quy_che.md",
            "chunker": RecursiveChunker(chunk_size=800),
            "strategy_name": "Recursive (size=800)"
        },
        {
            "id": "doc6_tot_nghiep",
            "file": "tot_nghiep_quy_trinh.md",
            "chunker": FixedSizeChunker(chunk_size=400, overlap=50),
            "strategy_name": "FixedSize (size=400, overlap=50) - Baseline"
        }
    ]

    store = EmbeddingStore(collection_name="benchmark_store")
    
    print("=== ĐANG INDEX DỮ LIỆU VÀO STORE ===")
    total_chunks = 0
    for cfg in configs:
        filepath = data_dir / cfg["file"]
        if not filepath.exists():
            print(f"Warning: Không tìm thấy {filepath}. Bỏ qua.")
            continue
            
        text = load_file(str(filepath))
        chunks = cfg["chunker"].chunk(text)
        
        docs = [
            Document(
                id=f'{cfg["id"]}_{i}',
                content=chunk,
                metadata={"source_file": cfg["file"], "strategy": cfg["strategy_name"], "doc_id": cfg["id"]}
            ) for i, chunk in enumerate(chunks)
        ]
        
        store.add_documents(docs)
        total_chunks += len(docs)
        print(f"Đã index {len(docs)} chunks từ {cfg['file']} bằng {cfg['strategy_name']}")

    print(f"\nTổng số chunks trong store: {store.get_collection_size()} (kỳ vọng: {total_chunks})")

    # 2. Định nghĩa Queries
    queries = [
        "Quy trình đăng ký môn học diễn ra như thế nào và kết quả mong đợi là gì?",
        "Khi nào thì sinh viên bị rơi vào các mức cảnh báo học vụ và buộc thôi học?",
        "Điều kiện tuyển sinh và thủ tục nhập học bao gồm những gì?",
        "Thời hạn đóng học phí và chính sách gia hạn học phí được quy định ra sao?",
        "Có quy định thi cử nào áp dụng riêng cho các môn thực hành hoặc đồ án không?",
        "Quy trình xét duyệt tốt nghiệp và tiêu chuẩn cấp phát văn bằng cử nhân là gì?"
    ]

    print("\n=== KẾT QUẢ BENCHMARK (TOP 1 CHUNK CHO MỖI QUERY) ===")
    for i, q in enumerate(queries, 1):
        print(f"\nQuery {i}: {q}")
        results = store.search(q, top_k=1)
        if not results:
            print("  Không tìm thấy kết quả.")
        else:
            best = results[0]
            print(f"  Score    : {best['score']:.4f}")
            print(f"  Strategy : {best['metadata'].get('strategy', 'N/A')} ({best['metadata'].get('source_file', 'N/A')})")
            content = best['content'].replace('\n', ' ')
            print(f"  Content  : {content[:100]}...")

if __name__ == '__main__':
    main()
