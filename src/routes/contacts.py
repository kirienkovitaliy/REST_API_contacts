from datetime import date, timedelta
from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Role
from src.repository import contacts as repository_contacts
from src.schemas import ContactBase, ContactUpdate, ContactResponse
from src.services.auth import auth_service
from src.services.roles import RoleAccess

router = APIRouter(prefix='/contacts', tags=["contacts"])

allowed_operation_get = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_create = RoleAccess([Role.admin, Role.moderator, Role.user])
allowed_operation_update = RoleAccess([Role.admin, Role.moderator])
allowed_operation_remove = RoleAccess([Role.admin])


@router.get("/", response_model=List[ContactResponse],
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=3, seconds=5))],
            description='Everyone can')
async def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse,
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=3, seconds=5))],
            description='Everyone can')
async def read_contact(contact_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(allowed_operation_create), Depends(RateLimiter(times=3, seconds=3))],
             description='Everyone can')
async def create_contact(body: ContactBase, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    return await repository_contacts.create_contact(body, db)


@router.put("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_update)],
            description='Admin/moderator only')
async def update_contact(body: ContactUpdate, contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(allowed_operation_remove)],
               description='Admin only')
async def remove_contact(contact_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get("/contacts/search", response_model=List[ContactResponse],
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=3, seconds=5))],
            description='Everyone can')
async def search_contacts(query: str, db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):
    contacts = repository_contacts.search_contacts(query, db)
    response_contacts = []
    for contact in contacts:
        response_contact = ContactResponse(
            id=contact.id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            email=contact.email,
            phone_number=contact.phone_number,
            birthday=contact.birthday,
            created_at=contact.created_at
        )
        response_contacts.append(response_contact)
    return response_contacts


@router.get("/contacts/birthdays", response_model=List[ContactResponse],
            dependencies=[Depends(allowed_operation_get), Depends(RateLimiter(times=3, seconds=5))],
            description='Everyone can')
async def get_birthdays(start_date: date = date.today(), db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    end_date = date.today() + timedelta(days=7)
    contacts = repository_contacts.get_birthdays(db, start_date, end_date)
    return contacts
