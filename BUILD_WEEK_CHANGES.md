# CodeRoad Build Week change specification

**Branch:** `build-week/attack-round`
**Baseline branch:** `main`
**Baseline commit:** `ef4d1d2b88921b3808193044a0efff1c9e2d7a2a`
**Baseline commit date:** 2026-04-18
**Build Week implementation date:** 2026-07-19
**Primary new capability:** Adversarial Test Arena
**AI model path:** Configured OpenAI model through the Responses API (default `gpt-4.1-mini`)

This is the exhaustive implementation record for the Build Week branch. It is
intended to serve four jobs:

1. explain the product to its owner and judges;
2. document the exact delta from the pre-existing CodeRoad repository;
3. provide a reproducible setup, verification, and deployment runbook;
4. make provenance explicit so the submission does not imply that the entire
   platform was created during Build Week.

It complements the source code. It does not replace the actual Git diff.

---

## 1. Executive summary

### Before this branch

CodeRoad was already a broad competitive-coding application. It had accounts,
profiles, match queues, WebSockets, ratings, coding and debugging arenas,
Monaco editors, challenge generation, persistence, and deployment material.

Its core competition loop was conventional:

> receive a challenge → write code → submit → run a fixed test suite → score

The repository also contained inherited security and credibility problems:

- player code could be launched through a host `python3` subprocess;
- production credentials appeared in tracked files;
- an exported database contained player emails and password hashes;
- the app could automatically restore that export from a public URL;
- an unauthenticated migration endpoint interpolated caller-controlled SQL
  identifiers;
- a paste-event heuristic was presented as an XGBoost AI-authorship result;
- landing-page counters were fabricated;
- the deployment blueprint contained duplicate/broken environment structure;
- the Docker backend referenced a missing requirements file and a mis-cased
  Dockerfile;
- several frontend type/lint defects prevented a clean verification gate.

### After this branch

CodeRoad has a focused, judgeable new loop:

> two solutions pass ordinary tests → GPT-5.6 attacks their assumptions →
> normal code validates the attacks → an isolated runner executes both → one
> verified counterexample reveals the more robust implementation

The result is visual, technically non-trivial, and inspectable. The language
model contributes reasoning without controlling truth.

The branch also removes the inherited high-risk migration and execution paths,
sanitizes current deployment material, replaces inflated claims with accurate
labels, and adds automated tests.

---

## 2. Provenance and eligibility boundary

### Pre-existing work

The following existed before the event and must be disclosed as the foundation:

| Area | Pre-existing capability |
|---|---|
| Identity | Registration, login, JWT authentication, profile data |
| Competition | Matchmaking, match state, ratings, leaderboard |
| Real time | WebSocket manager and live match messaging |
| Coding UI | Monaco editor and arena layouts |
| Challenges | Coding/debug challenge models and generation service |
| Persistence | SQLAlchemy models, SQLite/PostgreSQL support |
| Visual system | Landing-page art direction, navigation, cards, typography |
| Hosting | Render/Vercel/AWS-era deployment files and migration utilities |

### Build Week work

The following is the material new work on this branch:

| Area | Build Week capability |
|---|---|
| Product loop | Adversarial Test Arena and A/B robustness duel |
| OpenAI | One bounded GPT-5.6 structured-output call per uncached duel |
| Correctness | Typed candidates, constraint validation, deterministic oracle |
| Proof | Verified witness and deterministic winner selection |
| Safety | Judge0-only code execution with fail-closed behavior |
| Resilience | Explicit zero-credit fallback and model-call LRU cache |
| Frontend | Dedicated two-editor Attack Arena and animated result swarm |
| Public truth | Database-backed landing statistics and honest demo labels |
| Integrity truth | Behavioral signal labels replacing false XGBoost claims |
| Security | Secret cleanup, export removal, migration endpoint removal |
| Real-time safety | Authenticated, participant-only, bounded WebSocket relay |
| Quality | Backend tests, TypeScript build gate, zero-warning lint |
| Documentation | New README, security policy, env examples, this specification |

### Required submission wording

Use wording similar to this in Devpost:

> CodeRoad is my pre-existing competitive-coding platform. During OpenAI Build
> Week I created the Adversarial Test Arena: a new GPT-5.6-powered robustness
> round that proposes typed counterexamples, validates them with deterministic
> problem contracts, executes both programs in a separate sandbox, and reveals
> only independently verified witnesses. I also rebuilt the execution boundary
> and corrected inherited security and integrity-claim issues.

Do not say or imply that the entire CodeRoad platform was built during the
event. Preserve the repository history or otherwise publish the above
provenance with the code.

---

## 3. Product definition

### User

A learner, interviewer, competitive programmer, or reviewer comparing two
implementations that both appear correct against a basic suite.

### Problem

A fixed suite answers only:

> Did the program pass the cases someone already thought to write?

It does not reveal which assumptions were never tested. A plausible but wrong
solution can look identical to a robust solution on ordinary examples.

### New value proposition

CodeRoad turns testing into an adversarial second round. It tries to find one
small, understandable input that distinguishes the two implementations and then
proves the result without trusting model prose.

### Current demo contract

Problem: Maximum Subarray.

Input:

- one non-empty integer array;
- length from 1 through 30;
- each value from -100 through 100.

