"""FastAPI adapter for the local CapyVocab pipeline."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
_torch_lib = Path(__file__).resolve().parents[2] / ".venv/Lib/site-packages/torch/lib"
if _torch_lib.exists() and hasattr(os, "add_dll_directory"):
    try:
        os.add_dll_directory(str(_torch_lib))
    except Exception:
        pass
try:
    import torch
except Exception:
    pass

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

import yaml
from fastapi import Depends, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.concurrency import run_in_threadpool

from src.api.schemas import (
    ErrorResponse,
    FeedbackRequest,
    FeedbackResponse,
    PipelineResponse,
    ProcessRequest,
    RewriteRequest,
    RewriteResponse,
)
from src.artifacts.build_manifest import PROJECT_ROOT, SERVING_ARTIFACT_PATHS
from src.models.second_pair_of_eyes.service import QualityAuditorService
from src.models.sentence_rewriter.service import SentenceRewriterService
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


@lru_cache(maxsize=1)
def get_rewriter() -> SentenceRewriterService:
    """Lazy load Model 3b sentence rewriter service."""
    return SentenceRewriterService(device="auto")


@lru_cache(maxsize=1)
def get_auditor() -> QualityAuditorService:
    """Lazy load Model 4 quality auditor service."""
    return QualityAuditorService()


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
            "implemented": True,
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
        description="Vietnamese vocabulary to user-selected CEFR English vocabulary and rewriting. Non-commercial MVP.",
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
                "model3b": config["model3b"]["status"],
                "model4": "trained_pilot_auditor",
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

    @application.post(
        "/v1/rewrite",
        response_model=RewriteResponse,
        responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
        tags=["inference"],
    )
    async def rewrite(
        payload: RewriteRequest,
        pipeline: CapyVocabPipeline = Depends(get_pipeline),
        rewriter: SentenceRewriterService = Depends(get_rewriter),
        auditor: QualityAuditorService = Depends(get_auditor),
    ):
        sentence = payload.sentence.strip()
        target_level = payload.target_level.upper()
        detected = pipeline.cefr_engine.predict(sentence, route_override="sentence_mode")
        current_level = (payload.current_level or detected.get("predicted_level", "B2")).upper()

        levels = ["A1", "A2", "B1", "B2", "C1"]
        if levels.index(target_level) > levels.index(current_level):
            raise APIError(
                422,
                "unsupported_direction",
                f"Model 3b chỉ hỗ trợ đơn giản hóa hoặc giữ nguyên cấp độ (Cấp gốc: {current_level}, Cấp đích: {target_level}). Không hỗ trợ nâng cấp (upgrade).",
            )

        try:
            rewrite_res = await run_in_threadpool(
                rewriter.rewrite, sentence, current_level, target_level
            )
            rewritten_text = rewrite_res.get("rewritten_sentence", "")

            # CEFR verification on rewritten sentence
            cefr_check = pipeline.cefr_engine.predict(rewritten_text, route_override="sentence_mode")

            # Model 4 audit check
            audit_res = auditor.audit(
                model_name="model3b",
                source_text=sentence,
                model_output=rewritten_text,
                expected_level=target_level,
                predicted_level=cefr_check.get("predicted_level", ""),
            )

            return {
                "status": "success",
                "original_sentence": sentence,
                "target_level": target_level,
                "detected_current_level": current_level,
                "rewritten_sentence": rewritten_text,
                "direction": rewrite_res.get("direction"),
                "cefr_verification": cefr_check,
                "auditor_verification": {
                    "audit_verdict": audit_res.get("audit_verdict"),
                    "failure_probability": audit_res.get("failure_probability"),
                    "auditor_status": audit_res.get("auditor_status"),
                },
                "model": "Model 3b (Sentence Rewriter T5-small)",
            }
        except Exception as exc:
            LOGGER.exception("Rewrite failed: %s", exc)
            raise APIError(500, "rewrite_error", f"Model 3b error: {exc}")

    @application.post(
        "/v1/feedback",
        response_model=FeedbackResponse,
        responses={422: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
        tags=["feedback"],
    )
    async def submit_feedback(payload: FeedbackRequest):
        feedback_id = str(uuid.uuid4())
        feedback_dir = PROJECT_ROOT / "data/review"
        feedback_dir.mkdir(parents=True, exist_ok=True)
        queue_file = feedback_dir / "user_feedback_queue.jsonl"

        record = {
            "feedback_id": feedback_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_type": payload.task_type,
            "input_text": payload.input_text,
            "model_output": payload.model_output,
            "target_level": payload.target_level,
            "verdict": payload.verdict,
            "category": payload.category or "unspecified",
            "notes": payload.notes or "",
            "reviewer": payload.reviewer,
        }

        with queue_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return {
            "status": "success",
            "feedback_id": feedback_id,
            "message": "Feedback ghi nhận thành công vào hàng đợi kiểm định Model 4",
            "saved_to": "data/review/user_feedback_queue.jsonl",
            "record": record,
        }

    @application.get("/v1/feedback/stats", tags=["feedback"])
    async def feedback_stats():
        queue_file = PROJECT_ROOT / "data/review/user_feedback_queue.jsonl"
        if not queue_file.exists():
            return {"total": 0, "acceptable": 0, "failure": 0, "recent": []}

        lines = queue_file.read_text(encoding="utf-8").strip().split("\n")
        records = [json.loads(line) for line in lines if line.strip()]
        acceptable_cnt = sum(1 for r in records if r.get("verdict") == "acceptable")
        failure_cnt = sum(1 for r in records if r.get("verdict") == "failure")
        return {
            "total": len(records),
            "acceptable": acceptable_cnt,
            "failure": failure_cnt,
            "recent": records[-10:][::-1],
        }

    return application


app = create_app()
