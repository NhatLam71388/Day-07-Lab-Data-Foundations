# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Vũ Quang Bảo
**MSSV:** 2A202600610
**Nhóm:** VinUni Academic Policies — 6 thành viên (Member 3)
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

**Domain:** Quy chế học vụ & Quy trình/Tuyển sinh Đại học — VinUniversity (tiếng Việt)

**Tại sao nhóm chọn domain này?**
Tài liệu học vụ VinUniversity là thông tin mà sinh viên cần tra cứu thường xuyên nhưng phức tạp và phân tán trên nhiều văn bản thuộc nhiều phòng ban khác nhau (Registrar, Admissions, Finance). Đây là use case RAG thực tế và có thể đánh giá retrieval quality rõ ràng vì mỗi câu hỏi có đáp án chính xác trong tài liệu. Domain này đặc biệt phù hợp để test metadata filtering vì mỗi phòng ban phụ trách một loại quy chế khác nhau, dễ nhầm lẫn nếu ingestion không cẩn thận.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán | Owner |
|---|--------------|-------|----------|-----------------|-------|
| 1 | canh_bao_hoc_vu_quy_che.md | policy.vinuni.edu.vn | 6,097 | category=academic_warning, doc_type=policy, department=registrar | Member 1 — Trần Gia Huy |
| 2 | dang_ky_mon_hoc_sop.md | registrar.vinuni.edu.vn | 4,350 | category=course_registration, doc_type=sop, department=registrar | Member 2 |
| 3 | tuyen_sinh_faq.md | admissions.vinuni.edu.vn | 21,525 | category=admissions, doc_type=faq, department=admissions | **Member 3 — Vũ Quang Bảo** |
| 4 | hoc_phi_huong_dan.md | finance.vinuni.edu.vn | 21,340 | category=tuition_finance, doc_type=guideline, department=finance | Member 4 |
| 5 | khao_thi_quy_che.md | policy.vinuni.edu.vn | 6,335 | category=examination, doc_type=policy, department=registrar | Member 5 |
| 6 | tot_nghiep_quy_trinh.md | registrar.vinuni.edu.vn | 6,378 | category=graduation, doc_type=procedure, department=registrar | Member 6 |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| category | str | academic_warning, examination | Filter theo chủ đề — tránh nhầm quy chế học vụ với quy chế thi cử |
| doc_type | str | policy, sop, faq, procedure | Phân biệt loại tài liệu — FAQ cần cách chunking khác policy |
| department | str | registrar, admissions, finance | Filter theo phòng ban — câu hỏi học phí không cần search file Registrar |
| owner | str | member_3 | Gắn trách nhiệm chuẩn bị tài liệu theo implementation plan nhóm |
| doc_id | str | tuyen_sinh_faq | Gom hoặc xóa toàn bộ chunk thuộc cùng tài liệu khi cần update |
| chunk_index | int | 12 | Tái tạo context lân cận khi cần đọc thêm chunk trước/sau |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Tài liệu: `data/tuyen_sinh_faq.md` — 21,525 ký tự, crawl từ admissions.vinuni.edu.vn, domain tuyển sinh VinUni.

Chạy `ChunkingStrategyComparator.compare(text, chunk_size=200)`:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| tuyen_sinh_faq.md | FixedSizeChunker (`fixed_size`, size=200) | 144 | 199.1 | Không — cắt giữa câu/Q&A |
| tuyen_sinh_faq.md | SentenceChunker (`by_sentences`, max=3) | 53 | 403.8 | Tốt — giữ trọn câu |
| tuyen_sinh_faq.md | RecursiveChunker (`recursive`, size=200) | 146 | 145.8 | Tốt — tôn trọng đoạn văn |

### Strategy Của Tôi

**Loại:** `SentenceChunker(max_sentences_per_chunk=2)`

**Mô tả cách hoạt động:**

Dùng lookbehind regex `(?<=[.!?])\s+` để tách văn bản thành danh sách câu — dấu chấm câu (.!?) được giữ nguyên gắn với câu trước thay vì bị bỏ. Sau đó gom từng 2 câu liên tiếp thành một chunk bằng `" ".join()`. Kết quả: 79 chunks, avg 270.6 ký tự/chunk.

**Tại sao tôi chọn strategy này cho domain tuyển sinh VinUni?**

