from fastapi import APIRouter, HTTPException, Depends, Request, Response, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import httpx
from dotenv import load_dotenv
from datetime import datetime
import uuid  # Add UUID import

load_dotenv()

router = APIRouter(prefix="/gmail", tags=["gmail"])

# Environment variables
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5173/api/auth/gmail/callback")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Scopes required for Gmail API
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

class TokenRequest(BaseModel):
    user_id: str

class ConnectionStatus(BaseModel):
    is_connected: bool
    email: Optional[str] = None

def create_flow():
    """Create OAuth flow instance to manage the OAuth 2.0 Authorization Grant Flow."""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [REDIRECT_URI],
            }
        },
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    return flow

async def save_credentials_to_supabase(user_id: str, credentials: Dict[str, Any]):
    """Save Gmail credentials to Supabase for a specific user."""
    print(f"Saving Gmail credentials for user {user_id}")
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_SERVICE_KEY length: {len(SUPABASE_SERVICE_KEY) if SUPABASE_SERVICE_KEY else 'None'}")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("Error: Missing Supabase environment variables")
        raise HTTPException(status_code=500, detail="Server configuration error: Missing Supabase credentials")
    
    # Clean up credentials for storage - remove unnecessary fields for debugging
    credentials_to_save = credentials.copy() 
    credentials_to_save_debug = {k: "..." if k in ["token", "refresh_token", "client_secret"] else v for k, v in credentials_to_save.items()}
    print(f"Credentials to save: {credentials_to_save_debug}")
    
    # Verify that user_id is a valid UUID for all operations
    try:
        # Try to convert user_id to UUID
        user_uuid = str(uuid.UUID(user_id))
        print(f"User ID is a valid UUID: {user_uuid}")
    except ValueError:
        print(f"User ID is not a valid UUID: {user_id}")
        raise HTTPException(status_code=400, detail="Invalid user ID format. Must be a valid UUID.")
    
    async with httpx.AsyncClient() as client:
        try:
            # First check if the record already exists
            check_response = await client.get(
                f"{SUPABASE_URL}/rest/v1/gmail_connections",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json"
                },
                params={"user_id": f"eq.{user_uuid}", "select": "id"}
            )
            
            print(f"Check response status: {check_response.status_code}")
            print(f"Check response content: {check_response.text}")
            
            record_exists = check_response.status_code == 200 and check_response.json()
            
            if record_exists:
                # Update existing record
                print(f"Record exists for user {user_id}, updating...")
                update_response = await client.patch(
                    f"{SUPABASE_URL}/rest/v1/gmail_connections",
                    headers={
                        "apikey": SUPABASE_SERVICE_KEY,
                        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "return=minimal"
                    },
                    params={"user_id": f"eq.{user_uuid}"},
                    json={
                        "credentials": credentials_to_save,
                        "email": credentials_to_save.get("email", ""),
                        "updated_at": "now()"
                    }
                )
                print(f"PATCH response status: {update_response.status_code}")
                print(f"PATCH response content: {update_response.text}")
                
                if update_response.status_code >= 400:
                    print(f"Failed to update: {update_response.status_code} {update_response.text}")
                    raise HTTPException(status_code=500, detail=f"Failed to update Gmail credentials: {update_response.text}")
            else:
                # Insert new record
                print(f"No record exists for user {user_id}, creating new...")
                
                # User UUID is already validated above
                insert_response = await client.post(
                    f"{SUPABASE_URL}/rest/v1/gmail_connections",
                    headers={
                        "apikey": SUPABASE_SERVICE_KEY,
                        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "return=minimal"
                    },
                    json={
                        "user_id": user_uuid,  # Use the validated UUID
                        "credentials": credentials_to_save,
                        "email": credentials_to_save.get("email", "")
                    }
                )
                print(f"POST response status: {insert_response.status_code}")
                print(f"POST response content: {insert_response.text}")
                
                if insert_response.status_code >= 400:
                    print(f"Failed to insert: {insert_response.status_code} {insert_response.text}")
                    raise HTTPException(status_code=500, detail=f"Failed to insert Gmail credentials: {insert_response.text}")
                
        except httpx.RequestError as e:
            print(f"Request error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Network error when saving credentials: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def get_credentials_from_supabase(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve Gmail credentials from Supabase for a specific user."""
    print(f"Getting credentials from Supabase for user {user_id}")
    
    # Verify that user_id is a valid UUID
    try:
        # Try to convert user_id to UUID
        user_uuid = str(uuid.UUID(user_id))
        print(f"User ID is a valid UUID: {user_uuid}")
    except ValueError:
        print(f"User ID is not a valid UUID: {user_id}")
        return None
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/gmail_connections",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            },
            params={"user_id": f"eq.{user_uuid}", "select": "credentials,email"}
        )
        
        print(f"GET response status: {response.status_code}")
        print(f"GET response content: {response.text}")
        
        if response.status_code == 200 and response.json():
            print(f"Found credentials for user {user_id}")
            return response.json()[0]
        print(f"No credentials found for user {user_id}")
        return None

