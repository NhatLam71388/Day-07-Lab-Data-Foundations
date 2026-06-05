# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Trần Gia Huy  
**Nhóm:** Data Foundations - Nhóm 6 thành viên  
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**

High cosine similarity nghĩa là hai đoạn text có hướng vector gần giống nhau trong không gian embedding. Nói đơn giản hơn, hai đoạn đó đang nói về nội dung hoặc ý nghĩa gần nhau, dù câu chữ có thể không giống hoàn toàn.

**Ví dụ HIGH similarity:**

- Sentence A: Sinh viên cần đăng ký môn học trên hệ thống SIS.
- Sentence B: Quy trình đăng ký học phần được thực hiện qua cổng SIS.
- Tại sao tương đồng: Cả hai câu đều nói về cùng một hành động là đăng ký môn học trên hệ thống sinh viên.

**Ví dụ LOW similarity:**

- Sentence A: Sinh viên có cGPA thấp có thể bị cảnh báo học vụ.
- Sentence B: Hôm nay trời mưa và đường phố đông xe.
- Tại sao khác: Một câu nói về quy chế học vụ, còn câu kia nói về thời tiết và giao thông, nên hai câu gần như không liên quan về mặt ngữ nghĩa.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

Cosine similarity được ưu tiên hơn Euclidean distance bởi vì cosine tập trung vào hướng của vector, tức là cách vector biểu diễn ngữ nghĩa. Với text embedding, điều quan trọng nhất là hai đoạn văn có gần nhau về ý nghĩa hay không, chứ không phải độ dài tuyệt đối của vector lớn hay nhỏ như trong Euclidean distance.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**

```text
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
           = ceil((10000 - 50) / (500 - 50))
           = ceil(9950 / 450)
           = 23
```

**Đáp án:** 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

```text
num_chunks = ceil((10000 - 100) / (500 - 100))
           = ceil(9900 / 400)
           = 25
```

Số chunk tăng từ 23 lên 25 vì mỗi lần trượt cửa sổ chỉ tiến thêm 400 ký tự thay vì 450 ký tự. Overlap nhiều hơn giúp giữ lại ngữ cảnh giữa hai chunk liền nhau, đặc biệt khi một ý quan trọng nằm ở ranh giới giữa hai đoạn.

---

## 2. Document Selection - Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Quy chế học vụ & Quy trình/Tuyển sinh Đại học - VinUniversity

