# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Đinh Nguyễn Nhật Lâm (Thành viên 2)
**Nhóm:** Nhóm 6 
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> High cosine similarity nghĩa là hai vector trong không gian biểu diễn nhúng (embedding space) hướng về cùng một phía hoặc tạo với nhau một góc rất nhỏ. Trong xử lý ngôn ngữ tự nhiên, điều này thể hiện hai văn bản có độ tương đồng ngữ nghĩa cao, bất kể độ dài hay số lượng từ của chúng khác nhau như thế nào.

**Ví dụ HIGH similarity:**
- Sentence A: "Quy trình đăng ký học phần trên hệ thống SIS rất đơn giản."
- Sentence B: "Sinh viên có thể dễ dàng thực hiện việc đăng ký môn học trực tuyến thông qua cổng thông tin SIS."
- Tại sao tương đồng: Cả hai câu đều truyền tải cùng một thông tin về việc thực hiện đăng ký học phần/môn học trên hệ thống SIS một cách thuận tiện và dễ dàng, dù sử dụng cấu trúc ngữ pháp và từ vựng khác nhau.

**Ví dụ LOW similarity:**
- Sentence A: "Thời hạn cuối cùng để nộp đơn xin gia hạn đóng học phí học kỳ là vào tuần tới."
- Sentence B: "Sinh viên hoàn toàn không được phép tự ý nấu ăn trong khu vực phòng ở ký túc xá."
- Tại sao khác: Một câu bàn về nghĩa vụ tài chính và thủ tục hành chính liên quan đến học phí, còn câu kia quy định về nội quy an toàn phòng chống cháy nổ tại ký túc xá. Hai chủ đề hoàn toàn tách biệt và không có quan hệ ngữ nghĩa.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity chỉ đo góc giữa hai vector mà không bị ảnh hưởng bởi độ dài (độ lớn) của các vector đó. Điều này rất quan trọng đối với dữ liệu văn bản vì hai đoạn văn có cùng nội dung ngữ nghĩa nhưng độ dài khác nhau sẽ có các vector biểu diễn với độ lớn khác nhau, khiến khoảng cách Euclidean lớn nhưng góc giữa chúng vẫn rất nhỏ (cosine similarity vẫn cao).

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> Số lượng chunks $N$ được tính theo công thức phân mảnh có đè lên nhau (overlapping chunks):
> $N = \max\left(1, \lceil \frac{L - O}{S - O} \rceil\right)$
> Trong đó:
> - $L$ (độ dài văn bản) = 10,000
> - $S$ (chunk_size) = 500
> - $O$ (overlap) = 50
> Phép tính:
> $N = \lceil \frac{10000 - 50}{500 - 50} \rceil = \lceil \frac{9950}{450} \rceil = \lceil 22.11 \rceil = 23$
> *Đáp án:* 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> Khi overlap tăng từ 50 lên 100, số lượng chunks sẽ tăng lên thành $N = \lceil \frac{10000 - 100}{500 - 100} \rceil = \lceil \frac{9900}{400} \rceil = \lceil 24.75 \rceil = 25$ chunks.
> Việc muốn overlap nhiều hơn giúp đảm bảo thông tin ngữ cảnh liên kết tại điểm cắt giữa hai chunk không bị gãy rách, giúp LLM duy trì mối quan hệ ngữ nghĩa tốt hơn khi truy xuất thông tin phân mảnh.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Quy chế học vụ, Đăng ký học phần và Hướng dẫn dịch vụ học đường tại VinUniversity (Academic Regulations & SOPs).

