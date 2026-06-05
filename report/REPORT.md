# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu:*

**Ví dụ HIGH similarity:**
- Sentence A:
- Sentence B:
- Tại sao tương đồng:

**Ví dụ LOW similarity:**
- Sentence A:
- Sentence B:
- Tại sao khác:

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:*

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:*
> *Đáp án:*

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:*

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
> *Viết 2-3 câu: dùng regex gì để detect sentence? Xử lý edge case nào?*

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu: algorithm hoạt động thế nào? Base case là gì?*

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu: lưu trữ thế nào? Tính similarity ra sao?*

**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu: filter trước hay sau? Delete bằng cách nào?*

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu: prompt structure? Cách inject context?*

### Test Results

```
# Paste output of: pytest tests/ -v
```

**Số tests pass:** __ / __

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