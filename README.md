# 🐝 Differentiation Bee

**Differentiation Bee** é um jogo educacional competitivo de derivadas matemáticas, no estilo quiz, com pontuação baseada em acertos e tempo. Ele combina técnicas de **cálculo simbólico**, **autenticação segura** e **ranking global**, promovendo o aprendizado de forma divertida e progressiva (níveis 1 a 10).

---

## 🚀 Funcionalidades

- 🧠 Geração aleatória de funções simbólicas com diferentes níveis de dificuldade
- ✍️ Validação automática de derivadas com `SymPy`
- 🔐 Sistema de autenticação com JWT (registro e login via JSON)
- 📊 Ranking global e histórico pessoal
- ⏱️ Pontuação baseada em acertos e tempo de resposta
- 🗂️ Tracking detalhado de cada questão respondida

---

## 🔄 Fluxo de uso

### 1. Autenticação
- O usuário se registra (`POST /auth/register`) e faz login (`POST /auth/login`)
- Recebe um token JWT para usar nos endpoints protegidos

### 2. Início de uma sessão de treino
- Frontend chama `POST /ranking/start` para criar uma nova `GameSession`
- Backend retorna o `session_id` que será usado para rastrear cada questão

### 3. Rodadas de questões
Para cada questão:
1. `GET /question/generate?level=N` → Gera uma função simbólica
2. Usuário responde a derivada no frontend
3. `POST /validate/answer` → Valida a resposta com SymPy
4. `POST /session/track` → Registra a questão, o tempo e o resultado na sessão

### 4. Final da sessão
- Frontend calcula:
  - Pontuação total
  - Número de acertos
  - Tempo médio por questão
- Envia esses dados via `POST /ranking/save` para atualizar a sessão

### 5. Visualização do ranking
- Global: `GET /ranking/top`
- Histórico do usuário logado: `GET /ranking/my`

---

## 🧱 Tecnologias

- **Backend:** Python + FastAPI
- **Banco de dados:** PostgreSQL (Neon)
- **ORM:** SQLAlchemy
- **Validação matemática:** SymPy
- **Segurança:** OAuth2 com JWT (`python-jose`)
- **Hashing de senhas:** Passlib (bcrypt)

---

## 🗃️ Estrutura de pastas

```

app/
├── api/
│   ├── endpoints/         # Rotas organizadas (auth, question, validate, ranking)
│   │   ├── auth.py
│   │   ├── question.py
│   │   ├── ranking.py
│   │   ├── session_question.py
│   │   └── validate.py
│   └── router.py
├── core/                  # Segurança e token JWT
│   └── security.py
├── db/                    # Sessão de banco e criação de tabelas
│   └── session.py
├── models/                # ORM: User, GameSession, SessionQuestion
│   ├── session_question.py
│   ├── session.py
│   └── user.py
├── schemas/               # Pydantic: validação de entrada e saída
│   ├── auth.py
│   └── session_question.py
├── services/              # Lógica de negócio (auth, validação, geração)
│   ├── auth.py
│   ├── generator.py
│   └── validator.py
├── main.py

````

---

## 🛠️ Como rodar localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/differentiation-bee.git
cd differentiation-bee
````

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente `.env`

```
DATABASE_URL=postgresql://<user>:<password>@<host>/<db>?sslmode=require
JWT_SECRET_KEY=uma_senha_secreta
```

### 4. Criar tabelas no banco

```bash
python create_db.py
```

### 5. Iniciar o servidor

```bash
uvicorn main:app --reload
```

---

## 📘 Exemplos de uso (API)

* `POST /auth/register` — Registro
* `POST /auth/login` — Login (application/json)
* `POST /ranking/start` — Cria uma nova sessão de jogo
* `GET /question/generate?level=3` — Gera função para derivar
* `POST /validate/answer` — Valida derivada do usuário
* `POST /session/track` — Registra a questão respondida (requer `session_id`)
* `POST /ranking/save` — Salva a pontuação final da sessão
* `GET /ranking/top` — Retorna os melhores jogadores
* `GET /ranking/my` — Retorna sessões do usuário logado

---

## 📈 Possibilidades futuras

* Sistema de conquistas
* Feedback pedagógico por tipo de erro
* Modo multiplayer em tempo real
* Painel de estatísticas por usuário
* Exportação de sessões para PDF

---

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
