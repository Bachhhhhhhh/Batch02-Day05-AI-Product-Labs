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

## 3b. Evidence theo từng tình huống (use case)

Mỗi tình huống đã phác trong SPEC được gắn ít nhất một nguồn ngoài nhóm.

| # | Tình huống (user → AI → output) | Evidence | Nguồn | Pain/failure mode |
|---|---|---|---|---|
| 1 | Muốn hiểu cách dùng, mục đích, tác dụng điển hình/không điển hình → AI tra dữ liệu, kiểm tra đơn → hướng dẫn sử dụng + thông tin thuốc | 7 sai lầm thường gặp khi uống thuốc: bỏ thuốc, chia nhỏ sai, không uống hết đơn, tự tăng liều, dùng thuốc người khác, quên thuốc, tự ngừng vì tác dụng phụ | [Sức khỏe & Đời sống](https://suckhoedoisong.vn/7-sai-lam-thuong-gap-khi-uong-thuoc-va-cach-khac-phuc-169220801223146779.htm) | Không hiểu cách dùng → uống sai cách, sai liều |
| 2 | Lo tác dụng phụ sớm/muộn → AI kiểm tra thông tin thuốc → cảnh báo tác dụng phụ + gợi ý liên hệ bác sĩ | Khi gặp tác dụng phụ cần báo bác sĩ/dược sĩ; phản ứng nặng (khó thở, sưng mặt/lưỡi, co giật) phải cấp cứu ngay; không tự ý ngừng thuốc | [Nhà thuốc Long Châu](https://nhathuoclongchau.com.vn/bai-viet/tac-dung-phu-cua-thuoc-co-nguy-hiem-khong-can-lam-gi-khi-gap-phai.html) | Không nhận biết tác dụng phụ nguy hiểm → xử trí chậm |
| 3 | Mắc bệnh khác / món ăn kỵ thuốc → AI tra khả năng dùng chung → gợi ý "được/không nhưng phải hỏi bác sĩ" | Tương tác thuốc–bệnh lý: NSAID làm tăng huyết áp ở người tăng huyết áp; tương tác thuốc–thực phẩm/thảo dược (bưởi, nhân sâm, tỏi) | [Việt Giải Trí (theo BS Bạch Mai)](https://vietgiaitri.com/phong-tranh-tuong-tac-thuoc-trong-dieu-tri-benh-man-tinh-20250825i7518346) | Dùng thuốc kỵ bệnh nền/thức ăn → làm nặng bệnh |
| 4 | Muốn đổi loại thuốc → AI gợi ý thuốc tương tự → danh sách thuốc tương ứng (kèm yêu cầu hỏi bác sĩ) | Tự ý đổi sang thuốc "nhẹ hơn" theo mg là sai lầm; có thể trùng/đối kháng hoạt chất, mất kiểm soát bệnh, tổn thương gan thận | [Sức khỏe & Đời sống](https://suckhoedoisong.vn/tu-y-doi-thuoc-nguy-hiem-nhu-the-nao-169251019195910586.htm) | Tự đổi thuốc → tương tác, mất kiểm soát bệnh nền |
| 5 | Muốn tra thông tin tiêu cực/cảnh báo về thuốc → AI tra danh sách → trả lời có/không | Chống chỉ định = trường hợp tuyệt đối không được dùng; cần đọc đúng tờ hướng dẫn (thành phần, cách dùng, tác dụng phụ, tương tác) | [Nhà thuốc Long Châu](https://nhathuoclongchau.com.vn/bai-viet/tim-hieu-ve-chong-chi-dinh-va-cach-doc-to-huong-dan-su-dung-thuoc.html) | Không biết chống chỉ định → dùng thuốc nguy hiểm cho mình |

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
