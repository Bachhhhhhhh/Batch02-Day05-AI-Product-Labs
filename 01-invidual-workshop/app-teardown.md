# Workshop — Mổ App AI Thật

**Học viên:** Trần Trung Kiên - 2a202600850
**Sản phẩm phân tích:** V-AI (Vin AI Assistant)
**Thời gian:** 03/06/2026
**Output:** Finding note + 4 Paths Analysis

## 1. Chọn một sản phẩm để dùng thử

- **Sản phẩm:** V-AI
- **AI feature:** Trợ lý đa năng (Thông tin tập đoàn, hỗ trợ khẩn cấp, tra cứu pháp luật/chủ quyền).
- **Cách truy cập:** App V-App.

## 2. Dùng thử: promise vs reality

- **Product hứa gì?** Trợ lý thông minh, hiểu biết sâu rộng về hệ sinh thái Vingroup và tuân thủ pháp luật Việt Nam.
- **User nào được hứa sẽ được giúp?** Cư dân Vinhomes, khách hàng VinFast, và người dùng phổ thông tại Việt Nam.
- **Kỳ vọng:** AI trả lời nhanh, chính xác thông tin doanh nghiệp và có phản ứng phù hợp với các tình huống nhạy cảm hoặc khẩn cấp.
- **Thực tế (Reality):** 
    - AI cung cấp thông tin cực kỳ chi tiết về Vingroup (đến tận 2026).
    - AI có cơ chế "Safety Guardrail" rất tốt khi từ chối các câu hỏi nhạy cảm về chủ quyền nhưng vẫn khẳng định lập trường pháp lý.
    - Điểm gãy: Trong tình huống khẩn cấp ("bị tấn công"), AI chỉ đưa ra văn bản hướng dẫn dài, có thể gây khó khăn cho user đang hoảng loạn.

**Evidence (Ảnh đã phân loại):** 
- `images/TranTrungKien/v-ai-vingroup-info.jpg` (Kịch bản hỏi về Vingroup)
- `images/TranTrungKien/v-ai-safety-policy.jpg` (Kịch bản hỏi về chủ quyền)
- `images/TranTrungKien/v-ai-emergency-113.jpg` (Kịch bản khẩn cấp)

## 3. Vẽ 4 paths

| Path | Phân tích từ kịch bản của Kiên |
|---|---|
| **Happy** | Khi hỏi về "Vin group la", AI cung cấp data đầy đủ, có dẫn nguồn [1][2], thông tin cập nhật đến 14/04/2026 (Green SM). |
| **Low-confidence** | (Chưa thể hiện rõ trong kịch bản này, nhưng AI có xu hướng trả lời thẳng dựa trên data-văn bản có sẵn). |
| **Failure** | Khi hỏi về chủ quyền nhạy cảm, AI không "đoán" mà chuyển sang chế độ Safety: Từ chối trả lời trực tiếp nhưng đưa ra thông tin pháp lý chính thống. |
| **Correction** | Trong kịch bản khẩn cấp, AI cung cấp số 113 và gợi ý liên hệ An ninh Vinhomes (hành vi gợi ý dựa trên ngữ cảnh hệ sinh thái). |

## 4. Viết finding thành quyết định

### Finding 1: Thông tin hệ sinh thái cực tốt nhưng UX khẩn cấp chưa tối ưu
- **Khi user** báo đang bị tấn công (khẩn cấp),
- **AI/product** trả lời bằng một đoạn văn bản dài và yêu cầu user "giữ bình tĩnh, tìm nơi ẩn nấp",
- **Hậu quả là** user mất thời gian đọc trong lúc nguy hiểm.
- **Lỗi thuộc layer:** UX Recovery.
- **Nên sửa bằng:** Thêm nút bấm "GỌI NGAY 113" hoặc "GỌI AN NINH VINHOMES" ngay dưới câu trả lời thay vì chỉ đưa số điện thoại dạng text.

### Finding 2: Hiểu biết về Context doanh nghiệp vượt trội
- **Khi user** đặt câu hỏi về Vingroup, AI không chỉ đưa wiki cũ mà cập nhật được các thay đổi thương hiệu (Green SM).
- **Hệ quả:** Tạo lòng tin lớn về độ tươi của dữ liệu (Data freshness).
- **Lỗi thuộc layer:** Data-tool (Good).

## 5. Sketch as-is / to-be

- **As-is:** User kêu cứu -> AI trả lời text (dài) -> User tự đọc số -> User tự thoát app vào bàn phím gọi.
- **To-be:** User kêu cứu -> AI hiện Warning đỏ + 1 nút bấm "SOS gọi 113" + Tự động gửi vị trí GPS cho BQL Vinhomes (nếu trong khu vực).

## 6. Câu chốt cho SPEC
"Cần bổ sung một **Emergency Interface** (giao diện khẩn cấp) với các nút hành động (Call/GPS) thay vì chỉ dùng văn bản khi AI nhận diện được intent nguy hiểm đến tính mạng."
