#!/bin/bash

# Arthachitra Utility Functions

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${CYAN}[DEBUG]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if port is available
port_available() {
    local port=$1
    ! lsof -Pi :$port -sTCP:LISTEN -t >/dev/null
}

# Wait for service to be ready
wait_for_service() {
    local service_name=$1
    local url=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    log_info "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            log_info "$service_name is ready!"
            return 0
        fi
        
        log_debug "Attempt $attempt/$max_attempts failed, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "$service_name failed to start within $((max_attempts * 2)) seconds"
    return 1
}

# Generate random password
generate_password() {
    local length=${1:-32}
    openssl rand -base64 $length | tr -d "=+/" | cut -c1-$length
}

# Create directory if it doesn't exist
ensure_directory() {
    local dir=$1
    if [ ! -d "$dir" ]; then
        log_info "Creating directory: $dir"
        mkdir -p "$dir"
    fi
}

# Download file with progress
download_file() {
    local url=$1
    local output=$2
    
    log_info "Downloading $url..."
    
    if command_exists wget; then
        wget --progress=bar:force:noscroll -O "$output" "$url"
    elif command_exists curl; then
        curl -# -L -o "$output" "$url"
    else
        log_error "Neither wget nor curl is available"
        return 1
    fi
}

# Check system requirements
check_system_requirements() {
    log_info "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "OS: Linux ✓"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "OS: macOS ✓"
    else
        log_warn "OS: $OSTYPE (may not be fully supported)"
    fi
    
    # Check memory
    if command_exists free; then
        local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$mem_gb" -ge 4 ]; then
            log_info "Memory: ${mem_gb}GB ✓"
        else
            log_warn "Memory: ${mem_gb}GB (recommended: 4GB+)"
        fi
    fi
    
    # Check disk space
    local disk_space=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$disk_space" -ge 10 ]; then
        log_info "Disk space: ${disk_space}GB available ✓"
    else
        log_warn "Disk space: ${disk_space}GB (recommended: 10GB+)"
    fi
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "git")
    for cmd in "${required_commands[@]}"; do
        if command_exists "$cmd"; then
            log_info "$cmd: available ✓"
        else
            log_error "$cmd: not found (required)"
            return 1
        fi
    done
    
    return 0
}

# Cleanup Docker resources
cleanup_docker() {
    log_info "Cleaning up Docker resources..."
    
    # Stop all containers
    docker stop $(docker ps -q) 2>/dev/null || true
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    # Remove unused networks
    docker network prune -f
    
    log_info "Docker cleanup completed"
}

# Backup database
backup_database() {
    local db_name=${1:-arthachitra}
    local backup_dir=${2:-./backups}
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="$backup_dir/${db_name}_${timestamp}.sql"
    
    ensure_directory "$backup_dir"
    
    log_info "Creating database backup..."
    
    docker exec arthachitra-postgres-1 pg_dump -U postgres -d "$db_name" > "$backup_file"
    
    if [ -f "$backup_file" ]; then
        gzip "$backup_file"
        log_info "Database backup created: ${backup_file}.gz"
    else
        log_error "Database backup failed"
        return 1
    fi
}

# Restore database
restore_database() {
    local backup_file=$1
    local db_name=${2:-arthachitra}
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    log_info "Restoring database from $backup_file..."
    
    # Decompress if needed
    if [[ "$backup_file" == *.gz ]]; then
        zcat "$backup_file" | docker exec -i arthachitra-postgres-1 psql -U postgres -d "$db_name"
    else
        docker exec -i arthachitra-postgres-1 psql -U postgres -d "$db_name" < "$backup_file"
    fi
    
    log_info "Database restore completed"
}

# Get service logs
get_service_logs() {
    local service_name=$1
    local lines=${2:-100}
    
    log_info "Getting logs for $service_name (last $lines lines)..."
    docker-compose logs --tail="$lines" "$service_name"
}

# Monitor system resources
monitor_resources() {
    local duration=${1:-60}
    
    log_info "Monitoring system resources for $duration seconds..."
    
    # CPU and Memory usage
    echo "Timestamp,CPU%,Memory%,Disk%" > resource_usage.csv
    
    for i in $(seq 1 $duration); do
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
        local mem_usage=$(free | grep Mem | awk '{printf("%.2f", $3/$2 * 100.0)}')
        local disk_usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
        
        echo "$timestamp,$cpu_usage,$mem_usage,$disk_usage" >> resource_usage.csv
        sleep 1
    done
    
    log_info "Resource monitoring completed. Data saved to resource_usage.csv"
}

# Test API endpoints
test_api_endpoints() {
    local base_url=${1:-http://localhost:8000}
    
    log_info "Testing API endpoints..."
    
    # Health check
    if curl -f -s "$base_url/health" > /dev/null; then
        log_info "Health endpoint: ✓"
    else
        log_error "Health endpoint: ✗"
    fi
    
    # Market data
    if curl -f -s "$base_url/api/v1/market/symbols" > /dev/null; then
        log_info "Market data endpoint: ✓"
    else
        log_error "Market data endpoint: ✗"
    fi
    
    # Authentication
    if curl -f -s "$base_url/auth/me" > /dev/null 2>&1; then
        log_info "Auth endpoint: ✓"
    else
        log_warn "Auth endpoint: ✗ (may require authentication)"
    fi
}

# Export functions for use in other scripts
export -f log_info log_warn log_error log_debug
export -f command_exists port_available wait_for_service
export -f generate_password ensure_directory download_file
export -f check_system_requirements cleanup_docker
export -f backup_database restore_database get_service_logs
export -f monitor_resources test_api_endpoints
