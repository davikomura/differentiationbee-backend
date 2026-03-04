# Differentiation Bee Backend

API em FastAPI para autenticacao, jogo de derivadas, progresso por pontos e tiers, temporadas, rankings e modo competitivo.

## Visao Geral

O projeto expõe uma API para um jogo de treino de derivadas. O usuario se autentica, entra em uma sessao, recebe expressoes matematicas geradas pelo backend, envia respostas e acumula pontos com base em desempenho.

O sistema combina:

- progressao individual por pontos
- classificacao por tiers
- temporadas ativas para organizar ranking
- modo practice para evolucao individual
- modo ranked para confronto entre dois jogadores

Em termos de dominio, o fluxo principal e:

1. o usuario faz login
2. o backend identifica a season ativa
3. uma sessao e criada no nivel correspondente ao tier atual do usuario
4. o backend emite questoes com limite de tempo por nivel
5. o usuario envia tentativas
6. ao finalizar a sessao, o backend calcula variacao de pontos e atualiza tier/ranking

## Stack

- FastAPI
- SQLAlchemy 2
- PostgreSQL
- Alembic
- SymPy
- JWT com `python-jose`
- Redis opcional para estado compartilhado
- Pytest

## Funcionalidades

- Autenticacao com `access_token` e refresh token com rotacao
- Padronizacao de erros para consumo pelo frontend
- Tiers localizados e consulta do tier atual do usuario
- Temporadas com season ativa e criacao de season (admin)
- Sessao de jogo, emissao de questoes e validacao de tentativas
- Daily challenge deterministico
- Leaderboard global e por temporada
- Estatisticas basicas, avancadas e evolucao por periodo
- Rate limiting por IP com backend `inmemory` ou `redis`
- Fila ranked com estado compartilhado opcional via Redis
- Healthcheck, metricas basicas e logs de requisicao

## Como Funciona

### Autenticacao

- `POST /auth/login` retorna `access_token` e `refresh_token`.
- O `access_token` protege as rotas autenticadas via bearer token.
- O `refresh_token` pode ser rotacionado em `POST /auth/refresh`.
- `POST /auth/logout` revoga o refresh token informado.

### Temporadas

- Uma season precisa estar ativa para iniciar sessoes.
- A season ativa e definida por janela de tempo: `starts_at <= agora < ends_at`.
- O endpoint `POST /seasons` e administrativo.
- A criacao de season exige traducoes para todos os idiomas suportados pelo sistema.

### Tiers e nivel

- Os tiers representam faixas de pontos.
- Cada tier possui `rank_order`, e esse valor tambem define o nivel de jogo.
- Na pratica, 1 tier corresponde a 1 nivel do gerador, limitado entre `1` e `12`.
- O nivel da sessao e derivado dos pontos atuais do usuario, nao do payload enviado pelo cliente.

### Sessoes

- Um usuario pode ter apenas uma sessao ativa por vez.
- Ao iniciar uma sessao, o backend valida:
  - se ja existe sessao ativa
  - se ha season ativa
  - se o usuario existe
- A sessao fica vinculada a uma season e registra modo (`practice` ou `ranked`), nivel e seed.

### Questoes e tentativas

- A questao emitida sempre usa o nivel da sessao.
- O backend gera a expressao e a derivada correta com SymPy.
- Cada questao possui `time_limit_ms` calculado por nivel.
- A tentativa valida:
  - posse da questao pelo usuario
  - se a questao ja foi respondida
  - se a sessao ainda esta ativa
  - se o tempo informado pelo cliente nao excede o limite
  - se o tempo observado pelo servidor nao ultrapassa o limite com folga tecnica

### Pontuacao e progressao

- Em sessoes `practice`, os pontos finais sao calculados no encerramento da sessao.
- O calculo considera:
  - quantidade de acertos
  - quantidade de erros
  - nivel da sessao
  - tempo medio de resposta
- Existe bonus (ou penalidade) por velocidade.
- Existe protecao de rebaixamento leve entre tiers (`soft demotion gap`).

