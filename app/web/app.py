from __future__ import annotations

import logging
import tempfile
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import Settings
from app.domain.report import FilterReport
from app.infrastructure.pdf_reader import PdfAssemblyReader, PdfTicketReader
from app.infrastructure.pdf_writer import PdfPageWriter
from app.services.filter_service import FilterService
from app.services.ports import FilterRunner

log = logging.getLogger("app.web")
WEB_DIR = Path(__file__).parent
OUTPUT_NAME = "filtered_ticket.pdf"


def create_app(settings: Settings | None = None, service: FilterRunner | None = None) -> FastAPI:
    app = FastAPI(title="Ozon PDF — фильтр этикеток")
    app.state.settings = settings or Settings.from_env()
    app.state.jobs: dict[str, Path] = {}
    app.state.service = service or FilterService(PdfAssemblyReader(), PdfTicketReader(), PdfPageWriter())
    app.state.templates = Jinja2Templates(directory=str(WEB_DIR / "templates"))
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")
    _register_routes(app)
    return app


def _render(app: FastAPI, request: Request, name: str, **context: object) -> Response:
    return app.state.templates.TemplateResponse(request, name, context)


def _no_match_message(report: FilterReport) -> str:
    if not report.has_assembly:
        return "В листе сборки не найдено ни одного номера отправления."
    return "Совпадений нет — этот ticket не входит в лист сборки."


async def _store(upload: UploadFile, folder: Path) -> Path:
    target = folder / Path(upload.filename or "file.pdf").name
    target.write_bytes(await upload.read())
    return target


def _register_routes(app: FastAPI) -> None:
    @app.get("/", response_class=Response)
    def index(request: Request) -> Response:
        return _render(app, request, "index.html")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/filter", response_class=Response)
    async def filter_upload(
        request: Request,
        assembly: Annotated[UploadFile, File()],
        ticket: Annotated[UploadFile, File()],
    ) -> Response:
        folder = Path(tempfile.mkdtemp(prefix="ticket-job-"))
        assembly_path = await _store(assembly, folder)
        ticket_path = await _store(ticket, folder)
        report = app.state.service.filter(assembly_path, ticket_path, folder / OUTPUT_NAME)
        if not report.has_matches:
            return _render(app, request, "partials/message.html", message=_no_match_message(report))
        job_id = uuid.uuid4().hex[:12]
        app.state.jobs[job_id] = report.output
        return _render(app, request, "partials/result.html", report=report, job_id=job_id)

    @app.get("/download/{job_id}")
    def download(job_id: str) -> FileResponse:
        path = app.state.jobs.get(job_id)
        if path is None or not path.exists():
            raise HTTPException(status_code=404, detail="Файл не найден или устарел")
        return FileResponse(path, media_type="application/pdf", filename=OUTPUT_NAME)


app = create_app()
