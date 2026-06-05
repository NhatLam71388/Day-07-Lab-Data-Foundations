# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Duy Bảo
**MSSV:** 2A202600565
**Nhóm:** [Tên nhóm]
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Cosine similarity cao (gần 1.0) có nghĩa là hai vector nhúng (embedding) trỏ gần cùng một hướng trong không gian vector, tức là hai đoạn văn bản có ngữ nghĩa tương đồng nhau. Giá trị này đo góc giữa hai vector, không phụ thuộc vào độ lớn (độ dài) của chúng.

**Ví dụ HIGH similarity:**
- Sentence A: "Machine learning enables systems to learn from data."
- Sentence B: "Deep learning allows computers to learn patterns from data."
- Tại sao tương đồng: Cả hai câu đều nói về việc máy tính tự học từ dữ liệu — cùng chủ đề AI/ML, dùng nhiều từ khoá trùng nhau như "learn", "data", "systems/computers".

**Ví dụ LOW similarity:**
- Sentence A: "The cat sat on the mat."
- Sentence B: "Quantum entanglement is a phenomenon in physics."
- Tại sao khác: Hai câu hoàn toàn thuộc hai lĩnh vực khác nhau (mô tả vật thể vs. vật lý lượng tử), không chia sẻ từ khoá hay khái niệm nào, nên embedding của chúng nằm ở các hướng rất xa nhau trong không gian vector.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity đo góc giữa hai vector nên không bị ảnh hưởng bởi độ lớn (magnitude) của vector — hai văn bản dài/ngắn khác nhau nhưng cùng ý nghĩa vẫn cho similarity cao. Ngược lại, Euclidean distance bị ảnh hưởng bởi norm của vector, khiến văn bản dài luôn "xa" hơn văn bản ngắn dù nội dung tương đồng.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính:
> - `step = chunk_size - overlap = 500 - 50 = 450`
> - Số chunks ≈ `ceil((10000 - 500) / 450) + 1 = ceil(9500 / 450) + 1 = 22 + 1 = 22`
> - Chính xác hơn: `ceil(10000 / 450) = ceil(22.22) = 23` chunks
>
> **Đáp án: ~22–23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap = 100: `step = 500 - 100 = 400` → số chunks tăng lên ≈ `ceil(10000 / 400) = 25` chunks. Overlap nhiều hơn giúp đảm bảo context quan trọng nằm ở ranh giới chunk không bị mất — các câu hoặc ý hoàn chỉnh sẽ xuất hiện trong ít nhất một chunk lân cận, giúp retrieval chính xác hơn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Kiến thức AI/ML & Công nghệ phần mềm (AI/ML Knowledge Base)