### Modo ranked

- O modo ranked usa matchmaking por faixa de pontos com tolerancia inicial de 250.
- O jogador nao escolhe o nivel manualmente; o nivel tambem segue os pontos atuais.
- Quando dois jogadores casam, ambos recebem sessoes `ranked` com a mesma seed.
- A resolucao compara:
  - mais acertos
  - em caso de empate, menos erros
  - em caso de novo empate, menor tempo medio
- A variacao final usa uma formula tipo Elo com ajuste adicional por tempo medio.

## Configuracao

Crie um arquivo `.env` na raiz:

```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost/dbname
JWT_SECRET_KEY=supersecret
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
MAX_REFRESH_TOKENS_PER_USER=3
CORS_ALLOW_ORIGINS=http://localhost:5173
RATE_LIMIT_REQUESTS=120
RATE_LIMIT_WINDOW_SECONDS=60
STATE_BACKEND=inmemory
# REDIS_URL=redis://localhost:6379/0
```

`STATE_BACKEND` aceita `inmemory` ou `redis`. Se usar `redis`, configure `REDIS_URL`.

## Setup Local

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Aplique as migrations:

```bash
python -m app.scripts.create_tables
```

Opcionalmente, popule os tiers iniciais:

```bash
python -m app.scripts.seed_tiers
```

Suba a API:

```bash
uvicorn app.main:app --reload
```

Documentacao interativa:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Integracao

- Rotas protegidas usam `Authorization: Bearer <access_token>`.
- Localizacao pode ser influenciada por `Accept-Language`.
- Erros seguem payload padronizado documentado em `docs/api-contract.md`.
- O lock da especificacao OpenAPI fica em `openapi.lock.json`.

Para atualizar o lock da OpenAPI:

```bash
python -m app.scripts.export_openapi_lock
```

## Regras de Negocio

### Season ativa e obrigatoria

- `POST /sessions/start` exige que exista uma season ativa.
- `POST /competitive/queue` tambem depende de season ativa.
- Sem season ativa, a API retorna conflito (`409`) nesses fluxos.

### Uma sessao ativa por usuario

- O backend bloqueia a abertura de uma nova sessao enquanto outra estiver ativa.
- Essa regra evita concorrencia de progresso e inconsistencias de pontuacao.

### Nivel da sessao prevalece

- Mesmo que o cliente envie `level`, o backend usa o nivel derivado do tier atual do usuario ao criar a sessao.
- Ao emitir questoes, o backend reaproveita o nivel salvo na sessao.
- Isso impede que o frontend force dificuldades fora da progressao do usuario.

### Limite de tempo por nivel

Tabela atual:

- Nivel 1: `35_000 ms`
- Niveis 2-3: `45_000 ms`
- Niveis 4-5: `55_000 ms`
- Niveis 6-8: `60_000 ms`
- Niveis 9-10: `75_000 ms`
- Nivel 11: `90_000 ms`
- Nivel 12: `105_000 ms`

### Validacao de tempo da tentativa

- O cliente envia `time_taken_ms`.
- Esse valor precisa ser maior que `0` e menor que `10 minutos`.
- Se `time_taken_ms` ultrapassar o limite da questao, a tentativa e rejeitada.
- O servidor tambem mede o tempo desde a emissao da questao e aceita apenas uma folga tecnica de `5_000 ms`.

### Formula de pontuacao em practice

No encerramento da sessao `practice`, o backend calcula:

- `wrong_answers = total_questions - correct_answers`
- ganho por acerto: `6 + level`
- penalidade por erro: `4 + floor(level / 4)`
- bonus de velocidade: derivado do tempo medio, limitado entre `-12` e `+12`
- bonus adicional de consistencia: `+level` quando `acertos >= erros`

Depois disso:

- o delta final e limitado entre `-100` e `+100`
- a pontuacao nunca fica abaixo de `0`
- se a perda atravessar o piso do tier por margem pequena, o usuario fica travado no minimo do tier atual

