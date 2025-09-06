# Multi-stage Dockerfile for complete Arthachitra build

# Stage 1: Frontend build
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ .
RUN npm run build

# Stage 2: Backend build
FROM python:3.9-slim AS backend-builder
WORKDIR /app/backend
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# Stage 3: C++ Tick Engine build
FROM ubuntu:22.04 AS cpp-builder
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libhiredis-dev \
    nlohmann-json3-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app/tick_engine
COPY tick_engine/ .
RUN mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j$(nproc)

# Stage 4: ML Service build
FROM python:3.9-slim AS ml-builder
WORKDIR /app/ml
COPY ml/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ml/ .

# Stage 5: Final production image
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    nodejs \
    npm \
    libpq5 \
    libhiredis0.14 \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy built applications
COPY --from=frontend-builder /app/frontend/.next /app/frontend/.next
COPY --from=frontend-builder /app/frontend/public /app/frontend/public
COPY --from=frontend-builder /app/frontend/package*.json /app/frontend/
COPY --from=backend-builder /app/backend /app/backend
COPY --from=cpp-builder /app/tick_engine/build/tick_engine /app/tick_engine/
COPY --from=ml-builder /app/ml /app/ml

# Copy configuration files
COPY nginx/nginx.prod.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Install Node.js dependencies for frontend
WORKDIR /app/frontend
RUN npm ci --only=production

# Expose ports
EXPOSE 80 8000 8001 9091

# Start supervisor to manage all services
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
