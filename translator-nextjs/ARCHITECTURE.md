# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT (Browser)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    React UI (page.js)                     │  │
│  │  - API Key Input                                          │  │
│  │  - Drive Connection Status                                │  │
│  │  - File Selection Interface                               │  │
│  │  - Translation Controls                                   │  │
│  │  - Progress Tracking                                      │  │
│  │  - Download Management                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              │ fetch()                           │
│                              ▼                                   │
└─────────────────────────────────────────────────────────────────┘
                               │
                               │ HTTP/HTTPS
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NEXT.JS SERVER (API Routes)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────┐      ┌─────────────────────────────┐   │
│  │  Drive API Routes  │      │   Translation Route         │   │
│  ├────────────────────┤      ├─────────────────────────────┤   │
│  │ /api/drive/auth    │      │ /api/translate              │   │
│  │ /api/drive/callback│      │  - Process documents        │   │
│  │ /api/drive/folders │      │  - Batch paragraphs         │   │
│  │ /api/drive/files   │      │  - Call Gemini API          │   │
│  │ /api/drive/download│      │  - Generate DOCX            │   │
│  │ /api/drive/logout  │      │  - Return translated file   │   │
│  └────────────────────┘      └─────────────────────────────┘   │
│           │                              │                       │
│           │                              │                       │
└───────────┼──────────────────────────────┼───────────────────────┘
            │                              │
            ▼                              ▼
   ┌─────────────────┐          ┌──────────────────┐
   │  Google Drive   │          │   Gemini API     │
   │      API        │          │  (Translation)   │
   └─────────────────┘          └──────────────────┘
```

## Data Flow

### 1. Authentication Flow

```
User clicks "Connect"
    │
    ▼
GET /api/drive/auth
    │
    ▼
Generate OAuth URL
    │
    ▼
Redirect to Google
    │
    ▼
User authorizes
    │
    ▼
Redirect to /api/drive/callback
    │
    ▼
Exchange code for tokens
    │
    ▼
Store tokens in HTTP-only cookie
    │
    ▼
Redirect to homepage
    │
    ▼
User authenticated ✓
```

### 2. File Selection Flow (Link Method)

```
User enters Drive link
    │
    ▼
Extract ID from link
    │
    ▼
GET /api/drive/files?driveLink=...
    │
    ▼
Verify authentication (read cookie)
    │
    ▼
Call Google Drive API
    │
    ▼
Check if file or folder
    │
    ├─ File  ──────────────┐
    │                      ▼
    │              Return single file
    │                      │
    └─ Folder ─────────────┼──────┐
                           │      │
                List files in folder
                           │      │
                           ▼      ▼
                    Return file list
                           │
                           ▼
                    Display in UI
```

### 3. File Selection Flow (Browse Method)

```
User selects "Browse"
    │
    ▼
GET /api/drive/folders
    │
    ▼
Query Drive for folders
    │
    ▼
Display folder dropdown
    │
    ▼
User selects folder
    │
    ▼
GET /api/drive/files?folderId=...
    │
    ▼
List files in folder
    │
    ▼
Display file checkboxes
```

### 4. Translation Flow

```
User selects files + language + model
    │
    ▼
User clicks "Start Translation"
    │
    ▼
For each selected file:
    │
    ├─ Step 1: Download
    │    │
    │    ▼
    │  GET /api/drive/download?fileId=...&mimeType=...
    │    │
    │    ▼
    │  Authenticate via cookie
    │    │
    │    ▼
    │  Download from Google Drive
    │    │
    │    ▼
    │  Return file as base64
    │    │
    │    ▼
    ├─ Step 2: Translate
    │    │
    │    ▼
    │  POST /api/translate
    │    │
    │    ├─ Parse document
    │    │  Extract paragraphs
    │    │
    │    ├─ Batch paragraphs (10 per batch)
    │    │
    │    ├─ For each batch:
    │    │    │
    │    │    ├─ Create prompt
    │    │    ├─ Call Gemini API
    │    │    ├─ Parse JSON response
    │    │    └─ Store translations
    │    │
    │    ├─ Create new DOCX
    │    │  Add translated paragraphs
    │    │
    │    └─ Return translated document
    │         + logs + stats
    │         (as base64)
    │
    └─ Step 3: Store in memory
         │
         ▼
       Update UI with result
         │
         ▼
       Ready for download
```

### 5. Download Flow

```
User clicks "Download"
    │
    ▼
Convert base64 to Blob
    │
    ▼
Create download link
    │
    ▼
Trigger browser download
    │
    ▼
File saved to user's device
```

## Component Architecture

### Frontend Components (page.js)

```javascript
Home Component
├─ State Management
│  ├─ authenticated
│  ├─ loading
│  ├─ inputMethod
│  ├─ driveLink
│  ├─ folders
│  ├─ selectedFolder
│  ├─ files
│  ├─ selectedFiles
│  ├─ language
│  ├─ model
│  ├─ apiKey
│  ├─ translating
│  ├─ progress
│  └─ results
│
├─ Effects
│  └─ Check authentication on mount
│
├─ Event Handlers
│  ├─ handleConnect()
│  ├─ handleDisconnect()
│  ├─ loadFolders()
│  ├─ loadFilesFromLink()
│  ├─ loadFilesFromFolder()
│  ├─ handleFolderChange()
│  ├─ handleFileSelect()
│  ├─ handleSelectAll()
│  ├─ handleTranslate()
│  ├─ handleDownload()
│  └─ handleDownloadAll()
│
└─ UI Sections
   ├─ Header
   ├─ API Key Input
   ├─ Drive Connection
   ├─ Input Method Selection
   ├─ File Selection
   ├─ Translation Settings
   └─ Results Display