Solution interface:

```python
def solve(arr):
    # return one integer
    ...
```

Ordinary cases deliberately contain a non-negative optimum. This lets the
common zero-initialization bug qualify for the second round.

The adversarial witness is normally an all-negative array. The non-empty
contract means the correct result is the least-negative value, not zero.

### Non-goals for this build

- judging arbitrary natural-language problem statements;
- model-generated expected outputs;
- model-selected winners;
- formal proof of correctness for all inputs;
- every language or every CodeRoad challenge;
- multiplayer Attack Arena persistence;
- autonomous code repair;
- replacing the existing match system.

---

## 4. End-to-end user flow

1. A signed-in user opens `/attack-arena`.
2. The page loads a real Maximum Subarray contract and two editable Python
   implementations.
3. The user selects **Attack both solutions**.
4. The frontend sends both source strings to
   `POST /api/v1/attack-rounds/analyze`.
5. The backend runs both implementations against the ordinary suite in Judge0.
6. If either fails, the API returns `baseline_failed`; no OpenAI call is made.
7. If both pass, the generator checks its hash-keyed LRU cache.
8. On a cache miss and with `OPENAI_API_KEY`, one GPT-5.6 `responses.parse`
   request returns `CandidateBatch`.
9. Without an API key, on initialization failure, or on model-call failure, the
   generator explicitly chooses `deterministic-fallback`.
10. Normal Python validates every candidate's type, length, and range.
11. Duplicate candidates and candidates already in the ordinary suite are
    removed.
12. The deterministic Kadane oracle calculates each expected output.
13. Both solutions run against every verified candidate in Judge0.
14. A candidate becomes a witness only if exactly one solution passes.
15. The first verified witness determines the robustness winner.
16. The frontend renders ordinary trials, the candidate swarm, the source label,
    the witness, actual outputs, expected output, and verdict.

There is no client-side winner logic and no hardcoded response payload.

---

## 5. Trust-boundary design

### What GPT-5.6 may do

- inspect two source strings as data;
- infer likely hidden assumptions;
- propose small integer arrays;
- assign a bounded category;
- provide a short human-readable rationale;
- state which assumption a candidate targets.

### What GPT-5.6 may not do

- decide whether an input is valid;
- supply an expected answer;
- execute player code;
- change CPU/memory/network settings;
- decide pass/fail;
- select the winning solution;
- access database or deployment credentials.

### Deterministic ownership

| Decision | Owner |
|---|---|
| Candidate JSON shape | Pydantic structured-output schema |
| Length/value/type constraints | `ProblemContract.validate` |
| Expected answer | `ProblemContract.oracle` |
| Actual answer | Judge0 execution output |
| Pass/fail | string comparison after successful runner status |
| Winner | XOR of the two pass/fail values |
| Missing runner behavior | fail closed with HTTP 503 |
| Generation-source disclosure | backend response enum |

### Why this matters to the judging story

The implementation demonstrates useful AI orchestration while avoiding the weak
claim that an LLM is a source of mathematical truth. The model performs the
open-ended search; normal software verifies the result.

---

## 6. Backend file-by-file diff

### `backend/app/schemas/attack_round_schema.py` — new

Defines all new typed contracts:

- `AttackCategory` limits model categories;
- `CandidateInput` bounds values, rationale, and targeted assumption;
- `CandidateBatch` limits model output to 1–12 candidates;
- `AttackSolution` allows Python and caps source at 50,000 characters;
- `AttackRoundRequest` currently allows only `max-subarray`;
- `AttackProblem` exposes the public contract;
- `ExecutionView` normalizes runner output;
- `BaselineTrial` records an ordinary test;
- `AttackTrial` adds rationale, category, and distinction state;
- `AttackRoundResponse` exposes source, counts, witness, winner, and verdict.

The strict request literal prevents a client from claiming support for an
unimplemented arbitrary problem.

### `backend/app/services/attack_problem_registry.py` — new

Defines the deterministic problem boundary:

- `maximum_subarray` implements the non-empty Kadane oracle;
- `ProblemContract` binds UI metadata, ordinary tests, validator, parser/output
  functions, and limits;
- `MAX_SUBARRAY` is the only registered contract;
- `get_problem` fails for unknown IDs.

To add another problem, a developer must write a real validator and oracle.
Adding a prompt alone is insufficient by design.

### `backend/app/services/counterexample_generator.py` — new

Defines three generation modes:

1. `OpenAICandidateGenerator`
   - uses `client.responses.parse`;
   - defaults to model `gpt-5.6`;
   - requests the Pydantic `CandidateBatch` directly;
   - uses `store=False`;
   - caps output at 1,600 tokens;
   - treats supplied source as inert data;
   - asks for candidates, not answers;
   - hashes the problem and source pair for a bounded LRU cache.

2. `DeterministicCandidateGenerator`
   - uses a curated boundary library;
   - makes zero API calls;
   - returns the honest source label `deterministic-fallback`;
   - keeps local development and outage behavior demonstrable.

3. `ResilientCandidateGenerator`
   - prefers GPT-5.6 when a key exists;
   - catches initialization or request failure;
   - logs the failure without logging the key or source;
   - selects the fallback explicitly.

