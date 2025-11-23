# Full Stack Setup Guide - Next.js + FastAPI

Complete guide to run the Drive Document Translator with FastAPI backend and Next.js frontend.

## Architecture

```
┌─────────────────┐         HTTP         ┌─────────────────┐
│                 │  ←───────────────→    │                 │
│   Next.js       │     Port 3000         │   FastAPI       │
│   Frontend      │                       │   Backend       │
│                 │                       │   (Python)      │
└─────────────────┘                       └─────────────────┘
                                                  │
                                                  ├──→ Google Drive API
                                                  └──→ Gemini AI API
```

## Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.8+
- **Google Cloud Project** with Drive API enabled
- **Gemini API Key**

## Step 1: Google Cloud Setup

### 1.1 Create OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing one
3. Enable Google Drive API
4. Go to Credentials → Create Credentials → OAuth client ID
5. Add authorized redirect URIs:
   - `http://localhost:8000/api/drive/callback` (Backend)
6. Save Client ID and Client Secret

### 1.2 Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Create API key
3. Save the key (you'll enter it in the app UI)

## Step 2: Backend Setup (FastAPI)

### 2.1 Navigate to Backend Directory

```bash
cd backend
```

### 2.2 Create Virtual Environment

```bash
python -m venv venv

# Activate it:
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 2.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 2.4 Create .env File

Create `backend/.env`:

```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_PROJECT_ID=your_project_id_here

BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### 2.5 Start Backend Server

```bash
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

✅ **Backend is running at http://localhost:8000**

Check: http://localhost:8000/ (should show status message)

## Step 3: Frontend Setup (Next.js)

### 3.1 Open New Terminal

Keep the backend running, open a NEW terminal window.

### 3.2 Navigate to Project Root

```bash
cd /path/to/nextjs-drive-translator
```

### 3.3 Install Dependencies

```bash
npm install
```

### 3.4 Create .env.local File

Create `.env.local` in the project root:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3.5 Start Frontend Server

```bash
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000
```

✅ **Frontend is running at http://localhost:3000**

## Step 4: Using the Application

1. **Open Browser**: Go to http://localhost:3000

2. **Enter API Key**: Paste your Gemini API key in the first section

3. **Connect to Google Drive**:
   - Click "Connect to Google Drive"
   - You'll be redirected to Google OAuth
   - Approve permissions
   - You'll be redirected back to the app

4. **Select Files**:
   - **Option A**: Paste a Google Drive folder/file link
   - **Option B**: Browse your Drive folders

5. **Configure Translation**:
   - Choose target language
   - Select Gemini model
   - Click "Start Translation"

6. **Download**:
   - Download individual files or all at once

## Verification Checklist

### Backend Verification

- [ ] Virtual environment activated
- [ ] All packages installed (`pip list` shows packages)
- [ ] `.env` file created with correct credentials
- [ ] Server running on port 8000
- [ ] http://localhost:8000/ shows status
- [ ] http://localhost:8000/docs shows Swagger UI

### Frontend Verification

- [ ] Node modules installed
- [ ] `.env.local` file created
- [ ] Server running on port 3000
- [ ] http://localhost:3000/ loads the app
- [ ] No console errors in browser DevTools

### Integration Verification

- [ ] OAuth redirect works (redirects to Google then back)
- [ ] Can list folders from Drive
- [ ] Can download files
- [ ] Translation works and shows progress
- [ ] Can download translated files

## Common Issues

### Issue: "Connection Refused" when clicking Connect

**Solution**: Make sure backend is running on port 8000

```bash
cd backend
source venv/bin/activate
python main.py
```

### Issue: "CORS Error" in browser console

**Solution**: Check that `FRONTEND_URL` in backend `.env` matches your frontend URL

### Issue: OAuth Redirect Fails

**Solution**: 
1. Check backend logs for errors
2. Verify redirect URI in Google Cloud Console matches exactly:
   ```
   http://localhost:8000/api/drive/callback
   ```

### Issue: "Module not found" errors in backend

**Solution**: 
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Frontend can't connect to backend

**Solution**: Check `.env.local` has correct backend URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Tips

### Terminal Setup

**Terminal 1 (Backend)**:
```bash
cd backend
source venv/bin/activate
python main.py
```

**Terminal 2 (Frontend)**:
```bash
cd /path/to/project
npm run dev
```

### Viewing Logs

**Backend logs**: Show in Terminal 1 (Python output)
**Frontend logs**: Browser DevTools Console (F12)

### Restart After Changes

**Backend**: Ctrl+C then `python main.py` (auto-reload enabled)
**Frontend**: Ctrl+C then `npm run dev` (hot reload enabled)

## Production Deployment

### Backend

```bash
# Install production server
pip install gunicorn

# Run
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend

```bash
npm run build
npm start
```

### Update Environment Variables

Update URLs in production:
- Backend `.env`: `BACKEND_URL=https://your-api-domain.com`
- Frontend `.env.local`: `NEXT_PUBLIC_API_URL=https://your-api-domain.com`
- Google Cloud Console: Add production redirect URI

## Ports Summary

| Service | Port | URL |
|---------|------|-----|
| FastAPI Backend | 8000 | http://localhost:8000 |
| Next.js Frontend | 3000 | http://localhost:3000 |

## Architecture Benefits

✅ **Separation of Concerns**: Frontend and backend are independent
✅ **Python Backend**: Use existing Python libraries and logic
✅ **Scalability**: Can scale frontend and backend separately
✅ **Type Safety**: FastAPI provides automatic API documentation
✅ **Development**: Hot reload on both frontend and backend

## Need Help?

1. Check terminal output for error messages
2. View browser console (F12) for frontend errors
3. Check backend API docs: http://localhost:8000/docs
4. Verify all environment variables are set correctly

---

**Happy Translating! 🌐📄**
