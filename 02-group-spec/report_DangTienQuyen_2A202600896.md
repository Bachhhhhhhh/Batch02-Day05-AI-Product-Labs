# Báo Cáo Công Việc Của Thành Viên: Đặng Tiến Quyền
**Mã Sinh Viên:** 2A202600896
**Vai trò phụ trách (Day 06):** Prototype (Tra cứu Tương tác Thuốc-Thức ăn) & Tích hợp RAG

---

## 1. Tích Hợp Vector Database (RAG) Giữ Nguyên Cấu Trúc
- **Vấn đề:** Khi pull code từ `origin/main` của nhóm, thư mục Vector DB và cấu trúc app bị xung đột.
- **Giải quyết:** Tôi đã cherry-pick thư mục `vector_db` và file `data/sample_drugs.json` vào nhánh hiện tại mà không làm mất cấu trúc thư mục `app/` cốt lõi. Sau đó chạy thành công kịch bản `build_vector_db.py` để nhúng dữ liệu vào ChromaDB.
- **Tích hợp:** Import hàm `search_drugs` vào `app/services/chat_service.py` để mỗi câu hỏi của người dùng đều được đối chiếu với cơ sở dữ liệu y khoa của nhà thuốc.

## 2. Dạy lại AI (Prompt Engineering) theo Chuẩn Thin Spec
Dựa trên tài liệu `thin-spec.md`, tôi đã cập nhật System Prompt của 2 LLM (Gemini 1.5 và GPT-4o-mini) để giải quyết triệt để bài toán:
- **Happy Path (Tương tác thuốc-thức ăn):** Khi hỏi *“Uống Paracetamol với cà phê được không?”*, AI tự động đối chiếu dữ liệu RAG, đưa ra lời khuyên "Nên / Không nên" và bắt buộc ghim cảnh báo: *"Vui lòng tham khảo ý kiến bác sĩ/dược sĩ"*.
- **Xử lý Failure Mode Nguy Hiểm (Hỏi liều lượng):** Xây dựng rào chắn an toàn (Guardrails) cực kỳ khắt khe. Nếu người dùng hỏi *“Uống mấy viên?”* hay *“Ngày uống mấy lần?”*, AI sẽ lập tức chốt chặn, ép `is_emergency = true` để hiển thị cảnh báo đỏ trên giao diện và từ chối kê liều.
- **Đồng bộ Nguồn trích xuất (Self-Filtering):** Loại bỏ tình trạng RAG trả về nguồn rác. Ép AI tự trả về danh sách các nguồn nó thực sự sử dụng để hiển thị lên UI, đảm bảo mục **"Dữ liệu trích xuất từ"** luôn chính xác 100%.

## 3. Cải Tiến Giao Diện Người Dùng (Frontend - app.js & index.html)
- **Medical Disclaimer:** Viết mã JavaScript tự động đính kèm dòng chữ y khoa cảnh báo trách nhiệm ở dưới mọi tin nhắn của AI.
- **Custom Toast Notification:** Loại bỏ thông báo `alert()` gây lỗi trình duyệt. Lập trình một hệ thống thông báo dạng Toast trượt mượt mà (hiệu ứng CSS) khi người dùng ấn nút "Thêm vào giỏ hàng" hoặc "Xem trên Long Châu".
- **Bảng Cấu Hình Demo:** Đổi tên và thay đổi các Preset Button ở cột bên phải để hoàn toàn khớp với kịch bản kiểm thử 4 Paths (Happy, Low-confidence, Failure Mode). Giúp Giám khảo/Mentor có thể click test trực tiếp chỉ trong 3 giây.

## 4. Xây Dựng Module Theo Dõi Tài Nguyên AI (AI Resource Tracker)
(Tính năng Bonus Đột Phá)
- Tự thiết kế và lập trình module `app/core/ai_tracker.py` bằng Design Pattern (Context Manager / Decorator).
- Tích hợp ghi log bất đồng bộ (Threading Asynchronous) để không chặn Web Server.
- Đo lường chi tiết mọi request gọi API: *Latency, Token Đầu vào/Đầu ra, Chi phí (USD), và phần trăm CPU/RAM* tiêu thụ ngay trong tiến trình hiện tại bằng thư viện `psutil`.
- Xuất dữ liệu đạt chuẩn JSONL (`ai_resource_audit.jsonl`), sẵn sàng cho các Dashboard đánh giá hệ thống (ELK Stack / Grafana).

---
*Báo cáo được tạo và lưu trữ trên Repository để làm minh chứng đánh giá cá nhân (Evidence) cho Buổi Demo Day 06.*