The cache stores only typed candidate batches in process memory. It does not
persist source code to the application database. Its size is controlled by
`OPENAI_CACHE_MAX_ENTRIES`.

### `backend/app/services/attack_round_service.py` — new

Orchestrates the proof pipeline:

- retrieves the registered problem;
- runs the baseline cases;
- avoids model spend if baseline qualification fails;
- generates candidate hypotheses;
- truncates to the configured maximum;
- validates, normalizes, deduplicates, and removes ordinary cases;
- computes deterministic expected outputs;
- runs both solutions in the isolated execution boundary;
- flags XOR outcomes as distinguished;
- chooses a winner only from a verified witness;
- returns a draw when no bounded candidate distinguishes the programs.

Pseudocode:

```text
ordinary = execute(A, B, fixed_cases)
if not all_both_pass(ordinary):
    return baseline_failed

proposed = model_or_fallback(A, B, problem)
verified = validate_and_dedupe(proposed)

for candidate in verified:
    expected = oracle(candidate)
    actual_a = isolated_execute(A, candidate)
    actual_b = isolated_execute(B, candidate)
    pass_a = accepted(actual_a) and actual_a == expected
    pass_b = accepted(actual_b) and actual_b == expected
    if pass_a XOR pass_b:
        witness = candidate
        winner = A if pass_a else B
        break
```

### `backend/app/api/attack_round.py` — new

Adds authenticated endpoints:

- `GET /api/v1/attack-rounds/problems`
- `POST /api/v1/attack-rounds/analyze`

The synchronous runner/model orchestration is sent through Starlette's thread
pool so it does not block FastAPI's event loop. Known failures map to bounded
HTTP responses:

- Judge0 missing/unavailable → 503;
- invalid problem/value → 422.

### `backend/app/services/judge_service.py` — replaced

Before:

- wrote submitted source to a temporary file;
- called host `python3` with `subprocess`;
- placed untrusted code in the API server's process/container boundary.

After:

- `Judge0Client` posts to a separately hosted runner;
- `JudgeService` exposes normalized execution methods;
- source receives a stable driver that calls `solve`;
- CPU, wall-time, memory, file-size, and no-network fields are requested;
- language support is restricted to configured Python;
- missing configuration raises `CodeExecutionUnavailable`;
- normal submissions fail closed with `SECURITY_VIOLATION` rather than executing
  locally;
- runner errors are normalized and diagnostics are capped.

No `subprocess`, `eval`, or host runtime invocation remains in the module.

### `backend/app/api/public.py` — new

Adds `GET /api/v1/stats`. It returns exact counts for:

- players;
- concluded matches;
- challenges;
- active matches.

This replaces fabricated marketing counters with query-backed values. A new
database correctly reports zero.

### `backend/app/api/websocket.py` — changed

Before, any client that knew or guessed a match ID could join the room and
receive or inject code/chat messages.

After:

- the browser offers its JWT through a dedicated WebSocket subprotocol;
- the server validates the token before accepting;
- the server checks the player participates in the requested match;
- messages are byte and field bounded;
- only `CODE_SYNC` and `CHAT` are relayed;
- outgoing messages are rebuilt with server-owned player identity;
- invalid or unsupported messages receive bounded errors.

### `backend/app/app.py` — changed

- registers the public and Attack Round routers;
- updates application description/version;
- rejects the default development `SECRET_KEY` in production;
- removes automatic public backup restoration;
- removes the unauthenticated migration router;
- stops returning exception strings to clients;
- performs only schema creation automatically at startup.

### `backend/app/config.py` — changed

Adds:

