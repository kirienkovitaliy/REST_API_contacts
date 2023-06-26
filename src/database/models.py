import enum

from sqlalchemy import Column, Integer, String, Date, func, Enum
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Role(enum.Enum):
    admin: str = 'admin'
    moderator: str = 'moderator'
    user: str = 'user'


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    last_name = Column(String(20))
    email = Column(String(40), unique=True)
    phone_number = Column(String(40))
    birthday = Column(Date)
    created_at = Column('created_at', DateTime, default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    avatar = Column(String(255), nullable=True)
    roles = Column('roles', Enum(Role), default=Role.user)
