from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import User, Group

''' User '''
def create_user(db: Session, *, email: str, full_name: str) -> User:
    user = User(email=email, full_name=full_name)
    db.add(user)
    try: 
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as ex:
        print("DB error happened:", ex)
        db.rollback()
        raise

def update_user(db: Session, user: User, **fields) -> User:
    mapper = inspect(User)
    allowed_columns = {col.key for col in mapper.columns if col.key not in {"id", "created_at"}} # Half-baked solution until to implement pydantic schemas

    for key, value in fields.items():
        if key not in allowed_columns:
            raise ValueError(f"Cannot update '{key}': not an updatable column.")
        setattr(user, key, value)
    try:
        db.commit()
        db.refresh(user)
        return user
    except SQLAlchemyError as ex:
        print("DB error happened:", ex)
        db.rollback()
        raise

def delete_user(db: Session, user: User) -> None:
    try:
        db.delete(user)
    except SQLAlchemyError as ex:
        print("DB error happened:", ex)
        db.rollback()
        raise

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)

''' Group '''
# create group

# get group lable by whatsapp group id

# update group
# update group label

# get all groups by user id