Dữ liệu tuyển sinh gồm nhiều cặp Q&A ngắn và đoạn điều kiện/yêu cầu riêng lẻ. Mỗi câu thường mang một ý hoàn chỉnh (ví dụ: "IELTS tối thiểu 6.5." hay "Học phí khoảng 530 triệu VND/năm."). Gom 2 câu thành 1 chunk cân bằng giữa: đủ context để retrieval tìm ra câu trả lời đầy đủ, và đủ nhỏ để không bị pha loãng khi embed. FixedSizeChunker (199 ký tự) hay cắt giữa câu hỏi và câu trả lời — kịch bản tệ nhất với Q&A. RecursiveChunker tạo 146 chunk quá nhỏ (avg 145 ký tự) dễ mất context yêu cầu nhiều điều kiện liên quan.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| tuyen_sinh_faq.md | SentenceChunker (`by_sentences`, max=3) | 53 | 403.8 | Tốt nhưng chunk hơi lớn |
| tuyen_sinh_faq.md | **SentenceChunker(max=2) — của tôi** | **79** | **270.6** | **Tốt hơn — chunk cân bằng** |

Strategy của tôi tạo chunk nhỏ hơn baseline `by_sentences` (270 vs 403 ký tự) — phù hợp hơn với Q&A ngắn của domain tuyển sinh, tránh nhồi nhiều câu hỏi không liên quan vào cùng một chunk.

### So Sánh Với Thành Viên Khác

| Thành viên | Tài liệu | Strategy | Retrieval Score | Điểm mạnh | Điểm yếu |
|-----------|----------|----------|----------------|-----------|----------|
| Member 1 — Trần Gia Huy | canh_bao_hoc_vu_quy_che | **MarkdownHeadingChunker** (custom) | 9/10 | Giữ trọn từng mục quy chế, metadata rõ theo heading | FAQ không tách tốt nếu dùng bold thay vì heading |
| Member 2 | dang_ky_mon_hoc_sop | SentenceChunker(max=5) | 8/10 | Hợp quy trình dài, đọc tự nhiên | Có thể tách tên bước khỏi nội dung bước |
| **Member 3 — Tôi** | tuyen_sinh_faq | **SentenceChunker(max=2)** | 7/10 | Hợp Q&A ngắn, chunk cân bằng | Không overlap — có thể mất context ranh giới |
| Member 4 | hoc_phi_huong_dan | RecursiveChunker(size=300) | 8/10 | Tìm nhanh thông tin nhỏ về học phí | Hơi vụn với các điều kiện tài chính phức tạp dài |
| Member 5 | khao_thi_quy_che | RecursiveChunker(size=800) | 8/10 | Giữ trọn quy chế khảo thí phức tạp | Chunk dài, embedding bị pha loãng nhiều ý |
| Member 6 | tot_nghiep_quy_trinh | FixedSizeChunker(size=400) | 6/10 | Baseline dễ so sánh, kích thước nhất quán | Cắt ngang mục quy trình tốt nghiệp |

**Strategy nào tốt nhất cho domain này? Tại sao?**

`MarkdownHeadingChunker` của Member 1 là tốt nhất khi tài liệu được viết bằng Markdown có heading cấu trúc rõ ràng (canh_bao, hoc_phi, khao_thi, tot_nghiep). Lý do: các quy định học vụ được tổ chức theo mục, và câu hỏi thường hỏi theo đúng phạm vi một mục. Tuy nhiên với `tuyen_sinh_faq.md` — file FAQ dùng **bold question** thay vì heading — strategy này tạo ra 1 chunk duy nhất 4,439 ký tự, hoàn toàn không phù hợp. Với domain có loại tài liệu hỗn hợp, cần kết hợp: heading-based cho policy/procedure/sop, sentence-based cho FAQ.

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

**Setup thực tế:**
- Embedder: `LocalEmbedder` — `all-MiniLM-L6-v2` (Sentence Transformers, chạy local)
- Chunker: `SentenceChunker(max_sentences_per_chunk=2)`
- Tổng: 215 chunks từ 6 tài liệu VinUni
- LLM: không có API key → retrieval-only mode

### Benchmark Queries & Gold Answers

