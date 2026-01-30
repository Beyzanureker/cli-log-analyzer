FROM python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir pyyaml

COPY . .

RUN mkdir -p output

CMD ["python", "app.py"]
