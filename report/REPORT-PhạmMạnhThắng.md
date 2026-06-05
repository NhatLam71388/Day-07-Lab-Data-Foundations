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

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Strategy Của Tôi

**Loại:** [FixedSizeChunker / SentenceChunker / RecursiveChunker / custom strategy]

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*

**Code snippet (nếu custom):**
```python
# Paste implementation here
```

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
> *Viết 2-3 câu:*

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

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | high / low | | |
| 2 | | | high / low | | |
| 3 | | | high / low | | |
| 4 | | | high / low | | |
| 5 | | | high / low | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*

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
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

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
