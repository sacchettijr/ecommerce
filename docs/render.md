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
    │                                                        ▼
    │                                                  Postgres (gerenciado)
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
| **Redis** | usado como cache do Django e result backend do Celery; sem função sozinho no Render neste primeiro deploy. |
| **RabbitMQ** | broker do Celery; não existe um equivalente gratuito gerenciado pelo Render, e adicionar um pago não foi autorizado. |
| **Celery (worker)** | só processa os 3 e-mails abaixo; sem RabbitMQ, não há para onde rodar. |
| **CloudBeaver** | ferramenta de administração do banco, só para uso local. Nenhum código da aplicação depende dele. |
| **Nginx** | no Render, os `routes` do Static Site fazem esse papel; adicionar um Nginx próprio seria uma camada a mais sem necessidade. |

### O que isso quebra/limita no protótipo

Sem Celery/RabbitMQ, estes fluxos continuam respondendo com sucesso (não dão erro
500 — ver `backend/utils/dispatch_task.py`), mas **nenhum e-mail é enviado de verdade**:

- confirmação de cadastro (signup) e reenvio de confirmação;
- recuperação de senha;
- formulário de contato.

Ou seja: dá para testar o cadastro, mas o link de confirmação nunca chega; dá para
"pedir" a recuperação de senha, mas o e-mail não sai. Isso é esperado neste primeiro
deploy e está documentado aqui de propósito — não é um bug.

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
   repositório no GitHub. O Render lê `render.yaml` automaticamente e propõe os
   dois serviços (`ecommerce-django`, `ecommerce-frontend`) e o banco
   (`ecommerce-db`).
2. **Primeiro deploy**: aceite a criação. O Postgres e os dois serviços sobem.
   `DATABASE_URL` e `SECRET_KEY` já são preenchidos sozinhos pelo Blueprint.
3. **Configurar as variáveis marcadas como manuais** (aparecem em branco no
   painel, uma por serviço, em Environment):
   - No **ecommerce-django**: depois que o `ecommerce-frontend` tiver uma URL
     pública (ex.: `https://ecommerce-frontend.onrender.com`), volte aqui e
     defina `SITE_URL` com essa URL — é o endereço que vai para os links dos
     e-mails.
   - Se quiser que os e-mails realmente saiam, preencha `EMAIL_HOST`,
     `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` (mesmos
     valores que você usa no `.env` local) — mas lembre que sem Celery essas
     tarefas ainda não são processadas neste deploy (ver seção acima).
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
  `SECRET_KEY`, `SITE_URL`, `DATABASE_URL`, `EMAIL_HOST`, `EMAIL_HOST_USER`,
  `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`. As 4 de e-mail não tentam
  conectar em lugar nenhum na inicialização — só precisam *existir* com algum
  valor; use as credenciais reais se quiser e-mails funcionando no futuro
  (com Celery), ou um valor qualquer por enquanto.
- **Com valor padrão seguro quando ausentes** (não precisam ser configuradas
  no Render): `POSTGRES_*`, `REDIS_*`, `RABBITMQ_*`, `ALLOWED_HOSTS`,
  `INTERNAL_IP`, `FRONTEND_URL`, `CSRF_TRUSTED_ORIGINS` — o código detecta o
  ambiente (`DATABASE_URL` presente → usa o Postgres do Render; variável
  `RENDER` presente, injetada automaticamente pelo próprio Render → cache em
  memória em vez de Redis; `RENDER_EXTERNAL_HOSTNAME`, também automática →
  some ao `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` sozinha).

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
- **Sem e-mails de verdade** neste primeiro deploy, como explicado acima.

## Testar a configuração de produção localmente (antes de mexer no Render)

Não é necessário reproduzir o Render inteiro; isto usa o Postgres do Compose
local para simular o ambiente, sem tocar no `.env` real:

```sh
docker exec \
  -e RENDER=true \
  -e SECRET_KEY=alguma-chave-soh-para-teste \
  -e ALLOWED_HOSTS=localhost \
  -e SITE_URL=http://localhost \
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
