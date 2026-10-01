import logging
from collections.abc import Callable

logger = logging.getLogger(
    name=__name__,
)


def dispatch_task(
    action: Callable[[], object],
    *,
    description: str,
) -> None:

    try:
        action()
    except Exception:
        logger.warning(
            "Failed to dispatch task: %s",
            description,
            exc_info=True,
        )
