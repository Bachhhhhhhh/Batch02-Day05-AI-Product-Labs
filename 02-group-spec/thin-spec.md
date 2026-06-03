# Thin SPEC — AI trợ lý đọc & hiểu đơn thuốc

Bản cam kết đủ rõ để sáng Day 06 build ngay. Dựa trên `evidence-pack.md` và `synthesis-decide.md`.

## 1. Track, product/app và user

**Track:** Health / Consumer AI assistant
**Product/app thật:** AI trợ lý đọc & hiểu đơn thuốc cho người bệnh
**User cụ thể:** Người bệnh đang dùng thuốc tại nhà, không có bác sĩ/dược sĩ bên cạnh để hỏi
**Nhóm có phải user thật không?** Có một phần — thành viên/người nhà từng tự dùng thuốc và băn khoăn "thuốc này ăn/uống cùng món gì được không". Khác ở chỗ người bệnh mạn tính/cao tuổi gặp rủi ro nặng hơn → cần kiểm bằng phỏng vấn ngoài nhóm.

## 2. Evidence summary

| Evidence | Nguồn | User/pain nói lên điều gì? | SPEC phải đổi gì? |
|---|---|---|---|
| Bưởi tương tác >50 loại thuốc; dùng cùng felodipin tăng nồng độ gấp 3 lần; cùng statin nguy cơ suy thận | [Vinmec](https://www.vinmec.com/vie/bai-viet/canh-bao-buoi-co-tuong-tac-voi-cac-loai-thuoc-thong-thuong-vi) | Món ăn/đồ uống quen thuộc có thể kỵ thuốc mà người bệnh không biết | Chốt build slice vào tương tác thuốc–thức ăn |
| 50–70% người dân tự mua/dùng kháng sinh không theo đơn; ~300.000 ca tử vong liên quan kháng kháng sinh 2020–2023 | [Sở Y tế Hà Tĩnh](http://soyte.hatinh.gov.vn/tin-tuc-su-kien/thong-tin-y-te/duoc-my-pham-trang-thiet-bi-y-te/nguy-hiem-khon-luong-tu-viec-mua-thuoc-khong-ke-don-.html) | Tự dùng thuốc không bác sĩ rất phổ biến, hậu quả nặng | Bắt buộc đẩy quyết định y khoa về bác sĩ |
| Tương tác thuốc–bệnh: NSAID làm tăng huyết áp ở người tăng huyết áp | [Việt Giải Trí](https://vietgiaitri.com/phong-tranh-tuong-tac-thuoc-trong-dieu-tri-benh-man-tinh-20250825i7518346) | Bệnh nền ảnh hưởng độ an toàn của thuốc | Output luôn kèm "hỏi bác sĩ nếu có bệnh nền" |

## 3. Pain statement

```text
User người bệnh dùng thuốc tại nhà đang gặp khó ở bước "biết món ăn/đồ uống nào kỵ thuốc",
vì không có nguồn tra cứu đáng tin tại thời điểm dùng thuốc và không có bác sĩ bên cạnh,
dẫn tới dùng thuốc sai cách → tương tác nguy hiểm (tăng nồng độ thuốc, hại gan/thận).
Bằng chứng chính là bài Vinmec/Sức khỏe & Đời sống về tương tác bưởi–thuốc và NSAID–huyết áp.
```

## 4. Build slice

```text
Cho người bệnh đang dùng thuốc tại nhà và muốn biết thuốc có kỵ thức ăn/đồ uống nào không,
prototype sẽ dùng AI để tra thông tin thuốc và đối chiếu tương tác thuốc–thức ăn (augment),
tạo ra cảnh báo "nên / không nên dùng cùng" kèm câu bắt buộc hỏi bác sĩ/dược sĩ,
và xử lý failure mode (thuốc không nhận diện được / hỏi về liều) bằng từ chối trả lời và đẩy về bác sĩ.
```

## 5. Auto/Aug decision

- [x] **Augmentation:** AI gợi ý/cảnh báo, user quyết cuối (và xác nhận với bác sĩ).
- [ ] Conditional automation
- [ ] Automation

**Lý do chọn:** Rủi ro y khoa cao — sai sót có thể gây hại sức khỏe; AI chỉ cung cấp thông tin tham khảo, không được tự kê đơn/đổi liều.
**Human role:** decider (người bệnh) + rescuer (bác sĩ/dược sĩ cho mọi quyết định y khoa).

## 6. Four paths

| Path | Prototype phải thể hiện gì? |
|---|---|
| Happy | Nhận diện đúng thuốc → trả về cảnh báo tương tác thuốc–thức ăn rõ ràng, kèm nguồn + disclaimer |
| Low-confidence | Không chắc tên thuốc/thông tin → nói rõ "đây là phỏng đoán, chưa chắc" + đề nghị xác nhận với dược sĩ |
| Failure | Không nhận diện được thuốc / ngoài phạm vi → từ chối trả lời, hướng dẫn liên hệ bác sĩ |
| Correction | Người bệnh sửa lại tên thuốc → AI cập nhật và tra lại |

## 7. Failure mode nguy hiểm nhất

```text
Nếu user hỏi về liều lượng (vd "uống mấy viên") hoặc dùng tên thuốc mờ/sai,
AI có thể đưa sai số lượng / sai liều,
hậu quả là người bệnh uống quá liều → ngộ độc, hại gan/thận.
Prototype sẽ xử lý bằng: từ chối đưa con số liều (ask again + yêu cầu xác nhận từ đơn gốc),
chặn câu hỏi về thuốc hạn chế, và luôn show source + disclaimer "không thay thế chỉ định bác sĩ".
Owner kiểm thử path này là [tên thành viên].
```

## 8. Owner plan cho sáng Day 06

| Thành viên | Việc phụ trách | Bằng chứng cần có trong repo |
|---|---|---|
| DƯƠNG QUANG KHẢI — 2A202600708 | Research / evidence + viết doc | evidence-pack.md với link nguồn ngoài nhóm; thin-spec.md + synthesis-decide.md |
| _(điền)_ | SPEC | thin-spec.md + synthesis-decide.md |
| _(điền)_ | Prototype | prototype tra tương tác thuốc–thức ăn (1 thuốc × 1 món) |
| Vũ Xuân Bách - 2A202600776 | Test / failure path | log test 4 paths + case hỏi liều bị từ chối |
| _(điền)_ | Demo script / repo | kịch bản demo 3–5 phút + README |
