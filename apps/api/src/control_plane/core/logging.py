import json
import logging
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # Application events are fixed messages; exception details, URLs and headers are omitted.
        return json.dumps(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "level": record.levelname,
                "event": record.getMessage(),
                "request_id": request_id_context.get(),
            }
        )


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("control_plane")
    logger.handlers = [handler]
    logger.setLevel(logging.INFO)
    logger.propagate = False
