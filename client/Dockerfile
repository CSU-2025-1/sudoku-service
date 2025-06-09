FROM python:3.10-slim

WORKDIR /app/client

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
