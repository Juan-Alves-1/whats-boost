from datetime import datetime
from pydantic import BaseModel #, EmailStr

class UserCreate(BaseModel):
    email: str
    full_name: str

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    full_name: str | None = None
    evo_instance_id: str | None = None
    evo_api_key: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_secret_key: str | None = None
    logo_public_id: str | None = None

    class Config:
        extra = "ignore" # only send fields that were explicitly set
        orm_mode = True

class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    evo_instance_id: str | None
    evo_api_key: str     | None
    cloudinary_api_key: str | None
    cloudinary_secret_key: str | None
    logo_public_id: str  | None
    created_at: datetime
    last_login: datetime | None

    class Config:
        orm_mode = True

class UserSoftDelete(BaseModel):
    id: int
    deleted_at: datetime

    class Config:
        orm_mode = True