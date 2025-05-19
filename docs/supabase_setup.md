# Supabase Storage Setup for AudioBrew

This guide explains how to set up the Supabase storage bucket for storing podcast audio files in the AudioBrew application.

## Creating the Storage Bucket

1. Log in to your Supabase dashboard at https://app.supabase.com
2. Select your project
3. Navigate to the "Storage" section in the left sidebar
4. Click the "Create bucket" button
5. Enter the following details:
   - Bucket name: `podcasts`
   - Public bucket: ✅ (checked)
   - File size limit: `50MB` (or your preferred limit)
6. Click "Create bucket" to create the storage bucket

## Storage Bucket Permissions

To ensure the bucket is properly accessible:

1. Go to the "Policies" tab in the Storage section
2. For the `podcasts` bucket, add the following policies:

### Insert Policy (for uploading files)

- Policy name: `Allow authenticated users to upload MP3 files`
- Allowed operations: `INSERT`
- Policy definition: SQL
```sql
(bucket_id = 'podcasts' 
AND auth.role() = 'authenticated'
AND storage.extension(name) = 'mp3')
```

### Select Policy (for reading files)

- Policy name: `Allow public access to podcasts`
- Allowed operations: `SELECT`
- Policy definition: SQL
```sql
(bucket_id = 'podcasts')
```

### Update Policy (for updating files)

- Policy name: `Allow authenticated users to update their own MP3 files`
- Allowed operations: `UPDATE`
- Policy definition: SQL
```sql
(bucket_id = 'podcasts' 
AND auth.uid()::text = (storage.foldername(name))[1]
AND storage.extension(name) = 'mp3')
```

### Delete Policy (for deleting files)

- Policy name: `Allow authenticated users to delete their own files`
- Allowed operations: `DELETE`
- Policy definition: SQL
```sql
(bucket_id = 'podcasts' AND auth.uid()::text = (storage.foldername(name))[1])
```

## Folder Structure

The storage structure for podcasts follows this pattern:

```
podcasts/
  ├── {user_id}/
  │     ├── {uuid}.mp3
  │     ├── {uuid}.mp3
  │     └── ...
  ├── {another_user_id}/
  │     └── ...
  └── ...
```

Each user's audio files are stored in a folder named with their user ID, and each audio file has a unique UUID filename.

## Testing the Storage

After setting up the bucket and policies, you can test it by:

1. Running the AudioBrew application
2. Generating a podcast
3. Verifying that the audio file appears in the correct folder in the Supabase storage dashboard 