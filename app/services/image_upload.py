import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.config.settings import settings

# Initialize Cloudinary once
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

# Upload image bytes to Cloudinary and returns the secure URL.
async def upload_image(file_bytes: bytes, public_id: str = None) -> str:
    upload_options = {
        "asset_folder": "whats_boost_uploads",
        "transformation": [
            {
                "width": 1080,
                "height": 1080,
                "crop": "pad",
                "background": "white",
                "quality": "auto",
                "fetch_format": "auto"
            }
        ]
    }
    if public_id:
        upload_options["public_id"] = public_id

    result = cloudinary.uploader.upload(file_bytes, **upload_options)
    return result["secure_url"]