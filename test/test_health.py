from src.app.routers.health import health


def test_health():
    result = health()

    assert result["health"] == "ok"
