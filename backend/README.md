# CodeRoad backend

FastAPI service for CodeRoad's authentication, matchmaking, coding/debug
arenas, leaderboard, WebSocket relay, public statistics, and Adversarial Test
Arena.

## Runtime architecture

- **API:** FastAPI and SQLAlchemy.
- **Database:** PostgreSQL in production (including Supabase) or SQLite for
  isolated local development.
- **Real-time:** authenticated, participant-only WebSocket rooms.
- **Challenge selection:** NVIDIA NIM may prewarm a future template; a stored
  deterministic template is always available immediately for a matched pair.
- **Attack Arena:** NVIDIA NIM optionally proposes typed counterexamples. The
  backend validates them, computes the expected result with a deterministic
  oracle, and runs code only through a separately configured Judge0 service.

The API never runs player source code in its own process. If `JUDGE0_API_URL`
is missing or unavailable, execution fails closed with a `503` response.

## Local setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Set a unique `SECRET_KEY` in `.env`. For Attack Arena execution, configure a
private or managed Judge0 instance:

```env
JUDGE0_API_URL=https://your-judge0-host.example
JUDGE0_AUTH_TOKEN=your-runner-token-if-required
JUDGE0_AUTH_HEADER=X-Auth-Token
JUDGE0_PYTHON_LANGUAGE_ID=71
```

NVIDIA NIM is optional. Without a key, CodeRoad remains usable and transparently
uses deterministic challenge/candidate templates:

```env
NVIDIA_NIM_KEY=
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_NIM_MODEL=deepseek-ai/deepseek-v4-pro
NVIDIA_NIM_TIMEOUT_SECONDS=20
NVIDIA_NIM_CACHE_MAX_ENTRIES=128
```

Run the API:

```bash
uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

Health endpoints:

- `GET /health`
- `GET /api/v1/health`

## Main endpoints

- `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, and `GET /api/v1/auth/me`
- `POST /api/v1/matches/queue/join` and `POST /api/v1/matches/queue/leave`
- `GET /api/v1/matches/{match_id}` and `POST /api/v1/matches/{match_id}/done`
- `POST /api/v1/submissions/`
- `GET /api/v1/leaderboard/global`
- `GET /api/v1/stats`
- `GET /api/v1/attack-rounds/problems`
- `POST /api/v1/attack-rounds/analyze`
- `ws://localhost:8000/ws/{match_id}`

All non-public endpoints require a normal CodeRoad bearer token. Attack Arena
currently supports Python Maximum Subarray and returns a verified witness only
when exactly one solution passes a deterministically checked test.

## Verification

```bash
PYTHONPATH=. pytest -q
python -m compileall -q app tests
```

The tests cover adversarial-test validation, deterministic fallbacks, NVIDIA NIM
response handling, Judge0 request normalization, fail-closed execution,
matchmaking templates, deployment-secret assertions, and WebSocket access
checks.

## Deployment

Render installs `requirements-render.txt` and serves `/health`; configure all
credentials only in the provider's environment settings:

- `DATABASE_URL`
- `SECRET_KEY`
- `NVIDIA_NIM_KEY` (optional)
- `JUDGE0_API_URL` and `JUDGE0_AUTH_TOKEN` (required for execution)

Never commit database URLs, API keys, runner tokens, or database exports. Read
the repository [security policy](../SECURITY.md) before a public deployment.
