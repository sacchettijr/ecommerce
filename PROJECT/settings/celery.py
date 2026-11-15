import os

from utils.env import (
    env,
    env_int,
)

# =========================================================
#   CELERY
# =========================================================

#   Local (Docker Compose): broker = RabbitMQ, result backend = Redis, como sempre.
#   Render: não há RabbitMQ gerenciado, então o worker lá usa um Render Key Value
#   (compatível com Redis) como broker E result backend — REDIS_URL é a connection
#   string desse Key Value (fromService no render.yaml), ausente localmente.
#   Nada tenta discar para essas URLs na inicialização; só quando uma tarefa é de
#   fato despachada — e isso já é protegido por utils/dispatch_task.py.
REDIS_URL: str | None = os.getenv("REDIS_URL")


def _local_rabbitmq_broker_url() -> str:
    return (
        f"amqp://{env(name='RABBITMQ_DEFAULT_USER', default='guest')}:"
        f"{env(name='RABBITMQ_DEFAULT_PASS', default='guest')}@"
        f"{env(name='RABBITMQ_HOST', default='localhost')}:"
        f"{env_int(name='RABBITMQ_PORT', default=5672)}/"
        f"{env(name='RABBITMQ_DEFAULT_VHOST', default='/')}"
    )


def _local_redis_result_backend_url() -> str:
    return (
        f"redis://{env(name='REDIS_HOST', default='localhost')}:"
        f"{env_int(name='REDIS_PORT', default=6379)}/"
        f"{env_int(name='REDIS_CELERY_DB', default=0)}"
    )


CELERY_BROKER_URL: str = REDIS_URL or _local_rabbitmq_broker_url()
CELERY_RESULT_BACKEND: str = REDIS_URL or _local_redis_result_backend_url()

CELERY_ACCEPT_CONTENT: list[str] = [
    "json",
]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE: str = env(
    name="TIME_ZONE",
    default="America/Manaus",
)
