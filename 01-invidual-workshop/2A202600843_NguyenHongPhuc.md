# Bài phân tích Moni – Trợ thủ AI tài chính

## 1. App được chọn

**App:** MoMo  
**Tính năng:** Trợ thủ AI – Moni  
**Use case thử:** Hỏi Moni về tiết kiệm và phân tích chi tiêu cá nhân.

---

## 2. Các câu hỏi đã thử

### Query 1

**Người dùng hỏi:**

> Tôi nên tiết kiệm bao nhiêu mỗi tháng với lương 8 triệu?

**Moni trả lời:**

Moni gợi ý nên tiết kiệm từ **10% – 20% thu nhập**, tương đương khoảng **800.000đ – 1.600.000đ/tháng**.

Ngoài ra Moni còn đưa ra một số lời khuyên:

- Nếu có nhiều chi phí cố định → tiết kiệm khoảng 800.000đ.
- Nếu chi tiêu linh hoạt → có thể tiết kiệm 1.600.000đ.
- Nên đặt mục tiêu tiết kiệm rõ ràng.

---

### Query 2

**Người dùng hỏi:**

> Tôi đang tiêu quá nhiều ở khoản nào?

**Moni trả lời:**

Moni cho biết:

- Tổng chi tiêu: 95.000đ
- Số giao dịch: 3

Tuy nhiên Moni không chỉ ra khoản chi nào đang chiếm tỷ trọng lớn nhất mà chỉ gợi ý người dùng xem báo cáo chi tiêu theo nhóm.

---

### Query 3

**Người dùng hỏi:**

> Bạn muốn Moni giúp đặt ngân sách tiết kiệm hoặc theo dõi khoản tiết kiệm hàng tháng không? → Có

**Moni trả lời:**

Moni tiếp tục hỏi người dùng muốn chọn:

- 800.000đ/tháng
- 1.600.000đ/tháng

để làm mục tiêu tiết kiệm.

---

# 3. Flow hiện tại (As-Is)

## 3.1 Happy Path

### Query

> Tôi nên tiết kiệm bao nhiêu mỗi tháng với lương 8 triệu?

```text
User hỏi mức tiết kiệm phù hợp
        ↓
Moni phân tích theo quy tắc tiết kiệm
        ↓
Moni đề xuất 800.000đ – 1.600.000đ
        ↓
Moni hỏi có muốn đặt mục tiêu tiết kiệm không
        ↓
User tiếp tục hội thoại
```

### Đánh giá

✅ Trả lời đúng câu hỏi

✅ Có gợi ý bước tiếp theo

⚠️ Chưa có thao tác nhanh để tạo mục tiêu

---

## 3.2 Low-confidence Path

### Query

> Tôi đang tiêu quá nhiều ở khoản nào?

```text
User hỏi khoản chi tiêu cao nhất
        ↓
Moni truy xuất dữ liệu giao dịch
        ↓
Moni chỉ hiển thị tổng chi tiêu
        ↓
Moni đề nghị xem báo cáo hoặc xác nhận thêm
```

### Đánh giá

⚠️ Có dữ liệu nhưng không đưa ra được insight

⚠️ Trả lời chưa sát nhu cầu người dùng

---

## 3.3 Failure Path

```text
User muốn biết khoản nào đang chi nhiều nhất
        ↓
Moni chỉ hiển thị tổng chi tiêu
        ↓
Không xác định được nhóm chi tiêu lớn nhất
        ↓
User không nhận được câu trả lời mong muốn
```

### Điểm thất bại

Moni không trả lời được câu hỏi chính:

> "Tôi đang tiêu quá nhiều ở khoản nào?"

---

## 3.4 Correction Path

```text
User hỏi:
"Tôi đang tiêu quá nhiều ở khoản nào?"
        ↓
Moni trả lời chung chung
        ↓
User phải hỏi lại:
"Phân tích từng nhóm chi tiêu"
        ↓
Moni mới tiếp tục xử lý
```

### Điểm user bị kẹt

```text
User hỏi
        ↓
Moni trả lời tổng chi tiêu
        ↓
❌ Không biết nhóm nào chi nhiều nhất
        ↓
User phải hỏi lại hoặc tự xem báo cáo
```

---

# 4. Path yếu nhất được chọn

## Path được chọn

