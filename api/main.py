from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from pathlib import Path
from fastapi.responses import RedirectResponse

# Add the parent directory to the Python path
current_file = Path(__file__).resolve()
parent_directory = current_file.parent.parent
sys.path.append(str(parent_directory))

# Now import the routers
from api.routers import gmail, podcast, user

app = FastAPI(title="AudioBrew API")

# Add CORS middleware - Updated for Render production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://audiobrew.vercel.app",  # Your frontend on Vercel
        "http://localhost:5173",         # Local development
        "http://localhost:3000",         # Alternative local development
        "https://*.onrender.com",        # Allow any Render subdomain (for testing)
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
async def root():
    return {"message": "AudioBrew API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "audiobrew-api"}

# For local development and testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)