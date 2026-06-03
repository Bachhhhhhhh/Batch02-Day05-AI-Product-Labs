# Evidence Pack — AI trợ lý đọc & hiểu đơn thuốc

Nộp kèm thin SPEC cuối Day 05.

## 1. Nhóm và track

**Tên nhóm:** _(điền)_
**Track:** Health / Consumer AI assistant
**Product/app đã chọn:** AI trợ lý đọc & hiểu đơn thuốc cho người bệnh
**Build slice đang nghĩ:** Người bệnh hỏi "thuốc này có kỵ thức ăn/đồ uống nào không" → AI tra thông tin thuốc → trả về cảnh báo "nên / không nên dùng cùng", kèm câu bắt buộc hỏi bác sĩ/dược sĩ.

## 2. Self-use evidence

Nhóm tự dùng app/workflow và ghi lại điểm gãy.

| Observation | Screenshot/link | Path liên quan | Điều học được |
|---|---|---|---|
| Người nhà tự dùng lại đơn thuốc cũ / đơn của người khác vì thấy triệu chứng giống, không rõ có an toàn không | _(điền screenshot/ảnh đơn)_ | Failure | Người bệnh tự suy diễn khi không có bác sĩ → cần cảnh báo chống chỉ định |
| Hỏi "uống thuốc này có ăn được bưởi/uống rượu không" mà không biết tra ở đâu | _(điền)_ | Low-confidence | Nhu cầu tra tương tác thuốc–thức ăn rất thực tế |

## 3. User / review / social evidence

Nguồn có thể là review App Store/Play, group, comment, phỏng vấn nhanh, hoặc nguồn public khác.

| Quote / review / observation | Nguồn | User là ai? | Pain/failure mode |
|---|---|---|---|
| 15 nguy cơ khi dùng đơn thuốc của người khác: tương tác thuốc, dị ứng, sai liều theo cân nặng, chống chỉ định theo bệnh nền, hại gan/thận, kỵ thức ăn/rượu, thuốc hết hạn, che lấp triệu chứng | bvnguyentriphuong.com.vn | Người bệnh tự dùng thuốc ở nhà | Dùng thuốc sai cách → rủi ro sức khỏe thật |
| Bưởi/nước ép bưởi tương tác với hơn 50 loại thuốc; ăn bưởi cùng felodipin làm nồng độ thuốc trong máu tăng gấp 3 lần; uống cùng statin tăng nguy cơ tổn thương gan, cơ, suy thận | [Vinmec](https://www.vinmec.com/vie/bai-viet/canh-bao-buoi-co-tuong-tac-voi-cac-loai-thuoc-thong-thuong-vi) / [Sức khỏe & Đời sống](https://suckhoedoisong.vn/tuong-tac-bat-loi-cua-nuoc-buoi-voi-mot-so-loai-thuoc-169134508.htm) | Người bệnh dùng thuốc tại nhà, ăn uống thông thường | Không biết món ăn/đồ uống quen thuộc kỵ thuốc → tương tác nguy hiểm |
| Theo Bộ Y tế, 50–70% người dân từng tự mua và dùng kháng sinh không theo đơn; WHO ghi nhận VN có gần 300.000 ca tử vong liên quan kháng kháng sinh giai đoạn 2020–2023 | [Sở Y tế Hà Tĩnh](http://soyte.hatinh.gov.vn/tin-tuc-su-kien/thong-tin-y-te/duoc-my-pham-trang-thiet-bi-y-te/nguy-hiem-khon-luong-tu-viec-mua-thuoc-khong-ke-don-.html) | Người dân tự mua thuốc không qua bác sĩ | Tự ý dùng thuốc phổ biến → hại gan/thận, kháng kháng sinh |

Nếu chưa có nguồn ngoài nhóm, ghi rõ:

```text
Một phần là giả định. Nhóm sẽ kiểm bằng phỏng vấn 3–5 người bệnh có bệnh nền / dùng nhiều thuốc trước checkpoint M1 Day 06.
```

## 4. Competitor / analog evidence

| App / mô hình tham khảo | Họ xử lý task này thế nào? | Pattern học được | Có áp dụng trong 1 ngày không? |
|---|---|---|---|
| Drugs.com Interaction Checker | Nhập nhiều thuốc → liệt kê mức độ tương tác | Phân loại mức cảnh báo + nguồn | Có — bản tối giản 1 thuốc / 1 thức ăn |
| Long Châu / nhà thuốc online | Trang thông tin thuốc theo tên | Chuẩn hóa dữ liệu thuốc đầu vào | Có |
| _(điền)_ |  |  |  |

## 5. Evidence -> Insight

```text
Evidence nổi bật nhất:
BV Nguyễn Tri Phương — 15 nguy cơ khi dùng thuốc sai cách / dùng nhờ đơn người khác.

Insight:
User không chỉ gặp surface problem "không hiểu đơn thuốc".
Thật ra họ cần hỗ trợ ra quyết định an toàn ở khoảng trống sau khi rời phòng khám,
khi không có bác sĩ bên cạnh để hỏi "thuốc này dùng thế nào, kỵ gì, có hợp bệnh nền không".

Opportunity:
AI có thể giúp bằng cách tra thông tin thuốc và cảnh báo tương tác thuốc–thức ăn (augment),
luôn đẩy quyết định y khoa về bác sĩ.
```

## 6. Evidence đổi SPEC như thế nào?

- [ ] Đổi user chính.
- [x] Đổi pain statement.
- [x] Đổi build slice.
- [ ] Đổi Auto/Aug decision.
- [ ] Đổi 4 paths.
- [ ] Đổi failure mode.
- [ ] Đổi owner/test plan.

Ghi rõ 1-2 thay đổi quan trọng:

```text
Trước evidence, nhóm định làm "AI đọc/giải mã ký hiệu đơn thuốc khó đọc".
Sau evidence, nhóm đổi thành "AI tra thông tin thuốc + cảnh báo tương tác thuốc–thức ăn",
tập trung build slice vào câu hỏi "thuốc này kỵ thức ăn/đồ uống nào không".
Lý do: bằng chứng mạnh nhất (15 nguy cơ) cho thấy rủi ro thật nằm ở việc dùng thuốc sai cách
ở nhà, không phải chỉ ở việc đọc chữ bác sĩ.
```
