from fastapi.testclient import TestClient

from EVA.server.app import app


def test_health_does_not_expose_api_key():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "ark_api_key" not in body["settings"]
    assert "ark_api_key_configured" in body["settings"]
