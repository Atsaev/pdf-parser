from __future__ import annotations

import logging
import os
from dataclasses import dataclass

LOG_FORMAT = "%(asctime)s  %(levelname)-7s  %(name)s  %(message)s"
LOG_DATE_FORMAT = "%H:%M:%S"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_ROOT_PATH = ""


@dataclass(frozen=True, slots=True)
class Settings:
    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    log_level: str = DEFAULT_LOG_LEVEL
    root_path: str = DEFAULT_ROOT_PATH

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            host=os.getenv("OZON_HOST", DEFAULT_HOST),
            port=int(os.getenv("OZON_PORT", str(DEFAULT_PORT))),
            log_level=os.getenv("OZON_LOG_LEVEL", DEFAULT_LOG_LEVEL),
            root_path=os.getenv("OZON_ROOT_PATH", DEFAULT_ROOT_PATH),
        )


def configure_logging(level: str = DEFAULT_LOG_LEVEL) -> None:
    logging.basicConfig(
        level=logging.getLevelNamesMapping().get(level.upper(), logging.INFO),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
    )
