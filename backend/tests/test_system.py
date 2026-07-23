"""系统级接口行为测试。"""


def test_health_response_has_request_id(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 32
    assert all(character in "0123456789abcdef" for character in request_id)


def test_backend_does_not_serve_frontend_or_traverse_paths(client):
    root_response = client.get("/")
    traversal_response = client.get("/%2e%2e/backend/.env")

    assert root_response.status_code == 404
    assert traversal_response.status_code == 404
    assert root_response.json()["code"] == "NOT_FOUND"
    assert root_response.headers["X-Request-ID"]


def test_openapi_documents_unified_error_contract(client):
    schema = client.app.openapi()
    responses = schema["paths"]["/api/v1/users/register"]["post"]["responses"]

    assert responses["409"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ErrorResponse"
    }
    assert responses["422"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ValidationErrorResponse"
    }
    assert "X-Request-ID" in responses["422"]["headers"]
    assert "HTTPValidationError" not in schema["components"]["schemas"]


def test_local_vite_origin_passes_cors_preflight(client):
    origin = "http://127.0.0.1:5173"
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Client-Type",
        },
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == origin
    assert "x-client-type" in response.headers["Access-Control-Allow-Headers"].lower()
