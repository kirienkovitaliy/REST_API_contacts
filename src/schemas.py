from datetime import datetime
from pydantic import BaseModel, Field


class ContactBase(BaseModel):
    first_name: str = Field(max_length=20)
    last_name: str = Field(max_length=20)
    email: str = Field(max_length=40)
    phone_number: str = Field(max_length=40)
    birthday: str = Field(max_length=20)
    created_at: datetime


class ContactUpdate(ContactBase):
    id: int


class ContactResponse(ContactBase):
    id: int

    class Config:
        orm_mode = True
