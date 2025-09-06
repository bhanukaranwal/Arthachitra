#!/bin/bash
set -e

echo "🚀 Setting up Arthachitra Trading Platform..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Node.js (for development)
    if ! command -v node &> /dev/null; then
        print_warning "Node.js is not installed. Required for frontend development."
    fi
    
    # Check Python (for development)
    if ! command -v python3 &> /dev/null; then
        print_warning "Python 3 is not installed. Required for backend development."
    fi
    
    print_status "Prerequisites check completed ✅"
}

# Setup environment files
setup_environment() {
    print_status "Setting up environment configuration..."
    
    # Copy environment templates
    if [ ! -f ".env" ]; then
        cp config/env.template .env
        print_status "Created .env file from template"
    fi
    
    if [ ! -f "frontend/.env.local" ]; then
        cp frontend/.env.template frontend/.env.local
        print_status "Created frontend environment file"
    fi
    
    if [ ! -f "backend/.env" ]; then
        cp backend/.env.template backend/.env
        print_status "Created backend environment file"
    fi
    
    print_warning "Please update the environment files with your specific configuration"
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Start PostgreSQL container
    docker-compose up -d postgres redis
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run database migrations
    docker-compose exec backend python -m alembic upgrade head
    
    # Seed initial data
    docker-compose exec backend python database/seed_data.py
    
    print_status "Database setup completed ✅"
}

# Build and start services
start_services() {
    print_status "Building and starting all services..."
    
    # Build all services
    docker-compose build
    
    # Start all services
    docker-compose up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 15
    
    # Health check
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Backend service is healthy ✅"
    else
        print_error "Backend service health check failed"
    fi
    
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        print_status "Frontend service is healthy ✅"
    else
        print_error "Frontend service health check failed"
    fi
}

# Setup development environment
setup_development() {
    print_status "Setting up development environment..."
    
    # Frontend setup
    if command -v npm &> /dev/null; then
        print_status "Installing frontend dependencies..."
        cd frontend
        npm install
        cd ..
    fi
    
    # Backend setup
    if command -v python3 &> /dev/null; then
        print_status "Setting up Python virtual environment..."
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
        cd ..
    fi
    
    # ML setup
    if command -v python3 &> /dev/null; then
        print_status "Setting up ML environment..."
        cd ml
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        cd ..
    fi
}

# Build C++ tick engine
build_tick_engine() {
    print_status "Building C++ tick engine..."
    
    if command -v cmake &> /dev/null; then
        cd tick_engine
        mkdir -p build
        cd build
        cmake ..
        make -j$(nproc)
        cd ../..
        print_status "Tick engine built successfully ✅"
    else
        print_warning "CMake not found. Skipping tick engine build."
    fi
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║               Arthachitra (अर्थचित्र)                          ║"
    echo "║        Next-Generation Trading Platform Setup               ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_prerequisites
    setup_environment
    
    # Check if user wants development setup
    read -p "Do you want to set up development environment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        setup_development
        build_tick_engine
    fi
    
    setup_database
    start_services
    
    echo -e "\n${GREEN}🎉 Arthachitra setup completed successfully!${NC}"
    echo -e "\n📊 Access your trading platform:"
    echo -e "   ${BLUE}Frontend:${NC} http://localhost:3000"
    echo -e "   ${BLUE}Backend API:${NC} http://localhost:8000"
    echo -e "   ${BLUE}API Docs:${NC} http://localhost:8000/docs"
    echo -e "   ${BLUE}ML Services:${NC} http://localhost:8001"
    echo -e "\n📚 Documentation:"
    echo -e "   ${BLUE}Developer Guide:${NC} docs/DEV_GUIDE.md"
    echo -e "   ${BLUE}API Documentation:${NC} docs/API_DOCS.md"
    echo -e "   ${BLUE}Theme Guide:${NC} docs/THEME_GUIDE.md"
    
    print_status "Happy trading! 🚀"
}

# Run main function
main "$@"
