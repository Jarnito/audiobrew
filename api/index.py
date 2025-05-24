from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from mangum import Mangum
import os

# Import the routers
from .routers import gmail, podcast, user

app = FastAPI(title="AudioBrew API")

# Add CORS middleware to allow frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://audiobrew.vercel.app",  # Production domain
        "http://localhost:5173",         # Local development
        "http://localhost:3000",         # Alternative local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(gmail.router, prefix="/api")
app.include_router(podcast.router, prefix="/api")
app.include_router(user.router, prefix="/api")

# Add a special route to handle the auth/gmail/callback path
@app.get("/api/auth/gmail/callback")
async def auth_gmail_callback(code: str = None, state: str = None):
    """Redirect from /api/auth/gmail/callback to /api/gmail/callback"""
    if not code or not state:
        error_msg = "Missing required parameters (code or state)"
        return RedirectResponse(url=f"/dashboard/profile?gmail_error={error_msg}")
        
    return RedirectResponse(url=f"/api/gmail/callback?code={code}&state={state}")

@app.get("/")
@app.get("/api")
async def root():
    return {"message": "AudioBrew API is running"}

# Create the handler for Vercel
handler = Mangum(app, lifespan="off") 