```

### Backend Architecture

```
src/
├─ app/
│  ├─ api/
│  │  ├─ drive/
│  │  │  ├─ auth/route.js
│  │  │  │  └─ generateAuthUrl()
│  │  │  ├─ callback/route.js
│  │  │  │  └─ exchangeCodeForTokens()
│  │  │  ├─ folders/route.js
│  │  │  │  └─ listFolders()
│  │  │  ├─ files/route.js
│  │  │  │  └─ listFiles()
│  │  │  ├─ download/route.js
│  │  │  │  └─ downloadFile()
│  │  │  └─ logout/route.js
│  │  │     └─ clearCookies()
│  │  └─ translate/route.js
│  │     └─ translateDocument()
│  │
│  ├─ page.js (UI)
│  ├─ layout.js
│  └─ globals.css
│
└─ lib/
   ├─ driveClient.js
   │  ├─ createOAuth2Client()
   │  ├─ getDriveService()
   │  └─ extractDriveId()
   │
   └─ translator.js
      ├─ translateDocument()
      ├─ createBatchPrompt()
      ├─ callGeminiAPI()
      ├─ parseStructuredResponse()
      └─ createDocxFromContent()
```

## Security Architecture

```
┌─────────────────────────────────────────┐
│            Security Layers              │
├─────────────────────────────────────────┤
│                                         │
│  1. HTTPS (Production)                  │
│     └─ Encrypted transport              │
│                                         │
│  2. OAuth 2.0                           │
│     ├─ Authorization Code Flow          │
│     ├─ State parameter validation       │
│     └─ Secure token exchange            │
│                                         │
│  3. HTTP-only Cookies                   │
│     ├─ Cannot be accessed by JS         │
│     ├─ Secure flag in production        │
│     ├─ SameSite protection              │
│     └─ 7-day expiration                 │
│                                         │
│  4. API Key Handling                    │
│     ├─ Client-side only                 │
│     ├─ Never sent to our server         │
│     └─ Not stored anywhere              │
│                                         │
│  5. Environment Variables               │
│     ├─ Server-side only                 │
│     ├─ Not exposed to client            │
│     └─ .env.local (gitignored)          │
│                                         │
│  6. Memory-only Processing              │
│     ├─ No disk writes                   │
│     ├─ No file storage                  │
│     └─ Automatic cleanup                │
│                                         │
└─────────────────────────────────────────┘
```

## Deployment Architecture

### Development
```
localhost:3000
├─ Next.js Dev Server
├─ Hot Module Replacement
├─ Environment: .env.local
└─ Redirect URI: http://localhost:3000/api/drive/callback
```

### Production (Vercel)
```
yourdomain.com
├─ Vercel Edge Network
├─ Serverless Functions (API Routes)
├─ Environment Variables (Dashboard)
├─ HTTPS by default
└─ Redirect URI: https://yourdomain.com/api/drive/callback
```

## Performance Considerations

### Optimization Strategies

1. **API Batching**
   - Paragraphs grouped in batches of 10
   - Reduces API calls by 90%

2. **Retry Logic**
   - Automatic retries on failure
   - Exponential backoff (2 seconds)

3. **Memory Management**
   - Stream processing where possible
   - Immediate cleanup after download

4. **Caching**
   - OAuth tokens cached in cookies
   - Folder list can be cached client-side

5. **Parallel Processing**
   - Multiple files processed sequentially
   - Each batch processed in parallel (future enhancement)

## Error Handling

```
┌─────────────────────────────────────┐
│         Error Categories            │
├─────────────────────────────────────┤
│                                     │
│  1. Authentication Errors           │
│     ├─ No tokens → Redirect to auth │
│     ├─ Expired tokens → Re-auth     │
│     └─ Invalid tokens → Clear & retry│
│                                     │
│  2. API Errors                      │
│     ├─ Rate limit → Retry with delay│
│     ├─ Invalid request → Show error │
│     └─ Network error → Retry        │
│                                     │
│  3. File Errors                     │
│     ├─ Not found → Skip & continue  │
│     ├─ Permission denied → Show msg │
│     └─ Corrupted → Mark as failed   │
│                                     │
│  4. Translation Errors              │
│     ├─ API key invalid → Alert user │
│     ├─ Quota exceeded → Show error  │
│     └─ Parse error → Fallback method│
│                                     │
└─────────────────────────────────────┘
```

## Technology Stack

```
Frontend
├─ React 18
├─ Next.js 14 (App Router)
├─ Tailwind CSS
└─ Native Fetch API

Backend
├─ Next.js API Routes
├─ Node.js Runtime
└─ Serverless Functions

APIs & Services
├─ Google Drive API v3
├─ Google OAuth 2.0
└─ Google Generative AI (Gemini)

Document Processing
├─ docx (DOCX creation)
└─ Buffer (Memory operations)

Development
├─ ESLint
├─ PostCSS
└─ Autoprefixer
```

This architecture provides a scalable, secure, and maintainable solution for document translation with Google Drive integration.