- `JUDGE0_API_URL`
- `JUDGE0_AUTH_TOKEN`
- `JUDGE0_AUTH_HEADER`
- `JUDGE0_PYTHON_LANGUAGE_ID`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_TIMEOUT_SECONDS`
- `OPENAI_CACHE_MAX_ENTRIES`
- `ATTACK_ROUND_MAX_CANDIDATES`

The API key remains optional; Judge0 remains mandatory for any real execution.

### `backend/app/api/submission.py` — changed

- preserves the existing submission pipeline while routing evaluation through
  the new isolated judge service;
- removes response fields that implied an AI-authorship probability;
- reports the available integrity signal accurately;
- relies on real match identifiers rather than frontend prototypes.

### `backend/app/schemas/submission_schema.py` — changed

- caps code length;
- replaces an overstated AI-assistance probability with optional/accurately
  named integrity-signal fields;
- exposes the integrity model label used.

### `backend/app/services/integrity_service.py` — changed

Before, disabled or unavailable XGBoost behavior could still be surfaced as if
an ML classifier had made an AI-authorship judgment.

After:

- only paste-event behavioral information contributes to the current score;
- the model label is `behavioral_signals_v1`;
- the result is called an integrity signal, not proof or AI probability.

### `backend/app/services/challenge_service.py` — changed

- removes logging of API-key prefixes;
- logs key slot names only;
- keeps existing challenge behavior otherwise intact.

### `backend/app/api/data_migration.py` — deleted

The old route accepted arbitrary table names and row-column maps without
authentication. It constructed SQL identifiers from request data. This is not a
safe production migration interface and is removed.

### `backend/app/core/auto_migrate.py` — deleted

The old startup path fetched a repository-hosted production export and posted
its contents through the unsafe migration route. It is removed. Production
migration must be an authenticated, reviewed one-off job.

### `coderoad_production_export.json` — deleted

The tracked export contained personal data including emails and password hashes.
It is excluded from the Build Week tree and new export patterns are ignored.
History remediation and credential rotation are still required.

### `backend/requirements*.txt` — changed

Adds the supported OpenAI Python SDK range needed for `responses.parse` and
structured output. Runtime/dev/Render requirement files are kept aligned for
this dependency.

### `backend/.env.example` — new

Documents placeholders for database, signing, OpenAI, Judge0, and existing
challenge-generation configuration. It contains no live secret.

### `backend/Dockerfile` — renamed and fixed

- corrects the Linux filename from `DockerFile` to `Dockerfile`;
- installs the existing Render requirements instead of missing
  `requirements-prod.txt`;
- uses standard-library `urllib` for the health check instead of an undeclared
  `requests` dependency;
- runs as a non-root user.

---

## 7. Frontend file-by-file diff

### `frontend/src/pages/AttackArena.tsx` — new

Implements the complete judge-facing experience:

- authenticated page shell and profile loading/error states;
- problem statement and constraints;
- two independently editable Monaco instances;
- preloaded common-bug and robust solutions;
- real API request and loading state;
- ordinary test result grid;
- animated adversarial swarm;
- source disclosure (`gpt-5.6` or `Zero-credit fallback`);
- witness highlighting;
- actual and expected outputs;
- deterministic robustness verdict;
- runner/API error surface.

The preloaded source is a demo fixture. Trial and winner data are not fixture
objects in the frontend; they come from the backend response.

### `frontend/src/pages/AttackArena.css` — new

Provides:

- dark high-contrast arena art direction;
- A/B editor framing;
- responsive two-column/stacked layouts;
- clear stage hierarchy;
- animated candidate entry;
- pass/fail/witness states;
- verdict styling;
- loading and unavailable states.

### `frontend/src/services/attackRoundService.ts` — new

Defines TypeScript equivalents of the backend API and the two endpoint calls.
The union types prevent the frontend from silently treating arbitrary status or
generation-source strings as valid.

### `frontend/src/services/publicStatsService.ts` — new

Fetches the real public statistics endpoint. Network failure falls back to zero,
not invented social-proof values.

### `frontend/src/App.tsx` — changed

Adds the protected `/attack-arena` route.

### `frontend/src/components/Header.tsx` — changed

Adds a visible Attack Arena navigation action to signed-in application pages.

### `frontend/src/pages/Landing.tsx` — changed

- replaces static/fabricated totals with database-backed public stats;
- changes the animated duel label from `LIVE` to `INTERACTIVE SAMPLE`;
- introduces Adversarial Test Arena and inspectable verification messaging;
- updates hero copy to lead with robust testing instead of generic AI claims.

### `frontend/src/pages/Arena.tsx` — changed

- removes the `prototype_match_id` submission fallback;
- requires a real match before submission;
- shows compilation/security execution states;
- presents paste telemetry as an integrity signal;
- fixes conditional React hooks and malformed JSX;
- guards WebSocket payload parsing.
- sends the existing JWT through the WebSocket subprotocol;
- stops logging connection payloads/source updates in the browser console.

### Existing page/service typing fixes

The following receive narrow type-safety/lint fixes needed to make the entire
frontend pass, not just the new page:

- `frontend/src/components/MatchHistory.tsx`
- `frontend/src/pages/Login.tsx`
- `frontend/src/pages/Register.tsx`
- `frontend/src/services/authService.ts`
- `frontend/src/services/debugChallengeService.ts`
- `frontend/src/services/matchHistoryService.ts`
- `frontend/src/services/matchmakingService.ts`
- `frontend/src/services/submissionService.ts`

Changes replace implicit `any`, add response interfaces, guard unknown errors,
and align the frontend with real backend response shapes.

### `frontend/.env.example` — new

Provides safe local API and WebSocket URLs only. No secret belongs in a Vite
environment variable.

---

## 8. Deployment/configuration diff

### `render.yaml`

Before:

- database URL, multiple model keys, and signing secret appeared inline;
- secrets were deployable from Git;
- configuration did not include the new OpenAI/Judge0 boundaries.

After:

- `SECRET_KEY` is provider-generated;
- database, OpenAI, Judge0 URL, and runner token are provider secrets;
- model name is visible configuration only;
- the Build Week branch is named explicitly;
- the health endpoint is configured;
- no inline key or database URL remains.

### `docker-compose.yml`

- merges the backend environment into one valid mapping;
- parameterizes local database credentials;
- uses an explicitly local-only signing default;
- passes OpenAI/Judge0 configuration;
- removes broken PostgreSQL/ML/nginx service wiring and missing build/config
  references;
- starts Redis and the API with a zero-setup SQLite default while allowing a
  hosted PostgreSQL `DATABASE_URL` override;
- keeps Judge0 separate by design.

### `.gitignore`

Adds production-export patterns and continues ignoring real `.env`, virtual
environment, database, build, and dependency artifacts.

### Migration utilities

- `export_ec2_data.py` now requires `SOURCE_DATABASE_URL`;
- `migrate_ec2_postgres_to_render.py` requires
  `SOURCE_DATABASE_URL`/`TARGET_DATABASE_URL`;
- `migrate_to_postgres.py` reads `TARGET_DATABASE_URL`, requires TLS by
  default, and contains no production fallback credential;
- `RENDER_MIGRATION_GUIDE.md` directs operators to provider secrets instead of
  publishing URLs.

These scripts remain operational tools; they are not reachable as public API
routes.

---

## 9. API contract

### Authentication

The Attack Round API uses the existing CodeRoad bearer-token dependency.

### Request

```json
{
  "problem_id": "max-subarray",
  "solution_a": {
    "label": "Solution A",
    "code": "def solve(arr):\n    ...",
    "language": "python"
  },
  "solution_b": {
    "label": "Solution B",
    "code": "def solve(arr):\n    ...",
    "language": "python"
  }
}
```

### Successful response shape

```json
{
  "problem": {
    "id": "max-subarray",
    "title": "Maximum Subarray",
    "statement": "...",
    "input_format": "...",
    "constraints": ["1 ≤ n ≤ 30"],
    "ordinary_tests": [[4, -1, 2, 1]],
    "boilerplate_code": "..."
  },
  "generation_source": "gpt-5.6",
  "model": "gpt-5.6",
  "generation_note": "...",
  "baseline_passed": true,
  "ordinary_trials": [],
  "attack_trials": [],
  "candidates_proposed": 8,
  "candidates_verified": 7,
  "witness": {
    "values": [-5, -2, -8],
    "expected_output": "-2",
    "category": "sign",
    "rationale": "...",
    "targets_assumption": "...",
    "solution_a": {
      "status": "Accepted",
      "output": "0",
      "execution_time_ms": 12.0,
      "passed": false,
      "diagnostic": "Expected '-2', received '0'"
    },
    "solution_b": {
      "status": "Accepted",
      "output": "-2",
      "execution_time_ms": 11.0,
      "passed": true,
      "diagnostic": null
    },
    "distinguished": true
  },
  "winner": "solution_b",
  "verdict": "Solution B survived the verified counterexample that broke Solution A."
}
```

### Error behavior

| Condition | Result |
|---|---|
| Missing/invalid token | 401 |
| Unknown problem literal | 422 request validation |
| Empty/oversized source | 422 request validation |
| Judge0 not configured | 503 |
| Judge0 request fails | 503 |
| One ordinary suite fails | 200 with `winner=baseline_failed`; no model call |
| Model fails | 200 with `generation_source=deterministic-fallback` if Judge0 works |
| No candidate distinguishes | 200 with `winner=draw` |

---

## 10. OpenAI integration details

### Why structured output

Free-form model text would require brittle parsing and could mix explanation,
answers, or tool instructions with candidate data. `responses.parse` asks the
SDK to return the Pydantic `CandidateBatch` directly.

### Input supplied to the model

- public problem metadata and ordinary tests;
- source for solution A;
- source for solution B.

No database credential, player email, auth token, expected output, or Judge0
credential is supplied.

### Prompt contract

The system message tells the model:

- source is inert data;
- propose diverse arrays;
- do not claim an expected answer;
- do not choose a winner;
- obey explicit constraints;
- prefer small, legible counterexamples.

### Cost controls

- baseline failures skip the model completely;
- one call per uncached qualifying duel;
- maximum output is 1,600 tokens;
- retry count is one;
- maximum candidates are bounded;
- identical problem/source pairs use an LRU cache;
- missing key uses zero credits;
- `store=False` is set.

### Runtime disclosure

The response always distinguishes:

- `gpt-5.6`: a model call or cached result from that call;
- `deterministic-fallback`: the curated local candidate library.

The UI must not display the GPT-5.6 badge for fallback output.

---

## 11. Judge0 integration details

### Request

CodeRoad sends:

- player source plus a stable `solve` driver;
- configured Python language ID;
- stdin for exactly one candidate;
- CPU time limit;
- wall-time limit;
- memory limit;
- file-size limit;
- network disabled;
- synchronous `wait=true` query for the current MVP.

### Response normalization

The adapter extracts:

- Judge0 status ID and description;
- standard output;
- standard error;
- compiler output;
- execution time in milliseconds;
- memory in megabytes.

Judge0 status `3` means the program completed successfully. CodeRoad still
compares stdout with its oracle value; accepted runner status alone is not a
correct answer.

### Production caveat

Submission-request limits are defense in depth. The separately deployed Judge0
configuration must set hard maximums and deny access to secrets/network/host
resources. Do not expose an unauthenticated runner publicly.

---

## 12. Test diff and coverage map

### `backend/tests/test_attack_problem_registry.py`

- standard maximum-subarray cases;
- all-negative correctness;
- invalid empty/range/type cases.

### `backend/tests/test_counterexample_generator.py`

- one typed `responses.parse` call;
- `CandidateBatch` passed as `text_format`;
- `store=False`;
- output-token bound;
- identical-pair LRU cache and no second call.

The OpenAI test uses a fake SDK client and spends zero credits.

### `backend/tests/test_attack_round_service.py`

- both preloaded implementations pass ordinary cases;
- duplicate candidates are removed;
- out-of-range candidates are removed;
- deterministic expected output is `-2` for the witness;
- buggy output is `0`;
- robust output is `-2`;
- solution B wins;
- generation is skipped when the baseline is not a tie.

The service test uses a semantic fake runner; it never executes arbitrary code
on the test host.

### `backend/tests/test_judge_service.py`

- unconfigured runner fails closed;
- Judge0 request URL and auth header;
- CPU/memory/no-network fields;
- time/memory normalization;
- stable solve driver;
- no `eval` in driver;
- no `subprocess` import in judge module.

### `backend/tests/test_deployment_security.py`

- no inline Render secrets;
- all sensitive Render fields are provider-managed;
- one backend Compose environment mapping;
- unsafe migration route/module removed;
- production export removed;
- no tracked Python bytecode.

### `backend/tests/test_websocket_security.py`

- dedicated authentication subprotocol extraction;
- missing/empty token rejection.

### Frontend gates

The frontend has no separate component test framework in the baseline. The
branch therefore uses:

- ESLint across all source;
- TypeScript project build;
- Vite production bundle;
- local HTTP/startup inspection;
- browser inspection when the environment permits localhost access.

---

## 13. Reproducible verification procedure

### Clean backend environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
PYTHONPATH=. pytest -q
python -m compileall -q app tests
```

