#!/bin/bash

# Arthachitra Performance Monitoring Script

set -e

LOG_FILE="/var/log/arthachitra/monitor.log"
ALERT_EMAIL="admin@arthachitra.com"
SLACK_WEBHOOK=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

check_service() {
    local service_name=$1
    local service_url=$2
    local expected_status=$3
    
    log "Checking $service_name..."
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 $service_url || echo "000")
    
    if [ "$response" = "$expected_status" ]; then
        log "✅ $service_name is healthy (HTTP $response)"
        return 0
    else
        log "❌ $service_name is unhealthy (HTTP $response)"
        return 1
    fi
}

check_database() {
    log "Checking database connectivity..."
    
    if docker exec arthachitra-postgres-1 pg_isready -U postgres > /dev/null 2>&1; then
        log "✅ Database is healthy"
        return 0
    else
        log "❌ Database is unhealthy"
        return 1
    fi
}

check_redis() {
    log "Checking Redis connectivity..."
    
    if docker exec arthachitra-redis-1 redis-cli ping > /dev/null 2>&1; then
        log "✅ Redis is healthy"
        return 0
    else
        log "❌ Redis is unhealthy"
        return 1
    fi
}

check_disk_space() {
    local threshold=80
    log "Checking disk space..."
    
    usage=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    
    if [ "$usage" -lt "$threshold" ]; then
        log "✅ Disk usage is healthy (${usage}%)"
        return 0
    else
        log "⚠️ Disk usage is high (${usage}%)"
        return 1
    fi
}

check_memory() {
    local threshold=80
    log "Checking memory usage..."
    
    usage=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
    
    if [ "$usage" -lt "$threshold" ]; then
        log "✅ Memory usage is healthy (${usage}%)"
        return 0
    else
        log "⚠️ Memory usage is high (${usage}%)"
        return 1
    fi
}

check_websocket_connections() {
    log "Checking WebSocket connections..."
    
    # Get connection count from backend API
    connections=$(curl -s http://localhost:8000/health | jq -r '.connections // 0' 2>/dev/null || echo "0")
    
    log "Active WebSocket connections: $connections"
    
    if [ "$connections" -gt 1000 ]; then
        log "⚠️ High number of WebSocket connections ($connections)"
        return 1
    else
        log "✅ WebSocket connections are normal"
        return 0
    fi
}

send_alert() {
    local message=$1
    local severity=$2
    
    log "Sending alert: $message"
    
    # Send email alert
    if command -v mail > /dev/null 2>&1; then
        echo "$message" | mail -s "Arthachitra Alert - $severity" $ALERT_EMAIL
    fi
    
    # Send Slack alert
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 Arthachitra Alert: $message\"}" \
            $SLACK_WEBHOOK > /dev/null 2>&1
    fi
}

main() {
    log "Starting Arthachitra health monitoring..."
    
    local issues=0
    local alerts=()
    
    # Check all services
    if ! check_service "Frontend" "http://localhost:3000" "200"; then
        issues=$((issues + 1))
        alerts+=("Frontend service is down")
    fi
    
    if ! check_service "Backend API" "http://localhost:8000/health" "200"; then
        issues=$((issues + 1))
        alerts+=("Backend API is down")
    fi
    
    if ! check_service "ML Service" "http://localhost:8001/health" "200"; then
        issues=$((issues + 1))
        alerts+=("ML Service is down")
    fi
    
    if ! check_database; then
        issues=$((issues + 1))
        alerts+=("Database is unhealthy")
    fi
    
    if ! check_redis; then
        issues=$((issues + 1))
        alerts+=("Redis is unhealthy")
    fi
    
    if ! check_disk_space; then
        issues=$((issues + 1))
        alerts+=("Disk space is running low")
    fi
    
    if ! check_memory; then
        issues=$((issues + 1))
        alerts+=("Memory usage is high")
    fi
    
    if ! check_websocket_connections; then
        issues=$((issues + 1))
        alerts+=("High number of WebSocket connections")
    fi
    
    # Send alerts if issues found
    if [ $issues -gt 0 ]; then
        alert_message="Found $issues issues: ${alerts[*]}"
        send_alert "$alert_message" "WARNING"
        log "❌ Health check completed with $issues issues"
        exit 1
    else
        log "✅ All systems healthy"
        exit 0
    fi
}

# Create log directory
mkdir -p "$(dirname "$LOG_FILE")"

# Run main function
main "$@"
