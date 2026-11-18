# Phân tích trace: C-002@11

Trial `seeded_regression C-002@11` (xem `reports/eval_seeded_regression.json`): grader của Lab 8 báo sai trạng thái. Ledger ghi một khoản hoàn 20.000 đồng, trong khi nhãn yêu cầu từ chối và không hoàn tiền. Câu trả lời báo đã hoàn 20.000 đồng.

Bước sai đầu tiên là **sự kiện 3, `model_override`, `{"delay_days": 5}`**: thông tin từ ticket ghi đè dữ kiện cơ sở dữ liệu trả về ở sự kiện 2 (`investigator`). Sự kiện 1 chỉ bàn giao công việc, còn sự kiện 2 tra cứu dữ liệu; cả hai chưa thay đổi dữ kiện. Sự kiện 4 báo giá 20.000 đồng và sự kiện 6 thông báo hoàn tiền là hệ quả về sau. Đây là FM-03.

Ở đối chứng `fixed` với cùng claim và seed, không có sự kiện ghi đè: sự kiện 3 báo giá bằng 0, sự kiện 4 từ chối yêu cầu và ledger vẫn bằng 0. Test `src/tests/test_lab9_regression_case.py::test_ticket_override_regression` kiểm tra cả hai trace và kết quả. Trace chứng minh hành vi ghi đè và kết quả quan sát được, nhưng không chứng minh quá trình suy luận nội bộ của mô hình.
