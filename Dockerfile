# ============================================================
# FounderOS — Multi-Stage Dockerfile
# AMD AI Developer Hackathon Track 3 Submission
# Target: linux/amd64 (works on AMD64 and ARM64 via buildx)
# ============================================================

# Stage 1: Build Frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --production=false
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend
FROM python:3.11-slim AS backend-builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 3: Production
FROM python:3.11-slim

# Labels for hackathon
LABEL maintainer="FounderOS Team"
LABEL description="FounderOS - Multi-Agent AI Operating System for Startup Founders"
LABEL hackathon="AMD AI Developer Hackathon Track 3"

WORKDIR /app

# Install runtime dependencies
COPY --from=backend-builder /install /usr/local
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/ ./backend/
COPY requirements.txt .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/out ./frontend/out

# Create data directories
RUN mkdir -p /app/data/chroma /app/data

# Environment
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    DEV_MODE=false

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]