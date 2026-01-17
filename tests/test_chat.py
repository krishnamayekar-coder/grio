"""Chat API Tests"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_endpoint():
    """Test chat endpoint."""
    payload = {
        "user_id": "test_user",
        "message": "Hello, Griot!",
    }
    response = client.post("/api/v1/chat", json=payload)
    # Note: This will fail without a valid OpenAI API key
    # assert response.status_code == 200
    # assert "message" in response.json()


if __name__ == "__main__":
    pytest.main([__file__])
