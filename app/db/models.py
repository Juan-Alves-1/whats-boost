from sqlalchemy import Column, Integer, String, DateTime, func, Table, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

group_by_user = Table(
    "group_by_user",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id"), Integer, ForeignKey("groups.id", primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, unique=True, nullable=False)
    ''' 
    evo_instance_id = 
    evo_api_key =
    cloudinary_api_key =
    cloudinary_secret_key = 
    logo_public_id = 
    '''
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, onupdate=func.now())

    groups = relationship("Group", secondary=group_by_user, back_populates="users")

class Group(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)
    whatsapp_group_id = Column(String, unique=True, nullable=False)

    users = relationship("User", secondary=group_by_user, back_populates="groups")

