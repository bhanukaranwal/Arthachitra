#!/bin/bash

# Arthachitra Health Check Script

FRONTEND_URL="http://localhost:3000"
BACKEND_URL="http://localhost:8000"
ML_URL="http://localhost:8001"

echo "🔍 Running Arthachitra health checks..."

# Check frontend
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    echo "✅ Frontend: Healthy"
else
    echo "❌ Frontend: Unhealthy"
    exit 1
fi

# Check backend
if curl -f -s "$BACKEND_URL/health" > /dev/null; then
    echo "✅ Backend: Healthy"
else
    echo "❌ Backend: Unhealthy"
    exit 1
fi

# Check ML service
if curl -f -s "$ML_URL/health" > /dev/null; then
    echo "✅ ML Service: Healthy"
else
    echo "❌ ML Service: Unhealthy"
    exit 1
fi

echo "🎉 All services are healthy!"
