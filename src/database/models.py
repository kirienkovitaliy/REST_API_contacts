from sqlalchemy import Column, Integer, String, Date, func
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(20), nullable=False)
    email = Column(String(40), nullable=False, unique=True)
    phone_number = Column(String(40), nullable=False)
    birthday = Column(Date, nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