| # | Query | Gold Answer (từ tài liệu gốc) |
|---|-------|-------------------------------|
| 1 | Quy trình khiếu nại Quyết định Buộc thôi học: thời hạn, mẫu đơn, hội đồng? | **10 ngày làm việc** kể từ ngày QĐ công bố; mẫu **FRM02** (Student Misconduct/Academic Appeal Form); **Hội đồng Kỷ luật Sinh viên (SDC)** phúc quyết trong 15 ngày làm việc |
| 2 | Tín chỉ tối thiểu/tối đa học kỳ chính? Điều kiện overload? | Tài liệu không quy định rõ min/max tín chỉ chuẩn; điều kiện overload: **cGPA học kỳ trước ≥ 3.50** + phê duyệt bằng văn bản từ **Viện trưởng (Dean)** |
| 3 | Yêu cầu tiếng Anh từ 2026? Còn Placement Test và Pathway không? | Từ 2026 bắt buộc **IELTS ≥ 6.5 Overall** (không kỹ năng nào dưới 6.0) khi nhập học; **không còn** tổ chức Placement Test và Khóa Tiếng Anh Dự bị |
| 4 | cGPA tối thiểu giữ Học bổng Tài năng? Xử lý tự động nếu vi phạm? | cGPA lũy kế tối thiểu **2.50/4.00** hàng năm; nếu vi phạm: Hội đồng Học bổng điều chỉnh giảm bậc học bổng tại kỳ đánh giá Annual Review |
| 5 | Môn thực hành/lâm sàng: quy định hoãn thi/thi bù và tính điểm đạt/trượt? | **Không áp dụng** hoãn thi/thi bù tự động; vắng không có lý do cấp cứu đặc biệt = **điểm 0 ngay**; phải đạt "Đạt" ở **100% năng lực cốt lõi**; "Không đạt" bất kỳ kỹ năng then chốt nào = **điểm F mặc định** |

### Kết Quả Retrieval Chi Tiết

**Query 1 — Khiếu nại Buộc thôi học**

| Rank | Score | Source | Nội dung (preview) | Relevant? |
|------|-------|--------|---------------------|-----------|
| 1 | 0.8010 | canh_bao_hoc_vu_quy_che | "Vượt quá thời gian đào tạo tối đa: Sinh viên không hoàn thành trong thời gian tối đa..." | ❌ (về điều kiện buộc thôi, không phải quy trình khiếu nại) |
| 2 | 0.7848 | tot_nghiep_quy_trinh | "Thành phần Hội đồng bắt buộc gồm: Hiệu trưởng (Chủ trì hội đồng), Phó Hiệu trưởng Học thuật..." | ⚠️ Một phần (về hội đồng, nhưng là hội đồng tốt nghiệp, không phải SDC) |
| 3 | 0.7827 | canh_bao_hoc_vu_quy_che | "Thời hạn nộp đơn: Tối đa trong vòng 10 ngày làm việc kể từ ngày Quyết định Buộc thôi học được công bố..." | ✅ Trực tiếp — đúng câu trả lời |

**Relevant trong top-3:** 1/3 trực tiếp, 1/3 một phần. Top-1 bị nhiễu vì câu hỏi dùng "Buộc thôi học" nhưng chunk về điều kiện buộc thôi được embed gần với câu hỏi về quy trình. Đây là trường hợp **semantic confusion** — model không phân biệt được "điều kiện buộc thôi" vs "quy trình khiếu nại buộc thôi".

---

**Query 2 — Số tín chỉ đăng ký**

| Rank | Score | Source | Nội dung (preview) | Relevant? |
|------|-------|--------|---------------------|-----------|
| 1 | 0.7674 | tuyen_sinh_faq | "Với trao đổi ngắn hạn không phát sinh học phí với trường đối tác, chỉ đóng học phí tại VinUni..." | ❌ (về trao đổi quốc tế) |
| 2 | 0.7606 | tuyen_sinh_faq | "Ngoài ra sinh viên cần có kỷ luật tốt và không vi phạm nghiêm trọng các quy định của trường..." | ❌ (về điều kiện học bổng) |
| 3 | 0.7581 | khao_thi_quy_che | "Nếu sinh viên bị đánh giá là 'Không đạt' ở bất kỳ một kỹ năng thực hành then chốt nào..." | ❌ (về đánh giá thực hành) |

**Relevant trong top-3:** 0/3. **Retrieval failure hoàn toàn.** Thông tin về overload (cGPA ≥ 3.50, Dean approval) nằm trong `dang_ky_mon_hoc_sop.md` nhưng không được retrieve. Nguyên nhân: câu hỏi dùng từ "tín chỉ tối thiểu/tối đa" — model embed câu hỏi gần với các chunk về học bổng (cũng dùng "điều kiện", "sinh viên") hơn là chunk về đăng ký môn học.

