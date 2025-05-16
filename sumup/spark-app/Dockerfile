FROM bitnami/spark:latest

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY streaming_job.py .

CMD ["spark-submit", "streaming_job.py"]
