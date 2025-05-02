FROM python:3.9-slim
WORKDIR /app
COPY etl/etl.py ./
COPY etl/etl_api.py ./
COPY etl/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "etl_api.py"] 