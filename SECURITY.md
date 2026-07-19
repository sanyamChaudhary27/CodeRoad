# Security policy and deployment checklist

This document describes the security properties of the Build Week branch and
the actions required before it is exposed to untrusted users.

## Immediate credential action

Older repository revisions contained deployment credentials and database URLs.
They must be treated as compromised even though the current branch removes the
plaintext values.

Before deployment:

1. Revoke every previously exposed OpenAI, Groq, database, AWS, JWT, and runner
   credential.
2. Create replacements in the relevant provider dashboard.
3. Store replacements only in Render/Vercel/AWS/Supabase secret settings or a
   local ignored `.env` file.
4. Search the complete Git history with an approved secret scanner.
5. Rewrite public history if necessary, coordinate with collaborators, and
   invalidate old clones.
6. Assume history rewriting alone is insufficient: rotation is mandatory.

Never reuse a credential that appeared in a prompt, chat, issue, screenshot,
terminal transcript, commit, or deployment blueprint.

## Removed inherited attack surfaces

The Build Week branch removes:

- plaintext database/API secrets from `render.yaml` and migration scripts;
- a production database export containing player email addresses and password
  hashes;
- automatic startup restoration from a public GitHub JSON file;
- an unauthenticated endpoint that interpolated caller-controlled table and
  column names into SQL;
- tracked Python bytecode that could retain deleted configuration strings;
- host-process execution of player code through `subprocess`;
- model-key prefix logging;
- false XGBoost/AI-authorship claims when only paste-event heuristics ran;
- fabricated landing-page counters.
- unauthenticated WebSocket rooms that allowed non-participants to observe or
  inject match code/chat updates.

The deletions are present on the Build Week branch. Sensitive material remains
recoverable from old Git commits until history is scrubbed, so credential
rotation is still required.

## Untrusted code execution boundary

Player code is hostile input.

`backend/app/services/judge_service.py` therefore follows these invariants:

- never imports `subprocess`;
- never writes player source to a local executable file;
- never invokes a language runtime in the FastAPI process or container;
- calls a separately hosted Judge0 service over HTTP(S);
- supplies CPU, wall-time, memory, file-size, and network restrictions;
- supports only the configured Python language ID;
- fails closed with `CodeExecutionUnavailable` when the runner is missing;
- maps runner failures to bounded diagnostics rather than stack traces.

The API and Judge0 should run on different hosts or isolation domains. Do not
put a privileged Docker socket inside the API container. Do not add a local
`subprocess` fallback for convenience.

Before production, harden Judge0 itself:

- authenticate the Judge0 API;
- restrict ingress to the CodeRoad backend;
- deny submission network access;
- run workers without cloud instance credentials;
- prevent access to metadata endpoints;
- set process/thread, CPU, wall-time, memory, stack, and file limits at the
  runner level, not only in the client request;
- cap queue depth and concurrent jobs;
- monitor worker restarts and resource exhaustion;
- confirm the configured language ID and runtime version;
- keep Judge0 patched.

Client-supplied limits are defense in depth. The execution service's own policy
must impose hard ceilings.

## Language-model trust boundary

The configured OpenAI model receives the public problem contract and two submitted source strings.
Source is treated as inert data in the system prompt.

The model is allowed to propose only `CandidateBatch` values:

- a bounded list of integer arrays;
- a category;
- a short rationale;
- the assumption being targeted.

The model is not allowed to provide or control:

- expected outputs;
- pass/fail status;
- code-execution settings;
- problem constraints;
- the winning solution;
- database or runner credentials.

Every candidate is revalidated by normal code. The deterministic oracle computes
the expected output. Judge0 supplies actual execution output. The winner is
derived from those facts.

The OpenAI request uses `store=False`, a strict Pydantic response schema, a
bounded output-token limit, one retry, and one logical call per uncached duel.
Identical inputs use a bounded in-process cache.

## API controls still required for a public launch

The repository enforces authentication and request-size bounds on the Attack
Arena. A public deployment should additionally enforce, at the reverse proxy or
API gateway:

- per-account and per-IP request limits;
- an OpenAI spend limit and project budget alert;
- maximum concurrent attack rounds;
- a request timeout longer than the runner limit but short enough to release
  resources;
- body-size limits;
- abuse monitoring;
- structured logs without source code, tokens, or personal data;
- a circuit breaker for Judge0/OpenAI outages.

An in-process rate limiter is insufficient when multiple backend workers or
instances are used. Prefer a gateway or Redis-backed distributed limit.

## Authentication

- Production refuses to start with the repository's development `SECRET_KEY`.
- Generate a high-entropy secret and store it outside Git.
- Use HTTPS everywhere.
- Rotate the signing secret if token exposure is suspected.
- Consider shorter access-token lifetimes and refresh-token rotation before a
  long-term public release.
- Do not place tokens in query strings or logs.
- Native browser WebSockets authenticate through the dedicated
  `coderoad-auth.<JWT>` offered subprotocol; the server accepts the public
  `coderoad` protocol only after checking match membership.
- WebSocket messages are size bounded, type checked, and rebuilt server-side
  before relay.

## Database and personal data

- Do not commit exports, snapshots, SQLite databases, emails, password hashes,
  code submissions, or user telemetry.
- Use TLS for hosted PostgreSQL.
- Give the application a least-privileged database role.
- Run schema/data migrations through authenticated one-off jobs, never public
  HTTP endpoints.
- Back up the database through the provider and test restoration privately.
- Set retention rules for player source code and behavioral signals.
- Treat paste-event telemetry as personal behavioral data.

The removed `coderoad_production_export.json` contained personal data. If that
file was ever public, assess notification and remediation obligations for the
affected deployment.

## Integrity signal limitations

CodeRoad records paste-event information. The Build Week branch reports it as
`behavioral_signals_v1` and an `integrity_signal_score`.

It must not be described as:

- proof of cheating;
- proof that AI wrote the code;
- an XGBoost result;
- a reliable probability of misconduct.

Do not automatically punish or rank-freeze a player using that signal alone.
Provide human review and an appeal path if it is used beyond the demo.

## Environment files

Tracked `.env.example` files contain only placeholders. Real `.env` files are
ignored. Required production values are:

```text
SECRET_KEY
DATABASE_URL
JUDGE0_API_URL
JUDGE0_AUTH_TOKEN (when required)
OPENAI_API_KEY (for live OpenAI generation)
```

The OpenAI key belongs only on the backend. Never use a `VITE_` prefix for a
secret; Vite variables are shipped to the browser.

## Safe incident response

If a key or database export is exposed:

1. Disable or rotate it at the provider first.
2. Review access/spend/database logs.
3. Preserve evidence privately.
4. Remove the material from the current tree.
5. Scrub history and caches if the repository is public.
6. Redeploy with new values.
7. Verify the old credential no longer works.

Do not delete and re-upload a repository as a substitute for rotation or as a
way to conceal provenance. It is neither a reliable security remediation nor a
valid representation of when work was created.

## Verification commands

```bash
cd backend
PYTHONPATH=. pytest -q
python -m compileall -q app tests

cd ../frontend
npm run lint
npm run build:check

cd ..
git diff --check
git ls-files '*__pycache__*'
```

The final command should print nothing.

## Reporting a vulnerability

Do not place exploit details, credentials, personal data, or database exports in
a public issue. Contact the repository owner privately, include the affected
component and a minimal reproduction, and rotate exposed credentials before
discussing remediation publicly.