### Tentativas e score individual

- Cada tentativa salva `score`, `is_correct`, tempo e a expressao respondida.
- Quando a resposta esta correta, ha uma reducao de retorno nos niveis mais baixos:
  - niveis `1-3`: cerca de `65%` do score calculado
  - niveis `4-5`: cerca de `85%`
  - niveis `6+`: sem reducao

### Daily challenge

- O desafio diario e deterministicamente derivado da data UTC.
- O seed usado e o ordinal do dia.
- O nivel do desafio e `(dia % 12) + 1`.
- Isso garante que todos os clientes recebam a mesma questao para o mesmo dia.

### Resolucao do ranked

- Se um jogador termina a propria sessao mas o adversario ainda nao terminou, o status fica `pending`.
- Se ambos terminaram, o backend resolve a partida uma unica vez.
- Se um jogador nao respondeu nenhuma questao e o outro respondeu ao menos uma, ele perde.
- A resolucao aplica:
  - delta tipo Elo
  - bonus ou penalidade de tempo entre `-4` e `+4`
- O resultado de uma mesma partida nao e recalculado duas vezes.

## Fluxo Recomendado para o Frontend

Fluxo de jogo comum:

1. autenticar em `POST /auth/login`
2. consultar `GET /auth/me` para obter usuario, pontos e tier
3. iniciar a sessao em `POST /sessions/start`
4. solicitar questao em `POST /game/question`
5. enviar resposta em `POST /attempts`
6. repetir os passos 4 e 5 conforme necessario
7. encerrar em `POST /sessions/{session_id}/finish`
8. atualizar UI com `points_before`, `points_after`, `tier_before`, `tier_after` e `result_summary`

Fluxo ranked:

1. entrar na fila com `POST /competitive/queue`
2. se retornar `waiting`, consultar `GET /competitive/queue/status`
3. quando retornar `matched`, usar o `session_id` recebido
4. executar o loop normal de questoes/tentativas
5. finalizar a sessao
6. se necessario, consultar `POST /competitive/resolve/{session_id}` ate o resultado deixar de estar `pending`

## Endpoints

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`

### Seasons e Tiers

- `POST /seasons` (admin)
- `GET /seasons/active`
- `GET /tiers`
- `GET /tiers/me`

### Game Loop

- `POST /sessions/start`
- `POST /game/question`
- `POST /attempts`
- `POST /sessions/{session_id}/finish`

### Historico de sessoes

- `GET /sessions/{session_id}`
- `GET /sessions?limit=20`

### Rankings e Stats

- `GET /leaderboard/global`
- `GET /leaderboard/season/active`
- `GET /leaderboard/season/{season_id}`
- `GET /stats/me`
- `GET /stats/me/advanced`
- `GET /stats/me/evolution?days=30`

### Competitive

- `POST /competitive/queue`
- `GET /competitive/queue/status`
- `POST /competitive/resolve/{session_id}`

### Infra

- `GET /healthz`
- `GET /metrics`

## Regras de jogo

- O daily challenge e deterministico.
- O tempo limite da questao e definido por nivel.
- A validacao de tentativa aplica tolerancia de tempo no servidor.
- O `finish` da sessao retorna `result_summary` no formato `acertosxerros` (ex.: `6x4`).

## Persistencia e Estado

- Dados de dominio como usuarios, seasons, tiers, sessoes e tentativas ficam no PostgreSQL.
- Migrations sao gerenciadas por Alembic.
- O estado volatil de rate limit e matchmaking pode usar:
  - `inmemory` para desenvolvimento simples
  - `redis` para multiplas instancias e estado compartilhado

Se a aplicacao rodar em mais de uma instancia, `STATE_BACKEND=redis` e o modo recomendado para manter rate limiting e fila ranked consistentes.

## Testes

```bash
pytest -q
```

## CI

O workflow em `.github/workflows/ci.yml` instala dependencias e executa os testes em push e pull request.