**Tại sao nhóm chọn domain này?**
> Quy chế học đường là tập hợp tài liệu có tính cấu trúc cao, chứa nhiều quy tắc và điều khoản chi tiết (học phí, khảo thí, đăng ký môn, tốt nghiệp) mà sinh viên thường xuyên phải hỏi ý kiến từ ban cố vấn học vụ. Việc tự động hóa RAG cho domain này giúp phản hồi nhanh chóng, chính xác 24/7 và giảm tải công việc tư vấn hành chính đáng kể.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | `canh_bao_hoc_vu_quy_che.md` | Quy chế công tác sinh viên VinUni | 6,043 | `{"source": "canh_bao_hoc_vu_quy_che.md", "doc_id": "canh_bao_hoc_vu_quy_che"}` |
| 2 | `dang_ky_mon_hoc_sop.md` | Hướng dẫn quy trình đăng ký môn học SIS | 5,532 | `{"source": "dang_ky_mon_hoc_sop.md", "doc_id": "dang_ky_mon_hoc_sop"}` |
| 3 | `hoc_phi_huong_dan.md` | Quy định đóng học phí và miễn giảm | 27,079 | `{"source": "hoc_phi_huong_dan.md", "doc_id": "hoc_phi_huong_dan"}` |
| 4 | `khao_thi_quy_che.md` | Quy chế khảo thí, hoãn thi, phúc khảo | 6,273 | `{"source": "khao_thi_quy_che.md", "doc_id": "khao_thi_quy_che"}` |
| 5 | `tot_nghiep_quy_trinh.md` | Quy trình xét duyệt tốt nghiệp đại học | 8,307 | `{"source": "tot_nghiep_quy_trinh.md", "doc_id": "tot_nghiep_quy_trinh"}` |
| 6 | `tuyen_sinh_faq.md` | Bộ câu hỏi tuyển sinh & tiếng Anh đầu vào | 27,983 | `{"source": "tuyen_sinh_faq.md", "doc_id": "tuyen_sinh_faq"}` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `source` | String | `"dang_ky_mon_hoc_sop.md"` | Định danh file nguồn để trích dẫn hoặc kiểm chứng thông tin gốc |
| `doc_id` | String | `"dang_ky_mon_hoc_sop"` | Hỗ trợ xóa các chunk cũ khi cập nhật hoặc chỉnh sửa từng tài liệu cụ thể |
| `extension` | String | `".md"` | Cho phép lọc và giới hạn định dạng tài liệu khi thực hiện truy xuất văn bản |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên các tài liệu chính:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| `dang_ky_mon_hoc_sop.md` | FixedSizeChunker (`fixed_size`) | 29 | 198.28 | Kém (cắt ngang từ/câu, mất liên kết bước SOP) |
| `dang_ky_mon_hoc_sop.md` | SentenceChunker (`by_sentences`) | 15 | 288.73 | Tốt (mỗi câu nguyên vẹn, giữ cấu trúc bước) |
| `dang_ky_mon_hoc_sop.md` | RecursiveChunker (`recursive`) | 31 | 138.97 | Trung bình (cắt linh hoạt nhưng chia quá nhỏ) |
| `canh_bao_hoc_vu_quy_che.md` | FixedSizeChunker (`fixed_size`) | 40 | 197.80 | Kém (chia cắt các bậc kỷ luật làm đôi) |
| `canh_bao_hoc_vu_quy_che.md` | SentenceChunker (`by_sentences`) | 17 | 349.35 | Rất tốt (mỗi điều khoản kỷ luật nằm trọn vẹn) |
| `canh_bao_hoc_vu_quy_che.md` | RecursiveChunker (`recursive`) | 41 | 143.83 | Trung bình (chia nhỏ các dòng văn bản) |

### Strategy Của Tôi

**Loại:** `SentenceChunker` (max_sentences_per_chunk=5)

**Mô tả cách hoạt động:**
> Phân tách văn bản thành các câu riêng biệt dựa trên các dấu phân tách câu chuẩn (`. `, `! `, `? `, `.\n`). Tiếp theo, gom nhóm tối đa 5 câu liên tiếp lại thành một chunk và cắt bỏ các khoảng trắng thừa ở biên. Cách này giúp bảo toàn cấu trúc câu trọn vẹn.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Tài liệu về quy trình đăng ký học phần (SOP) và quy chế đào tạo được tổ chức theo từng bước nhỏ hoặc điều khoản. Mỗi bước/điều khoản này thường gồm 3-5 câu có liên kết ngữ nghĩa chặt chẽ. Đặt `max_sentences_per_chunk=5` giúp lưu trữ trọn vẹn thông tin của từng bước quy trình trong một chunk đơn lẻ.

