# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Độ tương đồng cosine cao nghĩa là vector biểu diễn của hai đoạn văn bản hướng về cùng một phía trong không gian nhiều chiều. Về mặt ngữ nghĩa, điều này thể hiện hai văn bản có độ tương đồng ngữ nghĩa cao (nói về cùng một chủ đề, ý nghĩa tương tự nhau) bất chấp sự khác biệt về độ dài hoặc cách diễn đạt.

**Ví dụ HIGH similarity:**
- Sentence A: "The weather is very sunny and hot today."
- Sentence B: "It is a warm and bright day outside."
- Tại sao tương đồng: Cả hai câu đều diễn đạt một ý chung là thời tiết ấm áp, đầy nắng và sáng sủa, do đó các biểu diễn ngữ nghĩa của chúng sẽ rất gần nhau.

**Ví dụ LOW similarity:**
- Sentence A: "Python is a popular programming language."
- Sentence B: "My favorite dessert is apple pie."
- Tại sao khác: Câu thứ nhất nói về chủ đề công nghệ/lập trình, còn câu thứ hai nói về chủ đề ẩm thực. Hai câu này hoàn toàn không có mối liên hệ ngữ nghĩa nào với nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Vì cosine similarity chỉ đo góc giữa hai vector (hướng ngữ nghĩa) mà không phụ thuộc vào độ dài (độ lớn) của vector đó. Đối với văn bản có độ dài khác nhau nhiều, khoảng cách Euclidean sẽ rất lớn mặc dù chúng nói cùng một chủ đề (vector dài hơn sẽ ở xa gốc tọa độ hơn), trong khi cosine similarity vẫn giữ nguyên giá trị cao.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = ceil(22.111...) = 23`
> *Đáp án:* 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Số lượng chunks sẽ tăng lên thành 25 (vì `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = ceil(24.75) = 25`). Chúng ta muốn overlap nhiều hơn để đảm bảo các câu hoặc ngữ cảnh không bị cắt cụt ở biên của các chunk, duy trì tính liên kết thông tin giữa các chunk liên tiếp giúp bộ retrieval hoạt động tốt hơn và LLM dễ hiểu trọn vẹn ngữ cảnh.

---

## 2. Document Selection — Nhóm (10 điểm)

<!-- HƯỚNG DẪN: Nhóm thống nhất chọn 1 domain chung, chuẩn bị 5-10 tài liệu (.txt/.md) bỏ vào thư mục data/ và thiết kế metadata schema -->

### Domain & Lý Do Chọn

**Domain:** [NHÓM ĐIỀN: Ví dụ Customer support FAQ / Vietnamese law / Cooking recipes...]

**Tại sao nhóm chọn domain này?**
> *NHÓM ĐIỀN: Viết 2-3 câu giải thích lý do lựa chọn domain này và ý nghĩa thực tiễn của nó.*

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | [Tên tài liệu 1] | [Nguồn] | [Số ký tự] | [Ví dụ: category=FAQ, date=2026] |
| 2 | [Tên tài liệu 2] | [Nguồn] | [Số ký tự] | [Ví dụ: category=SOP, date=2026] |
| 3 | [Tên tài liệu 3] | [Nguồn] | [Số ký tự] | [Ví dụ: category=FAQ, date=2026] |
| 4 | [Tên tài liệu 4] | [Nguồn] | [Số ký tự] | [Ví dụ: category=SOP, date=2026] |
| 5 | [Tên tài liệu 5] | [Nguồn] | [Số ký tự] | [Ví dụ: category=FAQ, date=2026] |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| [Ví dụ: category] | [String] | "FAQ" | Dùng để phân loại loại tài liệu và lọc khi tìm kiếm |
| [Ví dụ: date] | [String] | "2026-06-05" | Dùng để cập nhật hoặc lọc các văn bản mới nhất |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2 tài liệu mẫu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| `python_intro.txt` | FixedSizeChunker (`fixed_size`) | 13 | 195.69 | Không (cắt ký tự ngẫu nhiên, dễ chia đôi từ/câu) |
| `python_intro.txt` | SentenceChunker (`by_sentences`) | 5 | 387.40 | Có (giữ nguyên các câu trọn vẹn) |
| `python_intro.txt` | RecursiveChunker (`recursive`) | 12 | 160.08 | Khá tốt (ưu tiên giữ đoạn và câu cùng nhau) |
| `vector_store_notes.md` | FixedSizeChunker (`fixed_size`) | 14 | 198.07 | Không (cắt ký tự ngẫu nhiên, dễ chia đôi từ/câu) |
| `vector_store_notes.md` | SentenceChunker (`by_sentences`) | 8 | 264.12 | Có (giữ nguyên các câu trọn vẹn) |
| `vector_store_notes.md` | RecursiveChunker (`recursive`) | 15 | 139.67 | Khá tốt (ưu tiên giữ đoạn và câu cùng nhau) |

### Strategy Của Tôi

**Loại:** [CÁ NHÂN ĐIỀN: FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy]

**Mô tả cách hoạt động:**
> *CÁ NHÂN ĐIỀN: Viết 3-4 câu giải thích strategy chunk hoạt động thế nào? Dựa trên dấu hiệu phân tách gì? Quy mô chunk_size/overlap ra sao?*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *CÁ NHÂN ĐIỀN: Viết 2-3 câu: domain có đặc trưng hoặc pattern gì (ví dụ: chia theo Q&A, chia theo mục lục,...) mà strategy này có thể khai thác tối ưu?*

**Code snippet (nếu custom):**
```python
# CÁ NHÂN ĐIỀN: Paste implementation của custom chunker tại đây (nếu có)
```

### So Sánh: Strategy của tôi vs Baseline

<!-- HƯỚNG DẪN: Chạy thử nghiệm strategy của bạn so với baseline tốt nhất trên bộ tài liệu của nhóm -->

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| [Nhóm doc] | best baseline | [Số lượng] | [Độ dài TB] | [Đánh giá nhanh chất lượng] |
| [Nhóm doc] | **của tôi** | [Số lượng] | [Độ dài TB] | [Đánh giá nhanh chất lượng] |

### So Sánh Với Thành Viên Khác

<!-- HƯỚNG DẪN: So sánh kết quả chạy thử nghiệm của bạn với các thành viên khác trong nhóm sử dụng các strategy khác nhau -->

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | [Strategy của tôi] | [Điểm] | [Đặc điểm nổi bật] | [Hạn chế nếu có] |
| [Thành viên 2] | [Strategy 2] | [Điểm] | [Đặc điểm nổi bật] | [Hạn chế nếu có] |
| [Thành viên 3] | [Strategy 3] | [Điểm] | [Đặc điểm nổi bật] | [Hạn chế nếu có] |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *NHÓM THẢO LUẬN: Viết 2-3 câu tổng kết sau khi thảo luận nhóm.*

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Sử dụng biểu thức chính quy `re.split` với pattern `r'(\. |\! |\? |\.\n)'` giúp phân tách văn bản thành các câu mà vẫn giữ lại dấu câu biên của chúng. Sau đó, ghép cặp phần nội dung và dấu câu lại, lọc bỏ các chuỗi rỗng và gom nhóm các câu thành các chunk có số lượng câu tối đa là `max_sentences_per_chunk` trước khi gọi `.strip()` loại bỏ khoảng trắng dư.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Thực hiện thuật toán đệ quy duyệt qua danh sách các dấu phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Base case là khi độ dài văn bản hiện tại nhỏ hơn hoặc bằng `chunk_size` (trả về văn bản đó) hoặc không còn dấu phân cách nào hợp lệ (thực hiện cắt nhỏ văn bản theo độ dài `chunk_size`). Với mỗi dấu phân cách có trong văn bản, ta split, đệ quy chia nhỏ các phần con lớn hơn `chunk_size` rồi thực hiện gom các phần con này lại một cách tối ưu.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Tích hợp song song hai chế độ lưu trữ: sử dụng ChromaDB collection (nếu cài đặt thư viện) và in-memory list fallback (`self._store`). Khi tìm kiếm (`search`), ta tính tích vô hướng (dot product) giữa vector câu truy vấn với tất cả vector tài liệu đã lưu (đối với in-memory) hoặc gọi hàm query của ChromaDB, sau đó sắp xếp kết quả giảm dần theo score và lấy top_k tài liệu.

**`search_with_filter` + `delete_document`** — approach:
> Thực hiện pre-filtering (lọc trước) danh sách các tài liệu khớp với tất cả điều kiện của `metadata_filter` rồi mới tiến hành tìm kiếm tương đồng trên các tài liệu đã lọc đó (in-memory) hoặc truyền trực tiếp tham số `where` vào ChromaDB query. Để xóa tài liệu (`delete_document`), ta xóa các bản ghi có `metadata['doc_id'] == doc_id` khỏi `self._store` hoặc gọi hàm `.delete(where={"doc_id": doc_id})` của ChromaDB.

### KnowledgeBaseAgent

**`answer`** — approach:
> Áp dụng mô hình RAG tiêu chuẩn: Đầu tiên, truy vấn top_k tài liệu tương đồng nhất từ `EmbeddingStore`. Sau đó ghép nối nội dung các chunk này lại làm ngữ cảnh (context) và đưa vào cấu trúc prompt có dạng `Context:\n{context}\n\nQuestion: {question}\nAnswer:`. Cuối cùng, chuyển tiếp prompt này cho hàm LLM (`self.llm_fn`) để sinh ra câu trả lời.

### Test Results

```text
============================= test session starts =============================
platform win32 -- Python 3.11.3, pytest-9.0.3, pluggy-1.6.0 -- C:\Users\Dell\AppData\Local\Programs\Python\Python311\python.exe
cachedir: .pytest_cache
rootdir: D:\AI_20K\Day-07-Lab-Data-Foundations
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

