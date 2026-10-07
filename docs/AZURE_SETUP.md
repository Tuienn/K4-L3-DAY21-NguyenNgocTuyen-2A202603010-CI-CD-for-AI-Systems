# Setup lab với Azure và Python 3.11

> **Bản lưu tự học:** hạ tầng được thu hồi ngày 08/10/2026. Xem `CHECKPOINTS.md` và `../nop-bai/bang-chung/cleanup.json` để kiểm tra kết quả. VM/IP/Blob cũ không còn dùng được; SAS, SSH deployment key và Secrets triển khai đã được gỡ. Workflow CI/CD bị tắt để không tự triển khai lại. Các lệnh dưới đây là hướng dẫn tham khảo khi chủ động dựng một lab mới.

Chạy lệnh từ thư mục gốc repository. Dùng venv hiện có; không tạo lại venv.

## 1. Môi trường cục bộ

```bash
source .venv/bin/activate
python --version                   # Python 3.11.x
python -m pip install -r requirements.txt
cp -n .env.example .env
set -a
source .env
set +a
```

File `.env` không tự được Python đọc: cần `source` như trên trong mỗi terminal mới.
`MLFLOW_ARTIFACT_ROOT` được `src/train.py` dùng khi tạo experiment. SQLAlchemy được
ràng buộc dưới 2.1 vì MLflow 2.13 dùng API pool không còn trong SQLAlchemy 2.1.
`ARTIFACT_BUCKET` là **tên container**, không phải tên Storage Account.

Venv đã có đủ thư viện sau khi agent setup. Không cần chạy lại `prepare_data.py`
nếu CSV đã tồn tại: script này sẽ ghi đè dữ liệu Bước 3 bằng batch ban đầu.

```bash
python -m pytest tests/ -v
python scripts/run_experiments.py    # Chỉ chạy khi cần thực nghiệm lại
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```

Mở http://localhost:5000, chọn experiment `adult-income`, bật các cột `f1_score`,
`accuracy`, `n_estimators`, `learning_rate`, `max_depth` rồi sort F1 giảm dần.
Chụp `nop-bai/anh-chup-man-hinh/01-mlflow-ui.png`.
Script thực nghiệm tự chọn F1 cao nhất và khôi phục model/report/params của run đó.

## 2. Đăng nhập và tài nguyên Azure

```bash
az account show --query '{subscription:name,id:id}' -o table
# Nếu hết phiên: az login --use-device-code
# Nếu cần đổi subscription: az account set --subscription '<SUBSCRIPTION_ID>'
gh auth status
```

Cần một Resource Group riêng cho lab, Storage Account có Blob container private,
và Azure VM Ubuntu chạy API. Cấu hình cụ thể sẽ được chốt trước khi tạo.
VM cần Python 3.11 với cùng `scikit-learn==1.4.2` và `joblib==1.4.2` như máy train.
Chỉ Bước 2 dùng cloud; huấn luyện chạy trên GitHub Actions, không chạy trên VM.

## 3. DVC trên Azure Blob

Sau khi có container, điền connection string vào `.env`, đặt tên container vào
`ARTIFACT_BUCKET` và nạp lại biến môi trường. Không gửi connection string vào chat.
DVC đọc biến `AZURE_STORAGE_CONNECTION_STRING`; không lưu secret trong `.dvc/config`.

```bash
set -a
source .env
set +a
dvc remote add -d labstore "azure://${ARTIFACT_BUCKET}/dvc"
dvc add data/train_batch1.csv data/holdout.csv data/train_batch2.csv
dvc push
```

Nếu DVC đã có remote `labstore`, dùng `dvc remote modify labstore url ...`.
Chỉ commit con trỏ `.csv.dvc`, cấu hình DVC, code và tài liệu; CSV không đưa vào Git.

## 4. Secrets và VM

Workflow cần 5 repository secrets:

- `STORAGE_CREDENTIALS`: Azure Blob connection string.
- `ARTIFACT_BUCKET`: tên container chứa `dvc/` và `artifacts/current/`.
- `SERVER_HOST`: public IP của VM.
- `SERVER_USER`: user triển khai trên VM.
- `SERVER_SSH_KEY`: SSH private key riêng cho deployment.

Connection string có thể chứa container SAS để giới hạn quyền vào container;
VM chỉ cần quyền đọc model. API dùng Azure Blob SDK để tải model khi khởi động.