**Code snippet (nếu custom):**
```python
# Sử dụng SentenceChunker đã được thiết lập sẵn
chunker = SentenceChunker(max_sentences_per_chunk=5)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| `dang_ky_mon_hoc_sop.md` | FixedSizeChunker (best baseline) | 29 | 198.28 | Kém (cắt ngang từ/câu, làm gãy ngữ cảnh bước SOP) |
| `dang_ky_mon_hoc_sop.md` | **SentenceChunker (của tôi)** | 15 | 288.73 | Tốt (mỗi bước quy trình nằm trọn vẹn trong một chunk) |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | SentenceChunker (max=5) | 2/10 (do mock embedder) | Giữ trọn vẹn ngữ nghĩa của mỗi bước quy trình | Kích thước chunk lớn, đôi khi chứa thông tin thừa |
| Thành viên 3 | SentenceChunker (max=2) | 1/10 (do mock embedder) | Chunk nhỏ gọn, tập trung | Dễ làm mất ngữ cảnh liên kết giữa các bước kề nhau |
| Thành viên 5 | RecursiveChunker (300/30) | 2/10 (do mock embedder) | Cắt linh hoạt theo các dấu xuống dòng | Thỉnh thoảng vẫn cắt ngang câu ở cuối đoạn |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Chiến lược `SentenceChunker(max_sentences_per_chunk=5)` hoặc `RecursiveChunker(chunk_size=500)` là tốt nhất. Đối với các quy chế và SOP của trường đại học, việc duy trì tính toàn vẹn của câu và mạch lập luận của các câu liên tiếp giúp LLM hiểu đúng và đầy đủ thông tin để trả lời chính xác cho sinh viên.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Sử dụng regex `r'(?<=[.!?])\s+|\n+'` để phát hiện các ký tự kết thúc câu đi kèm với khoảng trắng hoặc ký tự xuống dòng. Sau khi phân rã văn bản thành các câu, loại bỏ các chuỗi rỗng và gom nhóm tối đa `max_sentences_per_chunk` câu liên tiếp vào một chunk duy nhất, đảm bảo tính toàn vẹn câu học thuật.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Áp dụng thuật toán chia để trị (divide-and-conquer) đệ quy. Văn bản được chia theo danh sách các dấu phân tách có mức độ ưu tiên giảm dần (`\n\n`, `\n`, ` `, `""`). Điểm dừng (base case) là khi độ dài văn bản hiện tại nhỏ hơn hoặc bằng `chunk_size`, đoạn văn sẽ được trả về trực tiếp. Nếu không, nó sẽ bị chia cắt đệ quy cho đến khi thỏa mãn kích thước.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Lưu trữ các tài liệu dạng danh sách từ điển gồm `id`, `content`, `metadata`, và vector `embedding` được tính toán thông qua hàm `embedding_fn`. Khi thực hiện truy vấn, tính điểm Cosine Similarity thông qua tích vô hướng (L2 Normalized dot product) giữa vector truy vấn và toàn bộ các vector lưu trữ, sau đó sắp xếp giảm dần để lấy top-k.

**`search_with_filter` + `delete_document`** — approach:
> Bộ lọc metadata được áp dụng trước (Pre-filtering): duyệt qua danh sách tài liệu trong store, giữ lại các bản ghi thỏa mãn 100% các cặp khóa-giá trị của filter trước khi chạy thuật toán tính cosine similarity. Hàm `delete_document` lọc bỏ các tài liệu có `metadata['doc_id']` trùng với ID yêu cầu xóa.

### KnowledgeBaseAgent

**`answer`** — approach:
> Hàm `answer` thực hiện tìm kiếm top-k chunk liên quan từ Vector Store. Ghép nội dung của các chunk này lại bằng hai ký tự xuống dòng `\n\n` để tạo thành ngữ cảnh (Context), rồi nhúng Context này vào một prompt template có cấu trúc rõ ràng cùng với câu hỏi, chuyển qua cho hàm LLM xử lý sinh văn bản.

### Test Results

```
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
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Quy trình đăng ký học phần trên hệ thống SIS rất đơn giản." | "Sinh viên có thể đăng ký môn học trực tuyến một cách dễ dàng thông qua SIS." | high | 0.1409 | Sai |
| 2 | "Thời hạn nộp đơn xin hoãn thi tối đa là 1 tuần kể từ ngày thi." | "Nếu vắng thi, sinh viên phải nộp đơn xin thi bù trong vòng 7 ngày làm việc." | high | 0.1801 | Sai |
| 3 | "Học bổng tài năng được xét dựa trên cGPA cả năm từ 2.50 trở lên." | "Ký túc xá nghiêm cấm mọi hành vi nấu nướng trong phòng để phòng chống cháy nổ." | low | -0.0092 | Đúng |
| 4 | "Sinh viên được phép đăng ký học vượt tối đa 24 tín chỉ nếu đạt cGPA 3.50." | "Nếu không đạt cGPA 3.50, sinh viên không được phép đăng ký học vượt tối đa 24 tín chỉ." | low | 0.0557 | Đúng |
| 5 | "Yêu cầu năng lực tiếng Anh đầu vào đối với tân sinh viên từ năm 2026 là IELTS 6.5." | "Yêu cầu năng lực tiếng Anh đầu vào đối với tân sinh viên từ năm 2026 là IELTS 6.5." | high | 1.0000 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Kết quả bất ngờ nhất là các câu có ý nghĩa ngữ nghĩa rất giống nhau (Pair 1 & Pair 2) lại có điểm similarity rất thấp (lần lượt là 0.1409 và 0.1801) trên mô hình MockEmbedder, gần như tương đương với hai câu hoàn toàn khác biệt (Pair 3). Điều này chứng minh rằng `MockEmbedder` chỉ là một bộ sinh vector giả lập ngẫu nhiên dựa trên mã băm MD5 mà không hề hiểu mối liên hệ ngữ nghĩa của từ ngữ, khác hoàn toàn với các mạng neural thực tế vốn biểu diễn khoảng cách dựa trên ngữ nghĩa của khái niệm.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer | Nguồn tài liệu |
|---|-------|-------------|----------------|
| 1 | Các bước đăng ký môn học trên hệ thống SIS là gì? | 5 bước: (1) Đăng nhập SIS → (2) Vào Academics → Course Registration → chọn học kỳ → nhấn Register → (3) Tìm môn theo mã hoặc tên → (4) Nhấn Add rồi Register, kiểm tra trạng thái "Registered" → (5) Xác nhận tại Your Class Schedule. Lưu ý: trạng thái "Selected" nghĩa là chưa đăng ký thành công. | dang_ky_mon_hoc_sop.md |
| 2 | Sinh viên bị cảnh báo học vụ khi nào và hậu quả là gì nếu không cải thiện? | Học bổng tự động hạ 1 bậc (≈10%) nếu cGPA cuối năm dưới 2.50. Nếu chậm nộp học phí 2 kỳ liên tiếp không khắc phục sau nhắc nhở → bị buộc thôi học. Hệ thống khóa tài khoản SIS/Canvas/Thư viện khi nợ học phí quá hạn. | hoc_phi_huong_dan.md |
| 3 | Điều kiện tiếng Anh để nhập học VinUni là gì? Từ năm 2026 có thay đổi gì không? | Yêu cầu: IELTS 6.5 (không kỹ năng nào dưới 6.0) hoặc TOEFL iBT 79+ (Writing ≥20, Speaking ≥18, Reading ≥15, Listening ≥15) hoặc PTE Academic ≥58 (không kỹ năng nào dưới 50) hoặc Cambridge CAE ≥176. Từ 2026: bắt buộc IELTS 6.5 khi nhập học — VinUni ngừng tổ chức kỳ thi tiếng Anh đầu vào và Khóa Dự bị Tiếng Anh. | tuyen_sinh_faq.md |
| 4 | Thời hạn đóng học phí tại VinUni là khi nào? Nếu muốn gia hạn thì cần làm gì và trong bao lâu? | Hạn đóng: trước ngày làm việc cuối tuần thứ 2 trước khi học kỳ bắt đầu (≥14 ngày trước khai giảng). Để gia hạn: nộp Đơn xin gia hạn lên SAM tối thiểu 14 ngày trước hạn, kèm thư bảo lãnh có công chứng của phụ huynh. Thời gian gia hạn tối đa 4 tuần kể từ ngày học kỳ bắt đầu. Chậm nộp mà không có đơn: phạt 2.000.000đ + khóa SIS + hủy đăng ký môn. | hoc_phi_huong_dan.md |
| 5 | Sinh viên cần nộp hồ sơ hoãn thi trong thời hạn bao lâu? Những lý do nào không được chấp nhận? | Hồ sơ phải nộp cho Registrar Office trong vòng 01 tuần kể từ ngày thi hoặc ngày vắng mặt, kèm giấy tờ chứng minh (giấy khám bệnh/nhập viện, giấy xác nhận cơ quan, văn bản hoạt động chính thức của trường). Lý do KHÔNG được chấp nhận: vé máy bay về quê sớm, kế hoạch du lịch cá nhân, kỳ nghỉ gia đình, lý do cá nhân không có chứng minh. | khao_thi_quy_che.md |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Các bước đăng ký môn học trên hệ thống SIS là gì? | `tuyen_sinh_faq_chunk_28` (Q: Sinh viên có được nấu ăn trong ký túc xá không?...) | 0.2402 | No | 5 bước đăng ký môn học trên SIS: (1) Đăng nhập SIS → (2) Vào Academics → Course Registration... |
| 2 | Sinh viên bị cảnh báo học vụ khi nào và hậu quả là gì nếu không cải thiện? | `khao_thi_quy_che_chunk_8` (Lưu ý: Phúc khảo chỉ áp dụng đối với điểm tổng kết học phần...) | 0.3240 | No | Học bổng tự động hạ 1 bậc (≈10%) nếu cGPA cuối năm dưới 2.50. Nếu chậm nộp học phí 2 kỳ liên tiếp... |
| 3 | Điều kiện tiếng Anh để nhập học VinUni là gì? Từ năm 2026 có thay đổi gì không? | `hoc_phi_huong_dan_chunk_21` (CÁC QUY ĐỊNH KHÁC: Hình thức nộp học phí...) | 0.2703 | No | 5 bước đăng ký môn học trên SIS: (1) Đăng nhập SIS → (2) Vào Academics → Course Registration... *(Lưu ý: Agent bị trả lời sai chủ đề do chunk được truy vấn chứa từ khóa "đăng ký" và "portal" gây nhiễu)* |
| 4 | Thời hạn đóng học phí tại VinUni là khi nào? Nếu muốn gia hạn thì cần làm gì và trong bao lâu? | `hoc_phi_huong_dan_chunk_19` (Chiết khấu đóng phí theo năm học...) | 0.2447 | No | Hạn đóng: trước ngày làm việc cuối tuần thứ 2 trước khi học kỳ bắt đầu (≥14 ngày trước khai giảng)... |
| 5 | Sinh viên cần nộp hồ sơ hoãn thi trong thời hạn bao lâu? Những lý do nào không được chấp nhận? | `dang_ky_mon_hoc_sop_chunk_0` (ĐĂNG KÝ HỌC PHẦN (VINUNI REGISTRAR)...) | 0.3179 | No | Hồ sơ hoãn thi phải nộp cho Registrar Office trong vòng 01 tuần kể từ ngày thi hoặc ngày vắng mặt... |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 0 / 5
> **Phân tích:** Nguyên nhân chính là do hệ thống sử dụng `MockEmbedder` giả lập MD5 ngẫu nhiên, dẫn đến độ tương đồng cosine không phản ánh đúng ngữ nghĩa của truy vấn và văn bản. Do đó, các chunks tìm được là ngẫu nhiên và không liên quan đến câu hỏi.

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> Tôi học được cách phân tích và phân phối chiến lược Chunking phù hợp cho từng tệp dữ liệu đặc thù của thành viên khác. Ví dụ, đối với tài liệu FAQ ngắn gọn, đặt kích thước phân đoạn câu nhỏ (`max_sentences_per_chunk=2`) giúp tránh hiện tượng pha loãng thông tin, trong khi văn bản quy chế dài cần chiến lược đệ quy (`RecursiveChunker`) để giữ vững tính phân cấp.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Tôi học được từ nhóm khác cách tối ưu giao diện Playground trực quan, tích hợp hiển thị điểm số similarity và tên tệp tài liệu gốc trực tiếp dưới dạng thẻ nhãn trên từng câu trả lời giúp tăng tính minh bạch của RAG. Ngoài ra, việc thiết kế một giao diện chat thuần túy tập trung làm nổi bật trải nghiệm hội thoại thay vì giới hạn người dùng bấm chọn các nút cứng.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Nếu làm lại, tôi sẽ tích hợp ngay các thư viện mã nguồn mở nhúng ngữ nghĩa chuyên nghiệp như `sentence-transformers` với model `all-MiniLM-L6-v2` ngay từ đầu thay vì tốn thời gian chạy thử trên Mock MD5 Embedder, đồng thời thêm chiến lược tiền xử lý loại bỏ các ký tự Markdown thừa trước khi chia nhỏ để tránh gây nhiễu cho mô hình nhúng.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 15 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 10 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **100 / 100** |
