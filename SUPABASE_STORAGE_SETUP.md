# Setting Up Supabase Storage for Profile Images

This guide explains how to set up Supabase storage for profile images in AudioBrew.

## Creating the 'profiles' Bucket

1. Log in to your Supabase dashboard: https://app.supabase.com/
2. Select your project
3. Navigate to "Storage" in the left sidebar
4. Click "Create bucket"
5. Enter the bucket name: `profiles`
6. Check "Public bucket" to allow public read access
7. Click "Create bucket"

## Setting Up Row-Level Security (RLS) Policies

After creating the bucket, you need to configure security policies to allow users to upload their profile images.

1. In the Storage section, click on your newly created `profiles` bucket
2. Click on the "Policies" tab
3. Add the following policies:

### Allow users to upload their own files (CREATE policy)

1. Click "Add Policy" 
2. Select "Create custom policy"
3. Fill in the form:
   - Name: `Allow users to upload their own files`
   - Definition: `CREATE`
   - Policy statement: `(bucket_id = 'profiles' AND auth.uid() = auth.uid())`
   - Comment: `Allow users to upload their own profile images`
4. Click "Create policy"

### Allow users to update their own files (UPDATE policy)

1. Click "Add Policy" 
2. Select "Create custom policy"
3. Fill in the form:
   - Name: `Allow users to update their own files`
   - Definition: `UPDATE`
   - Policy statement: `(bucket_id = 'profiles' AND auth.uid() = owner)`
   - Comment: `Allow users to update their own profile images`
4. Click "Create policy"

### Allow public read access (SELECT policy)

1. Click "Add Policy"
2. Select "Create custom policy"
3. Fill in the form:
   - Name: `Allow public read access`
   - Definition: `SELECT`
   - Policy statement: `(bucket_id = 'profiles')`
   - Comment: `Allow public read access to all profile images`
4. Click "Create policy"

## Testing the Configuration

After setting up the bucket and policies:

1. Return to your AudioBrew application
2. Try uploading a profile picture through the profile settings page
3. If the upload is successful, you should see your profile picture displayed in both the profile page and the sidebar

## Troubleshooting

If you're still having issues with profile image uploads:

1. Check the browser console for specific error messages
2. Verify that the RLS policies are correctly configured
3. Make sure your Supabase project has storage enabled (check subscription tier)
4. Check that the file size isn't too large (Supabase has file size limits based on your plan)

Feel free to reach out if you need further assistance. 