Nhóm chọn domain này vì đây là kiểu dữ liệu rất phù hợp để thử RAG: nội dung nhiều quy định, nhiều điều kiện cụ thể, nhiều phòng ban khác nhau và dễ cần metadata filtering. Với domain học vụ, nếu chunking hoặc metadata làm không tốt thì hệ thống rất dễ trả lời thiếu điều kiện, nhầm giữa tuyển sinh, học phí, khảo thí hoặc tốt nghiệp. Vì vậy domain này giúp đánh giá rõ chất lượng ingestion layer chứ không chỉ kiểm tra code có chạy hay không.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | canh_bao_hoc_vu_quy_che.md | `data/canh_bao_hoc_vu_quy_che.md` | 6097 | `category=academic_warning`, `doc_type=policy`, `department=registrar`, `owner=member_1` |
| 2 | dang_ky_mon_hoc_sop.md | `data/dang_ky_mon_hoc_sop.md` | 5727 | `category=course_registration`, `doc_type=sop`, `department=registrar`, `owner=member_2` |
| 3 | tuyen_sinh_faq.md | `data/tuyen_sinh_faq.md` | 4439 | `category=admissions`, `doc_type=faq`, `department=admissions`, `owner=member_3` |
| 4 | hoc_phi_huong_dan.md | `data/hoc_phi_huong_dan.md` | 5400 | `category=tuition_finance`, `doc_type=guideline`, `department=finance`, `owner=member_4` |
| 5 | khao_thi_quy_che.md | `data/khao_thi_quy_che.md` | 6335 | `category=examination`, `doc_type=policy`, `department=registrar`, `owner=member_5` |
| 6 | tot_nghiep_quy_trinh.md | `data/tot_nghiep_quy_trinh.md` | 6378 | `category=graduation`, `doc_type=procedure`, `department=registrar`, `owner=member_6` |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| `source` | string | `data/canh_bao_hoc_vu_quy_che.md` | Truy vết câu trả lời về đúng tài liệu gốc. |
| `category` | string | `academic_warning`, `course_registration`, `examination` | Lọc theo chủ đề khi query có phạm vi rõ ràng. |
| `language` | string | `vi` | Toàn bộ bộ dữ liệu là tiếng Việt, giúp tránh trộn với tài liệu tiếng Anh cũ trong repo. |
| `doc_type` | string | `policy`, `sop`, `faq`, `procedure` | Phân biệt quy chế, quy trình, FAQ và hướng dẫn. |
| `department` | string | `registrar`, `admissions`, `finance` | Lọc theo phòng ban phụ trách nội dung. |
| `owner` | string | `member_1` | Gắn trách nhiệm chuẩn bị tài liệu theo implementation plan. |
| `doc_id` | string | `canh_bao_hoc_vu_quy_che` | Gom hoặc xóa toàn bộ chunk thuộc cùng tài liệu. |
| `chunk_index` | int | `3` | Biết chunk nằm ở vị trí nào trong tài liệu gốc. |
| `strategy` | string | `markdown_heading` | Biết chunk được tạo bằng chiến lược nào. |
| `applies_to` | string | `general`, `practical_courses` | Dùng cho query cần metadata filtering, đặc biệt quy định khảo thí riêng cho môn thực hành/đồ án. |

---

## 3. Chunking Strategy - Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu với `chunk_size=500`:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| canh_bao_hoc_vu_quy_che.md | FixedSizeChunker | 14 | 481.9 | Trung bình, dễ cắt ngang quy định |
| canh_bao_hoc_vu_quy_che.md | SentenceChunker | 13 | 467.1 | Tốt hơn fixed-size nhưng chưa giữ trọn mục quy chế |
| canh_bao_hoc_vu_quy_che.md | RecursiveChunker | 20 | 302.9 | Tách nhỏ, dễ search nhưng đôi khi tách hơi vụn |
| dang_ky_mon_hoc_sop.md | FixedSizeChunker | 13 | 486.7 | Ổn định kích thước nhưng có thể cắt ngang bước |
| dang_ky_mon_hoc_sop.md | SentenceChunker | 14 | 407.2 | Dễ đọc, hợp với mô tả quy trình |
| dang_ky_mon_hoc_sop.md | RecursiveChunker | 16 | 356.1 | Cân bằng hơn, giữ paragraph tương đối tốt |
| tuyen_sinh_faq.md | FixedSizeChunker | 10 | 488.9 | Có thể cắt giữa câu hỏi và trả lời |
| tuyen_sinh_faq.md | SentenceChunker | 6 | 738.3 | Giữ ý nhưng chunk khá dài |
| tuyen_sinh_faq.md | RecursiveChunker | 17 | 259.6 | Dễ search nhưng có nguy cơ tách câu hỏi khỏi câu trả lời |

### Strategy Của Tôi

**Loại:** Custom Strategy - `MarkdownHeadingChunker`

**Mô tả cách hoạt động:**

Theo implementation plan, tôi là Thành viên 1 và chọn custom strategy cắt văn bản dựa trên heading Markdown `#`, `##`, `###`. Ý tưởng là mỗi mục quy chế thường đã được viết thành một section rõ ràng, ví dụ "Cảnh báo học vụ cấp độ 1", "Điều kiện buộc thôi học", hoặc "Quy trình khiếu nại". Nếu chunk theo heading, hệ thống giữ được trọn một mục chính sách thay vì cắt ngang điều kiện và hậu quả pháp lý.

**Code snippet custom chunker:**

