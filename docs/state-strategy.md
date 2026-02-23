# Production State Strategy

## Current state

- Ranked queue/match state: in-memory process variables.
- Rate limit counters: in-memory process variables.
- Metrics snapshot: in-memory counters.

This is acceptable for local dev and single-instance deployment only.

## Target architecture

- Redis for shared transient state:
  - ranked queue entries
  - pending matches
  - short-lived locks
  - rate limit buckets
- PostgreSQL remains source of truth for durable entities:
  - users, sessions, attempts, tiers, seasons

## Migration plan

1. Introduce `state_backend` config (`inmemory` | `redis`).
2. Extract interfaces:
   - `RankedStateStore`
   - `RateLimitStore`
3. Implement Redis adapters with TTL and atomic operations.
4. Keep in-memory adapters for tests/local.
5. Add integration tests for multi-worker behavior.

## Operational requirements

- Configure Redis URL and credentials.
- Set TTL for stale queue entries and pending match payloads.
- Add dashboards/alerts for limiter rejects and queue depth.
