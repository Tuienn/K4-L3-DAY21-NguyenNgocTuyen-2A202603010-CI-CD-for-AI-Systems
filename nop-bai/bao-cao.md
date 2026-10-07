# Báo Cáo Lab Day 21 - CI/CD cho AI Systems

| | |
|---|---|
| Họ và tên | Nguyen Ngoc Tuyen |
| MSSV | 2A202603010 |
| Lớp / Khóa | K4 |
| Repo GitHub | https://github.com/Tuienn/K4-L3-DAY21-NguyenNgocTuyen-2A202603010-CI-CD-for-AI-Systems |
| Ngày nộp | 08/10/2026 |

---

## 1. Bộ Siêu Tham Số Đã Chọn và Lý Do

| Lần chạy | n_estimators | learning_rate | max_depth | f1_score | accuracy |
|---|---|---|---|---|---|
| 1 | 100 | 0.1 | 3 | 0.7109 | 0.8780 |
| 2 | 50 | 0.05 | 2 | 0.6051 | 0.8460 |
| 3 | 200 | 0.1 | 5 | 0.7149 | 0.8740 |

**Bộ siêu tham số đã chọn:** `n_estimators=200`, `learning_rate=0.1`, `max_depth=5`.

**Lý do:** Bộ 200 cây, độ sâu 5 đạt F1 cao nhất (0,7149), vượt ngưỡng 0,65. Bộ mặc định có accuracy cao nhất (0,8780) nhưng F1 thấp hơn (0,7109), nên chọn theo accuracy sẽ chọn nhầm bộ so với mục tiêu lab. Bộ 50 cây với learning rate 0,05 và độ sâu 2 đạt F1 0,6051: cấu hình này chưa đủ khả năng học. Learning rate nhỏ thường cần nhiều cây hơn; các run chưa tách riêng tác động từng tham số.

---

## 2. Vì Sao Ngưỡng Chất Lượng Đặt Trên F1 Chứ Không Phải Accuracy

Dữ liệu Adult mất cân bằng: chỉ 24,8% mẫu có thu nhập trên 50K. Nếu luôn dự đoán thu nhập thấp, mô hình vẫn đạt accuracy 75,2% nhưng không nhận diện được người thu nhập cao nào; F1 lớp dương bằng 0. F1 là trung bình điều hòa của precision và recall, phản ánh đồng thời dự đoán dương đúng và khả năng tìm ra lớp dương. Vì vậy pipeline yêu cầu F1 tối thiểu 0,65. Tôi dùng F1 mặc định của lớp dương, không dùng weighted vì lớp đa số có thể kéo điểm lên, cũng không dùng macro vì đó là trung bình hai lớp, không phải chỉ số mà ngưỡng lab định nghĩa.

## 3. Khó Khăn Gặp Phải và Cách Giải Quyết

| Khó khăn | Nguyên nhân | Cách giải quyết |
|---|---|---|
| MLflow không mở SQLite. | SQLAlchemy 2.1 bỏ API pool mà MLflow 2.13 dùng. | Ràng buộc SQLAlchemy dưới 2.1 và kiểm thử lại. |
| Không tạo được VM B1s. | Subscription Students hạn chế SKU, security type và region. | Chọn B2ats_v2 1 GB RAM tại Singapore, dùng Trusted Launch. |
| Bootstrap VM lỗi quyền home. | Cloud-init tạo thư mục và file trước tài khoản triển khai. | Sửa owner về azureuser rồi cài Python 3.11 cùng dependency inference. |

## 4. So Sánh Bước 2 và Bước 3 (bắt buộc, 2 - 3 câu)

| | f1_score | accuracy |
|---|---|---|
| Bước 2 (22.361 mẫu) | 0.7149 | 0.8740 |
| Bước 3 (44.722 mẫu) | 0.7354 | 0.8820 |

**Nhận xét:** Trên cùng 500 mẫu holdout, F1 tăng 0,0205 và accuracy tăng 0,0080 sau khi thêm batch2. Dữ liệu mới giúp mô hình học thêm, nhưng kết quả này không chứng minh thêm dữ liệu luôn tốt hơn. Run Bước 3 được kích hoạt thủ công vì push chưa tạo run tự động; tiêu chí tự động hoàn toàn chưa được chứng minh.
