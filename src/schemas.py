from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):
    first_name: str = Field(min_length=3, max_length=20)
    last_name: str = Field(min_length=3, max_length=20)
    email: EmailStr
    phone_number: str = Field(min_length=10, max_length=40)
    birthday: date
    created_at: datetime


class ContactUpdate(ContactBase):
    id: int


class ContactResponse(ContactBase):
    id: int

    class Config:
        orm_mode = True
