from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_docs_and_openapi_are_available():
    assert client.get("/docs").status_code == 200
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    assert openapi.json()["paths"]


def test_required_localhost_origins_are_allowed():
    for origin in ("http://localhost:3000", "http://localhost:5173"):
        response = client.options(
            "/api/v1/status",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin


def test_unlisted_origin_is_rejected():
    response = client.options(
        "/api/v1/status",
        headers={
            "Origin": "https://unlisted.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_api_error_is_json_and_v1_prefixed():
    response = client.get("/api/v1/projects/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")
    assert isinstance(response.json()["detail"], str)