```python
class MarkdownHeadingChunker:
    def chunk(self, text: str) -> list[str]:
        chunks = []
        current = []

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
```

**Metadata khi ingest theo Thành viên 1:**

```python
metadata_by_file = {
    "canh_bao_hoc_vu_quy_che.md": {
        "category": "academic_warning",
        "language": "vi",
        "doc_type": "policy",
        "department": "registrar",
        "owner": "member_1",
    },
    "dang_ky_mon_hoc_sop.md": {
        "category": "course_registration",
        "language": "vi",
        "doc_type": "sop",
        "department": "registrar",
        "owner": "member_2",
    },
    "tuyen_sinh_faq.md": {
        "category": "admissions",
        "language": "vi",
        "doc_type": "faq",
        "department": "admissions",
        "owner": "member_3",
    },
    "hoc_phi_huong_dan.md": {
        "category": "tuition_finance",
        "language": "vi",
        "doc_type": "guideline",
        "department": "finance",
        "owner": "member_4",
    },
    "khao_thi_quy_che.md": {
        "category": "examination",
        "language": "vi",
        "doc_type": "policy",
        "department": "registrar",
        "owner": "member_5",
    },
    "tot_nghiep_quy_trinh.md": {
        "category": "graduation",
        "language": "vi",
        "doc_type": "procedure",
        "department": "registrar",
        "owner": "member_6",
    },
}
```

Khi tạo chunk, tôi thêm `doc_id`, `chunk_index`, `strategy=markdown_heading`, và nếu chunk thuộc phần khảo thí thực hành/đồ án thì thêm `applies_to=practical_courses`.

### So Sánh: Strategy của tôi vs Baseline

Với 6 tài liệu, custom heading strategy tạo tổng cộng **35 chunks**. Một vài thống kê:

| Tài liệu | Strategy của tôi | Chunk Count | Avg Length | Nhận xét |
|-----------|------------------|-------------|------------|----------|
| canh_bao_hoc_vu_quy_che.md | Markdown heading | 7 | 869.3 | Giữ tốt từng mục cảnh báo/thử thách/buộc thôi học |
| dang_ky_mon_hoc_sop.md | Markdown heading | 12 | 475.4 | Rất hợp vì mỗi bước đăng ký là một heading riêng |
| tuyen_sinh_faq.md | Markdown heading | 1 | 4439.0 | Chưa tốt vì file FAQ dùng bold question thay vì heading |
| hoc_phi_huong_dan.md | Markdown heading | 5 | 1078.4 | Giữ trọn từng nhóm chính sách học phí |
| khao_thi_quy_che.md | Markdown heading | 5 | 1265.4 | Giữ được phần quy định đặc thù cho thực hành/đồ án |
| tot_nghiep_quy_trinh.md | Markdown heading | 5 | 1274.0 | Giữ trọn từng bước xét tốt nghiệp |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | MarkdownHeadingChunker | 9/10 | Giữ trọn mục quy chế, metadata rõ, query top-3 tốt | FAQ không tách tốt nếu câu hỏi không dùng heading |
| Thành viên 2 | SentenceChunker, max_sentences=5 | 8/10 | Hợp quy trình dài, đọc tự nhiên | Có thể tách giữa tên bước và nội dung |
| Thành viên 3 | SentenceChunker, max_sentences=2 | 7/10 | Hợp Q&A ngắn | Dễ mất context với câu trả lời dài |
| Thành viên 4 | RecursiveChunker, chunk_size=300 | 8/10 | Tìm nhanh thông tin nhỏ | Có thể hơi vụn với điều kiện tài chính dài |
| Thành viên 5 | RecursiveChunker, chunk_size=800 | 8/10 | Hợp quy chế khảo thí phức tạp | Chunk có thể dài |
| Thành viên 6 | FixedSizeChunker, chunk_size=400 | 6/10 | Baseline dễ so sánh | Có thể cắt ngang mục quy trình |

