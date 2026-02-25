# Code Road - Backend

Real-time competitive coding platform backend built with FastAPI.

## Features

- **Real-time Matchmaking**: ELO-based matchmaking with WebSocket support
- **Code Execution**: Sandboxed code execution with multiple language support
- **ELO Rating System**: Standard chess.com ELO rating with confidence scoring
- **AI Integrity Verification**: Stylometric analysis and cheating detection
- **Tournament Support**: Knockout and battle royale tournament formats
- **Scalable Architecture**: Microservices with Redis caching

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **Real-time**: WebSockets
- **Code Execution**: Docker-based sandbox
- **Containerization**: Docker & Docker Compose

## Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── match.py      # Match endpoints
│   │   ├── submission.py # Submission endpoints
│   │   ├── leaderboard.py # Leaderboard endpoints
│   │   └── websocket.py  # WebSocket endpoints
│   ├── core/             # Core functionality
│   │   ├── database.py   # Database configuration
│   │   ├── security.py   # Authentication & security
│   │   └── utils.py      # Utility functions
│   ├── models/           # SQLAlchemy models
│   │   ├── player.py     # Player models
│   │   ├── match.py      # Match models
│   │   ├── submission.py # Submission models
│   │   ├── integrity.py  # Integrity models
│   │   └── rating.py     # Rating models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic services
│   │   ├── match_service.py      # Match lifecycle
│   │   ├── rating_service.py     # ELO calculations
│   │   ├── judge_service.py      # Code judging
│   │   ├── challenge_service.py  # Challenge management
│   │   ├── integrity_service.py  # Integrity verification
│   │   └── websocket_manager.py  # WebSocket management
│   ├── sandbox/          # Code execution sandbox
│   │   ├── executor.py   # Code execution logic
│   │   └── docker_runner.py # Docker container management
│   ├── app.py            # FastAPI application
│   └── config.py         # Configuration
├── requirements.txt      # Python dependencies
└── Dockerfile           # Docker configuration
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new player
- `POST /api/v1/auth/login` - Login player
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current player info

### Matches
- `POST /api/v1/matches/queue/join` - Join matchmaking queue
- `POST /api/v1/matches/queue/leave` - Leave matchmaking queue
- `GET /api/v1/matches/{match_id}` - Get match details
- `POST /api/v1/matches/{match_id}/done` - Mark player as done
- `GET /api/v1/matches/player/{player_id}` - Get player's matches

### Submissions
- `POST /api/v1/submissions/` - Submit code
- `GET /api/v1/submissions/{submission_id}` - Get submission details
- `GET /api/v1/submissions/match/{match_id}` - Get match submissions

### Leaderboard
- `GET /api/v1/leaderboard/global` - Global leaderboard
- `GET /api/v1/leaderboard/weekly` - Weekly leaderboard
- `GET /api/v1/leaderboard/domain/{domain}` - Domain-specific leaderboard

### WebSocket
- `ws://localhost:8000/ws/{match_id}` - Real-time match updates

## Database Schema

### Core Tables
- `players` - Player accounts and statistics
- `matches` - Match information and state
- `submissions` - Code submissions and results
- `challenges` - Coding challenges (from ML team)
- `test_cases` - Test cases for challenges

### Rating System
- `ratings` - Player ratings with confidence
- `rating_history` - Historical rating changes
- `leaderboard_snapshots` - Cached leaderboard data

### Integrity System
- `integrity_analysis` - AI integrity analysis results
- `player_integrity_profiles` - Player integrity profiles
- `integrity_audit_logs` - Audit trail for integrity actions

## Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone "https://sanyamChaudhary27/CodeRoad"
   cd code-road/backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Local Development (without Docker)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up database**
   ```bash
   # Start PostgreSQL and Redis
   # Update .env with local database URLs
   ```

3. **Run the application**
   ```bash
   uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
   ```

## Configuration

Environment variables in `.env`:

```env
# Application
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/coderoad

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production

# ML Services
CHALLENGE_SERVICE_URL=http://localhost:8001
JUDGE_SERVICE_URL=http://localhost:8002
INTEGRITY_SERVICE_URL=http://localhost:8003
```

## Development Workflow

### Running Tests
```bash
pytest tests/ -v
```

### Code Formatting
```bash
black app/
isort app/
```

### Database Migrations
```bash
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

### Production Build
```bash
docker build -t coderoad-backend:latest .
```

### Kubernetes Deployment
See `kubernetes/` directory for deployment manifests.

### Environment Variables for Production
- Set `DEBUG=false`
- Use strong `SECRET_KEY`
- Configure production database and Redis
- Set appropriate CORS origins

## Team Responsibilities

### Backend Team (You)
- Match lifecycle logic
- Code submission API
- Database schema design
- FastAPI backend structure
- ELO rating logic
- Integration with ML models

### ML Team (Gajendra)
- Problem statement generator
- Solution generator
- Test cases generator
- Judging services
- Orchestrator model

### Frontend Team (Ved)
- Login page
- Home page with challenge selection
- Sandbox UI
- Player profile
- WebSocket for real-time challenges
- Timer UI

### Data Team (Reddy)
- Data collection for model fine-tuning
- Problem statements with solutions
- Difficulty level matching with ELO
- Test case design
- Documentation & presentation

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Ensure code passes formatting checks
5. Submit a pull request

## License

[Your License Here]