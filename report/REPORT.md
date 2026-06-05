# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Quang Bảo
**MSSV:** 2A202600610
**Nhóm:** [Tên nhóm]
**Ngày:** 2026-06-05

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**

Hai text chunk có high cosine similarity khi vector embedding của chúng chỉ cùng hướng trong không gian vector — tức là nội dung và ngữ nghĩa của chúng tương đồng nhau, bất kể độ dài văn bản. Cosine similarity đo góc giữa hai vector, không đo khoảng cách tuyệt đối.

**Ví dụ HIGH similarity:**
- Sentence A: "Python is a high-level programming language used for data science."
- Sentence B: "Python is widely used in machine learning and software development."
- Tại sao tương đồng: Cả hai đều nói về Python trong bối cảnh lập trình/kỹ thuật, dùng nhiều từ khóa trùng lặp và cùng domain kỹ thuật.

**Ví dụ LOW similarity:**
- Sentence A: "Vector databases store embeddings for fast similarity search."
- Sentence B: "The recipe requires two cups of flour and one egg."
- Tại sao khác: Hai câu hoàn toàn khác domain — một câu về kỹ thuật phần mềm, một câu về nấu ăn. Không chia sẻ từ vựng hay khái niệm nào.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

Euclidean distance bị ảnh hưởng bởi magnitude của vector — một đoạn văn dài và một câu ngắn có cùng chủ đề sẽ cho Euclidean distance lớn dù ngữ nghĩa giống nhau. Cosine similarity chỉ đo góc giữa hai vector nên không bị ảnh hưởng bởi độ dài văn bản, phản ánh đúng sự tương đồng về ngữ nghĩa hơn.

---

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

Áp dụng công thức:
```
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
           = ceil((10,000 - 50) / (500 - 50))
           = ceil(9,950 / 450)
           = ceil(22.11)
           = 23 chunks
```

Xác minh: bước nhảy giữa các chunk = 500 - 50 = 450 ký tự. Chunk cuối bắt đầu tại vị trí 22 × 450 = 9,900 (< 10,000), kết thúc tại 10,400 nhưng bị giới hạn bởi cuối văn bản. Vậy **23 chunks**.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

```
num_chunks = ceil((10,000 - 100) / (500 - 100))
           = ceil(9,900 / 400)
           = ceil(24.75)
           = 25 chunks
```

Tăng overlap từ 50 lên 100 làm tăng số chunk từ 23 lên 25. Overlap lớn hơn có lợi khi câu trả lời nằm ở ranh giới giữa hai chunk — nếu overlap nhỏ, chunk có thể cắt đứt giữa câu và mất context quan trọng; overlap lớn đảm bảo thông tin tại biên giới xuất hiện ở ít nhất hai chunk, tăng khả năng retrieval tìm được chunk chứa đủ context.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** [Chờ nhóm thống nhất]

**Tại sao nhóm chọn domain này?**
> *[Điền sau khi họp nhóm]*

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

*[Điền sau khi có tài liệu nhóm và chạy ChunkingStrategyComparator]*

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Strategy Của Tôi

**Loại:** [Điền sau khi nhóm phân công strategy]

**Mô tả cách hoạt động:**
> *[Điền sau khi chọn strategy]*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *[Điền sau khi biết domain]*

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| | best baseline | | | |
| | **của tôi** | | | |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | | | | |
| [Tên] | | | | |
| [Tên] | | | | |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *[Điền sau khi so sánh kết quả nhóm]*

---

## 4. My Approach — Cá nhân (10 điểm)

### Chunking Functions

**`compute_similarity`** — approach:

Tính cosine similarity theo công thức `dot(a, b) / (||a|| × ||b||)`. Magnitude của mỗi vector tính bằng `math.sqrt(_dot(v, v))` — tái dùng `_dot()` có sẵn thay vì viết lại `sum(x**2 ...)`. Guard `if mag_a == 0.0 or mag_b == 0.0: return 0.0` đặt trước phép chia để tránh ZeroDivisionError khi gặp zero vector; đây là edge case bắt buộc theo docstring.

**`SentenceChunker.chunk`** — approach:

Dùng lookbehind regex `(?<=[.!?])\s+` để tách câu — lookbehind giữ dấu câu gắn với câu trước thay vì bỏ mất như khi split trực tiếp trên `". "`. Sau khi có danh sách câu, dùng `range(0, len(sentences), max_sentences_per_chunk)` để slice từng batch rồi `" ".join()` thành chunk. Edge case text không có dấu câu được xử lý tự nhiên: regex trả 1 phần tử, batch đó trở thành 1 chunk duy nhất.

