# CodeRoad Build Week changes

This public document describes the Build Week work relative to the pre-existing
CodeRoad platform. It is a release note and project overview, not a replacement
for Git history or a claim that all of CodeRoad was made during the event.

## Provenance

Before Build Week, CodeRoad already provided accounts, profiles, matchmaking,
ratings, WebSockets, coding and debugging arenas, Monaco editors, challenge
generation, persistence, and deployment infrastructure.

Build Week adds the **Adversarial Test Arena** and the release-hardening work
needed to demonstrate it safely. The current release is on both `main` and
`feature/aws-deployment` at the same commit.

Public project description:

> CodeRoad is a pre-existing competitive-coding platform. During OpenAI Build
> Week, the project introduced the Adversarial Test Arena: a robustness round
> that proposes bounded counterexamples, validates them against a deterministic
> contract, and reveals only independently verified witnesses. Codex with
> GPT-5.6 Terra (High) supported implementation, review, debugging, and release
> verification.

## AI disclosure

### Development

The project was built with Codex using GPT-5.6 Terra (High) for planning,
implementation, debugging, review, documentation, and test/release checks.
This satisfies the Build Week requirement to build with Codex using GPT-5.6; it
does not require the app to make an OpenAI API call at runtime.

### Production runtime

The deployed application uses NVIDIA NIM's OpenAI-compatible API for optional,
bounded hypothesis generation and future AI challenge prewarming. The default
configured model is `deepseek-ai/deepseek-v4-pro`.

The model is never the source of truth:

- deterministic validators reject invalid candidates;
- a problem-specific oracle computes expected results;
- the runner's output is independently compared with that oracle;
- only a verified XOR outcome decides an Attack Arena winner;
- a deterministic template/candidate fallback keeps the app responsive when
  NIM is missing, slow, or unavailable.

Do not describe GPT-5.6 as a live CodeRoad runtime feature unless that changes
and is independently verified before recording the demo.

## Product changes

### Adversarial Test Arena

- Adds the authenticated `/attack-arena` experience with two editable Python
  solutions and a Maximum Subarray contract.
- Adds `GET /api/v1/attack-rounds/problems` and
  `POST /api/v1/attack-rounds/analyze`.
- Runs ordinary qualification tests first, then validates model or deterministic
  counterexample proposals before execution.
- Shows a witness and winner only after one solution passes and the other fails
  a deterministic oracle check.
- Makes the generation source explicit as `nvidia-nim` or
  `deterministic-fallback`.

### Reliable arena matchmaking

- Keeps DSA and Debug queue pairing network-free.
- Delivers a stored deterministic challenge immediately after pairing.
- Prewarms NIM-selected templates in the background for future matches only.
- Retains the response schema and falls back rather than blocking either arena.

### Execution and trust boundary

- Routes player-code execution through a separately configured Judge0 runner.
- Fails closed when that runner is unavailable; no local host-process fallback
  executes untrusted player code.
- Bounds attack solution source, candidate types, values, and sizes.
- Requires an authenticated participant for WebSocket match-room access.

### Product truth and release safety

- Replaces fabricated landing statistics with database-backed public counts.
- Labels integrity output as a behavioral signal rather than proof of AI
  authorship.
- Removes unsafe migration/automatic public-export restoration paths and keeps
  provider secrets out of deployment configuration.
- Adds `requests` to Render requirements to prevent the observed startup import
  failure.
- Exposes `GET /health` and `GET /api/v1/health` for uptime monitoring.

## Configuration

Never commit secrets. Set these only in local ignored `.env` files or provider
environment settings:

```env
DATABASE_URL=postgresql://...
SECRET_KEY=replace-with-a-unique-secret
NVIDIA_NIM_KEY=optional-key
NVIDIA_NIM_BASE_URL=https://integrate.api.nvidia.com/v1
NVIDIA_NIM_MODEL=deepseek-ai/deepseek-v4-pro
NVIDIA_NIM_TIMEOUT_SECONDS=20
JUDGE0_API_URL=https://your-private-runner.example
JUDGE0_AUTH_TOKEN=optional-runner-token
```

`NVIDIA_NIM_KEY` is optional. `JUDGE0_API_URL` is required for actual code
execution, including the full Attack Arena proof path.

## Verification

Run from a clean checkout with no production secrets:

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
python -m compileall -q app tests

cd ../frontend
npm ci
npm run lint
npm run build:check
```

Manual release checks:

1. Check `/health` and `/api/v1/health` after deployment.
2. Register a disposable test account and test DSA, Debug, cancellation,
   logout, and two independent 1v1 sessions.
3. Test Attack Arena with a configured Judge0 runner and confirm the preloaded
   duel produces a verified all-negative Maximum Subarray witness.
4. Repeat with NVIDIA NIM disabled or delayed and confirm the deterministic
   fallback is shown without blocking the app.
5. Inspect Render logs for dependency imports, database connectivity, runner
   errors, and NIM fallback messages without exposing secrets or source code.

## Devpost submission checklist

- [ ] Choose the most appropriate track: **Education** or **Developer tools**.
- [ ] Add every team member to Devpost and confirm each invitation is accepted.
- [ ] Submit a public, under-three-minute YouTube demo with a voiceover.
- [ ] Show the app working and explain both Codex and GPT-5.6 Terra (High)'s
  development role in your own words.
- [ ] Add the primary Codex `/feedback` session ID to the submission.
- [ ] Link a public repository with this README and setup instructions, or share
  a private repository with `testing@devpost.com` and
  `build-week-event@openai.com`.
- [ ] Keep the pre-existing-platform provenance statement in the project
  description and video.
- [ ] Confirm no API keys, database URLs, exports, or personal data are in the
  repository or video.

Official references: [OpenAI Build Week](https://openai.com/build-week/) and
[Devpost resources](https://openai.devpost.com/resources).
