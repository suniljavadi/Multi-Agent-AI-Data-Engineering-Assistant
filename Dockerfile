FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000 8501

CMD ["bash", "-lc", "uvicorn app.api.main:app --host 0.0.0.0 --port 8000"]
