from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.dependencies.auth import auth_required
from app.services.image_upload_logo import upload_image_with_logo

router = APIRouter()

@router.post("/api/v1/images/upload-with-logo")
async def upload_image_endpoint(file: UploadFile = File(...), user=Depends(auth_required)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed.")

    file_bytes = await file.read()

    try:
        image_url = await upload_image_with_logo(file_bytes)
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
