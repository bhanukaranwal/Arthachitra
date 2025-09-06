# Arthachitra Setup Guide

Welcome to Arthachitra (अर्थचित्र) - the next-generation trading platform! This guide will help you set up the complete development environment.

## Quick Start (5 Minutes)

1. Clone the repository
git clone https://github.com/yourusername/arthachitra.git
cd arthachitra

2. Run automated setup
./scripts/setup.sh

3. Start development environment
make dev

4. Access the platform
open http://localhost:3000

text

## Manual Setup

### Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Python** 3.9+ ([Download](https://python.org/))
- **Docker** & Docker Compose ([Download](https://docker.com/))
- **Git** ([Download](https://git-scm.com/))

### Step-by-Step Installation

#### 1. System Dependencies

**Linux (Ubuntu/Debian):**
sudo apt-get update
sudo apt-get install -y build-essential cmake libssl-dev libpq-dev

text

**macOS:**
brew install cmake postgresql redis

text

#### 2. Frontend Setup

cd frontend
npm install
npm run build

text

#### 3. Backend Setup

cd backend
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

text

#### 4. ML Service Setup

cd ml
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

text

#### 5. C++ Tick Engine

cd tick_engine
mkdir build && cd build
cmake ..
make -j$(nproc)

text

#### 6. Database Setup

Start PostgreSQL and Redis
docker-compose up -d postgres redis

Run migrations
cd backend
python -m alembic upgrade head

Seed sample data
python database/seed_data.py

text

### Environment Configuration

#### 1. Backend Environment

Create `backend/.env`:
cp backend/.env.template backend/.env

Edit with your configuration
text

#### 2. Frontend Environment

Create `frontend/.env.local`:
cp frontend/.env.template frontend/.env.local

Edit with your configuration
text

### Broker Integration

#### Zerodha Kite Setup

1. Create a Kite Connect app at https://kite.trade/
2. Add your API credentials to `.env`:
ZERODHA_API_KEY=your_api_key
ZERODHA_API_SECRET=your_api_secret

text

#### Fyers Setup

1. Create a Fyers API app at https://myapi.fyers.in/
2. Add credentials to `.env`:
FYERS_APP_ID=your_app_id
FYERS_SECRET_KEY=your_secret_key

text

### Testing

#### Run All Tests
make test

text

#### Individual Test Suites
Frontend tests
cd frontend && npm test

Backend tests
cd backend && pytest

C++ tests
cd tick_engine/build && ctest

E2E tests
cd frontend && npx playwright test

text

### Development Workflow

#### Start Development Server
make dev

text

#### Individual Services
Frontend only
make frontend

Backend only
make backend

ML service only
make ml-service

Tick engine only
make tick-engine

text

### Production Deployment

#### Docker Compose
make deploy

text

#### Kubernetes
kubectl apply -f deploy/kubernetes/production/

text

### Troubleshooting

#### Common Issues

**Port Already in Use:**
Find and kill process using port 3000
sudo lsof -ti:3000 | xargs kill -9

text

**Docker Issues:**
Clean Docker resources
make clean
docker system prune -a

text

**Database Connection:**
Reset database
make db-reset

text

**Permission Errors:**
Fix file permissions
sudo chown -R $USER:$USER .

text

#### Getting Help

- 📚 **Documentation**: [docs/](docs/)
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/arthachitra/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/arthachitra/discussions)
- 💬 **Discord**: [Join our server](https://discord.gg/arthachitra)

### Next Steps

1. **Explore the Platform**: Navigate to http://localhost:3000
2. **Read the Documentation**: Check out [docs/DEV_GUIDE.md](docs/DEV_GUIDE.md)
3. **Customize Themes**: See [docs/THEME_GUIDE.md](docs/THEME_GUIDE.md)
4. **Add Brokers**: Follow [docs/BROKER_INTEGRATION.md](docs/BROKER_INTEGRATION.md)
5. **Contribute**: Read [CONTRIBUTING.md](CONTRIBUTING.md)

Happy Trading! 🚀
