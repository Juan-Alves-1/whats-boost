from fastapi import Request, HTTPException, Depends
from app.dependencies.db import get_db
from sqlalchemy.orm import Session
from app.db.crud import get_user_by_email
# from app.config.settings import settings

def auth_required(request: Request, db: Session = Depends(get_db) ):
    user = request.session.get("user")

    if not user:
        raise HTTPException(status_code=403, detail="User not found in this session")
    
    db_user = get_user_by_email(db, user["email"])
    if not db_user:
        raise HTTPException(status_code=403, detail="This email is not authorized to access this resource")
    
    return user 