### Route import assertion

```bash
PYTHONPATH=backend python - <<'PY'
from app.app import app
paths = {route.path for route in app.routes}
assert "/api/v1/attack-rounds/analyze" in paths
assert "/api/v1/stats" in paths
assert "/api/v1/migrate/table" not in paths
print("route registration: ok")
PY
```

### Frontend

```bash
cd frontend
npm ci
npm run lint
npm run build:check
```

### Diff hygiene

```bash
git diff --check
git status --short
git ls-files '*__pycache__*'
```

### Secret scan

Use GitHub secret scanning, Gitleaks, TruffleHog, or an equivalent approved tool
against both the current tree and all history. A clean current scan does not
make an already-published credential safe.

### Real Judge0 smoke test

1. Set a fresh development `SECRET_KEY`.
2. Set `JUDGE0_API_URL` and any auth token.
3. Leave `OPENAI_API_KEY` empty first.
4. Register a local user.
5. Open Attack Arena.
6. Run the preloaded duel.
7. Confirm `generation_source=deterministic-fallback`.
8. Confirm both ordinary suites pass.
9. Confirm an all-negative verified witness.
10. Confirm Solution B wins.
11. Add a fresh OpenAI key.
12. Repeat with modified source to avoid the previous cache key.
13. Confirm `generation_source=gpt-5.6`.
14. Repeat the exact pair.
15. Confirm the response note says the cached model result was reused.

