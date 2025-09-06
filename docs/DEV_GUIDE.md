# Arthachitra Developer Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Code Structure](#code-structure)
4. [Adding New Features](#adding-new-features)
5. [Testing Guidelines](#testing-guidelines)
6. [Deployment](#deployment)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

## Architecture Overview

Arthachitra follows a microservices architecture with the following components:

### Frontend (React + TypeScript)
- **Framework**: Next.js 13+ with App Router
- **State Management**: Redux Toolkit + Zustand for performance-critical components
- **UI Library**: TailwindCSS with custom theme system
- **Charts**: Custom WebGL renderer + Lightweight Charts integration
- **Real-time**: WebSocket connections for live data

### Backend (Python FastAPI)
- **API Framework**: FastAPI with async/await patterns
- **Database**: PostgreSQL with TimescaleDB for time-series data
- **Cache**: Redis for real-time data and sessions
- **Message Queue**: Kafka for order flow processing
- **Authentication**: JWT with refresh tokens

### C++ Tick Engine
- **Purpose**: Ultra-low latency order book processing
- **Libraries**: Boost, Redis++, nlohmann/json
- **Performance**: <1ms tick processing latency
- **Scalability**: Handles 100k+ ticks per second

### ML Services (Python)
- **Framework**: PyTorch + Scikit-learn
- **Deployment**: TensorFlow Serving for model inference
- **Features**: Pattern recognition, sentiment analysis, forecasting
- **Real-time**: Stream processing with Apache Kafka

## Development Environment Setup

### Prerequisites
Required software
Docker & Docker Compose

Node.js 18+

Python 3.9+

C++ compiler (GCC 9+ or Clang 10+)

CMake 3.16+

Redis

PostgreSQL 14+
### Quick Start
Clone repository
git clone https://github.com/yourusername/arthachitra.git
cd arthachitr

Start development environment
docker-compose -f docker-compose.dev.yml up -d

Or manual setup
./scripts/setup-dev.sh
### Manual Setup

#### Backend Setup
cd backend
python -m venv venv
source venv/bin/activate #

Install dependencies
pip install -r requirements.txt
pip

Setup database
python -m alembic upgrade head
python database/seed_data

Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
#### Frontend Setup
cd frontend
npm instal

Start development server
npm run dev

Run tests
npm test

Build for production
npm run build
#### C++ Tick Engine
cd tick_engine
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)

Run tests
ctest

Start tick engine
./tick_engine --config ../config/dev.yaml


#### ML Services
cd ml
pip install -r requirements.txt

Download pre-trained models
python scripts/download_models.py

Start ML API server
python inference/api_server.py

Train new models
python training/train_patterns.py
## Code Structure

### Frontend Components
src/components/
├── charts/ # Chart components
│ ├── CandlestickChart.tsx
│ ├── HeatmapChart.tsx
│ └── VolumeProfile.tsx
├── orderbook/ # Order book components
│ ├── OrderBookLadder.tsx
│ ├── DOM.tsx
│ └── MarketDepth.tsx
├── themes/ # Theme system
│ ├── ThemeProvider.tsx
│ └── ThemeSwitcher.tsx
├── trading/ # Trading components
│ ├── OrderEntry.tsx
│ ├── PositionManager.tsx
│ └── RiskManager.tsx
└── ui/ # Common UI components
├── Button.tsx
├── Modal.tsx
└── DataTable.tsx
### Backend Structure
backend/
├── api/ # API routes
│ ├── routes/
│ └── middleware/
├── core/ # Core business logic
│ ├── engine/
│ ├── models/
│ └── utils/
├── market_connectors/ # Broker integrations
│ ├── indian/
│ ├── global/
│ └── base/
├── database/ # Database models & migrations
└── tests/ # Test suites
## Adding New Features

### 1. Adding a New Chart Type

Create the component:
// src/components/charts/NewChartType.tsx
import React from 'react';
import { useTheme } from '../../hooks/useTheme';

interface NewChartTypeProps {
data: any[];
width?: number;
height?: number;
}

export const NewChartType: React.FC<NewChartTypeProps> = ({
data,
width = 800,
height = 400
}) => {
const { theme } = useTheme();

// Implementation here

return (
<div className="new-chart-container">
{/* Chart rendering */}
</div>
);
};
Add to chart selector:
// src/components/charts/ChartContainer.tsx
import { NewChartType } from './NewChartType';

const chartTypes = {
candlestick: CandlestickChart,
heatmap: HeatmapChart,
newType: NewChartType, // Add here
};
### 2. Adding a New Technical Indicator

Backend implementation:
backend/core/indicators/new_indicator.py
import numpy as np
import pandas as pd

def new_indicator(prices: np.ndarray, period: int = 14) -> np.ndarray:
"""
Calculate new technical indicator.

Args:
    prices: Array of price values
    period: Calculation period
    
Returns:
    Array of indicator values
"""
# Implementation here
result = np.zeros_like(prices)
# ... calculation logic
return result

Frontend integration:
// src/utils/indicators.ts
export const calculateNewIndicator = (
prices: number[],
period: number = 14
): number[] => {
// Frontend calculation or API call
return prices.map((_, index) => {
// Calculation logic
return 0;
});
};
### 3. Adding a New Broker Connector

Create connector class:
backend/market_connectors/new_broker/connector.py
from ..base.connector import BaseConnector
from typing import List, Optional

class NewBrokerConnector(BaseConnector):
def init(self, api_key: str, secret: str):
super().init()
self.api_key = api_key
self.secret = secretasync def connect(self) -> bool:
    # Implementation
    pass

async def place_order(self, symbol: str, side: str, quantity: int) -> Optional[str]:
    # Implementation
    pass

# ... other required methods

Register connector:
backend/core/broker_factory.py
from market_connectors.new_broker.connector import NewBrokerConnector

BROKERS = {
'zerodha': ZerodhaConnector,
'new_broker': NewBrokerConnector, # Add here
}


## Testing Guidelines

### Frontend Testing
Unit tests
npm test

Component tests
npm run test:components

E2E tests
npm run test:e2e

Coverage report
npm run test:coverage
Test example:
// tests/components/ChartComponent.test.tsx
import { render, screen } from '@testing-library/react';
import { ChartComponent } from '../../src/components/ChartComponent';

describe('ChartComponent', () => {
test('renders chart with data', () => {
const mockData = [/* test data */];
render(<ChartComponent data={mockData} />);

text
expect(screen.getByTestId('chart-container')).toBeInTheDocument();
});
});

text

### Backend Testing
Run all tests
pytest

Run specific test file
pytest tests/test_market_data.py

Run with coverage
pytest --cov=backend --cov-report=html

text

Test example:
tests/test_market_data.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_quote():
response = client.get("/api/v1/market/quote/NIFTY")
assert response.status_code == 200
data = response.json()
assert "price" in data
assert "symbol" in data

text

### Load Testing
Install locust
pip install locust

Run load test
locust -f tests/load/test_api.py --host=http://localhost:8000

text

## Performance Optimization

### Frontend Optimization

1. **Chart Rendering**
// Use React.memo for expensive components
export const Chart = React.memo(({ data }: ChartProps) => {
// Chart implementation
}, (prevProps, nextProps) => {
// Custom comparison logic
return prevProps.data.length === nextProps.data.length;
});

// Use useMemo for expensive calculations
const processedData = useMemo(() => {
return data.map(item => processItem(item));
}, [data]);

text

2. **WebSocket Optimization**
// Throttle high-frequency updates
const throttledUpdate = useCallback(
throttle((newData) => {
setChartData(newData);
}, 100), // Update every 100ms max
[]
);

text

### Backend Optimization

1. **Database Queries**
Use async queries
async def get_market_data(symbol: str, limit: int = 100):
query = """
SELECT * FROM market_data
WHERE symbol = $1
ORDER BY timestamp DESC
LIMIT $2
"""
return await database.fetch_all(query, symbol, limit)

Use database connection pooling
DATABASE_URL = "postgresql://user:pass@localhost/db?min_size=5&max_size=20"

text

2. **Caching Strategy**
Redis caching
@cache(expire=60) # Cache for 60 seconds
async def get_quote(symbol: str):
# Expensive operation
return quote_data

text

3. **Background Tasks**
Use background tasks for heavy operations
@app.post("/process-data/")
async def process_data(background_tasks: BackgroundTasks):
background_tasks.add_task(heavy_processing_function)
return {"status": "processing"}

text

## Deployment

### Development Deployment
docker-compose up -d

text

### Production Deployment

1. **Using Docker Swarm**
Initialize swarm
docker swarm init

Deploy stack
docker stack deploy -c docker-compose.prod.yml arthachitra

text

2. **Using Kubernetes**
Apply configurations
kubectl apply -f deploy/kubernetes/

Check deployment
kubectl get pods -n arthachitra

text

3. **Using Cloud Services (AWS)**
Deploy using Terraform
cd deploy/terraform
terraform init
terraform plan
terraform apply

text

### Environment Variables
Production environment variables
export DATABASE_URL="postgresql://user:pass@prod-db:5432/arthachitra"
export REDIS_URL="redis://prod-redis:6379"
export JWT_SECRET="your-production-secret"
export API_ENVIRONMENT="production"

text

## Troubleshooting

### Common Issues

1. **WebSocket Connection Issues**
// Check WebSocket status
const { isConnected, error } = useWebSocket(url);

if (error) {
console.error('WebSocket error:', error);
// Implement reconnection logic
}

text

2. **Database Connection Problems**
Check database connectivity
async def check_db_connection():
try:
await database.execute("SELECT 1")
return True
except Exception as e:
logger.error(f"Database connection failed: {e}")
return False

text

3. **High Memory Usage**
Monitor memory usage
docker stats

Check for memory leaks
npm run analyze # For frontend bundle analysis

text

4. **Performance Issues**
Profile Python code
python -m cProfile -o profile.stats main.py

Analyze profile
python -c "import pstats; pstats.Stats('profile.stats').sort_stats('time').print_stats(10)"

text

### Debug Mode

Enable debug logging:
backend/core/utils/logger.py
import logging

logging.basicConfig(
level=logging.DEBUG,
format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

text

Enable frontend debugging:
// src/utils/debug.ts
export const DEBUG = process.env.NODE_ENV === 'development';

export const debugLog = (message: string, data?: any) => {
if (DEBUG) {
console.log([Arthachitra Debug] ${message}, data);
}
};

text

### Health Checks

Backend health endpoint:
@app.get("/health")
async def health_check():
checks = {
"database": await check_db_connection(),
"redis": await check_redis_connection(),
"websocket": websocket_manager.is_healthy(),
"disk_space": check_disk_space() > 1024 # 1GB free
}

text
is_healthy = all(checks.values())
status_code = 200 if is_healthy else 503

return JSONResponse(
    status_code=status_code,
    content={"status": "healthy" if is_healthy else "unhealthy", "checks": checks}
)
text

Frontend health monitoring:
// src/hooks/useHealthCheck.ts
export const useHealthCheck = () => {
const [health, setHealth] = useState(null);

useEffect(() => {
const checkHealth = async () => {
try {
const response = await fetch('/api/health');
const data = await response.json();
setHealth(data);
} catch (error) {
setHealth({ status: 'error', error: error.message });
}
};

text
checkHealth();
const interval = setInterval(checkHealth, 30000); // Check every 30s

return () => clearInterval(interval);
}, []);

return health;
};

text

## Contributing Guidelines

1. **Code Style**
   - Frontend: ESLint + Prettier
   - Backend: Black + isort + flake8
   - C++: clang-format

2. **Git Workflow**
   - Feature branches: `feature/your-feature-name`
   - Bug fixes: `fix/issue-description`
   - Releases: `release/v1.x.x`

3. **Pull Request Process**
   - Write descriptive commit messages
   - Add tests for new features
   - Update documentation
   - Ensure CI passes

4. **Code Review Checklist**
   - [ ] Tests added/updated
   - [ ] Documentation updated
   - [ ] Performance impact considered
   - [ ] Security implications reviewed
   - [ ] Error handling implemented

This developer guide provides comprehensive instructions for setting up, developing, testing, and deploying the Arthachitra platform, ensuring consistent development practices across the team.
