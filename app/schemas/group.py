from datetime import datetime
from pydantic import BaseModel

class GroupCreate(BaseModel):
    label: str
    whatsapp_group_id: str

class GroupUpdate(BaseModel):
    label: str | None = None
    whatsapp_group_id: str | None = None

    model_config = {
        "extra": "ignore",
    }

class GroupRead(BaseModel):
    id: int
    label: str
    whatsapp_group_id: str

    model_config = {
            "from_attributes": True,
        }

class GroupSoftDelete(BaseModel):
    id: int
    deleted_at: datetime

    model_config = {
        "from_attributes": True,
    }