============================= 42 passed in 0.08s ==============================
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "The dog chased the cat up the tree." | "A dog ran after a cat up the tree." | High | 0.1285 | Đúng |
| 2 | "The weather is extremely hot today." | "It is a very warm and sunny day." | High | 0.0909 | Sai |
| 3 | "I love coding in Python." | "I absolutely hate programming in Python." | Low | 0.1055 | Sai |
| 4 | "The bank of the river is muddy." | "I went to the bank to deposit some money." | Low | 0.0535 | Đúng |
| 5 | "Deep learning models are based on neural networks." | "Making a chocolate cake requires sugar and flour." | Low | -0.1352 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả bất ngờ nhất là cặp câu trái nghĩa (Cặp 3) lại có điểm tương đồng cosine (0.1055) cao hơn cả cặp câu đồng nghĩa (Cặp 2 - 0.0909). Điều này xảy ra do chúng ta đang sử dụng `MockEmbedder` (tạo vector giả lập bằng mã hóa MD5 băm chuỗi văn bản thành số giả ngẫu nhiên) vốn hoàn toàn không thể hiểu ngữ nghĩa thật sự. Để biểu diễn được ngữ nghĩa thực của văn bản, chúng ta phải sử dụng các mô hình ngôn ngữ lớn được huấn luyện thực tế (như OpenAI hay sentence-transformers) để các vector có thể ánh xạ các từ đồng nghĩa/trái nghĩa vào các khoảng cách tương thích trong không gian.

