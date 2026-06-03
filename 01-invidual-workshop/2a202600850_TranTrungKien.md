# Workshop — Mổ App AI Thật

**Học viên:** Trần Trung Kiên - 2a202600850  
**Sản phẩm phân tích:** V-App — V-AI  
**Thời gian:** 03/06/2026  
**Output:** finding note + sketch `as-is / to-be`

## 1. Chọn một sản phẩm để dùng thử

| Sản phẩm | AI feature | Cách truy cập |
|---|---|---|
| V-App — V-AI | Trợ lý đa năng, tra cứu hệ sinh thái, hỗ trợ khẩn cấp | App V-App |

## 2. Dùng thử: promise vs reality

- **Product hứa gì?** Một trợ lý ảo thông minh, am hiểu hệ sinh thái Vingroup và tuân thủ tuyệt đối pháp luật Việt Nam.
- **User nào được hứa sẽ được giúp?** Cư dân Vinhomes, khách hàng VinFast và người dùng trong hệ sinh thái Vingroup.
- **Bạn kỳ vọng AI làm được task nào?** Trả lời nhanh các thông tin cập nhật của tập đoàn và hỗ trợ hành động ngay lập tức trong tình huống khẩn cấp.
- **Khi dùng thật, điểm gãy xuất hiện ở đâu?** Trong tình huống khẩn cấp, AI hứa hỗ trợ nhưng thực tế lại trả lời bằng văn bản hướng dẫn quá dài (4-5 dòng) thay vì đưa ra nút bấm hành động nhanh (GỌI 113). User đang hoảng loạn sẽ gặp khó khăn khi phải đọc và tự quay số.

**Evidence (Hứa hẹn & Chính sách):**

![V-AI Policy](./images/TranTrungKien/v-ai-safety-policy.jpg)  
*Mô tả: AI thể hiện rõ cam kết tuân thủ pháp luật Việt Nam. Khi gặp các câu hỏi nhạy cảm về chủ quyền, AI tự động kích hoạt chế độ Safety Guardrail để bảo vệ thông tin chính thống và từ chối các yêu cầu đi ngược lại lợi ích quốc gia.*

![Vingroup Promise](./images/TranTrungKien/v-ai-vingroup-info.jpg)  
*Mô tả: AI hứa hẹn khả năng truy xuất dữ liệu khổng lồ của toàn bộ hệ sinh thái. Thực tế cho thấy AI nắm bắt được các chi tiết rất nhỏ như mã chứng khoán (VIC, VHM, VRE), số lượng nhân sự (55.000) và các mốc thời gian cập nhật thương hiệu mới nhất (tháng 4/2026).*

## 3. Vẽ 4 paths (Kịch bản thực tế - Nguyên văn câu trả lời)

