FROM python:3.10-slim

WORKDIR /app/api_gateway

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
