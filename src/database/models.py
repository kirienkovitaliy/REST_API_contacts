from sqlalchemy import Column, Integer, String, Date, func
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    last_name = Column(String(20))
    email = Column(String(40), unique=True)
    phone_number = Column(String(40))
    birthday = Column(Date)
    created_at = Column('created_at', DateTime, default=func.now())