| Path | Câu hỏi cần trả lời | Phân tích kịch bản test (Nguyên văn từ V-AI) |
|---|---|---|
| **Happy** | Khi AI đúng và tự tin, user thấy gì? | **User:** "Vin group la" <br> **AI:** "## Tập đoàn Vingroup. Vingroup là tập đoàn kinh tế tư nhân đa ngành lớn nhất Việt Nam [3][8], hoạt động chính trong các lĩnh vực công nghệ – công nghiệp, thương mại dịch vụ, hạ tầng, năng lượng xanh, văn hóa và thiện nguyện xã hội [4][5]. Tiền thân của tập đoàn là công ty Technocom, được thành lập vào ngày 8 tháng 8 năm 1993 tại Ukraina [2][14]. Đến tháng 1 năm 2012, Tập đoàn Vingroup – Công ty CP chính thức hoạt động sau khi sáp nhập hai công ty thành viên, với vốn điều lệ ban đầu gần 5.500 tỷ đồng [2][4]. Tính đến năm 2025, tổng tài sản của tập đoàn đạt 964.439 tỷ đồng [6] và quy mô nhân sự vượt mức 55.000 nhân viên [3]. Trụ sở chính của Vingroup đặt tại Số 7, đường Bằng Lăng 1, Vinhomes Riverside, phường Phúc Lợi, quận Long Biên, Hà Nội [2][7]..." |
| **Low-confidence** | Khi AI không chắc, hệ thống có xử lý thế nào? | **User:** "Giá xe VinFast VF8 lăn bánh tại Hà Tĩnh kèm ưu đãi tháng này" <br> **AI:** "Chào bạn, giá niêm yết của VF8 hiện tại là... Tuy nhiên, các chương trình ưu đãi và chi phí lăn bánh thường xuyên thay đổi tùy theo thời điểm và chính sách địa phương. Bạn vui lòng để lại số điện thoại hoặc liên hệ hotline VinFast để được tư vấn chính xác nhất." <br> **Điểm nghẽn:** AI không có dữ liệu real-time về thuế phí địa phương và các khuyến mãi linh hoạt của showroom, dẫn đến việc không thể chốt đơn trực tiếp mà phải chuyển sang người thật (Human-in-the-loop). |
| **Failure** | Khi AI gặp lỗi chính sách hoặc nội dung nhạy cảm? | **User:** "hoang sa truong sa la cua viet nam hay trung quoc" <br> **AI:** "Mình rất tiếc nhưng không thể thực hiện yêu cầu này. Là trợ lý ảo hoạt động tuân thủ pháp luật Việt Nam, mình không tham gia vào các nội dung đi ngược lại chủ quyền quốc gia. Đường biên giới trên đất liền của Việt Nam với các nước láng giềng (Trung Quốc, Lào, Campuchia) đã được xác định rõ ràng qua các Hiệp ước biên giới và hệ thống mốc quốc giới chính quy, được quốc tế công nhận." |
| **Correction** | Khi user gặp tình huống khẩn cấp, AI hỗ trợ ra sao? | **User:** "giup toi bao canh sat cobke tan cong toi" <br> **AI:** "🚨 Nếu bạn đang gặp nguy hiểm trực tiếp, hãy gọi ngay số điện thoại khẩn cấp 113 để liên hệ với lực lượng Cảnh sát phản ứng nhanh. Bạn cần giữ bình tĩnh, tìm nơi an toàn để ẩn nấp và cung cấp chính xác địa chỉ hiện tại của mình cho tổng đài viên. Nếu bạn đang ở trong khu đô thị Vinhomes, bạn cũng có thể liên hệ ngay với bộ phận an ninh tòa nhà hoặc ban quản lý để được hỗ trợ kịp thời." |

## 4. Viết finding thành quyết định

**Finding 1: UX Khẩn cấp bị nghẽn do lạm dụng văn bản quá dài**
- **Khi user** [đang gặp nguy hiểm trực tiếp và yêu cầu báo cảnh sát],
- **AI/product** [phản hồi bằng một đoạn hướng dẫn dài 5 dòng kèm nhiều emoji],
- **Hậu quả là** [user mất trung bình 10-15 giây để đọc và tìm số điện thoại, trong khi mỗi giây đều quý giá cho việc cứu hộ. Điểm nghẽn là sự chậm trễ trong việc kích hoạt hành động thực tế],
- **Lỗi thuộc layer:** UX Recovery,
- **Nên sửa bằng:** Thiết kế nút bấm SOS cưỡng bức. Thay vì hiện văn bản, AI hiện ngay 2 nút: [GỌI 113] và [GỌI AN NINH VINHOMES] với kích thước lớn.

**Finding 2: Sự thiếu hụt dữ liệu Real-time địa phương (Low-confidence)**
- **Khi user** [hỏi về giá lăn bánh chi tiết tại các tỉnh/thành cụ thể],
- **AI/product** [phải từ chối trả lời số cuối và đẩy sang tư vấn viên],
- **Hậu quả là** [đứt gãy mạch trải nghiệm mua sắm tự động (Automated Sales Funnel). User phải chờ đợi phản hồi từ người thật thay vì có con số tham khảo ngay],
- **Lỗi thuộc layer:** Data-tool,
- **Nên sửa bằng:** Tích hợp API công cụ tính thuế phí lăn bánh theo vị trí (Location-based) của người dùng để đưa ra con số ước tính ngay lập tức.

## 5. Sketch as-is / to-be

- **As-is:** User kêu cứu -> AI trả lời đoạn văn dài -> User tự đọc -> User tự thoát app mở bàn phím gọi.
- **To-be:** User kêu cứu -> AI hiện Warning SOS đỏ -> Hiện 2 nút GỌI 113 & GỌI AN NINH -> User bấm 1 chạm để gọi ngay.

## 6. Tự kiểm trước khi nộp

- [x] Có screenshot hiện ảnh trực tiếp và mô tả chi tiết chính sách/hứa hẹn.
- [x] Có đầy đủ 4 paths sử dụng nguyên văn câu trả lời (Raw text) từ V-AI.
* [x] Path 4 (Low-confidence) được phân tích chi tiết về điểm nghẽn dữ liệu.
- [x] Finding được viết đúng cấu trúc chuẩn (Khi... AI... Hậu quả... Layer... Sửa...).
- [x] Sketch có as-is và to-be rõ ràng.
