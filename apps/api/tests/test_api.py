import json
import logging
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from control_plane.core.logging import JsonFormatter
from control_plane.core.settings import Settings
from control_plane.main import create_app


def test_live_is_independent_of_database(settings: Settings) -> None:
    with TestClient(create_app(settings)) as client:
        response = client.get("/health/live", headers={"X-Request-ID": "test-request"})
        assert response.json() == {"status": "ok"}
        assert response.headers["x-request-id"] == "test-request"


def test_readiness_hides_connection_errors(settings: Settings) -> None:
    with TestClient(create_app(settings)) as client:
        response = client.get("/health/ready")
        assert response.status_code == 503
        assert response.json()["error"]["code"] == "dependency.unavailable"
        assert "postgresql" not in response.text
        assert response.json()["error"]["request_id"] == response.headers["x-request-id"]


def test_readiness_success(settings: Settings) -> None:
    with patch("control_plane.core.dependencies.Resources.check_ready", new=AsyncMock()):
        with TestClient(create_app(settings)) as client:
            assert client.get("/health/ready").json() == {"status": "ok"}


def test_missing_route_and_invalid_correlation_id(settings: Settings) -> None:
    with TestClient(create_app(settings)) as client:
        response = client.get("/api/v1/servers", headers={"X-Request-ID": "!" * 100})
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "http.error"
        assert len(response.headers["x-request-id"]) == 36


def test_api_includes_foundation_and_auth_routes(settings: Settings) -> None:
    app = create_app(settings)
    assert set(app.openapi()["paths"]) == {
        "/health/live",
        "/health/ready",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
    }


def test_json_logging_omits_exception_details() -> None:
    record = logging.LogRecord("control_plane", logging.ERROR, "", 0, "dependency.failed", (), None)
    parsed = json.loads(JsonFormatter().format(record))
    assert parsed["event"] == "dependency.failed"
    assert set(parsed) == {"timestamp", "level", "event", "request_id"}
