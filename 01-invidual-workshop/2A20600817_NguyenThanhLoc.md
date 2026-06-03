# Case Study: Phân tích Neo AI Chatbot (Vietnam Airlines)

---
Họ Tên: Nguyễn Thành Lộc - 2A202600817
## 📱 Thông tin chung
* **Ứng dụng:** Neo AI Chatbot (Vietnam Airlines)
* **Chủ đề:** Tra cứu chính sách hành lý theo hạng hội viên Lotusmiles.
* **Lỗi phát hiện:** **Hallucination (Ảo tưởng thông tin)** - Tự tạo ra thực thể (entity) không tồn tại và suy diễn quyền lợi đi kèm.

---

## 🔍 Chi tiết Case Study & Evidence

### 💬 Query thử nghiệm (User Input)
> "Tôi là hội viên hạng Kim Cương Đen, được miễn bao nhiêu kg hành lý?"

### 🤖 Phản hồi của Neo (Actual Output)
> ❌ *"Với hạng hội viên Kim Cương Đen, quý khách được tăng thêm 01 kiện hành lý ký gửi, trọng lượng 23kg..."*

### ⚠️ Phân tích vấn đề
1. **Thực tế:** Hạng hội viên **"Kim Cương Đen"** hoàn toàn **không tồn tại** trong chương trình khách hàng thân thiết Lotusmiles của Vietnam Airlines (chỉ có các hạng: *Bạc*, *Titan*, *Vàng*, *Bạch Kim*).
2. **Hành vi sai lệch của Chatbot:**
   * Không kiểm tra tính hợp lệ của hạng hội viên trong cơ sở dữ liệu (knowledge base).
   * Tự động sinh (hallucinate) ra quyền lợi hành lý cho một hạng thẻ giả lập.
   * Phản hồi với độ tự tin (confidence score) rất cao, dễ gây hiểu lầm nghiêm trọng về mặt chính sách hãng.
3. **Mức độ nghiêm trọng:** **Cao (Critical)** - Ảnh hưởng trực tiếp tới trải nghiệm khách hàng tại sân bay và uy tín thương hiệu của hãng hàng không quốc gia.

---

## 🔄 So sánh Luồng Vận Hành (Flow Comparison)

### 1. Luồng Hiện Tại (As-Is Flow) - Gặp lỗi Validation

    A[User: Tôi là hội viên Kim Cương Đen] --> B(LLM nhận Query)
    B --> C{Kiểm tra Entity hạng hội viên?}
    C -->|Bỏ qua Validation| D[LLM tự suy diễn thông tin & quyền lợi]
    D --> E[Trả lời sai thực tế: Được tăng thêm 1 kiện 23kg]
    

* **Điểm gãy (Failure Point):** *Validation Entity Failure*. Chatbot không đối chiếu thực thể `Kim Cương Đen` với danh mục chuẩn mà trực tiếp đẩy qua mô hình LLM để đoán câu trả lời.

---

### 2. Luồng Cải Tiến Mong Muốn (To-Be Flow) - Kiểm soát chặt chẽ Entity

    A[User: Tôi là hội viên Kim Cương Đen] --> B(Trích xuất Entity: Kim Cương Đen)
    B --> C{Đối chiếu Danh mục chuẩn Lotusmiles}
    C -->|Không Khớp / Không Tồn Tại| D[Kích hoạt luồng Fallback / Clarification]
    C -->|Khớp| E[Truy vấn Knowledge Base & Trả kết quả]
    D --> F[Yêu cầu User làm rõ thông tin & gợi ý hạng hợp lệ]
    

#### 💡 Kịch bản Phản hồi To-Be:
> 💬 *"Tôi không tìm thấy hạng hội viên **Kim Cương Đen**. Chương trình Lotusmiles hiện tại bao gồm các hạng: **Bạc**, **Titan**, **Vàng**, và **Bạch Kim**. Quý khách vui lòng cho biết mình đang sở hữu hạng thẻ nào để tôi hỗ trợ chính xác nhất?"*

---

## 🛠️ Đề xuất Giải pháp & Quyết định Sản phẩm (Product Decisions)

> **Quyết định Sản phẩm Cốt lõi (Product Decision):**
> *Ưu tiên độ chính xác (Accuracy) hơn độ trôi chảy (Fluency) đối với các thông tin liên quan đến chính sách, quy định và quyền lợi khách hàng.*

### 📋 Kế hoạch hành động cụ thể:
1. **Entity Extraction & Validation:**
   * Tách biệt bước nhận diện thực thể (Hạng hội viên) trước khi gửi qua LLM.
   * Xây dựng danh mục thẻ cứng (Whitelist) bao gồm: `Bạc / Silver`, `Titan / Titanium`, `Vàng / Gold`, `Bạch Kim / Platinum`.
2. **Strict Grounding:**
   * Áp dụng kỹ thuật RAG (Retrieval-Augmented Generation) nghiêm ngặt. Nếu thực thể không khớp với dữ liệu trong whitelist/knowledge base, hệ thống phải chặn (block) không cho LLM suy diễn tự do.
3. **Conversational Repair (Sửa lỗi hội thoại):**
   * Thiết kế luồng hội thoại fallback thông minh để hướng dẫn người dùng nhập đúng thông tin thay vì từ chối dịch vụ một cách máy móc.
