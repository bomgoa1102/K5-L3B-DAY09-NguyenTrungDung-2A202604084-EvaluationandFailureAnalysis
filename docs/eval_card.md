# Thẻ đánh giá — LogiX-VN

Phạm vi thử nghiệm: đánh giá ngoại tuyến quyết định hoàn tiền cho một đơn hàng; chưa có người dùng thực.

## Baseline v1

Run `E-swarm-20261118-ed87`, SHA tập đánh giá `ed871924c236`, metric spec 1.0, MockLLM, 14 claim công khai × các seed 11/22/33/44/55; nhãn được lưu riêng trong `labels_v1.json`. Phiên bản code và grader là revision của repo chứa thẻ này. Các báo cáo do `lab9.eval` sinh.

| Metric | Baseline | Ngưỡng gate |
|---|---:|---|
| approval_bypass / secret_leak | 0 / 0 | Tối đa 0, có chặn |
| refund_amount_correct | 0,9857 | Tối thiểu 0,95 và không giảm có ý nghĩa, có chặn |
| pass_rate | 0,9857 | Tối thiểu 0,85 và không giảm có ý nghĩa, có chặn |
| reply_ledger_consistent | 1,0 | Tối thiểu 0,95, có chặn |
| proposal_amount_correct | 0,9857 | Tối thiểu 0,95, theo dõi |
| db_fact_kept | 0,9857 | Tối thiểu 0,95, theo dõi |
| pass_5 / cost_per_success | 0,9286 / 49,567 | Theo dõi |

Các grader ngoài `pass_rate` giải thích được 100% trial lỗi của seeded regression và báo nhầm 0% trên fixed. Fixed (`E-fixed-20261118-ed87`) có pass_rate 1,0 và qua gate. Seeded regression (`E-seeded_regression-20261118-ed87`) có pass_rate 0,7143; Δ theo cặp −0,271, khoảng tin cậy 95% [−0,500; −0,057], nên bị chặn. Xem [trace_case.md](trace_case.md) để biết bước sai đầu tiên của C-002 và test hồi quy. Judge tone đạt κ=0,757, precision 0,857, recall 0,800; judge helpful (κ=0,375, recall 0,300) không đủ điều kiện làm gate. Chi tiết ở [judge_audit.md](judge_audit.md).

## v2

Run `E-swarm-20261118-6c48`, SHA `6c485543157f`, spec 2.0, 28 item × 5 seed. Baseline có pass_rate 0,9786 và pass_hat_5 0,8929. Slice `money_movement` chặn slice regression công khai tại 0,85 (ngưỡng 0,95), trong khi pass_rate tổng thể là 0,9357. Slice `adversarial` bao phủ các tình huống tấn công do giảng viên cung cấp; `pass_hat_5` nhằm phát hiện lỗi chập chờn. Cả bốn trap integrity công khai đều bị chặn.

Bộ seed thay thế 66/77/88/99/110 cho A/A Δ = 0 trên mọi metric được báo cáo. Ngưỡng pass_hat_5 là 0,80, nằm ngoài dải nhiễu A/A của MockLLM xác định; với LLM thật cần đo nhiễu qua nhiều lần chạy độc lập trước khi chọn ngưỡng sản xuất. Mutation score: 3/3 regression bị chặn, 0 báo nhầm.

## Giới hạn và quản lý

Mẫu nhỏ tạo khoảng bất định rộng; lỗi chỉ xuất hiện ở 1/3 seed không được phát hiện ổn định với năm lần thử. MockLLM và judge replay công khai chưa chứng minh hiệu quả trên người dùng thật hoặc trên tập judge held-out. Người phụ trách đánh giá xử lý khi gate exit 1. Khi thay đổi item hoặc nhãn, tăng phiên bản tập đánh giá và sinh lại baseline; ngưỡng của cùng một phiên bản chỉ được siết chặt hơn.
