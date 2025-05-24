from fastapi import APIRouter, HTTPException
import httpx
import os
import uuid
import traceback
from typing import Dict, Any

router = APIRouter()

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Missing required environment variables: SUPABASE_URL, SUPABASE_SERVICE_KEY")

@router.delete("/user/{user_id}")
async def delete_user_account(user_id: str):
    """
    Delete a user account and all associated data including:
    - User podcasts and audio files from storage
    - Gmail credentials
    - User profile data
    """
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    # Validate user_id is a valid UUID
    try:
        user_uuid = str(uuid.UUID(user_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    async with httpx.AsyncClient() as client:
        try:
            # Step 1: Get all user's podcasts to delete audio files
            print(f"Fetching podcasts for user {user_id}")
            podcasts_response = await client.get(
                f"{SUPABASE_URL}/rest/v1/podcasts",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                },
                params={
                    "user_id": f"eq.{user_uuid}",
                    "select": "id,audio_url"
                }
            )
            
            if podcasts_response.status_code == 200:
                podcasts = podcasts_response.json()
                print(f"Found {len(podcasts)} podcasts to delete")
                
                # Step 2: Delete audio files from storage
                for podcast in podcasts:
                    audio_url = podcast.get("audio_url", "")
                    if audio_url and "/storage/v1/object/public/podcasts/" in audio_url:
                        storage_path = audio_url.split("/storage/v1/object/public/podcasts/")[1]
                        
                        try:
                            delete_file_response = await client.delete(
                                f"{SUPABASE_URL}/storage/v1/object/podcasts/{storage_path}",
                                headers={
                                    "apikey": SUPABASE_SERVICE_KEY,
                                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                                }
                            )
                            
                            if delete_file_response.status_code < 400:
                                print(f"Deleted audio file: {storage_path}")
                            else:
                                print(f"Failed to delete audio file {storage_path}: {delete_file_response.text}")
                        except Exception as e:
                            print(f"Error deleting audio file {storage_path}: {str(e)}")
            
            # Step 3: Delete all user's podcasts from database
            print(f"Deleting podcasts from database for user {user_id}")
            delete_podcasts_response = await client.delete(
                f"{SUPABASE_URL}/rest/v1/podcasts",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                },
                params={
                    "user_id": f"eq.{user_uuid}"
                }
            )
            
            if delete_podcasts_response.status_code >= 400:
                print(f"Failed to delete podcasts: {delete_podcasts_response.text}")
            else:
                print("Successfully deleted user podcasts")
            
            # Step 4: Delete Gmail credentials
            print(f"Deleting Gmail credentials for user {user_id}")
            delete_gmail_response = await client.delete(
                f"{SUPABASE_URL}/rest/v1/gmail_credentials",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                },
                params={
                    "user_id": f"eq.{user_uuid}"
                }
            )
            
            if delete_gmail_response.status_code >= 400:
                print(f"Failed to delete Gmail credentials: {delete_gmail_response.text}")
            else:
                print("Successfully deleted Gmail credentials")
            
            # Step 5: Delete user from auth.users (this will cascade to other tables)
            print(f"Deleting user account {user_id}")
            delete_user_response = await client.delete(
                f"{SUPABASE_URL}/rest/v1/auth/users/{user_uuid}",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                }
            )
            
            # Note: Supabase auth deletion might return different status codes
            # If the above doesn't work, we can try the admin API
            if delete_user_response.status_code >= 400:
                print(f"Standard user deletion failed, trying admin API: {delete_user_response.text}")
                
                # Try admin API for user deletion
                admin_delete_response = await client.delete(
                    f"{SUPABASE_URL}/auth/v1/admin/users/{user_uuid}",
                    headers={
                        "apikey": SUPABASE_SERVICE_KEY,
                        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    }
                )
                
                if admin_delete_response.status_code >= 400:
                    print(f"Admin user deletion also failed: {admin_delete_response.text}")
                    raise HTTPException(status_code=500, detail="Failed to delete user account")
                else:
                    print("Successfully deleted user account via admin API")
            else:
                print("Successfully deleted user account")
            
            return {"message": "Account and all associated data deleted successfully"}
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            print(f"Error deleting user account: {str(e)}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to delete account: {str(e)}") 