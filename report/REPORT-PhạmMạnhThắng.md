# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Mạnh Thắng
**Nhóm:** [Tên nhóm]
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> Hai văn bản có high cosine similarity nghĩa là vector embedding của chúng gần như cùng hướng trong không gian vector, tức là chúng mang ngữ nghĩa tương đồng nhau. Giá trị cosine similarity càng gần 1.0 thì hai đoạn văn càng "nói về cùng một thứ", bất kể độ dài của văn bản.

**Ví dụ HIGH similarity:**
- Sentence A: "Python là ngôn ngữ lập trình phổ biến và dễ học."
- Sentence B: "Python được sử dụng rộng rãi trong lĩnh vực lập trình phần mềm."
- Tại sao tương đồng: Cả hai đều đề cập đến Python trong ngữ cảnh lập trình, dùng từ ngữ cùng semantic field nên embedding của chúng sẽ gần nhau trong không gian vector.

**Ví dụ LOW similarity:**
- Sentence A: "Con mèo đang ngủ say trên chiếc ghế gỗ."
- Sentence B: "Vector database lưu trữ embeddings để phục vụ tìm kiếm ngữ nghĩa."
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn không liên quan (thú cưng vs. cơ sở dữ liệu), không có từ khóa hay khái niệm chung nào, nên góc giữa hai vector sẽ rất lớn.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> Cosine similarity chỉ đo góc giữa hai vector, nên không bị ảnh hưởng bởi độ dài (magnitude) của văn bản — một đoạn văn ngắn và dài nói về cùng chủ đề vẫn cho cosine similarity cao. Euclidean distance đo khoảng cách tuyệt đối giữa hai điểm, nên văn bản dài hơn tự nhiên tạo ra vector có magnitude lớn hơn và bị phạt khoảng cách, dù nội dung hoàn toàn tương đồng.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính (dùng formula từ exercises.md):
>
> ```
> num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
>            = ceil((10,000 - 50) / (500 - 50))
>            = ceil(9,950 / 450)
>            = ceil(22.11)
>            = 23 chunks
> ```
>
> **Đáp án: 23 chunks**

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> ```
> num_chunks = ceil((10,000 - 100) / (500 - 100))
>            = ceil(9,900 / 400)
>            = ceil(24.75)
>            = 25 chunks
> ```
> Tăng overlap từ 50 lên 100 làm tăng số chunks từ 23 lên 25, vì step (khoảng cách giữa các chunks) nhỏ hơn (400 thay vì 450) nên cần nhiều chunks hơn để phủ hết document. Muốn overlap nhiều hơn để đảm bảo các thông tin quan trọng nằm ở ranh giới chunk không bị cắt đứt giữa chừng — context luôn xuất hiện đầy đủ trong ít nhất một chunk.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** [ví dụ: Customer support FAQ, Vietnamese law, cooking recipes, ...]

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:*

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

Chạy `ChunkingStrategyComparator().compare(text, chunk_size=300)` trên tài liệu `hoc_phi_huong_dan.md` (21.340 ký tự — gồm chính sách học phí GDL-SAM-004 và biểu phí VU_TS03.VN):

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| hoc_phi_huong_dan.md | FixedSizeChunker (`fixed_size`) | 72 | 296 | Không — cắt giữa câu, phá vỡ bảng và bullet |
| hoc_phi_huong_dan.md | SentenceChunker (`by_sentences`) | 42 | 506 | Trung bình — giữ câu nguyên vẹn nhưng chunk quá dài cho tài liệu có bảng |
| hoc_phi_huong_dan.md | RecursiveChunker (`recursive`) | 106 | 200 | Tốt — ưu tiên tách theo `\n\n` và `\n`, giữ nguyên từng mục, từng dòng bảng |

### Strategy Của Tôi

**Loại:** `RecursiveChunker(chunk_size=300)`