### Failure smoke test

1. Clear `JUDGE0_API_URL`.
2. Run the duel.
3. Confirm the API responds 503.
4. Confirm the UI says isolated execution is unavailable.
5. Confirm no local Python process is launched by the application.

### Verification record (2026-07-19)

The final workspace run produced:

- backend: **21 tests passed**;
- Python dependency consistency: **no broken requirements**;
- Python compile/import and route assertions: **passed**;
- frontend ESLint: **passed**;
- TypeScript plus Vite production build: **passed**;
- npm production dependency audit: **0 vulnerabilities reported**;
- current source-tree credential-pattern scan: **clean**;
- Git whitespace check: **passed**;
- tracked Python bytecode check: **clean**;
- local HTTP smoke: health, exact stats, registration, protected problem list,
  fail-closed Attack endpoint, removed migration route, and Vite HTML all passed.

Two warnings remain inside third-party Python dependencies (`python-multipart`
import naming and Passlib's use of Python's deprecated `crypt` module). They do
not originate in CodeRoad source and did not fail the dependency consistency
check.

The cloud browser refused localhost before loading the page, so this environment
did not complete a visual click-through. The production frontend bundle is
verified, but the hosted desktop/mobile browser checkbox intentionally remains
open.

---

## 14. Deployment runbook

### Phase A: credentials

1. Revoke every credential that existed in old repository files or chat.
2. Create a fresh OpenAI project key with a small budget.
3. Generate a fresh application signing key.
4. Rotate database passwords.
5. Create a Judge0 API credential.
6. Store all values in provider secret managers.

### Phase B: isolated runner

1. Deploy self-hosted Judge0 or obtain managed Judge0 access.
2. Restrict ingress.
3. Deny worker network egress where feasible.
4. Verify worker resource ceilings.
5. Check the deployment's Python language ID.
6. Test one synchronous submission.
7. Record the HTTPS base URL and auth header/token.

### Phase C: database

1. Provision PostgreSQL or Supabase Postgres.
2. Require TLS.
3. Create a least-privileged app user.
4. Set `DATABASE_URL` in Render.
5. Start with a clean schema unless a reviewed migration is required.
6. Do not upload the deleted public export.

### Phase D: backend

1. Connect the repository/branch to Render.
2. Apply `render.yaml`.
3. Set `DATABASE_URL`.
4. Set `JUDGE0_API_URL`.
5. Set `JUDGE0_AUTH_TOKEN` if needed.
6. Set a fresh `OPENAI_API_KEY`.
7. Keep `OPENAI_MODEL=gpt-5.6`.
8. Deploy.
9. Confirm `/health`.
10. Confirm production does not expose `/docs` unless intentionally enabled.
11. Register a test account.
12. Run the deterministic and GPT smoke tests.

