# SPEC — AI trợ lý đọc & hiểu đơn thuốc cho người bệnh

## Nguồn evidence
- https://bvnguyentriphuong.com.vn/kien-thuc-duoc-cho-cong-dong/15-nguyen-nhan-ban-khong-duoc-su-dung-theo-don-thuoc-cua-nguoi-khac
- https://giathuoctot.com/huong-dan-cach-doc-don-thuoc-bac-si-giai-ma-ky-hieu-and-thuat-ngu-chi-tiet

---

## Mẫu opportunity (template)
> Cho **[user cụ thể]** đang **[task/workflow]**,
> prototype dùng AI để **[augment/automate hành động hẹp]**,
> tạo ra **[output]**,
> và xử lý **[failure mode]** bằng **[mitigation]**.

### Các tình huống đã phác (candidate slices)
1. Cho người bệnh đang muốn hiểu cách dùng, mục đích, tác dụng điển hình và không điển hình của thuốc → AI tự động tra dữ liệu, kiểm tra đơn → tạo ra hướng dẫn sử dụng + thông tin loại thuốc.
2. Cho người bệnh đang lo tác dụng phụ xuất hiện sớm/muộn (để chuẩn bị hoặc nhận biết) → AI kiểm tra thông tin các loại thuốc → tạo ra cảnh báo tác dụng phụ + gợi ý liên hệ bác sĩ.
3. Cho người bệnh đang mắc bệnh khác, hoặc băn khoăn món ăn có kỵ thuốc không → AI tra khả năng dùng chung → tạo ra gợi ý "được / không nhưng phải hỏi chỉ định bác sĩ".
4. Cho người bệnh đang muốn thay đổi loại thuốc → AI gợi ý các thuốc tương tự → tạo ra danh sách thuốc tương ứng (kèm yêu cầu hỏi bác sĩ).
5. Cho người bệnh đang muốn tra thông tin tiêu cực/cảnh báo về thuốc → AI tra danh sách → trả lời có / không.

---

## 1. Evidence pack
*User/pain có bằng chứng, không tự bịa. Có self-use và ít nhất một nguồn ngoài nhóm.*

**Pain chính (nguồn ngoài nhóm):**
- **Dùng thuốc sai cách / dùng nhờ đơn người khác gây nguy hiểm:** BV Nguyễn Tri Phương liệt kê 15 nguy cơ — tương tác thuốc, dị ứng không lường trước, sai liều theo cân nặng, chống chỉ định theo bệnh nền, hại gan/thận, kỵ thức ăn/rượu, thuốc hết hạn, che lấp triệu chứng bệnh khác.

**Self-use:** *(cần điền)* — ví dụ: "Người nhà tôi tự dùng lại đơn cũ / đơn của người khác vì thấy triệu chứng giống, không biết có an toàn không."

**Kế hoạch lấy thêm nguồn:** phỏng vấn 3–5 người bệnh có bệnh nền hoặc đang dùng nhiều thuốc; thu thập tình huống thực tế họ băn khoăn "thuốc này dùng chung được không / ăn món này khi uống thuốc được không".

---

## 2. Opportunity statement
*Bằng chứng nói gì sâu hơn về user; vì sao đây là việc đáng sửa.*

> Bằng chứng cho thấy rủi ro lớn nhất nằm ở **giai đoạn người bệnh tự dùng thuốc ở nhà mà không có bác sĩ bên cạnh**: họ không biết thuốc có kỵ thức ăn/thuốc khác, có chống chỉ định với bệnh nền không, nên dễ dùng sai hoặc dùng nhờ đơn người khác. Đáng sửa vì hậu quả là **rủi ro sức khỏe thật** (tương tác, quá liều, che lấp bệnh) và xảy ra ngay ở khoảng trống ngoài tầm với của bác sĩ.

---

## 3. Build slice
*Một user, một task, một AI decision, một output. Không build cả app.*

| | |
|---|---|
| **1 user** | Người bệnh đang dùng thuốc tại nhà |
| **1 task** | "Tôi muốn biết thuốc này có kỵ thức ăn/đồ uống nào không" |
| **1 AI decision** | Tra thông tin thuốc → xác định có cảnh báo tương tác thuốc–thức ăn hay không |
| **1 output** | Cảnh báo "nên / không nên dùng cùng" **kèm câu bắt buộc hỏi bác sĩ/dược sĩ** |

➡️ Không build cả app: tạm bỏ tính năng đổi thuốc, tra tương tác toàn diện, chat tự do ở slice này.

---

## 4. Auto / Aug decision
*AI gợi ý hay tự làm? Human giữ quyền ở đâu?*

- **Automate (AI tự làm):** tra thông tin thuốc, định dạng cảnh báo — việc tra cứu cơ học, ít rủi ro.
- **Augment (AI chỉ gợi ý):** cảnh báo tương tác, tác dụng phụ, "có nên đổi thuốc / ăn món này không" → **luôn kèm "hỏi bác sĩ/dược sĩ trước khi quyết định"**.
- **Human giữ quyền:** mọi **quyết định y khoa** (đổi thuốc, ngừng thuốc, kết hợp thuốc/bệnh nền) thuộc về bác sĩ. AI **không kê đơn, không thay liều**.

---

## 5. Four paths

| Path | Hành vi prototype |
|---|---|
| **Happy** | Nhận diện đúng thuốc → trả về cảnh báo tương tác thuốc–thức ăn rõ ràng, kèm nguồn |
| **Low-confidence** | Không chắc tên thuốc/thông tin → nói rõ "đây là phỏng đoán, chưa chắc" + đề nghị xác nhận với dược sĩ |
| **Failure** | Không nhận diện được thuốc / ngoài phạm vi → từ chối trả lời, hướng dẫn liên hệ bác sĩ |
| **Correction** | Người bệnh sửa lại tên thuốc → AI cập nhật và tra lại |

---

## 6. Failure mode
*Một lỗi nguy hiểm nhất và cách prototype xử lý.*

**Lỗi nguy hiểm nhất:** AI **đọc/đưa sai số lượng — sai liều thuốc** → người bệnh uống quá liều.

**Mitigation trong prototype:**
- Khi độ tin cậy về liều thấp → **không tự đưa con số**, yêu cầu người bệnh xác nhận lại từ đơn gốc (chỉnh sửa câu hỏi).
- **Chặn (refuse)** các câu hỏi nhạy cảm: hỏi thuốc hạn chế / kê toa đặc biệt, hỏi cách tự tăng liều → ngăn không trả lời, chuyển sang "hỏi bác sĩ".
- Mọi output gắn disclaimer cố định: *"Thông tin tham khảo, không thay thế chỉ định bác sĩ."*

---

## 7. Owner plan

| Vai trò | Phụ trách |
|---|---|
| Research / evidence | *(điền tên)* |
| SPEC | *(điền tên)* |
| Prototype | *(điền tên)* |
| Test (4 paths + failure) | *(điền tên)* |
| Demo | *(điền tên)* |
| Repo | *(điền tên)* |
