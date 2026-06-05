from __future__ import annotations

import math
import sys
import unicodedata
from pathlib import Path

from src import Document, EmbeddingStore

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class MarkdownHeadingChunker:
    def chunk(self, text: str) -> list[str]:
        chunks: list[str] = []
        current: list[str] = []

        for line in text.splitlines():
            stripped = line.lstrip()
            is_heading = (
                stripped.startswith("# ")
                or stripped.startswith("## ")
                or stripped.startswith("### ")
            )
            if is_heading and current:
                chunks.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)

        if current:
            chunks.append("\n".join(current).strip())

        return [chunk for chunk in chunks if chunk]


METADATA_BY_FILE = {
    "canh_bao_hoc_vu_quy_che.md": {
        "category": "academic_warning",
        "doc_type": "policy",
        "department": "registrar",
        "owner": "member_1",
    },
    "dang_ky_mon_hoc_sop.md": {
        "category": "course_registration",
        "doc_type": "sop",
        "department": "registrar",
        "owner": "member_2",
    },
    "tuyen_sinh_faq.md": {
        "category": "admissions",
        "doc_type": "faq",
        "department": "admissions",
        "owner": "member_3",
    },
    "hoc_phi_huong_dan.md": {
        "category": "tuition_finance",
        "doc_type": "guideline",
        "department": "finance",
        "owner": "member_4",
    },
    "khao_thi_quy_che.md": {
        "category": "examination",
        "doc_type": "policy",
        "department": "registrar",
        "owner": "member_5",
    },
    "tot_nghiep_quy_trinh.md": {
        "category": "graduation",
        "doc_type": "procedure",
        "department": "registrar",
        "owner": "member_6",
    },
}

VOCAB = [
    "dang ky",
    "mon hoc",
    "sis",
    "tin chi",
    "canh bao",
    "hoc vu",
    "thu thach",
    "buoc thoi hoc",
    "cgpa",
    "tuyen sinh",
    "nhap hoc",
    "ielts",
    "hoc phi",
    "gia han",
    "no dong",
    "hoc bong",
    "khao thi",
    "hoan thi",
    "phuc khao",
    "thuc hanh",
    "do an",
    "diem danh",
    "tot nghiep",
    "cap bang",
    "bang tam thoi",
]

QUERIES = [
    ("Quy trình đăng ký môn học trên SIS gồm những bước nào?", None),
    ("Khi nào sinh viên bị cảnh báo học vụ hoặc buộc thôi học?", None),
    ("Điều kiện tiếng Anh đầu vào khi nhập học là gì?", None),
    ("Sinh viên xin gia hạn học phí cần làm gì và thời hạn gia hạn tối đa bao lâu?", None),
    (
        "Quy định khảo thí áp dụng riêng cho môn thực hành hoặc đồ án là gì?",
        {"category": "examination", "applies_to": "practical_courses"},
    ),
]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d")


def keyword_embed(text: str) -> list[float]:
    normalized = normalize(text)
    vector = [float(normalized.count(term)) for term in VOCAB]
    magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / magnitude for value in vector]


def build_store() -> EmbeddingStore:
    chunker = MarkdownHeadingChunker()
    chunk_docs: list[Document] = []

    for filename, base_metadata in METADATA_BY_FILE.items():
        path = Path("data") / filename
        doc_id = path.stem
        text = path.read_text(encoding="utf-8")

        for chunk_index, chunk in enumerate(chunker.chunk(text)):
            normalized_chunk = normalize(chunk)
            is_practical_exam = base_metadata["category"] == "examination" and (
                "metadata_application: practical_courses_only" in normalized_chunk
                or "thuc hanh" in normalized_chunk
                or "do an" in normalized_chunk
            )
            applies_to = "practical_courses" if is_practical_exam else "general"
            chunk_docs.append(
                Document(
                    id=f"{doc_id}_chunk_{chunk_index}",
                    content=chunk,
                    metadata={
                        **base_metadata,
                        "source": str(path),
                        "language": "vi",
                        "doc_id": doc_id,
                        "chunk_index": chunk_index,
                        "strategy": "markdown_heading",
                        "applies_to": applies_to,
                    },
                )
            )

    store = EmbeddingStore("member1_benchmark", embedding_fn=keyword_embed)
    store.add_documents(chunk_docs)
    return store


def main() -> int:
    store = build_store()
    print(f"Stored chunks: {store.get_collection_size()}")

    for query_index, (query, metadata_filter) in enumerate(QUERIES, start=1):
        if metadata_filter:
            results = store.search_with_filter(query, top_k=3, metadata_filter=metadata_filter)
        else:
            results = store.search(query, top_k=3)

        print(f"\nQ{query_index}: {query}")
        print(f"Filter: {metadata_filter}")
        for rank, result in enumerate(results, start=1):
            metadata = result["metadata"]
            print(
                f"{rank}. score={result['score']:.3f} "
                f"source={metadata['source']} "
                f"chunk={metadata['chunk_index']} "
                f"category={metadata['category']} "
                f"applies_to={metadata['applies_to']}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
