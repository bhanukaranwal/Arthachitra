FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download pre-trained models
RUN python scripts/download_models.py

# Create non-root user
RUN useradd --create-home --shell /bin/bash ml
RUN chown -R ml:ml /app
USER ml

EXPOSE 8001

CMD ["python", "inference/api_server.py"]
