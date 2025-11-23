# 🚀 Quick Setup Guide

Follow these steps to get the Next.js Drive Document Translator up and running.

## Step 1: Install Dependencies

```bash
cd nextjs-drive-translator
npm install
```

## Step 2: Google Cloud Configuration

### 2.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter project name and click "Create"

### 2.2 Enable Google Drive API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click on it and press "Enable"

### 2.3 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in application name
   - Add your email as developer contact
   - Click "Save and Continue" through the steps
4. Back to creating OAuth client ID:
   - Application type: "Web application"
   - Name: "Next.js Drive Translator"
   - Authorized redirect URIs:
     - Add: `http://localhost:3000/api/drive/callback`
     - (For production, add your domain: `https://yourdomain.com/api/drive/callback`)
5. Click "Create"
6. **Save the Client ID and Client Secret** - you'll need these!

## Step 3: Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. **Copy and save the API key** - you'll need to enter this in the app

## Step 4: Create Environment File

Create a file named `.env.local` in the project root:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_PROJECT_ID=your_project_id_here
BASE_URL=http://localhost:3000
NEXT_PUBLIC_BASE_URL=http://localhost:3000
SESSION_SECRET=any_random_string_here
```

Replace the placeholders:
- `your_client_id_here` - From Step 2.3
- `your_client_secret_here` - From Step 2.3
- `your_project_id_here` - Your Google Cloud project ID
- `any_random_string_here` - Any random string (e.g., `my-secret-key-12345`)

## Step 5: Run the Application

```bash
npm run dev
```

Open your browser and go to: [http://localhost:3000](http://localhost:3000)

## Step 6: Using the Application

1. **Enter Gemini API Key** (from Step 3)
   - Paste it in the API Configuration section
   
2. **Connect to Google Drive**
   - Click "Connect to Google Drive"
   - A new window will open for Google authorization
   - Sign in and approve the permissions
   - You'll be redirected back to the app

3. **Select Files**
   - Choose to paste a Drive link OR browse folders
   - Select one or multiple files
   
4. **Translate**
   - Choose target language
   - Select Gemini model
   - Click "Start Translation"
   
5. **Download**
   - Download individual files or all at once

## 🎉 You're All Set!

Your application is now ready to translate documents from Google Drive.

## Common Issues

### Port Already in Use
If port 3000 is busy, run on a different port:
```bash
npm run dev -- -p 3001
```
Don't forget to update `NEXT_PUBLIC_BASE_URL` and redirect URI!

### OAuth Error
- Make sure redirect URI in Google Cloud exactly matches: `http://localhost:3000/api/drive/callback`
- Check that environment variables are loaded (restart dev server after creating .env.local)

### Translation Fails
- Verify your Gemini API key is correct
- Check that you have available quota
- Ensure the document contains text content

## Production Deployment

When deploying to production:

1. Update `NEXT_PUBLIC_BASE_URL` to your production domain
2. Add production redirect URI to Google Cloud OAuth settings
3. Use secure session secrets
4. Consider using environment variables from your hosting platform

## Need Help?

Check the main README.md for more detailed documentation, or open an issue on GitHub.