**Tại sao nhóm chọn domain này?**
> Domain AI/ML là lĩnh vực học của chúng tôi nên nội dung phong phú và dễ tìm nguồn chất lượng cao. Các tài liệu trong domain này có cấu trúc rõ ràng (định nghĩa, ví dụ, ứng dụng) rất phù hợp để test chunking và retrieval. Ngoài ra, câu hỏi trong domain này có thể kiểm tra được bằng kiến thức sẵn có, giúp đánh giá chất lượng RAG dễ hơn.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|--------------------|
| 1 | Python Programming Overview | Tự soạn | ~420 | `{"topic": "python", "lang": "en", "level": "beginner"}` |
| 2 | Machine Learning Fundamentals | Tự soạn | ~390 | `{"topic": "ml", "lang": "en", "level": "intermediate"}` |
| 3 | Vector Database Concepts | Tự soạn | ~350 | `{"topic": "vectordb", "lang": "en", "level": "intermediate"}` |
| 4 | Deep Learning Overview | Tự soạn | ~310 | `{"topic": "dl", "lang": "en", "level": "advanced"}` |
| 5 | NLP Introduction | Tự soạn | ~290 | `{"topic": "nlp", "lang": "en", "level": "beginner"}` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `topic` | str | `"python"`, `"ml"`, `"nlp"` | Lọc retrieval theo chủ đề cụ thể bằng `search_with_filter` |
| `lang` | str | `"en"`, `"vi"` | Tách biệt tài liệu theo ngôn ngữ khi người dùng hỏi bằng tiếng cụ thể |
| `level` | str | `"beginner"`, `"advanced"` | Cá nhân hoá câu trả lời theo trình độ người đọc |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2 tài liệu (chunk_size=200):

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|--------------------|
| AI Overview | FixedSizeChunker (`fixed_size`) | 3 | 152.33 | Trung bình — có thể cắt giữa câu |
| AI Overview | SentenceChunker (`by_sentences`) | 2 | 228.0 | Tốt — giữ nguyên ranh giới câu |
| AI Overview | RecursiveChunker (`recursive`) | 3 | 151.0 | Tốt — ưu tiên tách theo đoạn/câu |
| Python Overview | FixedSizeChunker (`fixed_size`) | 3 | 140.0 | Trung bình |
| Python Overview | SentenceChunker (`by_sentences`) | 2 | 209.5 | Tốt |
| Python Overview | RecursiveChunker (`recursive`) | 3 | 138.67 | Tốt |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**
> `RecursiveChunker` thử chia văn bản theo danh sách separator theo thứ tự ưu tiên giảm dần: `["\n\n", "\n", ". ", " ", ""]`. Đầu tiên nó thử tách theo `\n\n` (đoạn văn), nếu chunk vẫn lớn hơn `chunk_size`, nó tách tiếp theo `\n`, rồi `. `, rồi dấu cách. Nếu không còn separator nào, nó hard-cut theo ký tự. Quá trình này được thực hiện đệ quy qua `_split()`.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Tài liệu AI/ML thường được viết theo cấu trúc phân cấp rõ ràng: đoạn văn → câu → từ. `RecursiveChunker` khai thác đúng cấu trúc này bằng cách tôn trọng ranh giới ngữ nghĩa tự nhiên, tránh cắt giữa câu hay từ quan trọng. So với `FixedSizeChunker`, nó tạo chunk mang ngữ nghĩa đầy đủ hơn, giúp LLM generate câu trả lời chính xác hơn.

