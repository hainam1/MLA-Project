"""FastAPI adapter for the local CapyVocab pipeline."""

from __future__ import annotations

import json
import logging
import time
import uuid
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from fastapi import Depends, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.concurrency import run_in_threadpool

from src.api.schemas import ErrorResponse, PipelineResponse, ProcessRequest
from src.artifacts.build_manifest import PROJECT_ROOT, SERVING_ARTIFACT_PATHS
from src.pipeline.run_pipeline import CapyVocabPipeline
from src.version import __version__

LOGGER = logging.getLogger(__name__)


class APIError(Exception):
    def __init__(self, status_code: int, code: str, message: str, details: Any = None):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


@lru_cache(maxsize=1)
def get_pipeline() -> CapyVocabPipeline:
    """Load model services once, lazily on the first inference request."""
    return CapyVocabPipeline(device="auto")


def readiness_snapshot(root: Path = PROJECT_ROOT) -> dict:
    missing = [relative for relative in SERVING_ARTIFACT_PATHS if not (root / relative).exists()]
    review_path = root / "data/review/model4_review_summary.json"
    review = (
        json.loads(review_path.read_text(encoding="utf-8"))
        if review_path.exists()
        else {"model4_training_ready": False, "reviewed": 0}
    )
    return {
        "status": "ready" if not missing else "not_ready",
        "version": __version__,
        "missing_artifacts": missing,
        "model4": {
            "implemented": False,
            "training_ready": bool(review.get("model4_training_ready", False)),
            "reviewed": int(review.get("reviewed", 0)),
        },
        "commercial_use_allowed": False,
    }


def _error_response(request: Request, error: APIError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", "unknown")
    payload = {
        "error": {
            "code": error.code,
            "message": error.message,
            "request_id": request_id,
            "details": error.details,
        }
    }
    return JSONResponse(status_code=error.status_code, content=jsonable_encoder(payload))


def create_app() -> FastAPI:
    application = FastAPI(
        title="CapyVocab ML API",
        version=__version__,
        description="Vietnamese vocabulary to user-selected CEFR English vocabulary. Non-commercial MVP.",
    )

    @application.middleware("http")
    async def request_context(request: Request, call_next):
        request.state.request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        started = time.perf_counter()
        response = await call_next(request)
        response.headers["x-request-id"] = request.state.request_id
        response.headers["x-process-time-ms"] = f"{(time.perf_counter() - started) * 1000:.2f}"
        return response

    @application.exception_handler(APIError)
    async def handle_api_error(request: Request, error: APIError):
        return _error_response(request, error)

    @application.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, error: RequestValidationError):
        return _error_response(
            request,
            APIError(422, "validation_error", "Request validation failed", error.errors()),
        )

    @application.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, error: Exception):
        LOGGER.exception("Unhandled API error request_id=%s", request.state.request_id)
        return _error_response(
            request,
            APIError(500, "internal_error", "An unexpected internal error occurred"),
        )

    @application.get("/", response_class=HTMLResponse, tags=["web"])
    async def web_ui():
        html_path = PROJECT_ROOT / "src/web/index.html"
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

    @application.get("/favicon.ico", include_in_schema=False)
    async def favicon():
        return HTMLResponse(status_code=204, content="")

    @application.get("/health/live", tags=["health"])
    async def live():
        return {"status": "ok", "version": __version__}

    @application.get("/health/ready", tags=["health"])
    async def ready():
        snapshot = readiness_snapshot()
        return JSONResponse(
            status_code=200 if snapshot["status"] == "ready" else 503,
            content=snapshot,
        )

    @application.get("/v1/status", tags=["status"])
    async def status():
        config = yaml.safe_load((PROJECT_ROOT / "configs/config.yaml").read_text(encoding="utf-8"))
        return {
            "version": __version__,
            "models": {
                "translator": "ranked_vi_en_vocabulary_candidates",
                "model2a": config["model2a"]["task"],
                "model2b": config["model2b"]["task"],
                "model3a": config["model3a"]["status"],
                "model3b": "retained_for_research_not_served",
                "model4": config["model4"]["status"],
            },
            "serving_contract": config["pipeline"]["input_contract"],
            "target_level_required": config["pipeline"]["target_level_required"],
            "commercial_use_allowed": config["project"]["commercial_use_allowed"],
        }

    @application.post(
        "/v1/process",
        response_model=PipelineResponse,
        responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
        tags=["inference"],
    )
    async def process(
        payload: ProcessRequest,
        pipeline: CapyVocabPipeline = Depends(get_pipeline),
    ):
        result = await run_in_threadpool(
            pipeline.process, payload.vietnamese_vocabulary, payload.target_level
        )
        if result.get("status") != "success":
            raise APIError(422, "pipeline_input_error", result.get("message", "Pipeline failed"))
        return result

    return application


app = create_app()
