FROM python:3.12-slim

LABEL purpose="intentionally-vulnerable-test-app"
LABEL warning="DO NOT DEPLOY TO PRODUCTION"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
RUN mkdir -p uploads

EXPOSE 5000

CMD ["python", "app.py"]
