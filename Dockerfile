FROM python:3.14-slim

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--proxy-headers", "--port", "3000"]
