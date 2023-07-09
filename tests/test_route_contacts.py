from datetime import date, datetime
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from src.database.models import Contact, User
from src.services.auth import auth_service


CONTACT = {
    "id": 1,
    "first_name": "test_first_name",
    "last_name": "test_last_name",
    "email": "test@test.com",
    "phone_number": "+380663333333",
    "birthday": date.today().isoformat(),
    "created_at": datetime.now().isoformat()
}


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)

    current_user: User = session.query(User).filter(User.email == user.get("email")).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("/api/auth/login", data={"username": user.get("email"), "password": user.get("password")})
    data = response.json()
    return data["access_token"]


def test_create_contact(client, token):
    with patch.object(auth_service, "r") as redis_mock:
        redis_mock.get.return_value = None
        response = client.post("/api/contacts",
                               json=CONTACT,
                               headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 201, response.text
        data = response.json()
        assert "id" in data
