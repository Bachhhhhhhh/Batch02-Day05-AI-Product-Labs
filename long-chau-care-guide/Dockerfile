# Sử dụng Python image chính thức
FROM python:3.10-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết cho ChromaDB (hnswlib)
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code dự án
COPY . .

# Biến môi trường để Python không tạo file .pyc
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Mặc định khi chạy container sẽ build lại DB từ data hiện có
# Sau đó có thể chạy ứng dụng chính (main.py)
CMD ["python", "vector_db/build_vector_db.py"]
