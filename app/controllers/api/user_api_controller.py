from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session

from app.db import crud
from app.dependencies.db import get_db

router = APIRouter(prefix="/api/v1/users")

@router.get("/{user_id}")
def retrieve_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(404, f"No user found under ID number: {user_id}")
    return existing_user

@router.patch("/{user_id}")
def update_user_endpoint(user_id: int, fields: dict = Body(...), db: Session = Depends(get_db)):
    existing_user = crud.get_user_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(404, f"No user found under ID number: {user_id}")
    
    try: 
        updated_user = crud.update_user(db, existing_user, **fields)
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during update.",
        )
    
    return updated_user

@router.post("/")
def create_user_endpoint(email: str, full_name: str, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, email):
        raise HTTPException(400, "Email already registered")
    user = crud.create_user(db, email = email, full_name = full_name)
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "created_at": user.created_at.isoformat(),
    }
