from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import httpx
import os
from datetime import datetime
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import traceback

# Import the Gmail router functions to reuse email fetching
from .gmail import get_credentials_from_supabase

load_dotenv()

router = APIRouter(prefix="/podcast", tags=["podcast"])

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Configure OpenAI client
openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

class PodcastRequest(BaseModel):
    user_id: str
    email_ids: List[str]
    title: Optional[str] = None

class PodcastResponse(BaseModel):
    id: str
    status: str
    message: str

async def process_emails_to_text(emails: List[Dict[str, Any]]) -> str:
    """Process emails and extract their content into a structured text format."""
    combined_text = ""
    
    for email in emails:
        subject = email.get("subject", "No Subject")
        sender = email.get("from", "Unknown Sender").split('<')[0].strip()
        date = email.get("date", "Unknown Date")
        snippet = email.get("snippet", "")
        
        # Format the email content
        email_text = f"Email from {sender} on {date}\n"
        email_text += f"Subject: {subject}\n\n"
        email_text += f"{snippet}\n\n"
        email_text += "--------------------\n\n"
        
        combined_text += email_text
    
    return combined_text

async def generate_script_with_gpt4(emails_text: str) -> Dict[str, Any]:
    """
    Generate a podcast script using OpenAI's GPT-4o model.
    """
    try:
        # Create the prompt for GPT-4o
        prompt = f"""
You are a podcast host. Create a comprehensive, in-depth script based on the following newsletter content:

{emails_text}

Guidelines:
1. Start with a very brief intro mentioning this is the AudioBrew podcast
2. Cover ALL key insights, statistics, and quotes from EACH newsletter in detail
3. Keep the script under 4000 characters total, but use as much of that limit as possible
4. Write in a conversational tone suitable for speaking
5. Do not include any formatting instructions, notes, or meta-commentary
6. For each newsletter, extract and explain the most valuable insights without skipping any important context
7. End with a brief sign-off

Return ONLY the script text that should be read aloud, with no additional formatting or instructions.
"""

        # Call the OpenAI API
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert podcast script writer. Your output should be ONLY the script text with no additional comments or instructions. Make sure to cover all key insights from each newsletter in detail. Aim for 3800-4000 characters of content, or less when there is no more content to cover."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract the script from the response
        script_markdown = response.choices[0].message.content
        
        # Calculate approximate duration (130-160 words per minute)
        word_count = len(script_markdown.split())
        approx_duration_sec = int((word_count / 145) * 60)  # Using average of 145 wpm
        
        return {
            "script_markdown": script_markdown,
            "approx_duration_sec": approx_duration_sec,
            "word_count": word_count
        }
        
    except Exception as e:
        print(f"Error generating script with GPT-4o: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate script: {str(e)}")

async def generate_audio_from_text(text: str, user_id: str) -> str:
    """
    Generate audio from text using OpenAI's text-to-speech API.
    For longer texts, truncates to fit within the TTS character limit.
    Uploads the audio to Supabase storage and returns the URL.
    """
    try:
        import io
        import uuid
        
        # OpenAI TTS has a limit of 4096 characters
        MAX_CHARS = 4050  # Reduced from 4090 to 4050 for a safer margin
        
        # Truncate text if needed
        if len(text) > MAX_CHARS:
            print(f"Text too long ({len(text)} chars), truncating to {MAX_CHARS} chars")
            # Try to truncate at a sentence boundary
            truncated_text = text[:MAX_CHARS]
            last_period = truncated_text.rfind('.')
            if last_period > MAX_CHARS * 0.8:  # Only truncate at sentence if we don't lose too much
                truncated_text = truncated_text[:last_period+1]
            text = truncated_text + "... [Text truncated due to length limits]"
        
        # Additional safety check to ensure we're definitely under the limit
        if len(text) > 4096:
            print(f"Warning: Text still too long ({len(text)} chars) after initial truncation, forcing truncation")
            text = text[:4000] + "... [Text truncated due to length limits]"
        
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.mp3"
        storage_path = f"podcasts/{user_id}/{filename}"
        
        # Call OpenAI's TTS API with MP3 format
        print(f"Generating audio with OpenAI TTS API")
        response = await openai_client.audio.speech.create(
            model="tts-1-hd",  # Using higher quality model
            voice="nova",  # Options: alloy, echo, fable, onyx, nova, shimmer
            input=text,
            response_format="mp3"  # Explicitly request MP3 format
        )
        
        # Get audio content as bytes - FIX: response.read() returns bytes directly, not a coroutine
        audio_bytes = response.read()
        
        # Verify we have valid audio data
        if not audio_bytes or len(audio_bytes) < 1000:  # Arbitrary minimum size for valid audio
            raise Exception("Received invalid or empty audio data from TTS API")
        
        # Upload to Supabase storage
        print(f"Uploading audio to Supabase storage: {storage_path}")
        
        # Upload to Supabase storage using httpx
        async with httpx.AsyncClient() as client:
            # Upload the file to the existing 'podcasts' bucket
            upload_response = await client.post(
                f"{SUPABASE_URL}/storage/v1/object/podcasts/{storage_path}",
                headers={
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "audio/mpeg"  # Correct MIME type for MP3
                },
                content=audio_bytes
            )
            
            if upload_response.status_code >= 400:
                print(f"Error uploading to Supabase: {upload_response.text}")
                raise Exception(f"Failed to upload audio: {upload_response.text}")
            
            # Get the public URL
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/podcasts/{storage_path}"
            print(f"Audio uploaded successfully: {public_url}")
            
            return public_url
        
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        traceback.print_exc()
        # In case of error, return a placeholder URL
        return f"https://example.com/audio/{uuid.uuid4()}.mp3"

