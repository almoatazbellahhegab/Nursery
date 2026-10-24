"""Remove query strings before Uvicorn access records reach log handlers."""

import logging


class PrivateAccessFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        values = record.args
        if isinstance(values, tuple) and len(values) >= 3 and isinstance(values[2], str):
            path = values[2]
            if "?" in path:
                record.args = (*values[:2], path.split("?", 1)[0] + "?[redacted]", *values[3:])
        return True


def install_private_access_logging() -> None:
    logger = logging.getLogger("uvicorn.access")
    if not any(isinstance(value, PrivateAccessFilter) for value in logger.filters):
        logger.addFilter(PrivateAccessFilter())