**Mô tả cách hoạt động:**
> `RecursiveChunker` thử lần lượt các separator theo thứ tự ưu tiên: `\n\n` (đoạn văn) → `\n` (dòng) → `. ` (câu) → ` ` (từ) → `""` (ký tự). Với mỗi separator, văn bản được split thành các phần nhỏ, sau đó gộp dần cho đến khi vượt `chunk_size=300` thì flush chunk hiện tại ra. Nếu một phần đơn lẻ vẫn lớn hơn `chunk_size`, hàm `_split` đệ quy sang separator tiếp theo. Điều này đảm bảo chunk luôn được cắt tại ranh giới tự nhiên của văn bản thay vì cắt cứng theo số ký tự.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> Tài liệu học phí VinUni có cấu trúc phân cấp rõ ràng: tiêu đề section (`##`), điểm bullet (`-`), và bảng markdown (`|`). `RecursiveChunker` ưu tiên tách tại `\n\n` (phân cách giữa các section) và `\n` (phân cách giữa các dòng bảng), đảm bảo mỗi chunk chứa một mục hoàn chỉnh như "mức học phí cử nhân" hoặc "quy định gia hạn" — không bị ghép lẫn nội dung không liên quan như `FixedSizeChunker`. Với `chunk_size=300`, các chunk đủ ngắn để embedding nắm bắt chính xác từng quy định cụ thể.

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| hoc_phi_huong_dan.md | FixedSizeChunker (baseline tốt nhất về phân phối đều) | 72 | 296 | Thấp — chunk cắt ngang giữa bảng, mất nghĩa |
| hoc_phi_huong_dan.md | **RecursiveChunker (của tôi)** | **106** | **200** | **Cao** — mỗi chunk là 1 quy định/dòng bảng hoàn chỉnh |

> `RecursiveChunker` tạo nhiều chunk hơn nhưng trung bình ngắn hơn và có độ chính xác retrieval cao hơn vì mỗi chunk chứa một đơn vị thông tin độc lập. `FixedSizeChunker` tuy phân phối đều nhưng thường cắt giữa dòng bảng — query "học phí cử nhân điều dưỡng" có thể match chunk chứa nửa bảng không có giá trị.

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Tài liệu | Điểm mạnh | Điểm yếu |
|-----------|----------|----------|-----------|----------|

**Strategy nào tốt nhất cho domain này? Tại sao?**
> Với domain quy chế học vụ VinUni — nơi thông tin quan trọng nằm trong các bảng markdown và bullet point có cấu trúc rõ ràng — `RecursiveChunker` với `chunk_size=300` cho kết quả retrieval chính xác nhất vì tôn trọng ranh giới tự nhiên của văn bản. `SentenceChunker` phù hợp hơn cho tài liệu dạng hướng dẫn prose (như dang_ky_mon_hoc_sop.md), trong khi `FixedSizeChunker` chỉ nên dùng làm baseline để so sánh. Đối với tài liệu có bảng và quy định số liệu cụ thể, chiến lược tách theo cấu trúc luôn vượt trội hơn tách theo độ dài cố định.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> Dùng regex `re.split(r'(?<=[\.\!\?])\s+|(?<=\.)\n', text)` để tách text tại ranh giới câu (sau dấu `.`, `!`, `?` có khoảng trắng, hoặc sau dấu `.` có xuống dòng). Sau đó gom các câu thành nhóm theo `max_sentences_per_chunk` và nối lại bằng khoảng trắng. Edge case xử lý: text rỗng trả về `[]`, câu rỗng sau split bị lọc ra.

**`RecursiveChunker.chunk` / `_split`** — approach:
> Algorithm thử lần lượt từng separator theo thứ tự ưu tiên (`\n\n` → `\n` → `. ` → ` ` → `""`). Với mỗi separator, split text ra thành các phần rồi gom lại cho đến khi candidate vượt `chunk_size` thì flush chunk hiện tại. Nếu một phần đơn lẻ vẫn lớn hơn `chunk_size`, đệ quy gọi `_split` với danh sách separator còn lại. Base case: text đã nhỏ hơn `chunk_size` thì trả về nguyên, hoặc hết separator thì chia cứng theo `chunk_size`.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> Mỗi document được embed bằng `embedding_fn` và lưu vào `self._store` dưới dạng dict chứa `id`, `content`, `embedding`, `metadata` (có thêm `doc_id`). Khi search, embed query rồi tính dot product với tất cả embedding đã lưu, sort descending theo score và trả về top-k kết quả.

**`search_with_filter` + `delete_document`** — approach:
> `search_with_filter` filter trước — lọc `self._store` chỉ giữ lại các record có metadata khớp với `metadata_filter`, sau đó chạy similarity search trên tập đã lọc. `delete_document` dùng list comprehension để rebuild `self._store` loại bỏ tất cả record có `metadata['doc_id'] == doc_id`, trả về `True` nếu size giảm.

### KnowledgeBaseAgent

**`answer`** — approach:
> Retrieve top-k chunks từ store bằng `store.search(question, top_k)`. Build prompt theo cấu trúc: liệt kê các chunk dưới dạng `[1] content`, `[2] content`, ... làm context, sau đó append câu hỏi và `Answer:`. Gọi `llm_fn(prompt)` và trả về kết quả trực tiếp.