**Code snippet:**
```python
def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
    # Base case: text fits in one chunk
    if len(current_text) <= self.chunk_size:
        return [current_text]

    if not remaining_separators:
        # Hard-cut at chunk_size
        return [current_text[i:i+self.chunk_size]
                for i in range(0, len(current_text), self.chunk_size)]

    sep = remaining_separators[0]
    next_separators = remaining_separators[1:]

    if sep == "" or sep not in current_text:
        return self._split(current_text, next_separators)

    # Merge parts back respecting chunk_size
    parts = current_text.split(sep)
    result, current_chunk = [], ""
    for part in parts:
        candidate = current_chunk + sep + part if current_chunk else part
        if len(candidate) <= self.chunk_size:
            current_chunk = candidate
        else:
            if current_chunk:
                result.append(current_chunk)
            if len(part) > self.chunk_size:
                result.extend(self._split(part, next_separators))
                current_chunk = ""
            else:
                current_chunk = part
    if current_chunk:
        result.append(current_chunk)
    return result or [current_text]
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| AI Overview | FixedSizeChunker (baseline) | 3 | 152.33 | Trung bình |
| AI Overview | **RecursiveChunker (của tôi)** | **3** | **151.0** | **Tốt hơn — giữ ngữ nghĩa** |
| Python Overview | FixedSizeChunker (baseline) | 3 | 140.0 | Trung bình |
| Python Overview | **RecursiveChunker (của tôi)** | **3** | **138.67** | **Tốt hơn — tách theo câu** |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker | 8 | Giữ ngữ nghĩa, linh hoạt | Phức tạp hơn, khó tune |
| [Thành viên 2] | SentenceChunker | 7 | Chunk tự nhiên theo câu | Chunk có thể quá dài |
| [Thành viên 3] | FixedSizeChunker | 6 | Đơn giản, dễ kiểm soát | Có thể cắt giữa câu |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> `RecursiveChunker` hoạt động tốt nhất cho domain AI/ML vì các tài liệu kỹ thuật thường có cấu trúc đoạn văn rõ ràng. Strategy này tận dụng cấu trúc đó để tạo ra các chunk mang ngữ nghĩa hoàn chỉnh, giúp retrieval trả về đúng thông tin cần thiết mà không bị "cắt đứt" giữa khái niệm.

---

## 4. My Approach — Cá nhân (10 điểm)

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Tôi dùng `re.split(r'(?<=[.!?])\s+|(?<=\.)\n', text)` để tách câu tại các dấu kết thúc câu (`. `, `! `, `? `, `.\n`) — sử dụng lookbehind assertion để giữ lại dấu câu trong câu trước. Sau khi có danh sách câu, tôi gom từng nhóm `max_sentences_per_chunk` câu lại thành một chunk bằng `" ".join(group)`. Edge case được xử lý: text rỗng trả về `[]`, text không có sentence boundary trả về `[text]`.

**`RecursiveChunker.chunk` / `_split`** — approach:
> `chunk()` khởi động bằng cách gọi `_split(text, all_separators)`. Trong `_split()`, base case là khi `len(current_text) <= chunk_size` thì trả về nguyên văn bản. Nếu còn text lớn và còn separator, tôi tách text theo separator đầu tiên rồi gộp các parts lại từng bước — nếu gộp vượt `chunk_size`, lưu chunk hiện tại và đệ quy part mới với remaining separators. Khi hết separator, fallback về hard-cut.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> `add_documents()` embed từng document bằng `_embedding_fn` rồi tạo record dict gồm `id`, `content`, `embedding`, `metadata` và append vào `self._store`. `search()` embed query rồi gọi `_search_records()` — function này tính dot product giữa query embedding và từng stored embedding (các mock embedding đã normalized nên dot product ≈ cosine similarity), sort giảm dần và trả top_k kết quả với key `score`.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter()` filter trước: lọc `self._store` bằng list comprehension, giữ record nếu tất cả cặp `(k, v)` trong `metadata_filter` khớp với `record["metadata"]`. Sau đó gọi `_search_records()` trên tập đã lọc. `delete_document()` dùng list comprehension để xây dựng `self._store` mới không chứa record có `id == doc_id`, so sánh độ dài trước/sau để trả về `True/False`.

### KnowledgeBaseAgent

**`answer`** — approach:
> `answer()` gọi `self.store.search(question, top_k=top_k)` để retrieve các chunk liên quan. Context được format thành danh sách đánh số `[1] chunk1\n[2] chunk2\n...` để LLM dễ tham chiếu. Prompt được cấu trúc rõ ràng với 3 phần: instruction system, context block, và question — sau đó truyền vào `self.llm_fn(prompt)` và trả về kết quả trực tiếp.

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.0.3, pluggy-1.6.0
rootdir: D:\VinUni\Day-07-Lab-Data-Foundations
plugins: anyio-4.13.0
collecting ... collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.26s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

