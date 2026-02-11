# Bước 1: Sử dụng Python bản nhẹ (slim) để giảm dung lượng file
FROM python:3.10-slim

# Bước 2: Thiết lập thư mục làm việc bên trong Container
WORKDIR /app

# Bước 3: Cài đặt các công cụ hệ thống cần thiết (Java để chạy Tika)
# Vì Apache Tika cần Java nên chúng ta phải cài OpenJDK
RUN apt-get update && apt-get install -y \
    default-jre \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Bước 4: Sao chép file requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bước 5: Sao chép bộ não AI (mô hình đã train) vào Container
# Chúng ta copy thư mục model-best vào bên trong
COPY models/model-best /app/models/model-best

# Bước 6: Sao chép mã nguồn xử lý (file src) vào Container
COPY src /app/src

# Bước 7: Tạo các thư mục chứa dữ liệu
RUN mkdir -p /app/data/raw /app/data/processed

# Bước 8: Lệnh mặc định khi chạy Container
# Nó sẽ chạy file ocr_engine.py của bạn
CMD ["python", "src/ocr_engine.py"]