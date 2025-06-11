from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserUpdate, UserRead, UserSoftDelete
from app.db import crud
from app.dependencies.db import get_db
from app.db.models import User

router = APIRouter(prefix="/api/v1/users")

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserRead)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    try:
        user = crud.get_record(db, User, user_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    return user

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserRead)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(400, "Email already registered")
    
    data = payload.model_dump(exclude_unset=True)

    try:
        new_user = crud.insert_record(db, User, **data)
    except Exception as e:
        raise HTTPException(500, f"DB error: {e}")
    
    return new_user

@router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserRead)
def update_user_endpoint(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No updatable fields provided"
        )

    try: 
        updated_user = crud.update_record(db, User, user_id, **data)
    except ValueError as ve:
        msg = str(ve)
        if msg.startswith("No users"):
            # Instance not found
            raise HTTPException(
                status_code=status.HTTP_404_BAD_REQUEST, detail=msg
            )
    except SQLAlchemyError:
        # Something went wrong in commit/refresh
        raise HTTPException(
            status_code=500,
            detail="Unexpected database error. Please try again later"
        )
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserSoftDelete)
def delete_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    try:
        deleted_user = crud.soft_delete_record(db, User, user_id)
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error during soft delete",
        )
    return deleted_user