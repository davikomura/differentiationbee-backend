# Differentiation Bee – Backend API

API do **Differentiation Bee**, uma aplicação gamificada para treino de derivadas.
O sistema gera funções, valida respostas simbólicas e gerencia autenticação de usuários com JWT e refresh tokens.

---

## Visão geral

O backend é responsável por:

* Autenticação de usuários (JWT + refresh rotation)
* Geração de exercícios de derivadas
* Validação simbólica de respostas usando SymPy
* Gerenciamento de sessões de jogo e pontuação (em evolução)
* Persistência de usuários e tokens

---

## Stack

* FastAPI
* PostgreSQL
* SQLAlchemy
* Pydantic
* SymPy
* Passlib (bcrypt)
* Python-JOSE (JWT)

---

## Estrutura do projeto

```
app/
├── main.py
│
├── api/
│   └── router.py
│
├── core/
│   └── security.py
│
├── db/
│   ├── base.py
│   └── session.py
│
└── modules/
    ├── auth/
    │   ├── router.py
    │   ├── service.py
    │   ├── schemas.py
    │   ├── models.py
    │   └── refresh_tokens.py
    │
    ├── users/
    │   └── models.py
    │
    └── game/
        ├── generator.py
        └── validator.py
```

---

## Arquitetura

O projeto segue separação por domínio:

* router → endpoints HTTP
* service → regra de negócio
* models → ORM
* schemas → validação e serialização

Fluxo típico:

```
Request → Router → Service → Database
```

---

## Configuração do ambiente

Crie um arquivo `.env`:

```
DATABASE_URL=postgresql+psycopg2://user:password@localhost/dbname
JWT_SECRET_KEY=supersecret
REFRESH_TOKEN_EXPIRE_DAYS=30
CORS_ALLOW_ORIGINS=http://localhost:5173
```

---

## Instalação

Criar ambiente virtual:

```
python -m venv venv
```

Ativar:

Linux/macOS:

```
source venv/bin/activate
```

Windows:

```
venv\Scripts\activate
```

Instalar dependências:

```
pip install -r requirements.txt
```

---

## Rodando o servidor

```
uvicorn app.main:app --reload
```

Documentação automática:

```
http://127.0.0.1:8000/docs
```

---

## Endpoints principais

### Auth

POST `/auth/register`
Cria um usuário.

POST `/auth/login`
Retorna:

```
access_token
refresh_token
```

POST `/auth/refresh`
Gera novo access token e novo refresh token.

POST `/auth/logout`
Revoga refresh token.

GET `/auth/me`
Retorna dados do usuário autenticado.

---

## Sistema de Tokens

Access token:

* curta duração
* usado em todas as requisições

Refresh token:

* longa duração
* armazenado no banco
* rotacionado a cada refresh

Fluxo:

1. Login → access + refresh
2. Access expira
3. App chama `/auth/refresh`
4. Backend retorna novo par

---

## Geração de exercícios

O módulo `game/generator.py` cria funções simbólicas por nível:

* Polinomiais
* Trigonométricas
* Exponenciais
* Composição e produto

Cada exercício retorna:

* expressão
* derivada correta
* LaTeX
* nível

---

## Validação de respostas

O módulo `validator.py`:

1. Converte resposta para expressão simbólica
2. Simplifica diferença
3. Verifica equivalência matemática

Pontuação depende de:

* nível
* tempo de resposta

---

## Próximos passos planejados

* GameSession
* Attempt
* Leaderboard
* Ranking por temporada
* Daily challenge
* Estatísticas do usuário

---

## Boas práticas adotadas

* Tokens seguros com hash
* Refresh rotation
* Parsing simbólico controlado
* Separação por domínio
* Services desacoplados de routers

---

# 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
