# **Applied Data Science - CQ2021/21**

## **Group Project Application-Oriented**

### **Thành viên:**
| Họ và tên             | MSSV |
| :-----------          |     :----:|
| Nguyễn Hoài An | 21120035  |
| Hoàng Trung Nam  | 21120290 |
| Phan Cao Nguyên | 21120299  |
| Sần Dịch Anh  | 21120411 |

## **Giảng viên hướng dẫn: Thầy Lê Nhựt Nam**

## **Chủ đề: Hệ thống giới thiệu nghề nghiệp cho học sinh trung học phổ thông Việt Nam**

## **Nguồn dữ liệu sử dụng để crawl**
Dữ liệu điểm chuẩn trong dự án được thu thập từ nhiều nguồn uy tín, cụ thể:
### 1️⃣ Điểm chuẩn đại học 2024

- Trang web: [https://diemthi.tuyensinh247.com/diem-chuan.html](https://diemthi.tuyensinh247.com/diem-chuan.html)
- Nhóm đã crawl toàn bộ danh sách trường → sau đó crawl từng trường → lấy dữ liệu:  
  - **Mã ngành**
  - **Tên ngành**
  - **Tổ hợp môn**
  - **Điểm chuẩn**
  - **Ghi chú** (nếu có)

- Ngoài ra nhóm cũng **crawl riêng thêm** danh sách ngành theo nhóm ngành:
  - Link: [https://diemthi.tuyensinh247.com/nganh-dao-tao.html](https://diemthi.tuyensinh247.com/nganh-dao-tao.html)
  - Crawl **Nhóm ngành → Ngành → Trường → Mã ngành + tổ hợp + điểm chuẩn**.

### 2️⃣ Điểm chuẩn đại học các năm trước (2018–2023)

- Nhóm có sử dụng thêm file từ project cũ của một người bạn từng làm cùng project đó:  
  [https://github.com/daniele15/DV-Final-Crawler](https://github.com/daniele15/DV-Final-Crawler)  
  → đã có sẵn file `diemchuan_full.xlsx` cho các năm 2018–2023.

### 3️⃣ Dữ liệu điểm thi tốt nghiệp THPT (để huấn luyện mô hình gợi ý ngành học)

- Trang web: [https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-thi-tot-nghiep-thpt/](https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-thi-tot-nghiep-thpt/)
- Nhóm đã crawl từng thí sinh theo link:  
  `"https://vietnamnet.vn/giao-duc/diem-thi/tra-cuu-diem-thi-tot-nghiep-thpt/{}/{}.html".format(year, idx_str)`
- Dữ liệu thu thập gồm:
  - Số báo danh
  - Sở giáo dục
  - Điểm các môn: Toán, Văn, Lý, Hóa, Sinh, Sử, Địa, Ngoại ngữ, GDCD
  - Năm thi

## **Cây thư mục**
```
./
├── README.md
├── .git/
├── Data/
│   ├── diemchuan_full_18-23.xlsx
│   ├── diemthi.csv
│   ├── diem_chuan_2018-2023_full.csv
│   ├── diem_chuan_2024_backup.csv
│   ├── diem_chuan_2024_final.csv
│   ├── diem_chuan_2024_full.csv
│   ├── diem_chuan_full.csv
│   ├── mapping_ten_truong.csv
│   ├── nganh_dao_tao_backup_2.csv
│   ├── nganh_dao_tao_final_2.csv
│   ├── Final/
│   │   ├── diem_chuan_full.csv
│   │   ├── school_latlon.csv
│   ├── Model Data/
│   │   ├── dan_nhan_2021.csv
│   │   ├── diemchuan2021.csv
│   │   ├── diemchuan2022.csv
│   │   ├── diemchuan2023.csv
│   │   ├── diemchuan2024.csv
│   │   ├── diemchuan_ABCD(2).csv
│   │   ├── diemthi2021.csv
│   │   ├── diemthi2022.csv
│   │   ├── diemthi2023.csv
│   │   ├── diemthi2024.csv
│   │   ├── diemthi_tonghop2021.csv
│   │   ├── diemthi_tonghop2022.csv
│   │   ├── diemthi_tonghop2023.csv
│   │   ├── diemthi_tonghop2024.csv
│   │   ├── tohop_mon.csv
│   │   ├── tonghop_diem.csv
├── model/
│   ├── clf_multilabel.pkl
│   ├── mlb_majors.pkl
│   ├── reduced_df.csv
│   ├── score.pkl
├── Source/
│   ├── crawl_diem_chuan.ipynb
│   ├── crawl_diem_thi.ipynb
│   ├── dashboard.py
│   ├── Data Preprocessing.ipynb
│   ├── Labelling.ipynb
│   ├── model.ipynb
```

## **Hướng dẫn chạy Dashboard**

- Đầu tiên, clone project về từ GitHub:

```bash
git clone https://github.com/HTNam1710/ADS_Final
```

- Mở project bằng IDE bất kỳ (ở đây nhóm sử dụng VSCode).

- Mở Terminal mới trong IDE, đảm bảo đang đứng đúng folder project vừa tải về.

- Dùng câu lệnh sau để mở Dashboard:

```bash
python -m streamlit run ./Source/dashboard.py
```
- Trình duyệt sẽ tự động mở lên giao diện Dashboard.

---

## **Giới thiệu các tab chính trên Dashboard**

### Tab 1: Phân tích điểm chuẩn đại học tại Việt Nam (2018–2024)

- Phân tích dữ liệu điểm chuẩn qua các năm.
- Xem Top trường có điểm cao nhất / thấp nhất.
- Xem phân bố trường trên bản đồ.
- Lọc dữ liệu theo nhiều tiêu chí: năm, khu vực, nhóm ngành, phân ngành, tên ngành, phương thức tuyển sinh.

### Tab 2: Tham khảo trường phù hợp dựa trên dữ liệu điểm chuẩn năm 2024

- Giúp thí sinh tham khảo ngành + trường phù hợp với mức điểm của mình.
- Lọc theo khu vực, phương thức, tổ hợp môn, khoảng điểm.
- Cung cấp biểu đồ **Sankey 4 cấp** để drill-down: Phân ngành → Trường → Ngành → Điểm từng tổ hợp môn.
- **Sử dụng dữ liệu năm 2024** vì đây là năm gần nhất và có giá trị tham khảo cao nhất cho thí sinh thi năm 2025.

### Tab 3: Gợi ý ngành học phù hợp

- Cho phép thí sinh nhập điểm các môn thi tốt nghiệp THPT.
- Hệ thống dự đoán Top N ngành học phù hợp nhất (sử dụng mô hình Logistic Regression multi-label).
- Hiển thị độ phù hợp của từng ngành.
- Gợi ý trường đào tạo phù hợp cho từng ngành.