---

**Query 3 — Yêu cầu tiếng Anh từ 2026**

| Rank | Score | Source | Nội dung (preview) | Relevant? |
|------|-------|--------|---------------------|-----------|
| 1 | 0.7787 | khao_thi_quy_che | "Sinh viên nhận điểm F bắt buộc phải thực hiện thủ tục đăng ký học lại hoàn toàn..." | ❌ (về học lại) |
| 2 | 0.7460 | khao_thi_quy_che | "Điểm 'I' này không ảnh hưởng đến cGPA hiện tại. Sinh viên có nghĩa vụ phải tham gia làm bài thi bù..." | ❌ (về thi bù) |
| 3 | 0.7405 | tuyen_sinh_faq | "VinUni có lớp bồi dưỡng tiếng Anh cho sinh viên chưa đáp ứng điều kiện không? Không. Kể từ năm 2026, VinUni yêu cầu bắt buộc IELTS 6.5..." | ✅ Trực tiếp |

**Relevant trong top-3:** 1/3. Chunk đúng lọt vào Top-3 nhưng không phải Top-1. Model bị nhiễu bởi các từ "yêu cầu", "năm 2026", "tân sinh viên" — có nhiều chunk về các quy định khác cũng dùng từ "quy định", "sinh viên" dẫn đến false positives.

---

**Query 4 — cGPA giữ Học bổng Tài năng**

| Rank | Score | Source | Nội dung (preview) | Relevant? |
|------|-------|--------|---------------------|-----------|
| 1 | 0.7838 | tuyen_sinh_faq | "Ngoài ra sinh viên cần có kỷ luật tốt và không vi phạm nghiêm trọng các quy định của trường. VinUni xem xét lại kết quả mỗi năm..." | ⚠️ Một phần (đề cập review hàng năm nhưng không có số 2.50) |
| 2 | 0.7762 | tuyen_sinh_faq | "Nếu ứng viên phù hợp hơn với chương trình khác, VinUni có thể giới thiệu chương trình đó. Học bổng: Ứng viên không cần nộp đơn xin học bổng..." | ❌ (về tuyển sinh, không phải duy trì học bổng) |
| 3 | 0.7704 | tuyen_sinh_faq | "Học bổng Đặc biệt được cộng dồn gồm Học bổng đặc thù Ngành 5%..." | ❌ (về cộng dồn học bổng) |

**Relevant trong top-3:** 1/3 một phần. Thông tin cụ thể (cGPA ≥ 2.50, Annual Review, hình thức xử lý) nằm trong `hoc_phi_huong_dan.md` nhưng không được retrieve — thông tin bị phân tán qua 2 tài liệu (tuyen_sinh_faq và hoc_phi_huong_dan).

---

**Query 5 — Môn thực hành/lâm sàng: hoãn thi và tính điểm**

| Rank | Score | Source | Nội dung (preview) | Relevant? |
|------|-------|--------|---------------------|-----------|
| 1 | 0.7927 | khao_thi_quy_che | "Nếu sinh viên bị đánh giá là 'Không đạt' ở bất kỳ một kỹ năng thực hành then chốt nào, điểm tổng kết môn học sẽ bị tính là F mặc định..." | ✅ Trực tiếp |
| 2 | 0.7906 | canh_bao_hoc_vu_quy_che | "Hội đồng sẽ tổ chức phiên họp phúc quyết trong vòng 15 ngày làm việc kể từ ngày nhận đơn khiếu nại..." | ❌ (về hội đồng kỷ luật) |
| 3 | 0.7826 | tot_nghiep_quy_trinh | "Thành phần Hội đồng bắt buộc gồm: Hiệu trưởng..." | ❌ (về hội đồng tốt nghiệp) |

**Relevant trong top-3:** 1/3. Top-1 đúng và có score cao nhất — trường hợp retrieval tốt nhất trong 5 query. Tuy nhiên Top-2 và Top-3 bị nhiễu bởi từ "hội đồng" trong câu hỏi ("hội đồng đánh giá lâm sàng").

---

### Tổng Kết Retrieval