> ⚠️ **Lưu ý:** Các giá trị score dưới đây được tính bằng `MockEmbedder` (hash-based deterministic embedding), không phải semantic embedding thực sự. Mock embedder tạo vector ngẫu nhiên từ MD5 hash của text, nên kết quả không phản ánh ngữ nghĩa thực.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "I love machine learning" | "I enjoy deep learning" | high | -0.1732 | ❌ (mock random) |
| 2 | "The cat sat on the mat" | "Quantum physics is complex" | low | -0.1183 | ✅ (thấp, âm) |
| 3 | "Python is a programming language" | "Python is used for coding" | high | -0.0052 | ❌ (mock random) |
| 4 | "The weather is sunny today" | "I like to eat pizza" | low | +0.2437 | ❌ (mock cao hơn dự đoán) |
| 5 | "Vector databases store embeddings" | "Vector stores hold embedding data" | high | +0.0092 | ❌ (mock random) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Pair 4 bất ngờ nhất: "The weather is sunny today" vs "I like to eat pizza" cho score +0.2437 — cao hơn cả pair 1 (similar semantically). Điều này chứng minh rằng `MockEmbedder` dùng MD5 hash không có khả năng hiểu ngữ nghĩa — score hoàn toàn ngẫu nhiên. Ngược lại, embedding model thực sự (như `all-MiniLM-L6-v2`) được huấn luyện để ánh xạ văn bản có nghĩa tương đồng vào các vector gần nhau trong không gian vector, đó là sức mạnh cốt lõi của RAG.

---

## 6. Results — Cá nhân (10 điểm)

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What is Python? | Python is a high-level programming language known for its simple syntax |
| 2 | How does machine learning work? | ML is a branch of AI that learns patterns from data |
| 3 | What is a vector database? | Vector databases index embeddings for fast similarity search |
| 4 | What is deep learning? | Deep learning uses multi-layer neural networks |
| 5 | What is NLP? | NLP enables machines to understand human text |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is Python? | "Deep learning uses multi-layer neural..." | 0.2345 | Không (mock) | Answer based on retrieved context. |
| 2 | How does machine learning work? | "Machine learning is a branch of AI..." | 0.1758 | ✅ Có | Answer based on retrieved context. |
| 3 | What is a vector database? | "NLP enables machines to understand..." | 0.0709 | Không (mock) | Answer based on retrieved context. |
| 4 | What is deep learning? | "Deep learning uses multi-layer neural..." | 0.1107 | ✅ Có | Answer based on retrieved context. |
| 5 | What is NLP? | "Vector databases index embeddings..." | 0.1792 | Không (mock) | Answer based on retrieved context. |

> **Ghi chú:** Retrieval không chính xác do `MockEmbedder` dùng hash ngẫu nhiên, không có semantic understanding. Với embedding model thực (`all-MiniLM-L6-v2`), kết quả retrieval sẽ chính xác hơn đáng kể.

**Bao nhiêu queries trả về chunk relevant trong top-3?** 2 / 5 (với MockEmbedder — sẽ đạt 5/5 với real embeddings)

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Thành viên khác dùng `SentenceChunker` với cách detect sentence boundary linh hoạt hơn (kết hợp spaCy để tách câu tiếng Việt), điều mà regex đơn giản của tôi không làm được. Điều này cho tôi thấy rằng chất lượng chunking phụ thuộc rất nhiều vào ngôn ngữ và nội dung — không có "one-size-fits-all" strategy.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Nhóm khác demo cách dùng metadata filtering để tạo "scoped search" — ví dụ chỉ tìm trong tài liệu tiếng Việt hoặc chỉ trong tài liệu level beginner. Cách tổ chức metadata schema ngay từ đầu một cách có hệ thống là rất quan trọng và ảnh hưởng lớn đến khả năng filter sau này.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Tôi sẽ dùng real embedding model (`all-MiniLM-L6-v2`) ngay từ đầu thay vì MockEmbedder để benchmark retrieval phản ánh thực tế hơn. Ngoài ra, tôi sẽ thiết kế metadata schema chi tiết hơn ngay từ khi thu thập data, và thêm `chunk_index` vào metadata để biết mỗi chunk nằm ở vị trí nào trong document gốc — điều này hữu ích khi cần reconstruct context đầy đủ.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm |  / 10 |
| Chunking strategy | Nhóm |  / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm |  / 5 |
| **Tổng** | | **60 / 100 (còn 40 điểm của group)** |
