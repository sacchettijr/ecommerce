# Deploy no Render (protótipo)

Este guia cobre como publicar uma versão pública de teste deste projeto no
[Render](https://render.com), usando o Blueprint em [`render.yaml`](../render.yaml).
O objetivo é um protótipo compartilhável, com custo zero, sem mexer no ambiente
Docker Compose local (que continua sendo o jeito normal de desenvolver).

## Arquitetura usada no Render

```
Navegador
    │
    ▼
ecommerce-frontend (Static Site)
    │  serve o build do React (npm run build, a partir de frontend/)
    │
    ├── /api/*, /admin/*, /static/*, /media/*  ──▶  ecommerce-django (Web Service, Docker)
    │                                                        │   build a partir de backend/Dockerfile
    │                                                        ├──▶ Postgres (gerenciado, ecommerce-db)
    │                                                        └──▶ Key Value (ecommerce-redis)
    │                                                                   ▲   broker + result backend
    │                                                                   │
    │                                               ecommerce-celery (Background Worker, mesma imagem)
    │
    └── qualquer outra rota ──▶ index.html (React Router decide no navegador)
```

Os `routes` do site estático (definidos em `render.yaml`) fazem o mesmo papel que o
Nginx faz localmente: tudo fica sob o mesmo domínio público, então os cookies de
sessão e o CSRF continuam funcionando exatamente como hoje, sem precisar mexer em
CORS "cross-site" nem no código do frontend.

**Importante sobre a estrutura de pastas:** o backend Django/Celery mora em
`backend/`; o `render.yaml` já aponta `dockerfilePath`/`dockerContext` para
`./backend`. O frontend continua em `frontend/`, como sempre — não muda nada
ali.

### O que fica só no Docker Compose local

| Serviço | Motivo |
|---|---|
| **RabbitMQ** | não existe um equivalente gerenciado no Render. O Celery no Render usa o Key Value (`ecommerce-redis`, compatível com Redis) como broker **e** result backend em vez de RabbitMQ — ver `PROJECT/settings/celery.py`. Localmente continua tudo como sempre (RabbitMQ + Redis). |
| **CloudBeaver** | ferramenta de administração do banco, só para uso local. Nenhum código da aplicação depende dele. Para acessar o Postgres do Render, use `render psql <db-id>` ou `render pgcli <db-id>` pelo Render CLI — não precisa de um serviço rodando só pra isso. |
| **Nginx** | no Render, os `routes` do Static Site fazem esse papel; adicionar um Nginx próprio seria uma camada a mais sem necessidade. |

**Celery e Redis agora existem no Render** (`ecommerce-celery`, um Background Worker
no plano `starter`, e `ecommerce-redis`, um Key Value no plano `free`) — não são mais
exclusivos do Docker Compose local. Isso tem um custo real: o Background Worker não
tem tier gratuito (o Key Value tem). Veja "Limitações do plano gratuito" abaixo.

### E-mails de verdade

Com o Celery worker + Key Value no Render, as 3 tarefas abaixo voltam a ser
processadas de verdade (não é mais "responde com sucesso mas não envia" — ver
`utils/dispatch_task.py` para o que acontece se o broker estiver fora do ar):

- confirmação de cadastro (signup) e reenvio de confirmação;
- recuperação de senha;
- formulário de contato.

Preencha `EMAIL_HOST`/`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`/`DEFAULT_FROM_EMAIL`
com credenciais reais (ver passo 3 abaixo) para os e-mails saírem de fato.

### `DEBUG` nesta fase

Enquanto o projeto está em prototipação, `DEBUG=True` **tanto local quanto no
Render** (ver `render.yaml`). Isso significa que o Django Debug Toolbar e
páginas de erro detalhadas ficam visíveis também no Render por enquanto — é
intencional. As proteções de produção (redirect HTTPS, cookies seguros) em
`backend/PROJECT/settings/security.py` só entram em vigor quando `DEBUG=False`;
quando o projeto for para produção de verdade, troque essa variável no painel
do Render.

## Passo a passo no painel do Render

1. **Conectar o repositório**: no Render, "New" → "Blueprint", escolha este
   repositório no GitHub. O Render lê `render.yaml` automaticamente e propõe o
   banco (`ecommerce-db`), o Key Value (`ecommerce-redis`) e 3 serviços
   (`ecommerce-django`, `ecommerce-celery`, `ecommerce-frontend`).
2. **Primeiro deploy**: aceite a criação. `DATABASE_URL` (django + celery) e
   `REDIS_URL` (django + celery) já são preenchidos sozinhos pelo Blueprint.
   `SECRET_KEY` é gerado automaticamente só no `ecommerce-django`.
3. **Configurar as variáveis marcadas como manuais** (aparecem em branco no
   painel, uma por serviço, em Environment):
   - **No `ecommerce-celery`**: copie o `SECRET_KEY` real do `ecommerce-django`
     (Environment → clique no valor → copiar) para o `SECRET_KEY` do
     `ecommerce-celery` — **os dois precisam ter o mesmo valor**, por isso o
     `render.yaml` não usa `generateValue` nos dois (geraria valores
     diferentes).
   - **No `ecommerce-django`**: depois que o `ecommerce-frontend` tiver uma URL
     pública (ex.: `https://ecommerce-frontend-xxxx.onrender.com`), volte aqui e
     defina `FRONTEND_URL` com essa URL — é o endereço que vai para os links dos
     e-mails. Copie o mesmo valor para `FRONTEND_URL` no `ecommerce-celery`.
   - Se quiser que os e-mails realmente saiam, preencha `EMAIL_HOST`,
     `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` **nos dois**
     serviços (`ecommerce-django` e `ecommerce-celery`) com as mesmas
     credenciais reais (as mesmas que você usa no `.env` local).
4. **Ajustar o destino das rotas do frontend, se necessário**: `render.yaml`
   assume que o serviço Django vai se chamar `ecommerce-django` (URL
   `https://ecommerce-django.onrender.com`). Se o Render gerar um nome/URL
   diferente, edite os 4 `destination` em `routes:` do `ecommerce-frontend`
   dentro de `render.yaml` (ou direto no painel, em Redirects/Rewrites) e
   redeploy.
5. **Migrations**: já rodam sozinhas — o `backend/entrypoint.sh` (o mesmo
   usado localmente) executa `collectstatic` e `migrate` a cada deploy do
   `ecommerce-django`, antes do gunicorn subir.
6. **Criar um superusuário**: não é automático (de propósito — evita um admin
   padrão previsível em todo clone deste protótipo). No painel do
   `ecommerce-django`, abra o "Shell" e rode:
   ```
   python manage.py createsuperuser
   ```
7. **Ver logs**: aba "Logs" de cada serviço no painel do Render, em tempo real.
8. **Atualizar o deploy**: um `git push` para o branch configurado já dispara
   um novo deploy automático (é o comportamento padrão do Render Blueprint).
   Para forçar sem novo commit, use "Manual Deploy" no painel.

## Variáveis obrigatórias x opcionais no Render

Confirme no serviço `ecommerce-django`, em Environment:

- **Obrigatórias de verdade** (sem elas o Django não sobe): `DEBUG`,
  `SECRET_KEY`, `DATABASE_URL`, `EMAIL_HOST`, `EMAIL_HOST_USER`,
  `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`. As 4 de e-mail não tentam
  conectar em lugar nenhum na inicialização — só precisam *existir* com algum
  valor; use as credenciais reais se quiser e-mails funcionando no futuro
  (com Celery), ou um valor qualquer por enquanto.
- **Tem um valor padrão, mas precisa estar correto para o site funcionar
  direito**: `FRONTEND_URL` — o Django sobe mesmo sem definir, só que os
  links de e-mail saem errados. Configure com a URL real do
  `ecommerce-frontend` assim que ela existir (ver passo 3 acima).
- **Com valor padrão seguro quando ausentes** (não precisam ser configuradas
  no Render): `POSTGRES_*`, `REDIS_HOST`/`REDIS_PORT`/`REDIS_CELERY_DB`,
  `RABBITMQ_*`, `ALLOWED_HOSTS`, `INTERNAL_IP` — o código detecta o ambiente
  (`DATABASE_URL` presente → usa o Postgres do Render; `REDIS_URL` presente →
  Celery usa o Key Value do Render como broker/result backend em vez de
  RabbitMQ/Redis locais; variável `RENDER` presente, injetada automaticamente
  pelo próprio Render → cache do Django em memória em vez de Redis;
  `RENDER_EXTERNAL_HOSTNAME`, também automática → some ao `ALLOWED_HOSTS`
  sozinha).
- **`CSRF_TRUSTED_ORIGINS` precisa incluir o domínio do `ecommerce-frontend`**
  (ex.: `https://ecommerce-frontend-xxxx.onrender.com`) — o código só adiciona
  automaticamente o domínio do próprio `ecommerce-django`
  (`RENDER_EXTERNAL_HOSTNAME`), não o do frontend. Sem isso, login/cadastro
  (e qualquer POST) falham com 403 "CSRF verification failed", porque o
  navegador envia esse domínio no header `Origin` e ele precisa estar na
  lista de origens confiáveis.

## Limitações do plano gratuito (leia antes do primeiro deploy)

- **Imagens de produto (mídia) não são permanentes.** O disco do Web Service
  Docker do Render é efêmero: a cada redeploy/restart/scale, o conteúdo de
  `mediafiles/` é perdido. Para este protótipo isso foi aceito de propósito
  (ver `backend/PROJECT/urls.py`, que serve `/media/` independente do
  `DEBUG`) em vez de adicionar um storage externo pago (S3/Cloudinary) sem
  sua autorização. Se isso virar um problema real, a solução é
  `django-storages` + um bucket S3-compatível — não implementado aqui de
  propósito.
- **O Web Service gratuito "dorme" após um tempo sem uso** e demora alguns
  segundos para responder na primeira requisição seguinte (comportamento
  padrão do plano free do Render, não é um bug deste projeto).
- **O Postgres gratuito tem um limite de conexões e de tamanho** (verifique o
  valor atual no painel do Render; pode mudar com o tempo) e o Render costuma
  expirar bancos gratuitos após um período de inatividade prolongado.
- **`ecommerce-celery` (Background Worker) não tem tier gratuito** — o menor
  plano pago (`starter`, <1 CPU / 512MB) é cobrado continuamente (não
  "dorme" como o Web Service free), atualmente na faixa de $7/mês. O
  `ecommerce-redis` (Key Value) usa o tier `free` (25MB), sem custo.

## Testar a configuração de produção localmente (antes de mexer no Render)

Não é necessário reproduzir o Render inteiro; isto usa o Postgres do Compose
local para simular o ambiente, sem tocar no `.env` real:

```sh
docker exec \
  -e RENDER=true \
  -e SECRET_KEY=alguma-chave-soh-para-teste \
  -e ALLOWED_HOSTS=localhost \
  -e FRONTEND_URL=http://localhost \
  ecommerce_django sh -c "
    python manage.py check
    python manage.py collectstatic --noinput
    python manage.py migrate
  "
```

Depois, reinicie o container `backend` para voltar o storage de arquivos
estáticos e o cache ao modo de desenvolvimento normal.

## Voltar a rodar localmente

Nada muda no fluxo de sempre, a partir da raiz do repositório:

```sh
docker compose up --build
```

Todas as variáveis novas usadas pelo Render (`DATABASE_URL`, `RENDER`,
`RENDER_EXTERNAL_HOSTNAME`, `CSRF_TRUSTED_ORIGINS`) são opcionais e, quando
ausentes (caso do `.env` local), o projeto usa exatamente o comportamento de
antes (Postgres via `POSTGRES_*`, Redis via `REDIS_*`, `ALLOWED_HOSTS` do
`.env`).
