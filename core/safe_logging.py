"""Logging local opcional sem valores sensíveis."""

import logging
import os
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path


_SECRET_PATTERN = re.compile(
    r"(?i)(api[_-]?key|token|secret|password)\s*[=:]\s*[^\s,;]+"
)


def _redact(message: object) -> str:
    return _SECRET_PATTERN.sub(r"\1=[REDACTED]", str(message))


class _RedactingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _redact(record.getMessage())
        record.args = ()
        return True


def get_logger(name: str, log_dir: str | Path | None = None) -> logging.Logger:
    logger = logging.getLogger(f"atleta_ai.{name}")
    if logger.handlers or os.getenv("ATLETA_LOGGING", "").lower() not in {"1", "true", "yes"}:
        return logger
    directory = Path(log_dir or "logs")
    directory.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        directory / "atleta_ai.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.addFilter(_RedactingFilter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger
