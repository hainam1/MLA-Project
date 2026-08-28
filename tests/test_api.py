from fastapi.testclient import TestClient

from src.api.app import create_app, get_pipeline, readiness_snapshot


class FakePipeline:
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


def client():
    application = create_app()
    application.dependency_overrides[get_pipeline] = lambda: FakePipeline()
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
