import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def get_audit_logger() -> logging.Logger:
    logger = logging.getLogger("audit")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(log_dir / "audit.log", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

audit_logger = get_audit_logger()

