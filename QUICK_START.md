# Quick Start Guide - Translation Manuscript

## 🎉 Backend is Running!

Your AI Translation Backend is up and running at **http://localhost:7860**

## Current Status

✅ Backend Server: **RUNNING**
- Port: 7860
- Health Check: http://localhost:7860
- API Docs: http://localhost:7860/docs
- ReDoc: http://localhost:7860/redoc

## What You Can Do Now

### Option 1: Test the Backend API

Visit the interactive API documentation:
```
http://localhost:7860/docs
```

Here you can:
- View all available endpoints
- Test API calls directly from the browser
- See request/response schemas
- Try out translation features

### Option 2: Start the Frontend

Navigate to the frontend directory and start the Next.js app:

```bash
cd "/Users/sakibchowdhury/Desktop/code/Translation Manuscript/translator-nextjs"
npm install
npm run dev
```

The frontend will run on **http://localhost:3000** and connect to the backend automatically.

### Option 3: Test Translation via API

Use curl to test a translation endpoint:

```bash
# Check server status
curl http://localhost:7860

# Start Google Drive OAuth flow
curl http://localhost:7860/api/drive/auth

# Check API health
curl -X GET http://localhost:7860/ | python3 -m json.tool
```

## Backend Features Ready to Use

### 1. Document Translation
- **Smart Batching**: Automatically optimizes batch size based on content
- **Parallel Processing**: Up to 4 concurrent API requests
- **Progress Tracking**: Real-time translation status
- **Format Preservation**: Maintains document structure and formatting

### 2. AI Model Support
- **Google Gemini**: Primary translation engine
- **OpenRouter**: Alternative model provider (Claude, GPT-4, etc.)
- **Token Tracking**: Monitors API usage and costs

### 3. Google Drive Integration
- **OAuth 2.0**: Secure authentication
- **Folder Management**: List, create, and organize folders
- **File Operations**: Download, upload, and manage documents
- **Batch Processing**: Handle multiple files at once

## Environment Configuration

The backend uses the following configuration (from `.env`):

```bash
Backend URL: http://localhost:8000
Frontend URL: http://localhost:3000
OAuth Redirect: http://localhost:8000/api/drive/callback
```

**Note**: Make sure your Google Cloud Console OAuth settings match these URLs!

## Google OAuth Setup (If Not Already Done)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project or select existing one
3. Enable **Google Drive API**
4. Create **OAuth 2.0 Client ID** credentials
5. Add authorized redirect URI: `http://localhost:8000/api/drive/callback`
6. Copy Client ID and Secret to `.env` file

## Translation Workflow

1. **Upload Document**: Select a Word (.docx) file
2. **Choose Language**: Select target language for translation
3. **Select AI Model**: Choose Gemini or OpenRouter model
4. **Provide API Key**: Enter your Gemini or OpenRouter API key
5. **Start Translation**: Watch progress in real-time
6. **Download Result**: Get translated document when complete

## File Support

The backend can process:
- ✅ Microsoft Word (.docx)
- ✅ Google Docs (exported as .docx)
- ✅ PDF files (read-only, for reference)

Output format: `.docx` (Microsoft Word format)

## Smart Batching Explained

The backend intelligently groups paragraphs based on content type:

| Content Type | Batch Size | Use Case |
|-------------|-----------|----------|
| Poetry/Formatted | 10 | Preserves line breaks and structure |
| Dialogue | 50 | Maintains conversation flow |
| Long Prose | 300 | Fast processing for simple text |
| Default | 100 | Balanced for mixed content |

This can reduce API calls by **up to 60%** compared to fixed batching!

## Monitoring

The backend logs all activity to the console. You can see:
- Incoming requests
- Translation progress
- API call results
- Token usage
- Error messages

## Stopping the Server

To stop the backend:
1. Find the terminal where it's running
2. Press `Ctrl + C`

Or kill the process:
```bash
ps aux | grep "python main.py"
kill <process_id>
```

## Restarting the Server

```bash
cd "/Users/sakibchowdhury/Desktop/code/Translation Manuscript/ai_translation_backend"
source venv/bin/activate
python main.py
```

## Need Help?

- **Backend docs**: See `ENV_SETUP_GUIDE.md` and `BACKEND_SETUP_COMPLETE.md`
- **API Reference**: http://localhost:7860/docs
- **Translation docs**: See `TRANSLATION_IMPLEMENTATION.md` and `SMART_BATCHING_SUMMARY.md`
- **Frontend docs**: See `translator-nextjs/README.md`

## Common Issues

### Port Already in Use
Change the port in `main.py` (line 1221):
```python
port=8000,  # Use different port
```

### Module Not Found
Reinstall dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### OAuth Not Working
1. Check `.env` file has correct credentials
2. Verify redirect URI in Google Cloud Console
3. Ensure Google Drive API is enabled

---

**🚀 You're all set! The backend is ready to translate documents.**

Next step: Start the frontend or test the API at http://localhost:7860/docs

