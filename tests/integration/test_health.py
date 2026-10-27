from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint_returns_ok():
    # Given
    client = TestClient(create_app())

    # When
    response = client.get("/health")

    # Then
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
