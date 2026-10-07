# Bằng chứng thực tế của bản tự học

Các file JSON được lấy từ GitHub Actions, API hoặc Azure CLI/SDK trước khi hạ tầng bị thu hồi. Chúng không thay thế yêu cầu ảnh chụp màn hình của rubric.

- `actions-buoc-2.json`, `report-buoc-2.json`: run CI trên 22.361 mẫu; F1 0,7149.
- `actions-buoc-3.json`, `report-buoc-3.json`: run CI trên 44.722 mẫu; F1 0,7354. Event là `workflow_dispatch`, chưa chứng minh trigger bởi push.
- `api-public.json`: API đã phản hồi ở Bước 2.
- `api-buoc-3.json`: API sau cập nhật; SHA256 model trên VM khớp artifact CI.
- `actions-quality-gate.json`, `report-quality-gate.json`, `quality-gate-preserved-model.json`: kiểm chứng mô hình yếu bị chặn và model đang phục vụ không bị ghi đè.
- `azure-before-cleanup.json`: bảy tài nguyên thuộc riêng nhóm lab.
- `blob-before-cleanup.json`: tên và kích thước object; không chứa SAS.
- `cleanup.json`: thời điểm thu hồi, xác nhận Azure không còn nhóm/tài nguyên lab, workflow bị tắt, Secrets/key bị gỡ và cổng MLflow đã ngừng lắng nghe.

Endpoint và resource ID trong bằng chứng là thông tin lịch sử. Dataset, DVC cache, `mlflow.db`, model mới nhất và venv được giữ cục bộ, không đưa các file lớn đó vào Git. Có thể đọc báo cáo và JSON mà không cần dựng lại Azure.