### Test Results

```
python -m unittest discover -s tests -v
...
Ran 42 tests in 0.010s
OK
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

Embedding backend: `LocalEmbedder` (all-MiniLM-L6-v2, 384-dim). Ngưỡng phân loại: score ≥ 0.6 → high, < 0.6 → low.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | "Thời hạn đóng học phí trước ngày làm việc cuối cùng của tuần thứ hai." | "Hạn nộp học phí chậm nhất là 14 ngày trước khai giảng." | high | 0.674 | ✓ |
| 2 | "Sinh viên bị hạ bậc học bổng nếu cGPA dưới 2.50." | "Học bổng Tài năng tự động giảm 1 bậc khi điểm tích lũy không đạt chuẩn." | high | 0.539 | ✗ |
| 3 | "Phí thi lại môn lý thuyết là 1.500.000 đồng mỗi lần." | "Sinh viên cần nộp đơn xin gia hạn học phí 14 ngày trước hạn." | low | 0.480 | ✓ |
| 4 | "Học phí cử nhân điều dưỡng là 349.650.000 đồng mỗi năm." | "Học phí ngành y khoa và cử nhân khác là 815.850.000 đồng mỗi năm." | high | 0.824 | ✓ |
| 5 | "KTX phòng 4-8 sinh viên có giá 3.200.000 đồng mỗi tháng." | "Sinh viên vi phạm kỷ luật cấp độ 3 sẽ bị thu hồi học bổng." | low | 0.586 | ✓ |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> Pair 2 là bất ngờ nhất: dù cả hai câu đều diễn đạt cùng quy định (hạ bậc học bổng khi GPA không đạt), score thực tế chỉ đạt 0.539 — thấp hơn ngưỡng high. Điều này cho thấy `all-MiniLM-L6-v2` nhạy cảm với sự khác biệt từ vựng cụ thể: "cGPA" vs. "điểm tích lũy" và "hạ bậc" vs. "giảm 1 bậc" được biểu diễn ở các vùng khác nhau trong không gian vector, dù ý nghĩa hoàn toàn tương đồng. Điều này nhắc nhở rằng embedding model được huấn luyện chủ yếu trên tiếng Anh có thể chưa capture tốt paraphrase tiếng Việt chuyên ngành.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

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
> Qua việc so sánh kết quả giữa các thành viên, tôi nhận ra rằng không có một chunking strategy nào tốt nhất cho mọi loại tài liệu — mỗi strategy phù hợp với một cấu trúc văn bản riêng. Cụ thể, thành viên 3 dùng `SentenceChunker(max_sentences=2)` cho tài liệu FAQ tuyển sinh và cho kết quả retrieval rất tốt vì mỗi cặp Hỏi–Đáp vừa khít trong một chunk, trong khi strategy đó sẽ hoàn toàn thất bại với tài liệu bảng học phí của tôi vì bảng không có ranh giới câu rõ ràng. Điều này dạy tôi rằng bước phân tích cấu trúc tài liệu trước khi chọn strategy là không thể bỏ qua.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> Một nhóm khác đã minh họa cách thêm metadata `section` (tên mục lớn trong tài liệu) vào mỗi chunk, sau đó dùng `search_with_filter(metadata_filter={"section": "hoc_phi"})` để thu hẹp phạm vi tìm kiếm trước khi tính similarity — kết quả retrieval chính xác hơn đáng kể so với tìm kiếm toàn bộ store. Tôi chưa khai thác tính năng `search_with_filter` đủ sâu trong benchmark của mình và đây là cải tiến tôi sẽ áp dụng ngay. Điều này nhấn mạnh rằng metadata không chỉ là thông tin phụ mà là công cụ retrieval trực tiếp.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> Thứ nhất, tôi sẽ tách `hoc_phi_huong_dan.md` thành hai file riêng biệt: một file chứa chính sách/quy trình (văn bản prose) và một file chứa biểu phí (bảng số liệu), vì hai loại nội dung này cần chunk_size và strategy khác nhau — prose phù hợp với `SentenceChunker`, còn bảng phù hợp với `RecursiveChunker` chunk nhỏ. Thứ hai, tôi sẽ gán thêm metadata `content_type` (`"policy"` hoặc `"fee_table"`) để query về số tiền cụ thể chỉ search trong bảng phí, tránh nhiễu từ phần văn bản quy định. Hai thay đổi này kết hợp sẽ tăng precision của retrieval mà không cần thay đổi embedding model.

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
