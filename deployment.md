# 🚀 Deployment Guide

AURA is designed to be containerized and deployed to any cloud provider that supports Docker (e.g., Google Cloud Run, AWS Fargate, Azure Container Apps).

## 🐳 Docker Deployment

1.  **Build the Image**
    ```bash
    docker build -t aura-agent .
    ```

2.  **Run the Container**
    ```bash
    docker run -p 8000:8000 --env-file .env aura-agent
    ```

## ☁️ Google Cloud Run

1.  **Submit Build**
    ```bash
    gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/aura-agent
    ```

2.  **Deploy**
    ```bash
    gcloud run deploy aura-agent \
      --image gcr.io/YOUR_PROJECT_ID/aura-agent \
      --platform managed \
      --allow-unauthenticated \
      --set-env-vars GOOGLE_API_KEY=key,MAPS_API_KEY=key,OPEN_WEATHER_API=key,GEMINI_MODEL_NAME=gemini-2.5-flash-exp
    ```
