# Differentiation Bee – Backend API

API do **Differentiation Bee**, uma aplicação gamificada para treino de derivadas.

O sistema gera funções, valida respostas simbólicas, gerencia autenticação de usuários, progressão por pontos e estrutura de temporadas.

---

## Visão geral

O backend é responsável por:

* Autenticação de usuários (JWT + refresh rotation)
* Geração de exercícios de derivadas
* Validação simbólica de respostas usando SymPy
* Sistema de progressão baseado em pontos e tiers
* Estrutura de temporadas (seasons)
* Persistência de usuários, tokens e dados do jogo
* Suporte a múltiplos idiomas (pt-BR, en, es)

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
    ├── game/
    │   ├── generator.py
    │   └── validator.py
    │
    ├── seasons/
    │   ├── router.py
    │   ├── service.py
    │   ├── schemas.py
    │   └── models.py
    │
    └── tiers/
        ├── router.py
        ├── service.py
        ├── schemas.py
        └── models.py
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

## Sistema de Pontos e Tiers

O sistema de progressão é baseado em **points**.

Após cada exercício:

* acertos aumentam pontos
* erros reduzem pontos
* o tier é recalculado automaticamente

Existe uma margem de proteção contra rebaixamento imediato (**demotion gap**), evitando quedas de tier por pequenas perdas.

Os tiers são fixos e possuem nomes traduzidos automaticamente conforme o idioma do usuário.

---

## Sistema de Temporadas (Seasons)

O backend suporta temporadas com:

* período de início e fim
* nomes traduzidos
* identificação automática da temporada ativa
* suporte a ranking por temporada (em evolução)

O idioma é determinado pelo header:

```
Accept-Language
```

Idiomas suportados atualmente:

* pt-BR
* en
* es

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

## Internacionalização (i18n)

O sistema suporta múltiplos idiomas através de tabelas de tradução no banco.

Atualmente suportados:

* pt-BR
* en
* es

Novos idiomas podem ser adicionados sem alteração estrutural no código.

---

## Próximos passos planejados

* GameSession
* Attempt
* Leaderboard global
* Ranking por temporada
* Daily challenge
* Estatísticas do usuário
* Balanceamento adaptativo de pontos

---

## Boas práticas adotadas

* Tokens seguros com hash
* Refresh rotation
* Parsing simbólico controlado
* Separação por domínio
* Services desacoplados de routers
* Estrutura preparada para internacionalização
* Progressão desacoplada da lógica de jogo

---

# 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).