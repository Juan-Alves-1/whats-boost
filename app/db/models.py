from sqlalchemy import Column, Integer, String, DateTime, func, Table, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class SoftDeleteMixin:
    deleted_at = Column(DateTime, nullable=True)

group_by_user = Table(
    "group_by_user",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id"), primary_key=True)
)

class User(Base, SoftDeleteMixin):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, unique=True, nullable=False)

    evo_instance_id = Column(String, nullable=True)
    evo_api_key = Column(String, nullable=True)
    cloudinary_api_key = Column(String, nullable=True)
    cloudinary_secret_key = Column(String, nullable=True)
    logo_public_id = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, onupdate=func.now())

    groups = relationship("Group", secondary=group_by_user, back_populates="users")

    def __init__(self, *, email: str, full_name: str):
        self.email = email
        self.full_name = full_name

class Group(Base, SoftDeleteMixin):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    label = Column(String, nullable=False)
    whatsapp_group_id = Column(String, unique=True, nullable=False)

    users = relationship("User", secondary=group_by_user, back_populates="groups")

    def __init__(self, *, label: str, whatsapp_group_id: str):
        self.label = label
        self.whatsapp_group_id = whatsapp_group_id