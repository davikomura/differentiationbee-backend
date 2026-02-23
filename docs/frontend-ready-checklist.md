# Frontend-Ready Checklist

## Auth

- `POST /auth/register`: ready
- `POST /auth/login`: ready
- `POST /auth/refresh`: ready
- `POST /auth/logout`: ready
- `GET /auth/me`: ready
- Notes:
  - Use `Authorization: Bearer <access_token>` for protected routes.
  - Error payload is standardized.

## Game Loop

- `POST /sessions/start`: ready
- `POST /game/question`: ready
- `POST /attempts`: ready
- `POST /sessions/{session_id}/finish`: ready
- Notes:
  - Time limit is level-based (`app/modules/game/time_limits.py`).
  - Server-side grace is applied in attempt validation.

## Session History

- `GET /sessions/{session_id}`: ready
- `GET /sessions?limit=20`: ready

## Tiers and Seasons

- `GET /tiers`: ready
- `GET /tiers/me`: ready
- `GET /seasons/active`: ready
- `POST /seasons`: backend-ready, admin-only

## Leaderboard and Stats

- `GET /leaderboard/global`: ready
- `GET /leaderboard/season/active`: ready
- `GET /leaderboard/season/{season_id}`: ready
- `GET /stats/me`: ready
- `GET /stats/me/advanced`: ready
- `GET /stats/me/evolution?days=30`: ready

## Competitive

- `POST /competitive/queue`: ready
- `GET /competitive/queue/status`: ready
- `POST /competitive/resolve/{session_id}`: ready
- Notes:
  - Resolve now checks session ownership.

## Infra

- `GET /healthz`: ready
- `GET /metrics`: dev-ready
- Notes:
  - Metrics are in-memory counters, suitable for local/dev.

## Remaining for Production Hardening

- Replace ranked queue in-memory state with shared store (Redis).
- Replace in-memory rate limit with distributed limiter.
- Add observability pipeline (Prometheus/OpenTelemetry).
- Add integration tests for critical auth/ranked paths.
