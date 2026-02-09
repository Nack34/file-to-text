FROM python:3.13

RUN pip install --no-cache-dir uv uvicorn fastapi

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr-spa \
    libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

RUN uv sync --frozen || true

RUN pip install --no-cache-dir \
    "fastapi-mcp>=0.2.0" \
    "ipykernel>=6.29.5" \
    "linkup-sdk>=0.2.4" \
    "llama-index>=0.12.30" \
    "llama-index-llms-ollama>=0.5.4" \
    "llama-index-tools-mcp>=0.1.1" \
    "mcp[cli]>=1.6.0" \
    psycopg \
    python-dotenv \
    wikipedia \
    bs4 \
    uvicorn>=0.30.0

COPY . .


