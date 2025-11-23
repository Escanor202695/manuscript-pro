# Troubleshooting Guide - Google Drive Authentication

## Error: "Authentication Failed"

This error occurs when the Google Drive OAuth connection fails. Here's how to diagnose and fix it:

---

## 🔍 Step-by-Step Diagnosis

### 1. Check Backend Server is Running

**Symptom:** "Backend server is not running" error

**Fix:**
```bash
# Terminal 1 - Start Backend
cd /path/to/your/backend/folder
python main.py

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Verify:**
- Open browser: http://localhost:8000
- Should show: `{"status":"Drive Document Translator API is running"}`

---

### 2. Check Environment Variables

**Symptom:** 
- "Auth failed" error
- Backend logs show missing credentials

**Required Files:**

#### **Frontend `.env.local`** (in translator-nextjs folder)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### **Backend `.env`** (in backend folder)
```env
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_PROJECT_ID=your_project_id_here

# URLs
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# CORS (optional)
ALLOWED_ORIGINS=http://localhost:3000
```

**Get Google OAuth Credentials:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create Project (or select existing)
3. Enable Google Drive API
4. Create OAuth 2.0 Client ID (Web application)
5. Add authorized redirect URI: `http://localhost:8000/api/drive/callback`
6. Copy Client ID, Client Secret, Project ID to `.env`

---

### 3. Check Google Cloud Console Configuration

**Symptom:** OAuth redirect fails or shows "redirect_uri_mismatch"

**Fix:**

