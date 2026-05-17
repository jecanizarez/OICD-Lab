import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from authlib.integrations.starlette_client import OAuthError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Important: This secret key is for session signing. It should be strong in production.
# We generate a random one here for the lab, or could take from .env
SESSION_SECRET = os.getenv("SESSION_SECRET", os.urandom(24).hex())
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

templates = Jinja2Templates(directory="templates")

# Configure OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse(url="/landing")
    
    html_content = """
    <html>
        <head><title>AI Web Apps Lab</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
            <h1>Welcome to the AI Web Apps Lab</h1>
            <p>Please log in to continue.</p>
            <a href="/login" style="padding: 10px 20px; background-color: #4285F4; color: white; text-decoration: none; border-radius: 5px;">Login with Google</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/login")
async def login(request: Request):
    # The redirect URI should match what's in the Google Cloud Console
    redirect_uri = request.url_for('auth')
    # If developing locally and url_for gives http, but you need https, handle it here. 
    # For localhost, http is usually fine.
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>Error!</h1><p>{error.error}</p>')
    
    # User info is typically in the ID token for OIDC
    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    
    return RedirectResponse(url='/landing')

@app.get("/landing", response_class=HTMLResponse)
async def landing(request: Request):
    user = request.session.get('user')
    if not user:
        return RedirectResponse(url='/')
    
    return templates.TemplateResponse(
        request=request, name="landing.html", context={"user": user}
    )

@app.get("/logout")
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
