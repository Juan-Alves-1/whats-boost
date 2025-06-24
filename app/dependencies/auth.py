from fastapi import Request, HTTPException
from app.config.settings import settings


# Authorization, not just authentication: Verifies that the user is logged in and authorized
def auth_required(request: Request):
    user = request.session.get("user")
    if not user or user.get("email") not in settings.ALLOWED_EMAILS:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource.")
    return user  # Optionally pass user to route if needed
