from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.schemas.group import GroupCreate, GroupUpdate, GroupRead, GroupSoftDelete
from app.db.models import Group
from app.db import crud

router = APIRouter(prefix="/api/v1/groups")

@router.post( "/", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(payload: GroupCreate, db: Session = Depends(get_db)):
    if crud.get_group_by_whatsapp_id(db, payload.whatsapp_group_id):
        raise HTTPException(400, "WhatsApp Group ID already registered")

    data = payload.model_dump(exclude_unset=True)

    try:
        group = crud.insert_record(db, Group, **data)
    except Exception as e:
        raise HTTPException(500, f"DB error: {e}")
    
    return group


@router.get("/{group_id}", response_model=GroupRead, status_code=status.HTTP_200_OK)
def get_group(group_id: int, db: Session = Depends(get_db)):
    try:
        group = crud.get_record(db, Group, group_id)
    except ValueError as e:
        raise HTTPException(404, detail=str(e))
    return group

@router.patch("/{group_id}", response_model=GroupRead, status_code=status.HTTP_200_OK)
def update_group(group_id: int, payload: GroupUpdate, db: Session = Depends(get_db)):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )

    try:
        updated_group = crud.update_record(db, Group, group_id, **updates)
    except ValueError as ve:
        msg = str(ve)
        if msg.startswith("In the table"):
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

    return updated_group

@router.delete("/{group_id}", status_code=status.HTTP_200_OK, response_model=GroupSoftDelete)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    try:
        deleted_user = crud.soft_delete_record(db, Group, group_id)
    except ValueError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Unexpected error during soft delete for a whatsapp group",
        )
    return deleted_user
