import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email(self):
        email = "test@example.com"
        user = User()
        self.session.query().filter_by().first.return_value = user
        result = await get_user_by_email(email, db=self.session)
        self.assertEqual(result, user)

    async def test_create_user(self):
        body = UserModel(username="test_username", email="test@example.com", password="test_password")
        result = await create_user(body=body, db=self.session)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.password, body.password)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_token(self):
        refresh_token = "test_token"
        user = User()
        await update_token(user, refresh_token, db=self.session)
        self.assertEqual(user.refresh_token, refresh_token)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = "test@example.com"
        user = User()
        self.session.query().filter_by().first.return_value = user
        await confirmed_email(email, db=self.session)
        self.assertTrue(user.confirmed)
        self.session.commit.assert_called_once()

    async def test_update_avatar(self):
        email = "test@example.com"
        url = "http://example.com/avatar.jpg"
        user = User()
        self.session.query.return_value.filter_by.return_value.first.return_value = user
        result = await update_avatar(email, url, db=self.session)
        self.assertEqual(user.avatar, url)
        self.session.commit.assert_called_once()
        self.session.query.return_value.filter_by.assert_called_once_with(email=email)
        self.assertEqual(result, user)


if __name__ == "__main__":
    unittest.main()
