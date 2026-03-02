# Autonomous Data Analyst Backend

A comprehensive backend system for autonomous data analysis with LLM-based planning, step execution, real-time streaming, and audit logging.

## 🚀 Features

### Core Capabilities
- **LLM-Based Planning**: Intelligent analysis planning using transformer models with critic verification
- **Multi-Step Orchestration**: Executes complex analysis workflows with dependency management
- **Real-Time Streaming**: WebSocket-based progress updates and step traces
- **Immutable Audit Logs**: Tamper-evident logging with content hashing
- **Modular Architecture**: Pluggable executors for different analysis types

### Analysis Types
- **Data Profiling**: Comprehensive statistics, quality metrics, and data exploration
- **Data Cleaning**: Automated missing value handling, outlier detection, and standardization
- **Statistical Analysis**: Descriptive stats, correlations, hypothesis testing, clustering, PCA
- **Visualization**: Auto-generated charts using Vega-Lite specification
- **Anomaly Detection**: Isolation Forest, statistical methods, time series analysis
- **SQL Execution**: Safe SQL query execution with validation and limits

### Safety & Security
- **Input Validation**: Comprehensive validation for all user inputs
- **SQL Injection Protection**: Parameterized queries and pattern detection
- **Rate Limiting**: Configurable rate limits per client
- **Data Sanitization**: Automatic redaction of sensitive information
- **Human-in-the-Loop**: Configurable approval gates for destructive operations

## 📋 Requirements

- Python 3.11+
- PostgreSQL (production) or SQLite (development)
- Redis (optional, for caching)
- Docker & Docker Compose (recommended)

## 🛠️ Installation

### Quick Start with Docker

1. Clone the repository:
```bash
git clone <repository-url>
cd autonomous_data_analyst
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Start with Docker Compose:
```bash
docker-compose up -d
```

4. Access the API:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Manual Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Create necessary directories:
```bash
mkdir -p data/uploads data/processed data/raw logs
```

4. Initialize the database:
```bash
python -c "from app.models.database import create_tables; create_tables()"
```

5. Create demo data:
```bash
python scripts/create_demo_data.py
```

6. Start the application:
```bash
python main.py
```

## 📊 Usage

### Upload a Dataset

```python
import requests

# Upload a CSV file
with open('data.csv', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/upload',
        files={'file': ('data.csv', f, 'text/csv')},
        data={'name': 'My Dataset', 'description': 'Sample dataset'}
    )

dataset_id = response.json()['dataset_id']
```

### Ask a Question

```python
# Ask a question about the dataset
response = requests.post(
    'http://localhost:8000/api/ask',
    json={
        'question': 'What are the key insights from this dataset?',
        'dataset_id': dataset_id
    }
)

run_id = response.json()['run_id']
```

### Monitor Progress (WebSocket)

```javascript
const ws = new WebSocket(`ws://localhost:8000/ws/runs/${run_id}`);

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Event:', data.event_type, data.data);
};
```

### Get Results

```python
# Get final results
response = requests.get(f'http://localhost:8000/api/run/{run_id}')
results = response.json()
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./data/analyst.db` |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `ANTHROPIC_API_KEY` | Anthropic API key | None |
| `DEFAULT_LLM_PROVIDER` | LLM provider to use | `mock` |
| `MAX_FILE_SIZE` | Maximum file upload size | `104857600` (100MB) |
| `MAX_QUERY_ROWS` | Maximum rows for SQL queries | `100000` |
| `REQUIRE_HUMAN_APPROVAL` | Require approval for destructive ops | `true` |
| `MOCK_LLM_MODE` | Use mock LLM for testing | `true` |

### LLM Providers

The system supports multiple LLM providers:

#### OpenAI
```env
OPENAI_API_KEY=your-openai-api-key
DEFAULT_LLM_PROVIDER=openai
```

#### Anthropic Claude
```env
ANTHROPIC_API_KEY=your-anthropic-api-key
DEFAULT_LLM_PROVIDER=anthropic
```

#### Mock Mode (Testing)
```env
MOCK_LLM_MODE=true
DEFAULT_LLM_PROVIDER=mock
```

## 🏗️ Architecture

### Components

1. **API Layer** (FastAPI)
   - RESTful endpoints for all operations
   - WebSocket support for real-time updates
   - Authentication and authorization

2. **Orchestrator**
   - Manages analysis plan execution
   - Handles step dependencies
   - Coordinates between executors

3. **Planner** (LLM-based)
   - Creates analysis plans from natural language
   - Includes critic verification for safety
   - Supports multiple LLM providers

4. **Executors**
   - Modular step execution engines
   - Each handles specific analysis types
   - Pluggable architecture

5. **Audit System**
   - Immutable logging with content hashing
   - Complete traceability of all operations
   - Tamper evidence detection

### Data Flow

```
User Question → LLM Planner → Analysis Plan → Orchestrator → Step Executors → Results
     ↓              ↓              ↓            ↓           ↓
  WebSocket ← Audit Log ← Step Events ← Progress ← Results
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# API tests
pytest tests/test_api.py -v

# Integration tests
pytest tests/test_integration.py -v

# Performance tests
pytest tests/test_integration.py::TestPerformance -v
```

### Test Coverage
```bash
pytest --cov=app tests/
```

## 📈 Monitoring

### Health Checks
- `/health` - Basic health status
- `/api/metrics` - System metrics (authenticated)

### Prometheus Metrics
Enable in Docker Compose:
```bash
docker-compose --profile monitoring up -d
```

Access Grafana at http://localhost:3000 (admin/admin)

## 🔒 Security

### Authentication
- JWT tokens for user authentication
- API keys for programmatic access
- Configurable session management

### Input Validation
- Comprehensive validation for all inputs
- SQL injection protection
- File type and size validation
- Prompt injection detection

### Data Protection
- Sensitive data redaction in logs
- Configurable data retention policies
- Read-only mode for original datasets

## 🚀 Deployment

### Production Deployment

1. Use PostgreSQL for database:
```env
DATABASE_URL=postgresql://user:password@localhost/analyst_db
```

2. Configure real LLM provider:
```env
OPENAI_API_KEY=your-production-key
MOCK_LLM_MODE=false
```

3. Set up reverse proxy (nginx example):
```nginx
location /api/ {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
}
```

4. Enable monitoring:
```bash
docker-compose --profile monitoring up -d
```

### Scaling

- **Horizontal Scaling**: Multiple API instances behind load balancer
- **Database Scaling**: Read replicas for query performance
- **Caching**: Redis for session and result caching
- **Queue System**: Background job processing for long analyses

## 📚 API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload` | Upload dataset |
| GET | `/api/profile/{id}` | Get dataset profile |
| POST | `/api/clean/plan` | Create cleaning plan |
| POST | `/api/clean/execute` | Execute cleaning |
| POST | `/api/ask` | Ask question |
| GET | `/api/run/{id}` | Get run status |
| GET | `/api/audit/{id}` | Get audit logs |
| GET | `/api/datasets` | List datasets |

### WebSocket

- **Endpoint**: `/ws/runs/{run_id}`
- **Events**: `run_started`, `step_started`, `step_completed`, `run_completed`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check this README and inline code documentation
- **Issues**: Create an issue on the repository
- **Discussions**: Use GitHub Discussions for questions

## 🗺️ Roadmap

- [ ] Advanced ML model integration
- [ ] Real-time collaboration features
- [ ] Advanced visualization options
- [ ] Custom plugin system
- [ ] Multi-language support
- [ ] Advanced scheduling and automation
