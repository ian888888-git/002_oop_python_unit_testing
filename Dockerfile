# Menggunakan image Python resmi yang ringan (Slim)
FROM python:3.11-slim

# Mengatur variabel lingkungan agar Python tidak menulis file .pyc dan output log langsung keluar
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Menentukan folder kerja di dalam kontainer
WORKDIR /app

# Menyalin file dependensi terlebih dahulu (memanfaatkan layer caching Docker)
COPY requirements.txt .

# Menginstall dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Menyalin seluruh kode proyek ke dalam kontainer
COPY . .

# Secara default, kontainer akan menjalankan pytest saat dinyalakan
CMD ["pytest", "-v"]