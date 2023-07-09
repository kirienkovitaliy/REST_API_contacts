from datetime import date, datetime
import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactBase, ContactUpdate
from src.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
    search_contacts,
    get_birthdays
)


class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_contacts(self):
        skip = 0
        limit = 10
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=skip, limit=limit, db=self.session)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), limit)
        for i, contact in enumerate(result):
            self.assertEqual(contact, contacts[i])

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactBase(first_name="test_first_name", last_name="test_last_name", email="test@test.com",
                           phone_number="+380661111111", birthday=date.today(), created_at=datetime.now())
        result = await create_contact(body=body, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactUpdate(id=1, first_name="test_first_name", last_name="test_last_name", email="test@test.com",
                             phone_number="+380661111111", birthday=date.today(), created_at=datetime.now())
        phone_number = "+380662222222"
        contact = Contact(phone_number=phone_number)
        self.session.query().filter().first.return_value = contact
        self.session.query().filter().all.return_value = phone_number
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactUpdate(id=1, first_name="test_first_name", last_name="test_last_name", email="test@test.com",
                             phone_number="+380661111111", birthday=date.today(), created_at=datetime.now())
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1, body=body, db=self.session)
        self.assertIsNone(result)

    def test_search_contacts(self):
        query = "test_first_name"
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = search_contacts(query=query, db=self.session)
        self.assertIsInstance(result, list)

    def test_get_birthdays(self):
        start_date = date.today()
        end_date = date.today()
        result = get_birthdays(db=self.session, start_date=start_date, end_date=end_date)
        self.session.query().filter().all.return_value = MagicMock(return_value=result)


if __name__ == '__main__':
    unittest.main()
