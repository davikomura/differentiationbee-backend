# Differentiation Bee Backend

API do Differentiation Bee para autenticacao, geracao e validacao de questoes de derivadas, progresso por pontos/tiers e temporadas.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- SymPy
- JWT (python-jose)
- Pytest

## Funcionalidades

- Auth com `access_token` e refresh token com rotacao
- Seasons com traducoes e season ativa
- Tiers localizados por idioma
- Sessao de jogo, emissao de questoes e tentativas
- Leaderboard global e por temporada
- Daily challenge deterministico por dia
- Estatisticas do usuario
- Healthcheck e metricas basicas
- Rate limiting por IP em memoria

## Setup

Crie `.env`:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost/dbname
JWT_SECRET_KEY=supersecret
REFRESH_TOKEN_EXPIRE_DAYS=30
MAX_REFRESH_TOKENS_PER_USER=3
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ALLOW_ORIGINS=http://localhost:5173
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
```

Instalacao:

```bash
pip install -r requirements.txt
```

Rodar migrations:

```bash
python -m app.scripts.create_tables
```

Subir API:

```bash
uvicorn app.main:app --reload
```

Swagger:

`http://127.0.0.1:8000/docs`

## Endpoints principais

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

### Game

- `GET /game/daily-challenge`
- `POST /game/question`

### Sessions e Attempts

- `POST /sessions/start`
- `POST /sessions/{session_id}/finish`
- `GET /sessions/{session_id}`
- `GET /sessions?limit=20`
- `POST /attempts`

### Rankings e stats

- `GET /leaderboard/global`
- `GET /leaderboard/season/{season_id}`
- `GET /leaderboard/season/active`
- `GET /stats/me`

### Infra

- `GET /healthz`
- `GET /metrics`

## Testes

```bash
pytest -q
```

## CI

O repositório inclui workflow em `.github/workflows/ci.yml` para instalar dependencias e rodar testes em push/PR.
