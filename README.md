# E-Commerce

Django + DRF + Celery no backend, React + TypeScript + Vite no frontend,
Postgres/Redis/RabbitMQ/Nginx via Docker Compose em desenvolvimento, e Render
para um protótipo público.

## Estrutura do projeto

```
ecommerce/
├── backend/            Django + Celery (API, admin, e-mails, tasks)
│   ├── manage.py
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt / requirements-dev.txt
│   ├── pyproject.toml  (ruff, mypy, basedpyright, pytest)
│   ├── venv-ecommerce/ (venv local, não versionado)
│   ├── PROJECT/        settings, urls, celery app
│   ├── account/ address/ core/ product/   apps Django
│   ├── static/ staticfiles/ media/ mediafiles/ templates/ locale/
│   └── utils/
├── frontend/            React + Vite (projeto independente)
├── frontend.old/         referência histórica (Django templates) — não mexer
├── database/, redis/, rabbitmq/, cloudbeaver/   config de cada serviço (sem Dockerfile
│                          próprio — usam a imagem oficial direto; só o arquivo de config
│                          é montado no container)
├── nginx/                nginx.conf (proxy local para backend/frontend)
├── docker-compose.yml     orquestração do ambiente local
├── render.yaml            Blueprint do deploy de protótipo no Render
├── docs/render.md         guia de deploy no Render
├── .env / .env-example    variáveis de ambiente (ver seção abaixo)
└── dev_build.cmd          atalho local: down + up --build
```

## Desenvolvimento local

A partir da raiz do repositório:

```sh
docker compose up --build
```

Isso sobe Postgres, Redis, RabbitMQ, o worker do Celery, o Django (Gunicorn),
o Vite (modo dev) e o Nginx na frente de tudo. Acesse `http://localhost`.

Primeira vez: copie `.env-example` para `.env` e preencha os valores (nunca
coloque segredos reais em `.env-example`, só nomes de variável).

CloudBeaver (administração do Postgres) fica em `http://localhost:8978`.

### Rodar as verificações

Dentro do container (sempre disponível, não depende de venv local):

```sh
docker exec ecommerce_django python manage.py check
docker exec ecommerce_django python manage.py makemigrations --check --dry-run
docker exec ecommerce_django python -m pytest
```

No host, usando o venv em `backend/venv-ecommerce` (crie com
`python -m venv backend/venv-ecommerce` e
`backend/venv-ecommerce/Scripts/pip install -r backend/requirements-dev.txt`
se ainda não existir):

```sh
cd backend
./venv-ecommerce/Scripts/ruff check .
./venv-ecommerce/Scripts/ruff format --check .
./venv-ecommerce/Scripts/mypy --config-file=pyproject.toml .
npx basedpyright account address core product PROJECT utils
```

Frontend (dentro do container ou com Node local):

```sh
docker exec ecommerce_frontend npx tsc -b
docker exec ecommerce_frontend npm run lint
docker exec ecommerce_frontend npm run build
```

## Variáveis de ambiente

Ver `.env-example` — organizado por seção (geral, Django/backend, frontend,
banco, Redis, Celery/RabbitMQ, e-mail, superusuário). Dois pontos importantes:

- `SITE_URL` é o endereço público de todo o site (o que aparece nos links de
  e-mail); `FRONTEND_URL` é só o endereço interno do Vite, usado apenas para
  CORS. Não confundir os dois — já há comentários no `.env-example` e no
  código (`backend/utils/site_url.py`) explicando a diferença.
- `DATABASE_URL` nunca deve existir no `.env` local (nem comentada) — é
  exclusiva do Render, configurada direto no painel dele. Localmente o banco
  continua vindo das variáveis `POSTGRES_*`.

## Local × Render

| | Local (Docker Compose) | Render |
|---|---|---|
| Backend | `backend/Dockerfile`, Gunicorn | mesmo Dockerfile, Web Service Docker |
| Frontend | Vite dev server atrás do Nginx | Static Site (`npm run build`) |
| Banco | Postgres do Compose | Postgres gerenciado do Render |
| Cache | Redis do Compose | memória (sem Redis neste protótipo) |
| E-mail assíncrono | Celery + RabbitMQ | não roda (ver `docs/render.md`) |
| `DEBUG` | `True` | `True` (fase de protótipo) |

Detalhes completos, variáveis obrigatórias e limitações do plano gratuito:
[docs/render.md](docs/render.md).
