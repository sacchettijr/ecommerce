from utils.env import (
    env,
    env_int,
)

# =========================================================
#   CELERY (broker: RabbitMQ / result backend: Redis)
# =========================================================

#   Sem RabbitMQ/Redis provisionados no Render neste primeiro deploy (ver docs/render.md),
#   estas URLs ficam com valores inertes por padrão: nada tenta discar para elas na
#   inicialização do Django, só quando uma tarefa é de fato despachada — e isso já é
#   protegido por utils/dispatch_task.py. Os defaults existem só para o Django conseguir
#   subir mesmo sem essas variáveis configuradas; localmente o .env sempre as define.
CELERY_BROKER_URL: str = (
    f"amqp://{env(name='RABBITMQ_DEFAULT_USER', default='guest')}:"
    f"{env(name='RABBITMQ_DEFAULT_PASS', default='guest')}@"
    f"{env(name='RABBITMQ_HOST', default='localhost')}:"
    f"{env_int(name='RABBITMQ_PORT', default=5672)}/"
    f"{env(name='RABBITMQ_DEFAULT_VHOST', default='/')}"
)

CELERY_RESULT_BACKEND: str = (
    f"redis://{env(name='REDIS_HOST', default='localhost')}:"
    f"{env_int(name='REDIS_PORT', default=6379)}/"
    f"{env_int(name='REDIS_CELERY_DB', default=0)}"
)

CELERY_ACCEPT_CONTENT: list[str] = [
    "json",
]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE: str = env(
    name="TIME_ZONE",
    default="America/Manaus",
)
