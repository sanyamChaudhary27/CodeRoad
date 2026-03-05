# CodeRoad - Competitive Programming Arena

<div align="center">

**Real-time 1v1 coding battles with AI-generated challenges**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [API Docs](#api-documentation) • [Deployment](#deployment)

</div>

---

## 🎯 Overview

CodeRoad is a competitive programming platform where developers battle in real-time 1v1 coding duels. Solve AI-generated challenges, climb the ELO leaderboard, and prove your skills against opponents matched to your level.

### Key Features

- **🤖 AI-Generated Challenges**: Unique problems tailored to your skill level using Groq LLaMA 3.3
- **⚔️ Real-Time 1v1 Battles**: Compete against opponents in your ELO range
- **🐛 Debug Arena**: Find and fix bugs faster than your opponent
- **📊 ELO Rating System**: Sophisticated ranking with separate ratings for DSA and Debug arenas
- **🎯 Smart Matchmaking**: Fair matches within ±200 ELO range
- **🔒 Integrity Verification**: XGBoost-based cheating detection
- **📈 Performance Analytics**: Track your progress across 8 coding domains

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 18+**
- **Groq API Key** ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/sanyamChaudhary27/CodeRoad.git
cd CodeRoad
```

2. **Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Edit backend/.env and add your Groq API keys

# Start backend server
uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

4. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────┐
│   React Frontend │
│   (TypeScript)   │
└────────┬─────────┘
         │ REST API
         ▼
┌─────────────────┐
│  FastAPI Backend │
│    (Python)      │
└────────┬─────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌────────┐
│Database│ │ Groq │ │XGBoost │ │WebSocket│
│(SQLite)│ │  AI  │ │Integrity│ │ Manager │
└────────┘ └──────┘ └────────┘ └────────┘
```

### Tech Stack

**Frontend:**
- React 18 with TypeScript
- Vite for build tooling
- TailwindCSS for styling
- Lucide React for icons
- React Router for navigation

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- Pydantic (data validation)
- Groq AI (challenge generation)
- XGBoost (integrity detection)
- WebSockets (real-time updates)

**Database:**
- SQLite (development)
- PostgreSQL (production ready)

---

## 📚 Features Deep Dive

### 1. DSA Arena

Solve algorithmic problems from scratch across 8 domains:
- Arrays & Hashing
- Strings
- Trees & Graphs
- Dynamic Programming
- Sorting & Searching
- Math & Number Theory
- Linked Lists
- Bit Manipulation

**Challenge Generation:**
- AI-powered unique problems
- ELO-smart difficulty scaling
- Personalized based on history
- 4-8 test cases per problem
- 150-400 word descriptions

### 2. Debug Arena

Find and fix bugs in broken code:
- 1-3 intentional bugs per challenge
- Bug types: syntax, logic, algorithm, edge cases
- Realistic code without obvious hints
- Faster fixes = higher scores

### 3. Matchmaking System

**Smart Pairing:**
- ELO-based matching (±200 range)
- 60-second queue timeout
- Separate ratings for DSA and Debug
- Practice mode for solo play

**Rating System:**
- Starting ELO: 300 (Debug), 1200 (DSA)
- K-factor: 32
- Win/loss adjustments based on opponent rating
- Separate leaderboards per arena

### 4. Integrity System

**XGBoost-based Detection:**
- Stylometric analysis
- Code complexity metrics
- Submission timing patterns
- LLM-generated code detection

---

## 🔧 Configuration

### Environment Variables

**Backend (backend/.env)**
```bash
# Database
DATABASE_URL=sqlite:///./coderoad.db

# Security
SECRET_KEY=your-secret-key-here

# Groq API (Multiple keys for redundancy)
GROQ_API_KEY=gsk_...
GROQ_API_KEY_2=gsk_...
GROQ_API_KEY_3=gsk_...

# Server
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

---

## 📖 API Documentation

### Authentication

**Register**
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "player1",
  "email": "player1@example.com",
  "password": "securepass123"
}
```

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "player1",
  "password": "securepass123"
}
```

### Matchmaking

**Find Match**
```http
POST /api/match/find
Authorization: Bearer <token>

{
  "difficulty": "intermediate",
  "challenge_type": "dsa"
}
```

**Submit Solution**
```http
POST /api/submission/submit
Authorization: Bearer <token>

{
  "match_id": "...",
  "code": "def solve(arr):\n    return sum(arr)"
}
```

**Full API documentation:** http://localhost:8000/docs

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

### AWS Deployment

See [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 📊 Problem Generation

### AI Challenge Generation

**Quality Controls:**
- Description: 150-400 words
- Title: 3-8 words
- Test cases: 4-8 per problem
- ELO-smart difficulty scaling
- Personalization based on player history

**Fallback Hierarchy:**
1. Groq AI (multi-key rotation)
2. Template-based generation
3. Minimal hardcoded challenge

See [PROBLEM_GENERATION_IMPROVEMENTS.md](PROBLEM_GENERATION_IMPROVEMENTS.md) for details.

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License.

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/sanyamChaudhary27/CodeRoad/issues)
- **Documentation:** See `/docs` folder

---

## 🗺️ Roadmap

- [ ] Multi-language support (JavaScript, Java, C++)
- [ ] Team battles (2v2, 3v3)
- [ ] Tournament system
- [ ] Mobile app
- [ ] Achievement system

---

<div align="center">

**Built with ❤️ for competitive programmers**

</div>
