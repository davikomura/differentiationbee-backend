# 🐝 Differentiation Bee

**Differentiation Bee** é um jogo educacional competitivo de derivadas matemáticas, no estilo quiz, com progressão por habilidade baseada em **Elo**, **arenas** e **temporadas**, combinando cálculo simbólico, autenticação segura e ranking competitivo.

O objetivo é transformar o treino de derivadas em uma experiência semelhante a jogos competitivos, com progressão real de habilidade.

---

# 🚀 Funcionalidades

### Jogabilidade

* 🧠 Geração aleatória de funções simbólicas com diferentes níveis de dificuldade
* 🎯 Progressão automática de dificuldade baseada no Elo do jogador
* 🏟️ Sistema de arenas que determina o nível das questões
* 🔁 Sistema anti-repetição de questões para evitar “decoreba”
* 📊 Histórico completo de respostas salvo no banco

---

### Competitivo

* 🏆 Ranking principal baseado em Elo
* 📈 Elo global e Elo por temporada
* 📍 Endpoint para posição individual no ranking
* 🔄 Soft reset de Elo no início de cada temporada
* 🗓️ Sistema de temporadas independentes

---

### Segurança e backend

* 🔐 Autenticação JWT com access token e refresh token
* 🚦 Rate limit em endpoints críticos
* 🧮 Validação segura de derivadas com SymPy
* 🗂️ Tracking detalhado server-side (anti-cheat)

---

# 🔄 Fluxo de uso

## 1. Autenticação

* Usuário se registra:

```
POST /auth/register
```

* Usuário faz login:

```
POST /auth/login
```

Retorna:

* access_token
* refresh_token

---

## 2. Início de sessão

```
POST /ranking/start
```

Retorna:

* session_id

---

## 3. Rodadas de questões

Para cada questão:

1. Backend escolhe automaticamente o nível com base no Elo

```
GET /question/generate?session_id=ID
```

2. Usuário responde

3. Backend valida e atualiza Elo:

```
POST /session-question/track
```

O backend:

* valida a derivada
* calcula score
* atualiza Elo global
* atualiza Elo da temporada
* registra histórico

---

## 4. Final da sessão

```
POST /ranking/save
```

Atualiza:

* score
* tempo médio
* acertos

---

## 5. Ranking e progresso

Ranking por Elo:

```
GET /ranking/elo/top
```

Posição individual:

```
GET /ranking/elo/me
```

Ranking por sessões:

```
GET /ranking/top
```

---

# 🏟️ Arenas e Elo

O jogador progride por arenas conforme o rating:

Exemplo:

| Arena                  | Rating  |
| ---------------------- | ------- |
| Vale dos Polinômios    | 0–199   |
| Floresta das Tangentes | 200–399 |
| Planícies das Cadeias  | 400–649 |
| Torres do Produto      | 650–949 |

O nível das questões é escolhido automaticamente com base na arena.

---

# 🗓️ Temporadas

Cada temporada possui:

* ranking independente
* elo independente
* histórico preservado

No início de uma nova temporada:

Soft reset:

```
novo_rating = base + fator * (rating_antigo - base)
```

Isso mantém progressão sem zerar completamente.

Endpoints:

```
GET /seasons/current
POST /seasons/start
```

---

# 🔁 Anti-repetição de questões

O backend:

* guarda hash das expressões
* evita repetir funções já vistas recentemente
* gera novas variações automaticamente

Isso reduz memorização e incentiva compreensão.

---

# 🔐 Autenticação e segurança

Sistema inclui:

* JWT access token
* Refresh token
* Logout com revogação
* Rate limit em:

  * login
  * track
  * refresh

---

# 🧱 Tecnologias

Backend:

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL

Matemática:

* SymPy

Segurança:

* JWT (python-jose)
* Passlib (bcrypt)

---

# 🗃️ Estrutura de pastas

```
app/
├── api/
│   ├── endpoints/
│   │   ├── auth.py
│   │   ├── question.py
│   │   ├── ranking.py
│   │   ├── seasons.py
│   │   ├── session_question.py
│   │   └── validate.py
│   └── router.py
├── core/
│   ├── security.py
│   └── ratelimit.py
├── db/
│   └── session.py
├── models/
│   ├── user.py
│   ├── user_stats.py
│   ├── user_season_stats.py
│   ├── season.py
│   ├── session.py
│   ├── session_question.py
│   └── question_instance.py
├── schemas/
├── services/
│   ├── auth.py
│   ├── elo.py
│   ├── generator.py
│   ├── seasons.py
│   ├── season_reset.py
│   └── validator.py
├── scripts/
│   └── create_tables.py
├── main.py
```

---

# 🛠️ Como rodar localmente

## 1. Clonar o repositório

```
git clone https://github.com/seu-usuario/differentiation-bee.git
cd differentiation-bee
```

## 2. Criar ambiente virtual

```
python -m venv .venv
.venv\Scripts\activate
```

## 3. Instalar dependências

```
pip install -r requirements.txt
```

## 4. Configurar `.env`

```
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
```

Opcional:

```
SEASON_RESET_BASE=100
SEASON_RESET_FACTOR=0.76
RECENT_DEDUP_LIMIT=200
```

---

## 5. Criar tabelas

```
python -m app.scripts.create_tables
```

---

## 6. Iniciar servidor

```
uvicorn app.main:app --reload
```

Docs:

```
http://127.0.0.1:8000/docs
```

---

# 📘 Principais endpoints

Autenticação:

```
POST /auth/register
POST /auth/login
POST /auth/refresh
POST /auth/logout
GET /auth/me
```

Jogo:

```
POST /ranking/start
GET /question/generate
POST /session-question/track
POST /ranking/save
```

Ranking:

```
GET /ranking/elo/top
GET /ranking/elo/me
GET /ranking/top
```

Temporadas:

```
GET /seasons/current
POST /seasons/start
```

---

# 📈 Roadmap futuro

* Modo duelo entre jogadores
* Ranking por amigos
* Replay de questões
* Gráfico de evolução de Elo
* Sistema de conquistas
* Matchmaking

---

# 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
