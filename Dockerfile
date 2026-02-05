FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir playwright && playwright install --with-deps chromium

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]
