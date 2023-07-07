from datetime import date
from typing import List

from sqlalchemy import extract, or_
from sqlalchemy.orm import Session

from src.database.models import Contact
from src.schemas import ContactBase, ContactUpdate


async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    return db.query(Contact).offset(skip).limit(limit).all()  # noqa


async def get_contact(contact_id: int, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id).first()  # noqa


async def create_contact(body: ContactBase, db: Session) -> Contact:
    contact = Contact(first_name=body.first_name, last_name=body.last_name, email=body.email,
                      phone_number=body.phone_number, birthday=body.birthday)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def update_contact(contact_id: int, body: ContactUpdate, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.birthday = body.birthday
        db.commit()
    return contact


def search_contacts(query: str, db: Session):
    """
    The search_contacts function searches the database for contacts that match a given query.
    The function takes in a string and returns all contacts whose first name, last name, or email address contain the query.

    :param query: str: Search for a contact in the database
    :param db: Session: Pass a database session to the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(
        or_(
            Contact.first_name.ilike(f"%{query}%"),
            Contact.last_name.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%")
        )
    ).all()
    return contacts


def get_birthdays(db: Session, start_date: date, end_date: date) -> List[Contact]:
    """
    The get_birthdays function returns a list of contacts whose birthdays fall within the given date range.
    The start_date and end_date parameters are both datetime objects, which represent the beginning and ending dates of
    the desired date range. The function uses SQLAlchemy's extract method to compare only the month and day components of
    the birthday field in each contact with those same components from the start_date parameter.

    :param db: Session: Pass in the database session
    :param start_date: date: Filter the contacts by their birthday month and day
    :param end_date: date: Specify the end date for the range of birthdays to be returned
    :return: A list of contacts whose birthdays fall between the start_date and end_date
    :doc-author: Trelent
    """
    contacts = db.query(Contact).filter(
        extract('month', Contact.birthday) == extract('month', start_date),
        extract('day', Contact.birthday) >= extract('day', start_date),
        extract('day', Contact.birthday) <= extract('day', end_date)
    ).all()
    return contacts