```text
"Tôi đang tiêu quá nhiều ở khoản nào?"
```

### Lý do

- Là câu hỏi có giá trị cao với người dùng.
- Moni có dữ liệu nhưng không tạo được insight.
- Người dùng phải thực hiện thêm nhiều bước.
- Không thể hiện được vai trò AI Assistant.

---

# 5. Flow đề xuất (To-Be)

```text
User hỏi:
"Tôi đang tiêu quá nhiều ở khoản nào?"
        ↓
Moni phân tích dữ liệu giao dịch
        ↓
Xác định nhóm chi tiêu cao nhất
        ↓
Hiển thị insight
        ↓
Hiển thị Action Card
        ↓
User chọn hành động
        ↓
Hệ thống thực thi
```

---

## Source (Nguồn dữ liệu)

```text
Phân tích dựa trên:

- 23 giao dịch
- Thời gian: 01/06/2026 – 30/06/2026
```

Hiển thị nguồn dữ liệu giúp tăng độ tin cậy của AI.

---

## Insight đề xuất

```text
Khoản chi lớn nhất tháng này:

Ăn uống: 65%
(1.500.000đ)

Tăng 25% so với tháng trước.
```

---

## Button (Quick Actions)

```text
[Xem chi tiết]

[Đặt ngân sách ăn uống]

[Nhắc tôi khi vượt hạn mức]
```

---

## Undo

Nếu người dùng thao tác nhầm:

```text
Đã tạo ngân sách ăn uống:
2.000.000đ/tháng

[Hoàn tác]
```

---

## Handoff

Nếu dữ liệu không đủ:

```text
Moni chưa đủ dữ liệu để xác định nhóm chi tiêu lớn nhất.

[Xem báo cáo chi tiêu]

[Liên hệ hỗ trợ]
```

---

## Correction Log

```text
User:
"Tôi muốn biết nhóm chi tiêu cao nhất,
không phải tổng chi tiêu."

Moni:
"Đã ghi nhận.

Lần sau khi bạn hỏi về khoản chi tiêu nhiều nhất,
Moni sẽ ưu tiên hiển thị nhóm chi tiêu đứng đầu."
```

---

# 6. Product Decision

## Quyết định sản phẩm

### Triển khai Insight + Action Card

Thay vì chỉ trả lời bằng văn bản, Moni sẽ:

1. Trả lời trực tiếp câu hỏi.
2. Hiển thị nguồn dữ liệu đã sử dụng.
3. Đề xuất hành động liên quan.
4. Cho phép hoàn tác thao tác.
5. Hỗ trợ chuyển sang báo cáo hoặc CSKH khi AI không đủ dữ liệu.

---

## Lý do lựa chọn

### Đối với người dùng

- Giảm số bước hội thoại.
- Có câu trả lời rõ ràng hơn.
- Dễ thao tác trên mobile.
- Chuyển từ đọc thông tin sang hành động ngay.

### Đối với MoMo

- Tăng tỷ lệ tương tác với Moni.
- Tăng tỷ lệ tạo ngân sách và mục tiêu tiết kiệm.
- Tăng mức độ gắn bó với hệ sinh thái MoMo.
- Nâng vai trò Moni từ chatbot hỏi đáp thành AI Assistant thực sự.

---

# 7. Output cuối cùng

## As-Is

```text
User hỏi
        ↓
Moni trả lời bằng văn bản
        ↓
User đọc kết quả
        ↓
Tự quyết định bước tiếp theo
```

## User Stuck Point

```text
User hỏi:
"Tôi đang tiêu quá nhiều ở khoản nào?"
        ↓
Moni chỉ trả về tổng chi tiêu
        ↓
❌ Không biết khoản nào chi nhiều nhất
        ↓
User phải hỏi lại
```

## To-Be

```text
User hỏi
        ↓
Moni phân tích giao dịch
        ↓
Moni đưa ra insight cụ thể
        ↓
Hiển thị nguồn dữ liệu
        ↓
Hiển thị Action Card
        ↓
User chọn hành động
        ↓
Hệ thống thực thi ngay
```

## Product Decision

```text
Triển khai Insight + Action Card + Source + Undo + Handoff + Correction Log
để biến insight thành hành động và giảm tỷ lệ người dùng bị kẹt trong hội thoại.
```