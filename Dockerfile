# Python 3.9 kullan
FROM python:3.9-slim

# Çalışma dizini oluştur
WORKDIR /app

# PyYAML kütüphanesini kur
RUN pip install --no-cache-dir pyyaml

# Proje dosyalarını kopyala
COPY . .

# output klasörünü oluştur
RUN mkdir -p output

# Programı çalıştır
CMD ["python", "app.py"]