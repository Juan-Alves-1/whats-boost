from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from app.config.settings import settings

router = APIRouter()

# OAuth setup
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@router.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth")
async def auth(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token.get('userinfo')

    if user and user["email"] in settings.ALLOWED_EMAILS:
        request.session['user'] = dict(user)
        return RedirectResponse(url="/choose") # Make it dynamically later 
    else:
        return RedirectResponse(url="/unauthorized")

@router.get("/unauthorized")
async def unauthorized():
    return HTMLResponse(content="""
        <html>
            <head>
                <title>Unauthorized</title>
            </head>
            <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                <h1>🚫 Access Denied</h1>
                <p>This Google account is not allowed to access this </p>
                <a href="/login">Try a different account</a>
            </body>
        </html>
    """, status_code=403)

@router.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url="/")

@router.get("/me")
async def read_me(request: Request):
    user = request.session.get('user')
    if user:
        return {"authenticated": True, "user": user}
    return {"authenticated": False, "message": "You are not logged in."}
