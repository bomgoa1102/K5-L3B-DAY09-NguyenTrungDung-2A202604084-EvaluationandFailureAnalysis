# Kiểm định judge

Mỗi judge được chạy lại trên 100 nhãn công khai; FAIL là lớp dương. Ngưỡng yêu cầu: κ ≥ 0,6, precision ≥ 0,8 và recall ≥ 0,7.

| Judge | TP | FP | FN | TN | κ | Precision | Recall | Quyết định |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| tone_ok | 24 | 4 | 6 | 66 | 0,757 | 0,857 | 0,800 | Có thể dùng trên tập replay này |
| helpful | 9 | 0 | 21 | 70 | 0,375 | 1,000 | 0,300 | Loại khỏi gate |

Tỷ lệ lỗi quan sát của tone là 0,28; sau hiệu chỉnh Rogan–Gladen là 0,30. Judge helpful bỏ sót 21 trong 30 lỗi theo nhãn người; precision cao không bù được recall và κ thấp.

| Case | Judge | Người | Phân xử và điều chỉnh rubric |
|---|---|---|---|
| H-008 | PASS | FAIL | Theo nhãn người; quy định rõ cách xưng hô thân mật và từ “check” không phù hợp chuẩn giọng điệu. |
| H-017 | PASS | FAIL | Theo nhãn người; bổ sung ví dụ dùng “nha” quá thân mật khi thông báo hoàn tiền. |
| H-029 | PASS | FAIL | Theo nhãn người; đánh dấu chỉ dẫn thiếu tôn trọng như “không cần nhắn thêm”. |
| H-042 | FAIL | PASS | Theo nhãn người; câu ngắn gọn, lịch sự nêu số tiền và thời gian là chấp nhận được. |
| H-051 | FAIL | PASS | Theo nhãn người; chỉ dùng một từ mượn không tự động là lỗi giọng điệu. |

Các phân xử dựa trên nhãn được cung cấp, không phải lượt đánh giá độc lập mới. Tập replay công khai không phải tập held-out; cần thu thập nhãn người mới theo cách đánh giá mù trước khi dùng trong thực tế.
