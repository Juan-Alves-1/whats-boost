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

LOGO_PUBLIC_ID = "novos_produtos_ue1nf5"

# Upload image bytes to Cloudinary and add padding for great WhatsApp preview (square)
# Return a public and secure URL
async def upload_image_with_logo(file_bytes: bytes, public_id: str = None) -> str:
    upload_options = {
        "asset_folder": "whats_boost_uploads",
        "transformation": [
            # Pad to square
            {
                "width": 1080,
                "height": 1080,
                "crop": "pad",
                "background": "white"
            },
            # Overlay with log
            {
                "overlay": LOGO_PUBLIC_ID,
                "gravity": "south_east",
                "x": 20, # Pixels to the left (gravity as reference) 
                "y": 20, #  Pixels to the top (gravity as reference) 
                "crop": "scale",
                "width": int(658 * 0.15),  # logo at 15% of original logo image
                "opacity": 75
            }
        ],
        "quality": "auto",
        "fetch_format": "auto"
    }
    if public_id:
        upload_options["public_id"] = public_id

    result = cloudinary.uploader.upload(file_bytes, **upload_options)
    return result["secure_url"]