---

## 6. Results — Cá nhân (10 điểm)

<!-- HƯỚNG DẪN: Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn (phải trùng với các thành viên khác trong nhóm để tiện so sánh) -->

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | [Query 1 của nhóm] | [Gold Answer tương ứng] |
| 2 | [Query 2 của nhóm] | [Gold Answer tương ứng] |
| 3 | [Query 3 của nhóm] | [Gold Answer tương ứng] |
| 4 | [Query 4 của nhóm] | [Gold Answer tương ứng] |
| 5 | [Query 5 của nhóm] | [Gold Answer tương ứng] |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | [Query 1] | [Tóm tắt chunk lấy được] | [Score] | [Yes / No] | [Tóm tắt câu trả lời từ Agent] |
| 2 | [Query 2] | [Tóm tắt chunk lấy được] | [Score] | [Yes / No] | [Tóm tắt câu trả lời từ Agent] |
| 3 | [Query 3] | [Tóm tắt chunk lấy được] | [Score] | [Yes / No] | [Tóm tắt câu trả lời từ Agent] |
| 4 | [Query 4] | [Tóm tắt chunk lấy được] | [Score] | [Yes / No] | [Tóm tắt câu trả lời từ Agent] |
| 5 | [Query 5] | [Tóm tắt chunk lấy được] | [Score] | [Yes / No] | [Tóm tắt câu trả lời từ Agent] |

**Bao nhiêu queries trả về chunk relevant trong top-3?** __ / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *CÁ NHÂN ĐIỀN: Viết 2-3 câu chia sẻ bài học hoặc góc nhìn mới nhận được từ đồng đội.*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *CÁ NHÂN ĐIỀN: Viết 2-3 câu nhận xét từ buổi demo chung giữa các nhóm.*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *CÁ NHÂN ĐIỀN: Viết 2-3 câu đề xuất cải tiến về cách chọn dữ liệu, cách chunk hoặc gán metadata.*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