**Strategy nào tốt nhất cho domain này? Tại sao?**

Với domain quy chế học vụ, tôi cho rằng heading-based chunking là strategy tốt nhất khi tài liệu được viết bằng Markdown có heading rõ ràng. Lý do là các quy định thường có cấu trúc theo mục, và người dùng thường hỏi theo đúng mục đó. Tuy nhiên, với file FAQ không dùng heading mà dùng `**Câu hỏi**`, strategy này cần được mở rộng để tách theo Q&A pair.

---

## 4. My Approach - Cá nhân (10 điểm)

### Chunking Functions

**`SentenceChunker.chunk`** - approach:

Tôi implement `SentenceChunker` bằng cách dùng regex để tách văn bản theo ranh giới câu, cụ thể là sau các dấu `.`, `!`, `?` kết hợp với khoảng trắng hoặc xuống dòng. Sau đó tôi gom tối đa `max_sentences_per_chunk` câu vào một chunk. Cách này giúp chunk giữ nghĩa câu tốt hơn fixed-size chunking.

**`RecursiveChunker.chunk` / `_split`** - approach:

Tôi implement `RecursiveChunker` theo hướng thử separator từ lớn đến nhỏ: đoạn văn `\n\n`, dòng `\n`, câu `. `, khoảng trắng, rồi cuối cùng cắt cứng theo ký tự nếu cần. Base case là khi đoạn text đã nhỏ hơn hoặc bằng `chunk_size`.

### EmbeddingStore

**`add_documents` + `search`** - approach:

Tôi dùng in-memory store để lưu mỗi record gồm `id`, `doc_id`, `content`, `metadata`, và `embedding`. Khi search, query được embed rồi so sánh với từng document embedding bằng dot product, sau đó sort giảm dần theo score.

**`search_with_filter` + `delete_document`** - approach:

Với `search_with_filter`, tôi filter metadata trước rồi mới search trong candidate set còn lại. Cách này đúng với retrieval pipeline vì metadata nên giúp thu hẹp phạm vi tìm kiếm trước khi ranking. Với `delete_document`, tôi xóa tất cả chunk có `doc_id` trùng với document cần xóa.

### KnowledgeBaseAgent

**`answer`** - approach:

Tôi implement `KnowledgeBaseAgent.answer` theo RAG pattern: nhận câu hỏi, retrieve top-k chunks, build prompt chứa context, rồi gọi `llm_fn`. Prompt yêu cầu model chỉ trả lời dựa trên context đã retrieve, nếu thiếu thông tin thì nói không biết.

### Test Results