@router.get("/auth")
async def gmail_auth(user_id: str):
    """Start the Gmail OAuth flow."""
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=user_id  # Pass user_id as state to retrieve it in the callback
    )
    
    return {"authorization_url": authorization_url}

@router.get("/callback")
async def gmail_callback(request: Request, code: str, state: str):
    """Handle the OAuth callback from Google."""
    print(f"Received callback for user_id (state): {state}, code: {code[:10]}...")
    user_id = state  # Retrieve user_id from state
    
    if not code:
        error_msg = "OAuth code is missing from callback request"
        print(error_msg)
        return RedirectResponse(url=f"/dashboard/profile?gmail_error={error_msg}")
    
    if not user_id:
        error_msg = "User ID is missing from state parameter"
        print(error_msg)
        return RedirectResponse(url=f"/dashboard/profile?gmail_error={error_msg}")
    
    try:
        # Create flow and fetch token
        flow = create_flow()
        try:
            print(f"Fetching token with code...")
            flow.fetch_token(code=code)
        except Exception as token_error:
            error_msg = f"Failed to fetch OAuth token: {str(token_error)}"
            print(error_msg)
            return RedirectResponse(url=f"/dashboard/profile?gmail_error={error_msg}")
            
        credentials = flow.credentials
        print(f"Successfully fetched token for user {user_id}")
        
        # Get user email from Google API
        try:
            print("Building OAuth service...")
            service = build("oauth2", "v2", credentials=credentials)
            
            print("Getting user info...")
            user_info = service.userinfo().get().execute()
            
            email = user_info.get("email", "")
            print(f"Got user email: {email}")
            
            if not email:
                error_msg = "Could not retrieve email from Google account"
                print(error_msg)
                return RedirectResponse(url=f"/dashboard/profile?gmail_error={error_msg}")
            
            # Store credentials in a dictionary format that can be saved to Supabase
            creds_dict = {
                "token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "email": email
            }
            
            try:
                print("Saving credentials to Supabase...")
                await save_credentials_to_supabase(user_id, creds_dict)
                print(f"Credentials saved successfully for user {user_id}")
                
                # Redirect back to the frontend with success - update to profile page
                return RedirectResponse(url=f"/dashboard/profile?gmail_connected=true&email={email}")
            except Exception as save_error:
                error_msg = f"Failed to save credentials: {str(save_error)}"
                print(f"Error saving credentials: {error_msg}")
                return RedirectResponse(url=f"/dashboard/profile?gmail_error={error_msg}")
            
        except Exception as google_api_error:
            error_msg = f"Error accessing Google API: {str(google_api_error)}"
            print(f"Google API error: {error_msg}")
            return RedirectResponse(url=f"/dashboard/profile?gmail_error={error_msg}")
    except Exception as e:
        error_msg = f"Failed to process Gmail connection: {str(e)}"
        print(f"Unexpected error in callback: {error_msg}")
        return RedirectResponse(url=f"/dashboard/profile?gmail_error={error_msg}")

@router.get("/status", response_model=ConnectionStatus)
async def connection_status(user_id: str):
    """Check if a user has connected their Gmail account."""
    print(f"Checking connection status for user {user_id}")
    creds_data = await get_credentials_from_supabase(user_id)
    
    if creds_data and "credentials" in creds_data:
        email = creds_data.get("email", "")
        print(f"User {user_id} is connected with email {email}")
        return ConnectionStatus(
            is_connected=True,
            email=email
        )
    print(f"User {user_id} is not connected")
    return ConnectionStatus(is_connected=False)

