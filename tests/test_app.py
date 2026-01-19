import pytest
from app.app import app


def test_app_creation():
    """Basic test to ensure Flask app is created correctly."""
    assert app is not None
    assert app.name == "app.app"


def test_index_route():
    """Test that the index route returns 200."""
    with app.test_client() as client:
        response = client.get("/")
        # We expect 200 OK since it's a GET request to home
        assert response.status_code == 200
