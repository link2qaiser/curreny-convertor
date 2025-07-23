import logging
import logging.config
from pathlib import Path

# Ensure log directory exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in [%(name)s] [%(filename)s]: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": str(LOG_DIR / "app.log"),
            "maxBytes": 5 * 1024 * 1024,  # 5MB
            "backupCount": 3,
            "level": "DEBUG",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "DEBUG"},
    "loggers": {
        # Optional: fine-tune module-specific loggers
        "uvicorn.error": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        # Ensure all app.* modules are captured
        "app": {"handlers": ["console", "file"], "level": "DEBUG", "propagate": False},
    },
}