### Phase E: frontend

1. Configure the Vercel project root as `frontend`.
2. Set `VITE_API_URL` to the HTTPS backend plus `/api/v1`.
3. Set `VITE_WS_URL` to the WSS backend plus `/ws`.
4. Deploy.
5. Register and log in.
6. Open Attack Arena.
7. Verify desktop and mobile layouts.
8. Verify network errors are intelligible.

### Phase F: abuse/cost controls

1. Configure per-user/IP limits at the gateway.
2. Set OpenAI project spend limits and alerts.
3. Cap runner concurrency.
4. Monitor 429/5xx latency and queue depth.
5. Ensure logs do not include source, bearer tokens, or API keys.
6. Configure uptime monitoring for backend/frontend only after the app works;
   monitoring does not make a sleeping free-tier service production-grade.

---

## 15. Three-minute demo script

### 0:00–0:20 — problem

> “A coding solution can pass every test you happened to write and still be
> wrong. CodeRoad makes passing the obvious suite only the qualification round.”

Show the two solutions side by side. Point at the different initialization.

### 0:20–0:45 — ordinary tie

Press **Attack both solutions**. Show all four ordinary tests passing for A and
B.

> “A normal judge calls this a tie.”

### 0:45–1:20 — model role

Show the candidate swarm and source badge.

> “GPT-5.6 reads both programs and proposes typed inputs targeting their hidden
> assumptions. It never supplies an answer or a winner.”

### 1:20–1:55 — proof moment

Focus on the all-negative witness.

> “Normal code validates this input. A deterministic Kadane oracle says the
> non-empty answer is minus two. Both solutions execute in a separate Judge0
> sandbox. A returns zero. B returns minus two.”

Show the witness and verdict.

### 1:55–2:25 — architecture

> “The model proposes; code proves. If OpenAI is unavailable, the UI says it is
> using the zero-credit fallback. If the isolated runner is unavailable, the app
> refuses to execute rather than running hostile code on the server.”

### 2:25–2:50 — extension

> “Each new problem requires an explicit input contract and oracle. That makes
> the approach extensible without turning an LLM into a source of truth.”

### 2:50–3:00 — provenance

> “CodeRoad is my pre-existing platform. The Adversarial Test Arena, GPT-5.6
> pipeline, deterministic proof engine, isolated execution rebuild, and security
> corrections are my Build Week work.”

---

## 16. Acceptance checklist

### Product

- [x] Dedicated Attack Arena route
- [x] Two editable real source inputs
- [x] Ordinary qualification suite
- [x] Model/fallback candidate generation
- [x] Deterministic candidate validation
- [x] Deterministic oracle
- [x] Isolated execution client
- [x] Verified witness calculation
- [x] Winner/draw/baseline-failed states
- [x] Generation source disclosure
- [x] Model-result cache
- [x] Database-backed landing counts

### Credibility

- [x] No model-generated expected answer
- [x] No model-selected winner
- [x] No fake GPT badge in fallback mode
- [x] No fabricated landing counts
- [x] No XGBoost claim without XGBoost execution
- [x] Pre-existing foundation documented
- [x] Current limitation to one problem documented

### Security

- [x] No host subprocess execution path
- [x] Missing Judge0 fails closed
- [x] Player code length bounded
- [x] Candidate size/range bounded
- [x] Model output typed
- [x] Runner limits requested
- [x] Render secrets externalized
- [x] Automatic public backup restore removed
- [x] Unauthenticated migration route removed
- [x] Production export removed
- [x] Tracked bytecode removed
- [x] WebSocket rooms require a valid participant token
- [x] WebSocket message type and size bounds
- [ ] All historical credentials rotated by repository owner
- [ ] Full Git history scrubbed/scanned by repository owner
- [ ] Public runner ingress/rate limits configured

### Verification

- [x] Backend unit tests written
- [x] Backend test suite passes locally
- [x] Python compile/import check passes
- [x] Frontend lint passes
- [x] TypeScript + production build passes
- [x] Diff whitespace check passes
- [ ] Real deployed Judge0 smoke test (requires runner URL)
- [ ] Live GPT-5.6 smoke test (requires fresh key)
- [ ] Hosted desktop/mobile browser pass

Unchecked items are genuine deployment dependencies, not hidden successes.

---

## 17. Remaining two-day priorities

Priority order:

1. Rotate the exposed credentials.
2. Deploy/configure Judge0 and run the preloaded duel end to end.
3. Create a fresh low-budget OpenAI project key and run one GPT-5.6 smoke test.
4. Deploy backend and frontend.
5. Record a tight three-minute video using the script above.
6. Add one more deterministic problem contract only if the first five items are
   complete and the first contract is flawless.
7. Finish Devpost text and provenance disclosure.

Do not spend the remaining window on:

- renaming the entire repository to conceal history;
- another broad dashboard;
- Supabase integration when existing PostgreSQL works;
- more landing-page animation before the execution service works;
- arbitrary-language support;
- a chatbot panel;
- unsupported probability or cheating claims;
- fake user counts;
- a third hosting migration.

---

## 18. Adding a second adversarial problem

Only do this after the deployed Maximum Subarray path passes.