1. Go to [Google Cloud Console Credentials](https://console.cloud.google.com/apis/credentials)
2. Click on your OAuth 2.0 Client ID
3. Under "Authorized redirect URIs", add:
   ```
   http://localhost:8000/api/drive/callback
   ```
4. Click "Save"

**Important:** The redirect URI must match EXACTLY:
- ✅ `http://localhost:8000/api/drive/callback`
- ❌ `http://localhost:7860/api/drive/callback` (wrong port)
- ❌ `https://localhost:8000/api/drive/callback` (wrong protocol)
- ❌ `http://127.0.0.1:8000/api/drive/callback` (use localhost, not 127.0.0.1)

---

### 4. Check CORS Configuration

**Symptom:** 
- Browser console shows CORS error
- "Access to fetch has been blocked by CORS policy"

**Fix in Backend:**

Check your backend `.env` has:
```env
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000
```

The backend should have CORS middleware configured (it does by default).

---

### 5. Check Port Configuration

**Symptom:** Connection refused or wrong port

**Verify:**
- Backend runs on: **Port 8000** (not 7860)
- Frontend runs on: **Port 3000**
- Frontend `.env.local` points to: `http://localhost:8000`

**If backend runs on different port:**
Update both:
1. Backend `.env`: `BACKEND_URL=http://localhost:YOUR_PORT`
2. Frontend `.env.local`: `NEXT_PUBLIC_API_URL=http://localhost:YOUR_PORT`
3. Google Cloud Console redirect URI: `http://localhost:YOUR_PORT/api/drive/callback`

---

## 🐛 Debug Checklist

Run through this checklist:

### Backend Checks
- [ ] Backend server is running (`python main.py`)
- [ ] Backend responds at http://localhost:8000
- [ ] Backend `.env` file exists with credentials
- [ ] `GOOGLE_CLIENT_ID` is set
- [ ] `GOOGLE_CLIENT_SECRET` is set
- [ ] `GOOGLE_PROJECT_ID` is set
- [ ] `BACKEND_URL=http://localhost:8000`
- [ ] `FRONTEND_URL=http://localhost:3000`

### Frontend Checks
- [ ] Frontend is running (`npm run dev`)
- [ ] Frontend `.env.local` exists
- [ ] `NEXT_PUBLIC_API_URL=http://localhost:8000` is set
- [ ] Browser can reach http://localhost:3000

### Google Cloud Console Checks
- [ ] Project exists
- [ ] Google Drive API is enabled
- [ ] OAuth 2.0 Client ID exists
- [ ] Redirect URI is `http://localhost:8000/api/drive/callback`
- [ ] OAuth consent screen is configured
- [ ] Test users are added (if in testing mode)

---

## 📋 Common Error Messages

### "Backend server is not running"

**Cause:** Backend not started or wrong URL

**Fix:**
```bash
cd /path/to/backend
python main.py
```

---

### "Auth request failed: 500"

**Cause:** Backend error, likely missing credentials

**Check backend logs:**
```bash
# In backend terminal, look for:
# Auth failed: 'GOOGLE_CLIENT_ID'
```

**Fix:** Add credentials to backend `.env`

---

### "redirect_uri_mismatch"

**Cause:** Redirect URI in Google Cloud Console doesn't match

**Fix:**
1. Check backend logs for actual redirect URI
2. Add that EXACT URI to Google Cloud Console
3. Common issue: Port mismatch (8000 vs 7860)

---

### "Invalid state"

**Cause:** Backend sessions cleared or state expired

**Fix:**
- Restart backend
- Try connecting again
- Clear browser localStorage: `localStorage.clear()`

---

## 🔧 Testing OAuth Flow

### Manual Test

1. **Start backend:**
   ```bash
   python main.py
   ```

2. **Test auth endpoint:**
   ```bash
   curl http://localhost:8000/api/drive/auth
   ```
   
   Should return:
   ```json
   {
     "authUrl": "https://accounts.google.com/o/oauth2/auth?...",
     "state": "some_random_state"
   }
   ```

3. **Check state in backend logs:**
   ```
   [CALLBACK] Available sessions: ['state_value']
   ```

4. **Try the authUrl in browser:**
   - Copy the authUrl from step 2
   - Paste in browser
   - Should redirect to Google OAuth

---

## 🚀 Quick Start Commands

### Fresh Start (Both Servers)

```bash
# Terminal 1 - Backend
cd /path/to/backend
source venv/bin/activate  # if using venv
python main.py

# Terminal 2 - Frontend  
cd /path/to/translator-nextjs
npm run dev

# Terminal 3 - Test Backend
curl http://localhost:8000/

# Terminal 4 - Test Frontend
curl http://localhost:3000/
```

---

## 📊 Port Summary

| Service | Port | URL | Purpose |
|---------|------|-----|---------|
| Backend (FastAPI) | 8000 | http://localhost:8000 | API endpoints |
| Frontend (Next.js) | 3000 | http://localhost:3000 | Web interface |
| OAuth Callback | 8000 | http://localhost:8000/api/drive/callback | Google redirects here |

---

## 🔍 Browser Console Debugging

Open browser console (F12) and look for:

**Successful Connection:**
```
[CONNECT] Attempting to connect to: http://localhost:8000
[CONNECT] Backend is reachable, requesting auth URL...
[CONNECT] Auth response status: 200
[CONNECT] Auth data received: {authUrl: "https://...", state: "..."}
[CONNECT] Redirecting to Google OAuth...
```

**Failed Connection:**
```
[CONNECT] Backend not reachable: TypeError: Failed to fetch
❌ Shows: "Backend server is not running"
```

---

## 🛠️ Advanced Debugging

### Enable Verbose Logging

**Backend:**
```python
# In main.py, add at top:
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Frontend:**
All console logs are already enabled in the code.

### Check Network Tab

1. Open browser DevTools (F12)
2. Go to Network tab
3. Click "Connect to Google Drive"
4. Look for:
   - Request to `/api/drive/auth`
   - Response status (should be 200)
   - Response body (should have authUrl)

### Check Backend Logs

When clicking "Connect", backend should log:
```
[CALLBACK] Received callback with state: abc123
[CALLBACK] Available sessions: ['abc123']
[CALLBACK] Fetching token with code...
[CALLBACK] Credentials obtained successfully
[CALLBACK] Redirecting to frontend with state: abc123
```

---

## ✅ Verification Steps

After fixing, verify everything works:

1. ✅ Backend responds: http://localhost:8000
2. ✅ Frontend loads: http://localhost:3000
3. ✅ Click "Connect to Google Drive"
4. ✅ Redirects to Google OAuth page
5. ✅ Google shows permission request
6. ✅ After approval, redirects back to frontend
7. ✅ Shows "Successfully connected to Google Drive!" toast
8. ✅ Source method shows "Google Drive" with green checkmark

---

## 💡 Pro Tips

1. **Use localhost, not 127.0.0.1** - Google OAuth prefers localhost
2. **Keep ports consistent** - Don't change ports mid-session
3. **Check .env files** - Most issues are missing environment variables
4. **Restart after changes** - Restart backend after editing .env
5. **Check consent screen** - Make sure test users are added in Google Cloud Console

---

## 🆘 Still Not Working?

If you've tried everything above:

1. **Check browser console** - Look for specific error messages
2. **Check backend terminal** - Look for Python errors
3. **Verify API is enabled** - Google Drive API must be enabled in Google Cloud Console
4. **Check OAuth consent screen** - Must be configured with app name
5. **Try incognito mode** - Rules out browser cache issues
6. **Clear localStorage** - Run `localStorage.clear()` in browser console

---

## 📞 Error Reference

| Error Message | Cause | Fix |
|--------------|-------|-----|
| Backend server is not running | Backend not started | Run `python main.py` |
| Auth request failed: 500 | Missing credentials | Add to backend `.env` |
| redirect_uri_mismatch | URI mismatch | Update Google Cloud Console |
| Invalid state | Session expired | Restart backend, try again |
| CORS error | CORS misconfigured | Check `FRONTEND_URL` in backend |
| Failed to fetch | Port mismatch | Check `NEXT_PUBLIC_API_URL` |

---

## 🎯 Success Indicators

You'll know it's working when:
- ✅ No errors in browser console
- ✅ Backend logs show successful OAuth flow
- ✅ Frontend shows green "Connected" status
- ✅ Can browse folders/files
- ✅ Can download and translate files

Happy debugging! 🚀

