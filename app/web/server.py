from __future__ import annotations

import argparse

import uvicorn

from app.config import Settings, configure_logging
from app.web.app import app


def parse_args() -> argparse.Namespace:
    settings = Settings.from_env()
    parser = argparse.ArgumentParser(description="HTMX-интерфейс фильтра этикеток Ozon.")
    parser.add_argument("--host", default=settings.host)
    parser.add_argument("--port", type=int, default=settings.port)
    parser.add_argument("--root-path", default=settings.root_path, help="префикс, если сервис стоит за reverse-proxy")
    parser.add_argument("--reload", action="store_true", help="автоперезапуск при изменении кода")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_logging(Settings.from_env().log_level)
    target = "app.web.app:app" if args.reload else app
    uvicorn.run(target, host=args.host, port=args.port, root_path=args.root_path, reload=args.reload)


if __name__ == "__main__":
    main()
