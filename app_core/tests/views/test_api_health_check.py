from django.test import Client


def test_health_check_returns_ok() -> None:
    response = Client().get("/api/core/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_check_rejects_non_get_methods() -> None:
    response = Client().post("/api/core/health/")

    assert response.status_code == 405


def test_health_check_requires_no_authentication() -> None:
    response = Client().get("/api/core/health/")

    assert response.status_code != 401
    assert response.status_code != 403
