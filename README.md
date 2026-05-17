# OpenID Connect Lab: Google Authentication

## Purpose of the Lab
This project is an educational laboratory designed to demonstrate the practical integration of **OpenID Connect (OIDC)** using **Google as the Identity Provider (IdP)**. The primary goal is to understand the OAuth 2.0 authorization code flow combined with OIDC for secure user authentication in a modern web application.

The application simulates a realistic scenario: users must authenticate via their Google accounts before gaining access to a protected workspace, which in this context, is an AI Web Builder landing page.

## Tech Stack
The application is built using a modern Python web stack:

*   **FastAPI**: The core web framework. It provides a highly performant and easy-to-use API backend for handling our routes and HTTP requests.
*   **Authlib**: A powerful Python library used to handle the heavy lifting of the OAuth 1.0, OAuth 2.0, and OpenID Connect protocols. In this lab, it manages the redirection to Google, the token exchange, and parsing the user's ID token.
*   **Starlette SessionMiddleware**: Used alongside FastAPI to manage encrypted, cookie-based sessions, allowing the application to "remember" the authenticated user across page reloads.
*   **Jinja2**: A templating engine for Python, used to render the dynamic `landing.html` page (injecting the user's name, email, and profile picture).
*   **Uvicorn**: The ASGI web server used to run the FastAPI application.
*   **Python-dotenv**: Used to securely load environment variables (like the Google Client ID and Secret) from a `.env` file during local development.

## How to Run

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Ensure you have a `.env` file in the root directory containing your Google OAuth credentials:
   ```env
   CLIENT_ID=your-google-client-id
   SECRET=your-google-client-secret
   ```
   *Note: Ensure `http://localhost:8000/auth` is added to your Authorized Redirect URIs in the Google Cloud Console.*

3. **Start the Server:**
   ```bash
   uvicorn main:app --reload
   ```
   Navigate to `http://localhost:8000` in your browser.