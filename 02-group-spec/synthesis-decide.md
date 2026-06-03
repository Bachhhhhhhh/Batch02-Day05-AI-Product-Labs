# Synthesis & Decide — AI trợ lý đọc & hiểu đơn thuốc

Điền theo `synthesis-decide-toolkit.md`, dựa trên evidence trong `evidence-pack.md`.

## 1. Gom evidence thành cụm

Gom theo workflow/pain (khớp 5 tình huống use case), mỗi cụm có nguồn ngoài nhóm.

| # | Cụm pain (workflow) | Evidence chính | Nguồn |
|---|---|---|---|
| 1 | **"Không hiểu cách dùng thuốc"** — uống sai liều/sai thời điểm | 7 sai lầm khi uống thuốc: bỏ thuốc, chia nhỏ sai, không uống hết đơn, tự tăng liều, dùng thuốc người khác | [Sức khỏe & Đời sống](https://suckhoedoisong.vn/7-sai-lam-thuong-gap-khi-uong-thuoc-va-cach-khac-phuc-169220801223146779.htm) |
| 2 | **"Không nhận biết tác dụng phụ"** — sớm/muộn | Gặp tác dụng phụ phải báo bác sĩ; phản ứng nặng (khó thở, sưng mặt/lưỡi, co giật) cần cấp cứu ngay | [Nhà thuốc Long Châu](https://nhathuoclongchau.com.vn/bai-viet/tac-dung-phu-cua-thuoc-co-nguy-hiem-khong-can-lam-gi-khi-gap-phai.html) |
| 3 | **"Không biết thuốc kỵ bệnh nền / món ăn"** | Tương tác thuốc–bệnh (NSAID tăng huyết áp), thuốc–thức ăn (bưởi tăng nồng độ thuốc gấp 3 lần) | [Việt Giải Trí](https://vietgiaitri.com/phong-tranh-tuong-tac-thuoc-trong-dieu-tri-benh-man-tinh-20250825i7518346) · [Vinmec](https://www.vinmec.com/vie/bai-viet/canh-bao-buoi-co-tuong-tac-voi-cac-loai-thuoc-thong-thuong-vi) |
| 4 | **"Tự ý đổi sang thuốc tương tự"** | Đổi sang thuốc "nhẹ hơn" theo mg là sai lầm; trùng/đối kháng hoạt chất, mất kiểm soát bệnh | [Sức khỏe & Đời sống](https://suckhoedoisong.vn/tu-y-doi-thuoc-nguy-hiem-nhu-the-nao-169251019195910586.htm) |
| 5 | **"Không biết cảnh báo/chống chỉ định của thuốc"** | Chống chỉ định = tuyệt đối không được dùng; cần đọc đúng tờ HDSD | [Nhà thuốc Long Châu](https://nhathuoclongchau.com.vn/bai-viet/tim-hieu-ve-chong-chi-dinh-va-cach-doc-to-huong-dan-su-dung-thuoc.html) |
| — | **"Tự dùng thuốc khi không có bác sĩ"** (nền chung) | 50–70% người dân tự mua/dùng kháng sinh không theo đơn; 15 nguy cơ dùng đơn người khác | [Sở Y tế Hà Tĩnh](http://soyte.hatinh.gov.vn/tin-tuc-su-kien/thong-tin-y-te/duoc-my-pham-trang-thiet-bi-y-te/nguy-hiem-khon-luong-tu-viec-mua-thuoc-khong-ke-don-.html) · [BV Nguyễn Tri Phương](https://bvnguyentriphuong.com.vn/kien-thuc-duoc-cho-cong-dong/15-nguyen-nhan-ban-khong-duoc-su-dung-theo-don-thuoc-cua-nguoi-khac) |

## 2. Insight

```text
Người bệnh tự dùng thuốc tại nhà không chỉ cần biết "thuốc tên gì".
Họ thật ra cần hỗ trợ ra quyết định an toàn ở khoảng trống không có bác sĩ,
vì cả 5 cụm evidence đều cho thấy một gốc chung: thiếu thông tin đáng tin tại thời điểm dùng thuốc
dẫn tới dùng sai cách, kỵ thức ăn/bệnh nền, tự đổi thuốc, hoặc bỏ qua chống chỉ định.
```

## 3. Opportunity

```text
Cơ hội là dùng AI để tra thông tin thuốc và cảnh báo (augment) cho 5 nhu cầu trên,
giúp người bệnh biết "nên / không nên / cần hỏi bác sĩ" trước khi hành động,
trong khi vẫn kiểm soát rủi ro bằng cách luôn đẩy quyết định y khoa về bác sĩ
và chặn các câu hỏi nhạy cảm (liều, đổi thuốc, thuốc hạn chế).
```

## 4. Chọn build slice — kiểm qua 5 câu hỏi

5 cụm trên đều có evidence, nhưng để demo được trong 1 ngày, **chốt 1 slice** từ cụm #3 (rủi ro cao, evidence mạnh nhất, output rõ ràng nhất).

**Slice:** Người bệnh hỏi "thuốc này có kỵ thức ăn/đồ uống nào không" → AI tra → trả về cảnh báo nên/không nên dùng cùng, kèm câu hỏi bác sĩ/dược sĩ.

| Câu hỏi | Đạt? | Vì sao |
|---|---|---|
| User cụ thể chưa? | ✅ | Người bệnh đang dùng thuốc tại nhà |
| Task đủ hẹp chưa? | ✅ | 1 thuốc × 1 loại thức ăn/đồ uống, demo được 3–5 phút |
| AI decision rõ chưa? | ✅ | Tra thông tin thuốc → có/không cảnh báo tương tác |
| Failure path rõ chưa? | ✅ | Thuốc không nhận diện được / hỏi liều → từ chối, đẩy về bác sĩ |
| Có evidence không? | ✅ | Cụm #3: tương tác bưởi–thuốc, NSAID–huyết áp |

> Cụm #1, #2, #4, #5 có evidence nhưng đưa vào backlog để giữ slice đủ nhỏ cho Day 06.

## 5. Quyết định: giữ / giảm scope / đổi hướng

| Tình huống | Áp dụng cho dự án |
|---|---|
| Rủi ro cao | **Chọn augmentation** — AI chỉ cảnh báo, không kê đơn/đổi liều |
| Ý tưởng quá rộng (5 use case) | **Giữ domain "đơn thuốc", cắt xuống 1 flow** (cụm #3) |
| Không demo được trong 1 ngày | Đưa cụm #1, #2, #4, #5 vào backlog |

➡️ **Quyết định: GIỮ, nhưng giảm scope** từ 5 use case về đúng 1 flow tương tác thuốc–thức ăn.

## 6. Câu chốt cuối

```text
Dựa trên evidence tương tác bưởi–thuốc, NSAID–bệnh nền và thống kê người dân tự dùng thuốc,
nhóm sẽ build prototype tra cảnh báo tương tác thuốc–thức ăn,
cho người bệnh đang dùng thuốc tại nhà,
để giải quyết việc dùng thuốc sai cách do không biết món ăn/đồ uống kỵ thuốc,
bằng cách AI tra thông tin thuốc và cảnh báo nên/không nên dùng cùng,
và sẽ test failure path: thuốc không nhận diện được hoặc câu hỏi về liều → từ chối và đẩy về bác sĩ.
```

## 7. Backlog — KHÔNG build trong Day 06

- (Cụm #1) Hướng dẫn cách dùng/mục đích/tác dụng đầy đủ của thuốc.
- (Cụm #2) Cảnh báo tác dụng phụ theo dòng thời gian (sớm/muộn).
- (Cụm #4) Gợi ý đổi sang thuốc tương tự.
- (Cụm #5) Tra cảnh báo/chống chỉ định toàn diện.
- Tra tương tác giữa nhiều thuốc cùng lúc (đa thuốc); OCR/giải mã đơn viết tay; chat tự do y khoa mở.
