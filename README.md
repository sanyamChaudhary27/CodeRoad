# Code Road - Competitive Coding Arena

A real-time competitive coding platform with AI-generated challenges, multiplayer battles, and skill-based ranking.

## 🚀 Quick Start

To get the project up and running, follow these simple steps:

### 1. Installation

Run the following commands from the project root:

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
pip install -r requirements.txt
```

### 2. Configuration

Ensure your `.env` file in the root is set up (one is provided by default).

### 3. Running the Application

Open two terminals and run:

**Frontend:**

```bash
npm run start-frontend
```

**Backend:**

```bash
npm run start-backend
```

---

## 🛠 Project Structure

- **frontend/**: React + Vite application (Arena, Dashboard, Matchmaking).
- **backend/**: FastAPI server (Match Service, Judge Service, Ratings).
- **ml/**: Python services for challenge generation and integrity checks.

## 🔑 Key Features

- **Real-time Arena**: Live coding matches with WebSocket updates.
- **AI Challenges**: Problems generated dynamically for various skill levels.
- **Robust Judging**: Sandbox execution with detailed traceback feedback.
- **Multiplayer/Solo**: Practice in solo mode or compete in 1v1 battles.
- **ELO System**: Skill-based matchmaking and rankings.

## ⚖️ License

MIT License - see LICENSE file for details.
