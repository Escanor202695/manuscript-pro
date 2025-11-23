# Google Drive OAuth Connection Fix

## Problem Fixed
1. ✅ Frontend was connecting to wrong port (7860 instead of 8000)
2. ✅ Frontend always showed "connected" even when not authenticated
3. ✅ Session validation now happens with backend
4. ✅ Translation endpoints now use correct service routes

## Setup Instructions

### Step 1: Create Frontend Environment File

Create `.env.local` in the `translator-nextjs` folder:

```bash
cd translator-nextjs
```

Create a file named `.env.local` with this content:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 2: Create Backend Environment File

In your **backend folder** (where your FastAPI `main.py` is), create a `.env` file:

```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_PROJECT_ID=your_project_id_here

# URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Optional: CORS origins (comma-separated, or "*" for all)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Get Google OAuth Credentials:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create OAuth 2.0 Client ID (Web application)
3. Add authorized redirect URI: `http://localhost:8000/api/drive/callback`
4. Copy Client ID and Client Secret to `.env` file

### Step 3: Start Backend Server

```bash
# Navigate to your backend folder
cd /path/to/your/backend

# Activate virtual environment (if using one)
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies (if not already installed)
pip install fastapi uvicorn python-dotenv google-generativeai google-auth-oauthlib google-api-python-client python-docx aiohttp

# Start the server
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 4: Start Frontend Server

Open a **new terminal window**:

```bash
# Navigate to translator-nextjs folder
cd translator-nextjs

# Install dependencies (if not already)
npm install

# Start frontend
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000
```

### Step 5: Test the Connection

1. Open browser: http://localhost:3000
2. Click "Connect to Google Drive"
3. You'll be redirected to Google OAuth
4. Approve permissions
5. You'll be redirected back with "Successfully connected to Google Drive!" toast

## What Changed

### Frontend Changes (`src/app/page.js`)

1. **Session Validation**: Now validates saved sessions with backend before showing "connected"
   ```javascript
   const validateSession = async (state) => {
     const response = await fetch(`${API_BASE_URL}/api/drive/folders?state=${state}`)
     if (response.ok) {
       setAuthenticated(true)
     } else {
       localStorage.removeItem('drive_session_state')
       setAuthenticated(false)
     }
   }
   ```

2. **Service-Specific Endpoints**: Uses correct translation endpoint based on service
   ```javascript
   const translateEndpoint = service === 'openrouter' 
     ? `${API_BASE_URL}/api/translate/openrouter`
     : `${API_BASE_URL}/api/translate`
   ```

3. **Port Configuration**: Uses environment variable pointing to port 8000

## Troubleshooting

### Issue: "Connection Refused" 
**Solution**: Make sure backend is running on port 8000
```bash
# Check if backend is running
curl http://localhost:8000/
# Should return: {"status":"Drive Document Translator API is running"}
```

### Issue: "Always shows connected but can't load folders"
**Solution**: Clear localStorage and reconnect
```javascript
// In browser console:
localStorage.removeItem('drive_session_state')
// Then refresh page and reconnect
```

### Issue: OAuth redirect fails
**Solution**: Check Google Cloud Console redirect URI matches exactly:
- Must be: `http://localhost:8000/api/drive/callback`

### Issue: CORS errors
**Solution**: Check backend `.env` has correct FRONTEND_URL:
```env
FRONTEND_URL=http://localhost:3000
```

## Ports Summary

| Service | Port | URL |
|---------|------|-----|
| FastAPI Backend | 8000 | http://localhost:8000 |
| Next.js Frontend | 3000 | http://localhost:3000 |

## Notes

- Backend sessions are stored in-memory (for production, use Redis/database)
- OAuth tokens are stored in backend sessions dictionary
- Frontend only stores session state ID in localStorage
- Session validation happens on page load to prevent "always connected" bug

