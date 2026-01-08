# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install build deps and Chinese fonts
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    libpq-dev \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fontconfig && \
    fc-cache -fv && \
    rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn uvicorn

COPY backend/app /app/app

EXPOSE 8000
CMD ["gunicorn","app.main:app","-k","uvicorn.workers.UvicornWorker","-b","0.0.0.0:8000","--workers","2","--timeout","120"] 