1. Define the input type and explicit bounds.
2. Write a deterministic oracle.
3. Write a deterministic serializer for stdin.
4. Add ordinary cases that create a meaningful tie.
5. Add validators that reject booleans, invalid types, ranges, and sizes.
6. Add a `ProblemContract` to the registry.
7. Extend the Pydantic `problem_id` literal.
8. Extend the TypeScript request literal.
9. Add UI problem selection only when at least two contracts exist.
10. Add oracle unit tests.
11. Add service tests with one known buggy and one robust solution.
12. Confirm the model cannot provide the expected output.
13. Confirm the runner uses the right input driver.
14. Run the real Judge0 smoke test.

Good second-problem candidates have a small input format and a crisp witness:

- binary search boundary errors;
- duplicate-sensitive two-sum semantics;
- interval endpoint inclusivity;
- empty/singleton dynamic-programming initialization.

Avoid graph/string formats until the driver and validator abstraction is
expanded deliberately.

---

## 19. Troubleshooting

### `503 Isolated execution is not configured`

Cause: `JUDGE0_API_URL` is empty or invalid.

Fix:

1. configure a separately hosted runner;
2. verify its HTTPS URL;
3. set the auth token/header if required;
4. restart the backend;
5. verify a direct non-private smoke submission.

Do not add local host execution as a fallback.

### Runner returns unknown/compile errors

- check `JUDGE0_PYTHON_LANGUAGE_ID` on that deployment;
- inspect bounded runner diagnostics;
- verify `wait=true` support;
- verify the source exposes `solve(arr)`;
- verify the runner accepts the requested attributes.

### UI returns to login

- verify `VITE_API_URL`;
- inspect `/auth/me` response;
- clear an expired local token and sign in again;
- confirm backend CORS contains the exact frontend HTTPS origin.

### GPT path always uses fallback

- create a fresh, unexposed key;
- set it only on the backend;
- confirm the model name is available to the project;
- check backend logs for the bounded generation failure;
- edit one solution before retrying if testing a new uncached call.

### Identical retry does not spend credits

Expected behavior: the LRU cache returns the previous typed candidate batch and
adds a note that no new API credits were used. Restarting or scaling the backend
clears the per-process cache.

### Landing counts are zero

That is correct for a new database. Create real users/matches/challenges or
migrate data through a reviewed private job. Do not restore the deleted public
export and do not hardcode counters.

---

## 20. Rollback plan

The Build Week work is isolated on `build-week/attack-round`.

If the Attack Arena must be disabled without reverting security fixes:

1. remove the `/attack-arena` link and route from the frontend;
2. remove only the `attack_round` router registration;
3. keep the Judge0 execution replacement;
4. keep secret cleanup;
5. keep migration endpoint/export removal;
6. keep honest integrity labels and public statistics.

Do not rollback to the host `subprocess` judge or unauthenticated migration
endpoint.

---

## 21. Devpost technical summary draft

### Inspiration

Fixed test suites reward the assumptions test authors already anticipated. Two
programs can look equally correct until one carefully chosen input exposes a
hidden rule violation.

### What it does

CodeRoad's Adversarial Test Arena lets two implementations qualify on ordinary
tests, then uses GPT-5.6 to propose structured counterexample hypotheses. A
deterministic problem contract validates each input and calculates the expected
answer. Both programs run in a separate Judge0 sandbox. Only a verified input
that one solution passes and the other fails becomes a winning witness.

### How it was built

The new backend uses FastAPI, Pydantic Structured Outputs through the OpenAI
Responses API, deterministic Python oracles, and a Judge0 execution adapter.
The React/TypeScript frontend uses two Monaco editors and a visual candidate
swarm. The model is bounded to candidate generation; normal code owns truth and
the verdict.

### Challenges

The central challenge was building a real trust boundary. The earlier platform
ran Python via a host subprocess, which was not acceptable for arbitrary code.
The Build Week branch replaces it with a fail-closed separate runner and removes
an inherited unsafe migration route and exposed deployment material.

### Accomplishments

- one memorable verified-counterexample loop;
- typed GPT-5.6 output;
- zero model-authored expected answers;
- independently executed proof;
- explicit offline fallback;
- repeat-call cache;
- clean automated build/test gates;
- honest provenance and limitation disclosure.

### What was learned

Language models are strongest as hypothesis generators, not authorities. The
most credible AI product is often a hybrid: use the model for search and use
deterministic tools for claims that must be true.

### What's next

Add more problem contracts with explicit validators/oracles, persist verified
witnesses as shareable challenge artifacts, and create a player-vs-player mode
where competitors write adversarial tests for one another.

---

## 22. Final truth checklist for the submission

Before publishing each claim, ask:

- Did GPT-5.6 actually run in the recorded demo, or was it fallback mode?
- Did both programs actually execute in Judge0?
- Is the displayed expected output from the deterministic oracle?
- Are the player/match counts from the database?
- Is an integrity value labeled as a signal rather than proof?
- Is pre-existing CodeRoad work clearly separated from event work?
- Are all reused components owned/licensed appropriately?
- Are exposed historical credentials revoked?
- Does the public repository exclude personal data and secrets?
- Does the video show the product rather than only slides?

If any answer is no, change the claim or complete the missing verification. Do
not hide the distinction.