@router.delete("/disconnect")
async def disconnect_gmail(user_id: str):
    """Disconnect Gmail integration for a user."""
    print(f"Disconnecting Gmail for user {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    # Verify that user_id is a valid UUID
    try:
        # Try to convert user_id to UUID
        user_uuid = str(uuid.UUID(user_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format. Must be a valid UUID.")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.delete(
                f"{SUPABASE_URL}/rest/v1/gmail_connections",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                },
                params={"user_id": f"eq.{user_uuid}"}
            )
            
            if response.status_code >= 400:
                print(f"Error disconnecting Gmail: {response.status_code} {response.text}")
                raise HTTPException(status_code=500, detail="Failed to disconnect Gmail integration")
                
            return {"success": True, "message": "Gmail disconnected successfully"}
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")

@router.get("/labels")
async def get_labels(user_id: str):
    """Get all Gmail labels for a user, with special focus on finding the AudioBrew label."""
    print(f"Getting Gmail labels for user {user_id}")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    # Get credentials from Supabase
    credentials_data = await get_credentials_from_supabase(user_id)
    if not credentials_data:
        raise HTTPException(status_code=404, detail="Gmail credentials not found")
    
    try:
        # Create credentials object
        credentials_dict = credentials_data.get("credentials", {})
        credentials = Credentials(
            token=credentials_dict.get("token"),
            refresh_token=credentials_dict.get("refresh_token"),
            token_uri=credentials_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=credentials_dict.get("client_id", GOOGLE_CLIENT_ID),
            client_secret=credentials_dict.get("client_secret", GOOGLE_CLIENT_SECRET),
            scopes=credentials_dict.get("scopes", SCOPES)
        )
        
        # Build Gmail service
        service = build("gmail", "v1", credentials=credentials)
        
        # Get all labels
        results = service.users().labels().list(userId="me").execute()
        labels = results.get("labels", [])
        
        # Check if AudioBrew label exists
        audiobrew_label = next((label for label in labels if label["name"].lower() == "audiobrew"), None)
        
        return {
            "labels": labels,
            "audiobrew_label": audiobrew_label,
            "has_audiobrew_label": audiobrew_label is not None
        }
        
    except HttpError as error:
        print(f"Gmail API error: {error}")
        raise HTTPException(status_code=500, detail=f"Gmail API error: {str(error)}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/emails")
async def get_emails(user_id: str, label_id: str = None):
    """Get emails from a specific label (default to AudioBrew if not specified)."""
    print(f"Getting emails for user {user_id} from label {label_id}")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    # Get credentials from Supabase
    credentials_data = await get_credentials_from_supabase(user_id)
    if not credentials_data:
        raise HTTPException(status_code=404, detail="Gmail credentials not found")
    
    try:
        # Create credentials object
        credentials_dict = credentials_data.get("credentials", {})
        credentials = Credentials(
            token=credentials_dict.get("token"),
            refresh_token=credentials_dict.get("refresh_token"),
            token_uri=credentials_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=credentials_dict.get("client_id", GOOGLE_CLIENT_ID),
            client_secret=credentials_dict.get("client_secret", GOOGLE_CLIENT_SECRET),
            scopes=credentials_dict.get("scopes", SCOPES)
        )
        
        # Build Gmail service
        service = build("gmail", "v1", credentials=credentials)
        
        # If no label_id provided, try to find the AudioBrew label
        if not label_id:
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])
            audiobrew_label = next((label for label in labels if label["name"].lower() == "audiobrew"), None)
            
            if not audiobrew_label:
                return {
                    "emails": [],
                    "message": "AudioBrew label not found. Please create a label named 'AudioBrew' in your Gmail account."
                }
            
            label_id = audiobrew_label["id"]
        
        # Get emails from the specified label
        results = service.users().messages().list(
            userId="me", 
            labelIds=[label_id],
            maxResults=10  # Limit to 10 emails for now
        ).execute()
        
        messages = results.get("messages", [])
        emails = []
        
        # Get details for each email
        for message in messages:
            msg = service.users().messages().get(userId="me", id=message["id"]).execute()
            
            # Extract headers
            headers = msg["payload"]["headers"]
            subject = next((header["value"] for header in headers if header["name"].lower() == "subject"), "No Subject")
            from_email = next((header["value"] for header in headers if header["name"].lower() == "from"), "Unknown Sender")
            date = next((header["value"] for header in headers if header["name"].lower() == "date"), "Unknown Date")
            
            # Extract snippet
            snippet = msg.get("snippet", "")
            
            emails.append({
                "id": msg["id"],
                "subject": subject,
                "from": from_email,
                "date": date,
                "snippet": snippet
            })
        
        return {
            "label_id": label_id,
            "emails": emails,
            "total": len(emails)
        }
        
    except HttpError as error:
        print(f"Gmail API error: {error}")
        raise HTTPException(status_code=500, detail=f"Gmail API error: {str(error)}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")