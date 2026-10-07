# Trạng thái checkpoint — bản lưu tự học

Đối chiếu `tasks/tong-hop.txt` và ba hướng dẫn `tasks/buoc-*.md`. Các số liệu trong báo cáo lấy từ run thật; không thay bằng số liệu giả. Ngày kết thúc: 08/10/2026 (Việt Nam).

## Checkpoint 0 — môi trường

- [x] Venv Python 3.11, dependency huấn luyện/serving, Azure CLI đã đăng nhập.
- [x] Provider Azure, private Blob container làm DVC remote và nơi lưu model.
- [x] Không commit SAS hoặc SSH private key; credentials được thu hồi khi dừng lab.

## Checkpoint 1 — MLflow và lựa chọn mô hình

- [x] Ba lần chạy với tham số khác nhau, log params, F1 lớp dương, accuracy và model.
- [x] Chọn 200 cây, learning rate 0,1, max depth 5; F1 0,7149 vượt 0,65.
- [x] Giải thích vì sao accuracy cao nhất không đồng nghĩa F1 cao nhất.
- [x] Bằng chứng: `nop-bai/ket-qua-buoc-1.json`; database `mlflow.db` còn ở máy cục bộ, được Git ignore.

## Checkpoint 2 — DVC, CI/CD, VM và API

- [x] Dataset được version hóa bằng `.dvc` và đẩy lên Azure; giữ cache cục bộ để xem lại sau khi xóa remote.
- [x] 17 unit tests đã pass; workflow có Unit Test → Train → Quality Gate → Release.
- [x] Cả bốn job thành công ở [run Bước 2](https://github.com/Tuienn/K4-L3-DAY21-NguyenNgocTuyen-2A202603010-CI-CD-for-AI-Systems/actions/runs/37664834346).
- [x] Mô hình yếu F1 0,5907 bị Quality Gate chặn; Release skipped, hash model phục vụ giữ nguyên. Bằng chứng ở [run quality gate](https://github.com/Tuienn/K4-L3-DAY21-NguyenNgocTuyen-2A202603010-CI-CD-for-AI-Systems/actions/runs/37665927030).
- [x] FastAPI trên VM tải model từ Blob, `/healthz` và `/score` được gọi thành công qua public 8080.
- [x] JSON bằng chứng ở `nop-bai/bang-chung/`: actions, report, API và inventory Azure/Blob.

## Checkpoint 3 — bổ sung dữ liệu

- [x] Chạy `append_batch.py` đúng một lần: 22.361 → 44.722 mẫu; holdout vẫn 500 mẫu.
- [x] Cập nhật con trỏ DVC, push object trước git push; commit dữ liệu `b4648f9`.
- [x] [Run dữ liệu mới](https://github.com/Tuienn/K4-L3-DAY21-NguyenNgocTuyen-2A202603010-CI-CD-for-AI-Systems/actions/runs/37665877892) thành công đủ bốn job; F1 0,7354, accuracy 0,882. Hash model phục vụ khớp artifact CI, API phản hồi thành công.
- [x] Bảng so sánh trong `tasks/buoc-3.md` và báo cáo đã điền bằng hai report CI thật.
- [ ] Trigger tự động bởi push: chưa chứng minh được. GitHub không tạo run sau push; run kiểm chứng dùng `workflow_dispatch`. Không coi kích hoạt thủ công là đạt tiêu chí tự động hoàn toàn.

## Hồ sơ tự học

Báo cáo và các JSON được lưu để đọc lại. Chưa có đủ năm ảnh chụp màn hình đúng rubric; không dựng ảnh giả. Chưa nộp VLearn hoặc kiểm tra URL bằng cửa sổ ẩn danh. Bonus không thực hiện. Đây là bản lưu các kết quả đã kiểm chứng, không tuyên bố đủ toàn bộ điểm rubric.

## Thu hồi hạ tầng

Đã tắt workflow, gỡ năm Secrets và hai biến GitHub, xóa SAS/SSH deployment key cục bộ. Không còn tiến trình MLflow nghe cổng 5000. Azure đã xóa cả nhóm lab và bảy tài nguyên thuộc nhóm; dữ liệu/venv/model cục bộ được giữ để xem lại. Kết quả kiểm tra sau xóa được lưu ở `nop-bai/bang-chung/cleanup.json`. Hướng dẫn dựng lại ở `docs/AZURE_SETUP.md`; các IP và tên tài nguyên cũ chỉ có ý nghĩa lịch sử. Không chạy lại `append_batch.py` trên dữ liệu hiện tại vì script sẽ thêm trùng batch2.

## Xem lại cục bộ

Mở `nop-bai/bao-cao.md` và các JSON trong `bang-chung/` trước. Trên checkout hiện tại, CSV, DVC cache và model đã được giữ lại; `dvc checkout` có thể khôi phục từ cache mà không tải Azure. Khi muốn chủ động mở lại MLflow, dùng venv Python 3.11 và lệnh `mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000`. Không cần provisioning VM để đọc kết quả. Clone GitHub trên máy khác sẽ không có những artifact cục bộ được Git ignore; cần chuẩn bị lại dữ liệu hoặc sao chép cache/model trước khi chạy inference.
