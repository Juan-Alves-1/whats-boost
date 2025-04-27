from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.image_upload import upload_image

router = APIRouter()


@router.post("/api/v1/images/upload")
async def upload_image_endpoint(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image uploads are allowed.")

    file_bytes = await file.read()

    try:
        image_url = await upload_image(file_bytes)
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))