async def save_podcast_to_supabase(user_id: str, title: str, script_markdown: str, audio_url: str, source_emails: int, duration: int = 300) -> str:
    """Save podcast metadata to Supabase."""
    podcast_id = str(uuid.uuid4())
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/podcasts",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=minimal"
            },
            json={
                "id": podcast_id,
                "user_id": user_id,
                "title": title,
                "audio_url": audio_url,
                "script_markdown": script_markdown,  # Store the script in the podcast record
                "duration": duration,  # in seconds
                "source_emails": source_emails,
                "created_at": datetime.now().isoformat()
            }
        )
        
        if response.status_code >= 400:
            raise HTTPException(status_code=500, detail=f"Failed to save podcast: {response.text}")
    
    return podcast_id

async def fetch_email_content(user_data: Dict[str, Any], email_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Fetch full email content using Gmail API.
    """
    try:
        # Get credentials from user_data
        credentials_dict = user_data.get("credentials", {})
        credentials = Credentials(
            token=credentials_dict.get("token"),
            refresh_token=credentials_dict.get("refresh_token"),
            token_uri=credentials_dict.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=credentials_dict.get("scopes")
        )
        
        # Build Gmail API service
        service = build("gmail", "v1", credentials=credentials)
        
        # Fetch emails
        emails = []
        for email_id in email_ids:
            # Get the email
            message = service.users().messages().get(userId="me", id=email_id).execute()
            
            # Extract headers
            headers = message.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"].lower() == "subject"), "No Subject")
            from_header = next((h["value"] for h in headers if h["name"].lower() == "from"), "Unknown Sender")
            date = next((h["value"] for h in headers if h["name"].lower() == "date"), "Unknown Date")
            
            # Extract snippet
            snippet = message.get("snippet", "")
            
            # Add to emails list
            emails.append({
                "id": email_id,
                "subject": subject,
                "from": from_header,
                "date": date,
                "snippet": snippet
            })
        
        return emails
        
    except Exception as e:
        print(f"Error fetching emails: {str(e)}")
        # In case of error, return empty list
        return []

async def process_podcast_generation(user_id: str, email_ids: List[str], title: str = None):
    """
    Background task to process podcast generation.
    This would be a long-running task in a real application.
    """
    try:
        # Fetch user's Gmail credentials
        user_data = await get_credentials_from_supabase(user_id)
        if not user_data or "credentials" not in user_data:
            print(f"No Gmail credentials found for user {user_id}")
            return
        
        # Fetch email content
        emails = await fetch_email_content(user_data, email_ids)
        
        # Process emails to text
        emails_text = await process_emails_to_text(emails)
        
        # Generate a title if not provided
        if not title:
            title = f"AudioBrew Podcast - {datetime.now().strftime('%B %d, %Y')}"
        
        # STEP 1: Generate script using GPT-4o
        print(f"Generating script for podcast: {title}")
        script_data = await generate_script_with_gpt4(emails_text)
        script_markdown = script_data["script_markdown"]
        duration = script_data["approx_duration_sec"]
        
        print(f"Script generated: {len(script_markdown)} characters, {script_data['word_count']} words")
        
        # STEP 2: Generate audio from script
        print("Generating audio from script")
        
        audio_url = await generate_audio_from_text(script_markdown, user_id)
        
        # Save podcast to database
        podcast_id = await save_podcast_to_supabase(
            user_id=user_id,
            title=title,
            script_markdown=script_markdown,
            audio_url=audio_url,
            source_emails=len(emails),
            duration=duration
        )
        
        print(f"Podcast generation completed. ID: {podcast_id}")
        
    except Exception as e:
        print(f"Error in podcast generation: {str(e)}")
        traceback.print_exc()  # Print full traceback for debugging

@router.post("/generate", response_model=PodcastResponse)
async def generate_podcast(request: PodcastRequest, background_tasks: BackgroundTasks):
    """
    Start the podcast generation process.
    This endpoint returns immediately and processes the podcast in the background.
    """
    if not request.user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    if not request.email_ids or len(request.email_ids) == 0:
        raise HTTPException(status_code=400, detail="At least one email ID is required")
    
    # Validate user_id is a valid UUID
    try:
        user_uuid = str(uuid.UUID(request.user_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    # Add the task to the background tasks
    background_tasks.add_task(
        process_podcast_generation,
        user_id=user_uuid,
        email_ids=request.email_ids,
        title=request.title
    )
    
    return {
        "id": str(uuid.uuid4()),  # This would be a job ID in a real implementation
        "status": "processing",
        "message": "Podcast generation started. This may take a few minutes."
    }

@router.get("/list")
async def list_podcasts(user_id: str):
    """List all podcasts for a user."""
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    
    # Validate user_id is a valid UUID
    try:
        user_uuid = str(uuid.UUID(user_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/podcasts",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            },
            params={
                "user_id": f"eq.{user_uuid}",
                "select": "*",
                "order": "created_at.desc"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Failed to fetch podcasts: {response.text}")
        
        return response.json()

@router.get("/{podcast_id}")
async def get_podcast(podcast_id: str, user_id: str):
    """Get a specific podcast."""
    if not podcast_id or not user_id:
        raise HTTPException(status_code=400, detail="Podcast ID and User ID are required")
    
    # Validate IDs are valid UUIDs
    try:
        podcast_uuid = str(uuid.UUID(podcast_id))
        user_uuid = str(uuid.UUID(user_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/podcasts",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            },
            params={
                "id": f"eq.{podcast_uuid}",
                "user_id": f"eq.{user_uuid}",
                "select": "*"
            }
        )
        
        if response.status_code != 200 or not response.json():
            raise HTTPException(status_code=404, detail="Podcast not found or doesn't belong to the user")
        
        return response.json()[0]

@router.delete("/{podcast_id}")
async def delete_podcast(podcast_id: str, user_id: str):
    """Delete a podcast and its associated audio file from storage."""
    if not podcast_id or not user_id:
        raise HTTPException(status_code=400, detail="Podcast ID and User ID are required")
    
    # Validate IDs are valid UUIDs
    try:
        podcast_uuid = str(uuid.UUID(podcast_id))
        user_uuid = str(uuid.UUID(user_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")
    
    async with httpx.AsyncClient() as client:
        # First check if the podcast belongs to the user and get the audio_url
        check_response = await client.get(
            f"{SUPABASE_URL}/rest/v1/podcasts",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            },
            params={
                "id": f"eq.{podcast_uuid}",
                "user_id": f"eq.{user_uuid}",
                "select": "id,audio_url"
            }
        )
        
        if check_response.status_code != 200 or not check_response.json():
            raise HTTPException(status_code=404, detail="Podcast not found or doesn't belong to the user")
        
        podcast_data = check_response.json()[0]
        audio_url = podcast_data.get("audio_url", "")
        
        # Extract the storage path from the audio URL
        if audio_url and "/storage/v1/object/public/podcasts/" in audio_url:
            storage_path = audio_url.split("/storage/v1/object/public/podcasts/")[1]
            
            # Delete the audio file from storage
            try:
                delete_file_response = await client.delete(
                    f"{SUPABASE_URL}/storage/v1/object/podcasts/{storage_path}",
                    headers={
                        "apikey": SUPABASE_SERVICE_KEY,
                        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    }
                )
                
                if delete_file_response.status_code >= 400 and delete_file_response.status_code != 404:
                    # Log the error but continue with deleting the database record
                    print(f"Failed to delete audio file: {delete_file_response.text}")
            except Exception as e:
                # Log the error but continue with deleting the database record
                print(f"Error deleting audio file: {str(e)}")
        
        # Delete the podcast record from the database
        delete_response = await client.delete(
            f"{SUPABASE_URL}/rest/v1/podcasts",
            headers={
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            },
            params={
                "id": f"eq.{podcast_uuid}"
            }
        )
        
        if delete_response.status_code >= 400:
            raise HTTPException(status_code=500, detail=f"Failed to delete podcast: {delete_response.text}")
        
        return {"message": "Podcast and audio file deleted successfully"} 