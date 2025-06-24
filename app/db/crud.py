from typing import Type, TypeVar
from datetime import datetime
from sqlalchemy import inspect
from sqlalchemy.orm import Session, DeclarativeMeta
from sqlalchemy.exc import SQLAlchemyError
from .base import Base
from .models import User, Group

T = TypeVar("T", bound=Base)

def is_sqlalchemy_model(cls) -> bool:
    return isinstance(cls, DeclarativeMeta) and issubclass(cls, Base)

''' Generic CRUD operations '''
def get_record(db: Session, model_cls: Type[T], pk: int, *, include_deleted: bool = False) -> T:
    if not is_sqlalchemy_model(model_cls):
        raise ValueError(f"{model_cls!r} is not a recognized SQLAlchemy model.")
    
    q = db.query(model_cls)
    mapper = inspect(model_cls)
    pk_column = mapper.primary_key[0]
    q = q.filter(pk_column == pk)
    
    if hasattr(model_cls, "deleted_at") and not include_deleted:
        q = q.filter(model_cls.deleted_at.is_(None))

    instance = q.first()
    if not instance:
        raise ValueError(f"There is no row with ID: {pk} in the table: {model_cls.__tablename__} ")
    return instance

def get_all_records(db: Session, model_cls: Type[T], *, include_deleted: bool = False) -> list[T]:
    if not is_sqlalchemy_model(model_cls):
        raise ValueError(f"{model_cls!r} is not a recognized SQLAlchemy model.")
    
    q = db.query(model_cls)
    if hasattr(model_cls, "deleted_at") and not include_deleted:
        q = q.filter(model_cls.deleted_at.is_(None))
    return q.all()

def insert_record(db: Session, model_cls: Type[T], **fields) -> T:
    if not is_sqlalchemy_model(model_cls):
        raise ValueError(f"{model_cls!r} is not a recognized SQLAlchemy model.")
    
    record = model_cls(**fields)
    db.add(record)

    try: 
        db.commit()
        db.refresh(record)
        return record
    except SQLAlchemyError as ex:
        print("DB error happened:", ex)
        db.rollback()
        raise

def update_record(db: Session, model_cls: Type[T], pk: int, **fields) -> T:
    if not is_sqlalchemy_model(model_cls):
        raise ValueError(f"{model_cls!r} is not a recognized SQLAlchemy model.")
    
    instance = db.get(model_cls, pk)
    if instance is None:
        raise ValueError(f"In the table '{model_cls.__tablename__}', no row with ID: {pk} was found")
    
    # Which columns may we update?
    mapper = inspect(model_cls)
    forbidden = {c.key for c in mapper.columns if c.primary_key or c.server_default}
    allowed = {c.key for c in mapper.columns} - forbidden

    for key, val in fields.items():
        if key not in allowed:
            raise ValueError(f"Cannot update the column {key} in the table {model_cls.__tablename__}")
        setattr(instance, key, val)

    try:
        db.commit()
        db.refresh(instance)
        return instance
    except SQLAlchemyError as ex:
        print("DB error happened while trying to update a row:", ex)
        db.rollback()
        raise

def soft_delete_record(db: Session, model_cls: Type[T], pk: int) -> T:
    if not is_sqlalchemy_model(model_cls):
        raise ValueError(f"{model_cls!r} is not a recognized SQLAlchemy model.")
    
    instance = get_record(db, model_cls, pk, include_deleted=True)
    if not instance:
        raise ValueError(f"In the table {model_cls.__tablename__}, no row was found with ID: {pk}")
    instance.deleted_at = datetime.now()

    try:
        db.commit()
        db.refresh(instance)
        return instance
    except SQLAlchemyError as ex:
        print("DB error happened while trying to update a row:", ex)
        db.rollback()
        raise


''' Specific database operations for users ''' 
def get_user_by_email(db: Session, user_email: str) -> User | None:
    return db.query(User).filter(User.email == user_email).first()

''' Specific database operations for groups '''
def get_group_by_whatsapp_id(db: Session, whatsapp_group_id: str) -> Group | None:
    return db.query(Group).filter(Group.whatsapp_group_id == whatsapp_group_id).first()

''' Specific database operations for join table '''
def get_all_groups_by_user(db: Session, user_email: str) -> list[str]:
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        return []
    
    whatsapp_group_ids = []
    for group in user.groups:
        whatsapp_group_ids.append(group.whatsapp_group_id)
    
    return whatsapp_group_ids

def link_group_to_user(db: Session, *, user_email: str, whatsapp_group_id: str) -> bool:
    try:
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise ValueError(f"User with email '{user_email}' not found.")

        group = db.query(Group).filter(Group.whatsapp_group_id == whatsapp_group_id).first()
        if not group:
            raise ValueError(f"Group with ID '{whatsapp_group_id}' not found.")

        if group in user.groups:
            return False  # Already linked

        user.groups.append(group)
        db.commit()
        return True

    except SQLAlchemyError as e:
        db.rollback()
        raise RuntimeError(f"Database error while linking group to user: {str(e)}")

