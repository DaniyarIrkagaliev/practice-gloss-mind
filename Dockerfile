
FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .
COPY main.py .
COPY templates/ ./templates/
COPY graph.json .
COPY database.db .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]