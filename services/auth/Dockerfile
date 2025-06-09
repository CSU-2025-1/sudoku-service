FROM python:3.10-slim

WORKDIR /app/services/auth

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "server.py"]