VM cần có bản `src/serve.py` đúng với commit được triển khai, venv Python 3.11,
file môi trường được bảo vệ và systemd service `income-api`. `ExecStart` phải trỏ
vào Python của venv. User deployment cần quyền `sudo -n systemctl restart income-api`.
Workflow tự copy `src/serve.py` theo commit lên `/home/SERVER_USER/src/` trước
release rồi restart service. Provisioning/service sẽ được agent cấu hình ở bước cloud.

Pipeline: Unit Test → Train → Quality Gate → Release. Train chỉ lưu candidate vào
GitHub Actions artifacts. Release mới upload model vào Blob và restart VM sau khi
F1 lớp dương đạt 0.65. Model không đạt ngưỡng không ghi đè model đang phục vụ.
Kiểm tra `curl http://VM_IP:8080/healthz` và POST `/score` theo `tasks/buoc-2.md`.

## 5. Dữ liệu mới và nộp bài

Chỉ làm sau khi Bước 2 đã chạy thành công và đã lưu bằng chứng/số liệu.

```bash
python append_batch.py             # Chạy đúng một lần; không idempotent
dvc add data/train_batch1.csv
dvc push                          # Luôn trước git push
git add data/train_batch1.csv.dvc
git commit -m 'data: bổ sung 22361 mẫu dữ liệu mới (train_batch2)'
git push origin main
```

Lưu hai report thực tế từ Actions để so sánh, chụp đủ 5 ảnh theo
`nop-bai/anh-chup-man-hinh/README.md`, hoàn thiện `nop-bai/bao-cao.md` (450–550 từ,
không còn chú thích hướng dẫn). Không coi chỉ số chạy cục bộ là bằng chứng CI/CD.

Tham khảo API/credentials đã đối chiếu:
[Azure Blob SDK](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-python-get-started),
[DVC Azure remote](https://github.com/treeverse/dvc.org/blob/main/content/docs/user-guide/data-management/remote-storage/azure-blob-storage.md).

## Hạ tầng lịch sử trước khi thu hồi

- Resource Group: `rg-income-lab`, region `southeastasia`.
- VM: `income-api`, SKU `Standard_B2ats_v2`, 2 vCPU burstable, RAM 1 GiB.
- Ubuntu 24.04, Python 3.11.16, Standard HDD 30 GiB, swap 1 GiB.
- Public IP: `20.212.210.172`; SSH user: `azureuser`.
- Storage Account: `stincometuyen261008`; container private: `income-lab`.
- DVC đã push 3 dataset và phiên bản bổ sung batch2. Model seed ban đầu lấy từ MLflow cục bộ; sau đó CI/CD đã huấn luyện và triển khai lại thành công.
- Credential từng ở `.env`, SSH key ở `.secrets/income_deploy`, được Git ignore. Khi thu hồi, connection string được xóa và thư mục key được gỡ; VM từng dùng SAS chỉ đọc.
- SAS ban đầu có hạn 30 ngày; đã mất hiệu lực khi Storage Account bị xóa.
- Năm GitHub Secrets và hai biến SSH từng được cấu hình; đã gỡ khi thu hồi.
- NSG từng mở TCP 8080 public; endpoint lịch sử là `http://20.212.210.172:8080`, đã ngừng phục vụ.

Lệnh SSH lịch sử (chỉ có hiệu lực sau khi dựng lại và thay IP/key):

```bash
ssh -i .secrets/income_deploy -o UserKnownHostsFile=.secrets/known_hosts azureuser@20.212.210.172
```

Trong VM:

```bash
source ~/.venv/bin/activate
python --version
systemctl status income-api --no-pager
curl http://127.0.0.1:8080/healthz
```

Có thể dùng tunnel để thử API từ máy cá nhân, không mở cổng public:

```bash
ssh -i .secrets/income_deploy -o UserKnownHostsFile=.secrets/known_hosts \
  -N -L 127.0.0.1:18080:127.0.0.1:8080 azureuser@20.212.210.172
# Trong terminal khác:
curl http://127.0.0.1:18080/healthz
```

Khi nghỉ làm lab, giải phóng compute để tiết kiệm credit:

```bash
az vm deallocate -g rg-income-lab -n income-api
# Khi tiếp tục:
az vm start -g rg-income-lab -n income-api
```

Deallocate ngừng phí compute; đĩa, public IP và Blob Storage vẫn có thể tính phí.
Giá retail compute đã kiểm tra: 0,0118 USD/giờ, chưa gồm đĩa, IP và storage.
Nguồn: Azure Retail Prices API, SKU B2ats v2 tại southeastasia, loại Consumption.
Không mặc định rằng credit Students sẽ miễn toàn bộ các khoản phí này.
