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
        <head>
            <title>AI Web Apps Lab</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin-top: 100px; background-color: #f4f7f6; color: #333; }
                .login-container { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: inline-block; }
                .google-btn {
                    display: inline-flex; align-items: center; background-color: #fff; color: #3c4043; border: 1px solid #dadce0; 
                    border-radius: 4px; padding: 0 16px; height: 40px; text-decoration: none; font-family: 'Google Sans', Roboto, Arial, sans-serif; 
                    font-size: 14px; font-weight: 500; cursor: pointer; transition: background-color .2s, box-shadow .2s;
                }
                .google-btn:hover { background-color: #f8f9fa; box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15); }
                .google-icon { width: 18px; height: 18px; margin-right: 12px; }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>Welcome to the AI Web Apps Lab</h1>
                <p style="margin-bottom: 30px; color: #666;">Please sign in to access your workspace.</p>
                <a href="/login" class="google-btn">
                    <svg class="google-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
                        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                        <path fill="none" d="M0 0h48v48H0z"/>
                    </svg>
                    Sign in with Google
                </a>
            </div>
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