**`RecursiveChunker.chunk` / `_split`** — approach:

`chunk()` chỉ là entry point gọi `_split(text, self.separators)`. Toàn bộ logic nằm ở `_split()` với 2 base case: `len(text) <= chunk_size` trả về ngay; `remaining_separators` rỗng trả về `[text]` dù text quá lớn (graceful fallback). Với separator `""` xử lý đặc biệt thành character-level split cố định. Bước quan trọng nhất là **merge back**: sau khi expand đệ quy ra nhiều piece nhỏ (ví dụ 200 "word" 4-ký-tự từ split theo `" "`), gộp liền kề lại miễn là `joined <= chunk_size` để tránh trả ra hàng trăm micro-chunk vô dụng.

---

### EmbeddingStore

**`add_documents` + `search`** — approach:

Mỗi `Document` được chuyển thành một record dict gồm 4 field: `id`, `content`, `embedding` (kết quả gọi `embedding_fn`), và `metadata` (metadata gốc cộng thêm `doc_id` để hỗ trợ delete sau này). Record được append vào `self._store` — list đơn giản trong RAM. `search()` embed query rồi tính dot product với từng record, sort descending, trả `top_k` đầu dưới dạng `{"content", "score", "metadata"}`.

**`search_with_filter` + `delete_document`** — approach:

`search_with_filter` dùng **filter-first**: lọc `self._store` giữ lại các record có metadata khớp toàn bộ key-value trong `metadata_filter` (dùng `all(...)`), sau đó mới chạy similarity search trên subset đó. Khi `filter=None` delegate thẳng cho `search()` để không duplicate code. `delete_document` lưu `before = len(self._store)`, dùng list comprehension lọc ra records có `r["id"] != doc_id`, trả `True` nếu size giảm — cách tiếp cận immutable tránh bug iterator invalidation.

---

### KnowledgeBaseAgent

**`answer`** — approach:

RAG pattern 3 bước: (1) `store.search(question, top_k)` lấy các chunk liên quan, (2) `"\n\n".join(c["content"] for c in chunks)` ghép thành context block, (3) format prompt `"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"` rồi gọi `llm_fn`. Đặt context trước câu hỏi là convention phổ biến để LLM "đọc" tài liệu trước khi trả lời; `"Answer:"` là cue kết thúc prompt để LLM biết bắt đầu generate.

---

### Test Results

```
============================= test session starts =============================
platform win32 -- Python 3.13.13, pytest-9.0.3, pluggy-1.6.0
rootdir: 2A202600610-Vũ Quang Bảo
collected 42 items

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

============================= 42 passed in 0.40s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

Chạy với `_mock_embed` (MockEmbedder, 64 chiều, hash-based). Dự đoán dựa trên ngữ nghĩa câu trước khi biết kết quả.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a programming language. | Python is used for data science and machine learning. | high | -0.0065 | ❌ |
| 2 | The cat sat on the mat. | A feline rested on a rug. | high | 0.0584 | ❌ |
| 3 | Vector databases store embeddings for fast similarity search. | I love eating pizza on Sundays. | low | 0.1766 | ❌ |
| 4 | Machine learning uses algorithms to learn from data. | Deep learning is a subset of machine learning using neural networks. | high | -0.1741 | ❌ |
| 5 | The weather is sunny today. | Stock prices rose by 3% this morning. | low | -0.1443 | ✅ |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**

Bất ngờ nhất là Pair 3: cặp câu hoàn toàn khác domain ("vector database" vs "pizza") lại có score cao nhất (0.1766), trong khi Pair 1 và 4 — hai câu rõ ràng cùng chủ đề Python/ML — lại cho score âm. Điều này xảy ra vì `MockEmbedder` tạo vector từ MD5 hash của chuỗi ký tự, không từ nghĩa của từ — kết quả hoàn toàn ngẫu nhiên về mặt ngữ nghĩa. Đây là minh chứng quan trọng: chất lượng retrieval phụ thuộc trực tiếp vào chất lượng embedding backend; mock embedder chỉ đủ để kiểm tra tính đúng đắn của code (API, data flow), không phản ánh được semantic similarity thực sự. Với một embedder được train để biểu diễn ngữ nghĩa (như `sentence-transformers`), các cặp cùng chủ đề (Pair 1, 2, 4) sẽ cho score cao hơn đáng kể và các cặp khác domain (Pair 3, 5) sẽ cho score thấp hơn — đúng với trực giác ban đầu.

---

## 6. Results — Cá nhân (10 điểm)

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *[Điền sau demo]*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *[Điền sau demo]*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *[Điền sau demo]*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **50 / 100** *(+50 chờ nhóm)* |
