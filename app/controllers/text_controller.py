from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List, Optional
from app.services.send_text import send_group_text_messages
from app.dependencies.auth import auth_required

router = APIRouter()

class BulkTextRequest(BaseModel):
    group_ids: List[str]
    message_text: str
    initial_delay: Optional[int] = 10000
    subsequent_delay: Optional[int] = 70000

@router.post("/text")
def send_bulk_text(payload: BulkTextRequest, user=Depends(auth_required)):
    try:
        results = send_group_text_messages(
            group_ids=payload.group_ids,
            message_text=payload.message_text,
            initial_delay=payload.initial_delay,
            subsequent_delay=payload.subsequent_delay
        )
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
