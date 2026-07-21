"""系统级接口行为测试。"""


def test_health_response_has_request_id(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) == 32
    assert all(character in "0123456789abcdef" for character in request_id)
