# Environment Setup Guide

## Required Environment Variables

The backend requires a `.env` file in the `ai_translation_backend` directory. Create this file with the following variables:

```bash
# Google OAuth Configuration
# Get these from: https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000

# API URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# CORS Configuration (optional)
# Uncomment and customize if needed
# ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# OpenRouter Configuration (optional)
OPENROUTER_REFERER=https://yourdomain.com
```

## How to Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
5. Configure the OAuth consent screen if needed
6. Set application type to "Web application"
7. Add authorized redirect URIs:
   - `http://localhost:8000/api/drive/callback`
   - (Add production URL when deploying)
8. Copy the Client ID and Client Secret to your `.env` file

## Installation Steps

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   ```

2. Activate virtual environment:
   ```bash
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with the variables above

5. Run the backend:
   ```bash
   python main.py
   ```

The backend will run on `http://localhost:8000` (default port is 7860 as configured in main.py)

## API Endpoints

- `GET /` - Health check
- `GET /api/drive/auth` - Start OAuth flow
- `GET /api/drive/callback` - OAuth callback
- `GET /api/drive/folders` - List Drive folders
- `GET /api/drive/files` - List files in folder
- `GET /api/drive/download` - Download file from Drive
- `POST /api/translate` - Translate document (Gemini)
- `POST /api/translate/openrouter` - Translate document (OpenRouter)
- `GET /api/translate/progress/{id}` - Get translation progress
- `POST /api/drive/create-folder` - Create folder in Drive
- `POST /api/drive/upload` - Upload file to Drive
- `POST /api/drive/logout` - Clear session