```text
pytest tests\ -v

42 passed, 1 warning
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions - Cá nhân (5 điểm)

Tôi dùng keyword-based embedding cục bộ cho benchmark tiếng Việt và gọi `compute_similarity()` để tính cosine similarity.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký môn học trên SIS và kiểm tra trạng thái Registered. | Quy trình đăng ký học phần yêu cầu chọn môn học trên hệ thống SIS. | high | 1.000 | Đúng |
| 2 | Sinh viên có cGPA dưới 2.00 có thể bị cảnh báo học vụ. | Cảnh báo học vụ được áp dụng khi kết quả học tập rơi dưới chuẩn tối thiểu. | high | 0.816 | Đúng |
| 3 | Sinh viên xin gia hạn học phí phải nộp đơn trước hạn thanh toán. | Gia hạn học phí cần đơn đề nghị và cam kết tài chính hợp lệ. | high | 1.000 | Đúng |
| 4 | Ứng viên cần chứng chỉ IELTS khi nhập học. | Sinh viên nhận bằng tốt nghiệp tạm thời sau hội đồng xét duyệt. | low | 0.000 | Đúng |
| 5 | Quy định khảo thí áp dụng cho môn thực hành và đồ án. | Hôm nay trời mưa và đường phố rất đông xe. | low | 0.000 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**

Kết quả không quá bất ngờ vì keyword-based embedding bám khá sát các từ khóa quan trọng. Tuy nhiên điều này cũng cho thấy một giới hạn: nếu hai câu giống nhau về nghĩa nhưng dùng từ khác hoàn toàn, keyword embedding có thể bỏ sót. Với hệ thống thật, semantic embedding sẽ tốt hơn vì nó hiểu được quan hệ nghĩa chứ không chỉ đếm từ khóa.

---

## 6. Results - Cá nhân (10 điểm)

Tôi chạy benchmark theo strategy cá nhân: `MarkdownHeadingChunker` + metadata theo implementation plan. Để đánh giá tiếng Việt ổn định trong môi trường offline, tôi dùng một keyword-based embedding nhỏ, normalize dấu tiếng Việt về ASCII và tính cosine similarity trên nhóm từ khóa học vụ. Store vẫn là `EmbeddingStore` trong package `src`.

### Benchmark Queries & Gold Answers

| # | Query | Gold Answer | Chunk chứa thông tin |
|---|-------|-------------|----------------------|
| 1 | Quy trình đăng ký môn học trên SIS gồm những bước nào? | Sinh viên rà soát lộ trình, kiểm tra prerequisite, đăng ký trên SIS theo cohort, rồi kiểm tra trạng thái Registered. | `dang_ky_mon_hoc_sop.md`, các bước 1-4 |
| 2 | Khi nào sinh viên bị cảnh báo học vụ hoặc buộc thôi học? | Cảnh báo khi Semester GPA hoặc cGPA dưới 2.00; buộc thôi học khi vi phạm giới hạn thử thách, vượt thời gian đào tạo hoặc vi phạm kỷ luật nghiêm trọng. | `canh_bao_hoc_vu_quy_che.md`, mục 1 và 3 |
| 3 | Điều kiện tiếng Anh đầu vào khi nhập học là gì? | Ứng viên phải có chứng chỉ tiếng Anh còn hiệu lực, tối thiểu IELTS Academic 6.5 Overall không kỹ năng nào dưới 6.0, hoặc TOEFL iBT/PTE tương đương. | `tuyen_sinh_faq.md`, câu hỏi 4 |
| 4 | Sinh viên xin gia hạn học phí cần làm gì và thời hạn gia hạn tối đa bao lâu? | Sinh viên nộp đơn xin gia hạn học phí trước hạn thanh toán, kèm cam kết tài chính; thời gian gia hạn tối đa không quá 4 tuần từ ngày học kỳ mới bắt đầu. | `hoc_phi_huong_dan.md`, mục 2 |
| 5 | Quy định khảo thí áp dụng riêng cho môn thực hành hoặc đồ án là gì? | Môn thực hành/đồ án không được tự động hoãn thi hoặc thi bù; vắng không lý do đặc biệt có thể bị điểm 0 và phải đạt toàn bộ năng lực cốt lõi. | `khao_thi_quy_che.md`, mục 4 |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|----------------------|-------|-----------|------------------------|
| 1 | Quy trình đăng ký môn học trên SIS gồm những bước nào? | `dang_ky_mon_hoc_sop.md`, chunk 1 | 0.962 | Có | Trả lời về rà soát lộ trình, prerequisite, thao tác SIS và xác nhận Registered. |
| 2 | Khi nào sinh viên bị cảnh báo học vụ hoặc buộc thôi học? | `canh_bao_hoc_vu_quy_che.md`, chunk 0 | 0.866 | Có | Trả lời đúng về GPA/cGPA dưới 2.00 và các mức cảnh báo/thử thách/buộc thôi học. |
| 3 | Điều kiện tiếng Anh đầu vào khi nhập học là gì? | `tuyen_sinh_faq.md`, chunk 0 | 0.479 | Có | Trả lời được IELTS 6.5 Overall, không kỹ năng nào dưới 6.0, hoặc chứng chỉ tương đương. |
| 4 | Sinh viên xin gia hạn học phí cần làm gì và thời hạn gia hạn tối đa bao lâu? | `hoc_phi_huong_dan.md`, chunk 2 | 0.933 | Có | Trả lời đúng về đơn gia hạn, cam kết tài chính và giới hạn tối đa 4 tuần. |
| 5 | Quy định khảo thí áp dụng riêng cho môn thực hành hoặc đồ án là gì? | `khao_thi_quy_che.md`, chunk 4 | 0.842 | Có | Trả lời đúng về quy định đặc thù, không tự động thi bù và yêu cầu core competencies. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

### Top-3 Retrieved Chunks

| # | Top-3 chunks |
|---|--------------|
| 1 | 1. `dang_ky_mon_hoc_sop.md` chunk 1, score 0.962; 2. `dang_ky_mon_hoc_sop.md` chunk 3, score 0.943; 3. `dang_ky_mon_hoc_sop.md` chunk 11, score 0.913 |
| 2 | 1. `canh_bao_hoc_vu_quy_che.md` chunk 0, score 0.866; 2. `canh_bao_hoc_vu_quy_che.md` chunk 6, score 0.775; 3. `canh_bao_hoc_vu_quy_che.md` chunk 1, score 0.730 |
| 3 | 1. `tuyen_sinh_faq.md` chunk 0, score 0.479; 2. `canh_bao_hoc_vu_quy_che.md` chunk 0, score 0.000; 3. `canh_bao_hoc_vu_quy_che.md` chunk 1, score 0.000 |
| 4 | 1. `hoc_phi_huong_dan.md` chunk 2, score 0.933; 2. `hoc_phi_huong_dan.md` chunk 0, score 0.775; 3. `hoc_phi_huong_dan.md` chunk 1, score 0.447 |
| 5 | 1. `khao_thi_quy_che.md` chunk 4, score 0.842; 2. `khao_thi_quy_che.md` chunk 1, score 0.252 |

Query 5 dùng metadata filtering: tôi lọc `category=examination` và `applies_to=practical_courses` trước khi search. Nhờ vậy kết quả chỉ lấy từ phần khảo thí đặc thù cho môn thực hành/đồ án, tránh bị lẫn với quy định thi chung.

---

## 7. What I Learned (5 điểm - Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**

Tôi học được rằng cùng một domain nhưng mỗi kiểu tài liệu lại cần chunking khác nhau. SOP đăng ký môn học hợp với sentence/heading chunking, FAQ tuyển sinh nên tách theo từng cặp hỏi-đáp, còn quy chế khảo thí dài thì recursive chunking có thể ổn hơn nếu section quá lớn.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**

Điều quan trọng nhất là benchmark query phải bám sát gold answer và phải chỉ ra được source chunk. Nếu chỉ nhìn agent answer mà không kiểm tra chunk được retrieve, rất dễ nhầm một câu trả lời nghe có vẻ đúng với một câu trả lời thật sự grounded.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**

Nếu làm lại, tôi sẽ mở rộng `MarkdownHeadingChunker` để nhận diện thêm pattern `**Câu hỏi ...**` trong file FAQ. Như vậy `tuyen_sinh_faq.md` sẽ không bị giữ thành một chunk quá lớn, và retrieval cho các câu hỏi tuyển sinh sẽ chính xác hơn.

**Failure analysis:**

Failure case rõ nhất là file `tuyen_sinh_faq.md`: vì câu hỏi được viết bằng bold text thay vì heading Markdown, custom heading chunker chỉ tạo 1 chunk rất dài cho toàn bộ FAQ. Điều này vẫn retrieve đúng ở benchmark nhưng chunk chưa tối ưu, vì agent phải đọc quá nhiều nội dung không liên quan trong cùng một chunk. Cách cải thiện là thêm rule tách theo `**Câu hỏi` hoặc chuẩn hóa dữ liệu FAQ thành heading `## Câu hỏi 1`, `## Câu hỏi 2` trước khi ingest.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 14 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 9 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **87 / 100** |
