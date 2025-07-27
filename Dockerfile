FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--proxy-headers", "--port", "8000"]
