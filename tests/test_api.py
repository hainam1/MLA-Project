from pathlib import Path
from fastapi.testclient import TestClient

from src.api.app import (
    create_app,
    get_auditor,
    get_pipeline,
    get_rewriter,
    readiness_snapshot,
)


class FakeCEFR:
    def predict(self, text, route_override=None):
        return {
            "status": "success",
            "predicted_level": "B2",
            "confidence": 85.0,
            "probabilities": {"A1": 1.0, "A2": 4.0, "B1": 15.0, "B2": 70.0, "C1": 10.0},
        }


class FakePipeline:
    def __init__(self):
        self.cefr_engine = FakeCEFR()

    def process(self, vocabulary, target_level):
        if "." in vocabulary:
            return {"status": "error", "message": "Only vocabulary items are accepted"}
        return {
            "status": "success",
            "input_vi": vocabulary,
            "route": "word_mode",
            "requested_level": target_level,
            "baseline_translation_en": "good",
            "translation_en": "excellent",
            "selected_vocabulary": {
                "word": "excellent",
                "requested_level": target_level,
                "predicted_level": target_level,
                "target_match": True,
            },
            "cefr": {"status": "success", "predicted_level": target_level},
            "generated_example": {
                "status": "success",
                "sentence": "The result was excellent.",
                "target_level": target_level,
                "level_match": True,
            },
            "capabilities": {"translation": True},
        }


class FakeRewriter:
    def rewrite(self, sentence: str, source_level: str, target_level: str):
        return {
            "rewritten_sentence": "The committee conducted an investigation into the allegations.",
            "direction": "simplify",
            "source_level": source_level,
            "target_level": target_level,
        }


class FakeAuditor:
    def audit(
        self,
        model_name: str,
        source_text: str,
        model_output: str,
        expected_level: str = "",
        predicted_level: str = "",
        **kwargs,
    ):
        return {
            "audit_verdict": "acceptable",
            "failure_probability": 0.15,
            "auditor_status": "PILOT_PRELIMINARY_FILTER",
        }


def client():
    application = create_app()
    application.dependency_overrides[get_pipeline] = lambda: FakePipeline()
    application.dependency_overrides[get_rewriter] = lambda: FakeRewriter()
    application.dependency_overrides[get_auditor] = lambda: FakeAuditor()
    return TestClient(application, raise_server_exceptions=False)


def test_web_ui_returns_html():
    response = client().get("/")
    assert response.status_code == 200
    assert "CapyVocab ML" in response.text
    assert "text/html" in response.headers["content-type"]


def test_liveness_does_not_load_models():
    response = client().get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.headers["x-request-id"]


def test_process_success_contract():
    response = client().post(
        "/v1/process",
        json={"vietnamese_vocabulary": "tốt", "target_level": "B2"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["translation_en"] == "excellent"
    assert body["requested_level"] == "B2"
    assert body["selected_vocabulary"]["target_match"] is True


def test_target_level_is_required():
    response = client().post("/v1/process", json={"vietnamese_vocabulary": "tốt"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_old_request_contract_is_rejected():
    response = client().post(
        "/v1/process",
        json={"vietnamese_text": "tốt", "rewrite_target_level": "B2"},
    )
    assert response.status_code == 422


def test_sentence_input_is_rejected():
    response = client().post(
        "/v1/process",
        json={"vietnamese_vocabulary": "Tôi đang học.", "target_level": "A1"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "pipeline_input_error"


def test_validation_error_is_structured():
    response = client().post(
        "/v1/process",
        json={"vietnamese_vocabulary": "   ", "target_level": "A1"},
    )
    assert response.status_code == 422
    body = response.json()["error"]
    assert body["code"] == "validation_error"
    assert body["request_id"]


def test_readiness_reports_missing_artifacts(tmp_path):
    snapshot = readiness_snapshot(tmp_path)
    assert snapshot["status"] == "not_ready"
    assert snapshot["missing_artifacts"]


# =========================================================================
# NEW TESTS: Tab 2 (Sentence Rewriting) & Tab 3 (Human Feedback / Auditor)
# =========================================================================

def test_rewrite_success_contract():
    response = client().post(
        "/v1/rewrite",
        json={
            "sentence": "The committee conducted an extensive investigation into the allegations.",
            "target_level": "A1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["target_level"] == "A1"
    assert "rewritten_sentence" in body
    assert body["direction"] == "simplify"
    assert "cefr_verification" in body
    assert "auditor_verification" in body


def test_rewrite_validation_error():
    # Blank sentence rejected
    res1 = client().post("/v1/rewrite", json={"sentence": "   ", "target_level": "A1"})
    assert res1.status_code == 422

    # Unsupported upgrade direction rejected (A1 -> C1)
    res2 = client().post(
        "/v1/rewrite",
        json={
            "sentence": "This is good.",
            "current_level": "A1",
            "target_level": "C1",
        },
    )
    assert res2.status_code == 422
    assert res2.json()["error"]["code"] == "unsupported_direction"


def test_feedback_persists_to_disk():
    feedback_payload = {
        "task_type": "sentence_rewrite",
        "input_text": "Sample sentence input for testing feedback.",
        "model_output": "Sample model output for testing feedback.",
        "target_level": "B1",
        "verdict": "acceptable",
        "category": "none",
        "notes": "Automated integration test feedback entry.",
        "reviewer": "test_runner",
    }
    response = client().post("/v1/feedback", json=feedback_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert "feedback_id" in body
    assert "saved_to" in body

    # Verify stats endpoint returns non-zero count
    stats_res = client().get("/v1/feedback/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total"] >= 1