| Query | Relevant trong top-3 | Top-1 đúng? | Ghi chú |
|-------|----------------------|-------------|---------|
| Q1 — Khiếu nại buộc thôi | 1/3 trực tiếp (Top-3) | ❌ | Top-1 bị nhiễu: semantic confusion "điều kiện" vs "quy trình" |
| Q2 — Tín chỉ đăng ký | 0/3 | ❌ | Retrieval failure — info trong dang_ky file bị miss hoàn toàn |
| Q3 — Tiếng Anh 2026 | 1/3 (Top-3) | ❌ | Đúng vào Top-3 nhưng bị đẩy xuống |
| Q4 — cGPA học bổng | 1/3 một phần | ❌ | Info phân tán 2 file; số 2.50 không xuất hiện trong retrieved chunk |
| Q5 — Thực hành lâm sàng | 1/3 (Top-1) | ✅ | Retrieval tốt nhất — từ khóa kỹ thuật đặc thù rõ ràng |

**Bao nhiêu queries trả về chunk relevant trong top-3:** 4/5 có ít nhất 1 chunk relevant, nhưng chỉ 1/5 có Top-1 chính xác.

---

## 7. What I Learned (5 điểm — Demo)

**Phân tích failure mode chính:**

Dù dùng semantic embedder (all-MiniLM-L6-v2) thay vì TF-IDF, retrieval vẫn thất bại ở Q2 và không ổn định ở Q1, Q3, Q4 vì:

1. **Cross-document information split (Q2, Q4):** Thông tin nằm ở file khác với file mà câu hỏi "gợi" về mặt từ vựng. Model embed "tín chỉ đăng ký" gần với các chunk về học bổng hơn là với file `dang_ky_mon_hoc_sop.md` — vì file đó nói về thao tác SIS, không nói về con số tín chỉ cụ thể trong tài liệu này.

2. **Semantic confusion (Q1):** Câu hỏi "quy trình khiếu nại Buộc thôi học" được embed gần với "điều kiện Buộc thôi học" vì hai chủ đề dùng chung nhiều từ khóa (buộc thôi học, quyết định, sinh viên). Cần thiết kế câu hỏi benchmark cụ thể hơn ("mẫu đơn FRM02" thay vì "mẫu đơn nào").

3. **Model không biết tiếng Việt tốt (Q3):** `all-MiniLM-L6-v2` được train chủ yếu trên tiếng Anh — embedding chất lượng thấp hơn cho tiếng Việt, dẫn đến ranking không ổn định. Cần dùng multilingual model như `paraphrase-multilingual-MiniLM-L12-v2`.

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**

Member 1 (Trần Gia Huy) dùng `MarkdownHeadingChunker` — cắt theo heading `#`, `##`, `###` thay vì cắt theo câu hay ký tự. Điều này tôi chưa nghĩ đến: khi tài liệu đã có cấu trúc heading rõ ràng, tốt nhất là tôn trọng cấu trúc đó thay vì cắt nhỏ hơn. Kết quả: 35 chunks với score 9/10, retrieval 5/5 queries đều relevant. So với approach của tôi (79 chunks, 1/5 top-1 đúng), heading-based rõ ràng chiếm ưu thế với domain quy chế văn bản có Markdown heading.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**

Tầm quan trọng của việc thiết kế **metadata schema trước khi ingest**: Member 1 đã nghĩ trước về `applies_to=practical_courses` cho các chunk quy chế thực hành — field này cho phép dùng `search_with_filter` để tách biệt quy chế thi thực hành khỏi quy chế thi lý thuyết. Đây là kiểu "metadata engineering" mà tôi đã bỏ qua — tôi chỉ thêm metadata mô tả nguồn, không thêm metadata mô tả phạm vi áp dụng.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**

Ba thay đổi chính:
1. **Embedder đa ngữ:** Thay `all-MiniLM-L6-v2` bằng `paraphrase-multilingual-MiniLM-L12-v2` — được train trên tiếng Việt, embedding chất lượng cao hơn cho Q&A tiếng Việt.
2. **Metadata có `applies_to`:** Thêm field `applies_to` (ví dụ: `practical_courses`, `undergraduate`, `medicine`) để dùng `search_with_filter` thay vì search toàn bộ 215 chunks — giảm nhiễu đáng kể cho các query có context cụ thể.
3. **Hybrid chunker cho FAQ:** File `tuyen_sinh_faq.md` nên dùng chunker tách theo Q&A pair (split tại `**Q:**`) thay vì SentenceChunker — mỗi chunk chứa đúng 1 câu hỏi + câu trả lời hoàn chỉnh, không bị cắt đứt giữa Q và A.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 *(5 queries với kết quả thật, phân tích failure mode đầy đủ)* |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **58 / 100** *(+42 chờ nhóm)* |
