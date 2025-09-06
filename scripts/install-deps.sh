#!/bin/bash

# Arthachitra Dependencies Installation Script

set -e

echo "🚀 Installing Arthachitra dependencies..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
        log_info "Detected Linux OS"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        log_info "Detected macOS"
    else
        log_error "Unsupported OS: $OSTYPE"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    if [[ "$OS" == "linux" ]]; then
        # Update package list
        sudo apt-get update
        
        # Install required packages
        sudo apt-get install -y \
            curl \
            wget \
            git \
            build-essential \
            cmake \
            libssl-dev \
            libpq-dev \
            pkg-config \
            python3 \
            python3-pip \
            python3-venv \
            nodejs \
            npm
            
    elif [[ "$OS" == "macos" ]]; then
        # Check if Homebrew is installed
        if ! command -v brew &> /dev/null; then
            log_info "Installing Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        # Install required packages
        brew install \
            git \
            cmake \
            postgresql \
            redis \
            python3 \
            node \
            npm
    fi
    
    log_info "System dependencies installed ✅"
}

# Install Docker
install_docker() {
    if command -v docker &> /dev/null; then
        log_info "Docker already installed ✅"
        return
    fi
    
    log_info "Installing Docker..."
    
    if [[ "$OS" == "linux" ]]; then
        # Install Docker on Linux
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker $USER
        rm get-docker.sh
        
        # Install Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
    elif [[ "$OS" == "macos" ]]; then
        # Install Docker Desktop for Mac
        log_warn "Please install Docker Desktop for Mac from: https://www.docker.com/products/docker-desktop"
        log_warn "After installation, make sure Docker Desktop is running"
    fi
    
    log_info "Docker installation completed ✅"
}

# Install Node.js dependencies
install_node_deps() {
    log_info "Installing frontend dependencies..."
    
    cd frontend
    
    # Check Node.js version
    NODE_VERSION=$(node --version 2>/dev/null || echo "not installed")
    log_info "Node.js version: $NODE_VERSION"
    
    if [[ "$NODE_VERSION" == "not installed" ]]; then
        log_error "Node.js is not installed"
        exit 1
    fi
    
    # Install dependencies
    npm install
    
    cd ..
    log_info "Frontend dependencies installed ✅"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    # Backend dependencies
    log_info "Installing backend dependencies..."
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    
    cd ..
    
    # ML dependencies
    log_info "Installing ML dependencies..."
    cd ml
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    cd ..
    
    log_info "Python dependencies installed ✅"
}

# Build C++ tick engine
build_tick_engine() {
    log_info "Building C++ tick engine..."
    
    cd tick_engine
    
    # Create build directory
    mkdir -p build
    cd build
    
    # Run CMake
    cmake -DCMAKE_BUILD_TYPE=Release ..
    
    # Build
    make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
    
    cd ../..
    
    log_info "C++ tick engine built ✅"
}

# Install hiredis (Redis C client)
install_hiredis() {
    log_info "Installing hiredis..."
    
    if [[ "$OS" == "linux" ]]; then
        sudo apt-get install -y libhiredis-dev
    elif [[ "$OS" == "macos" ]]; then
        brew install hiredis
    fi
    
    log_info "hiredis installed ✅"
}

# Main installation function
main() {
    log_info "Starting Arthachitra dependency installation..."
    
    check_os
    install_system_deps
    install_docker
    install_hiredis
    install_node_deps
    install_python_deps
    build_tick_engine
    
    log_info "🎉 All dependencies installed successfully!"
    log_info ""
    log_info "Next steps:"
    log_info "1. Run 'make dev' to start the development environment"
    log_info "2. Visit http://localhost:3000 to access Arthachitra"
    log_info "3. Check the README.md for more information"
}

# Run main function
main "$@"
