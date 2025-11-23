# Dual Source Flow - Manual Upload + Google Drive

The application now supports two ways to provide documents for translation:

## 🎯 Flow Overview

### Step 1: Choose Document Source
Users see **two options**:

1. **📤 Upload Files** - Upload .docx files directly from computer
2. **☁️ Google Drive** - Connect to Google Drive and select files

### Step 2: API Configuration
After choosing a source, configure the AI service:
- Select **Google Gemini** or **OpenRouter**
- Enter API key

### Step 3: File Selection
- **Upload Flow**: Review uploaded files, select/deselect
- **Drive Flow**: Choose input method (paste link or browse folders), then select files

### Step 4/5: Translation Settings
- Select target language
- Choose AI model
- Start translation

---

## 📤 Manual Upload Flow

### User Experience
```
Step 1: Upload Files
  ↓ (User clicks "Choose Files" and selects .docx files)
Step 2: API Configuration  
  ↓ (User selects service and enters API key)
Step 3: Uploaded Files
  ↓ (Files are shown with checkboxes, all selected by default)
Step 4: Translation Settings
  ↓ (User configures language and model)
Translation begins!
```

### Key Features
✅ **Instant upload** - Files are read and converted to base64 immediately
✅ **No backend needed** - Files stay in browser memory until translation
✅ **Multiple files** - Upload multiple .docx files at once
✅ **File validation** - Only .docx files are accepted
✅ **Auto-selection** - All uploaded files are selected by default
✅ **File size display** - Shows file size in KB

### Technical Implementation

**File Upload Handler:**
```javascript
const handleManualUpload = (event) => {
  // Filter for .docx files only
  const docxFiles = Array.from(event.target.files).filter(file => 
    file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
    file.name.endsWith('.docx')
  )
  
  // Convert to base64 and store
  // Each file gets: id, name, size, mimeType, data (base64)
  // Auto-select all uploaded files
  // Set sourceMethod to 'upload'
}
```

**Translation Logic:**
```javascript
if (sourceMethod === 'upload') {
  // File is already in base64, use directly
  fileData = file.data
} else {
  // Download from Google Drive
  fileData = downloadData.data
}

// Send to translation API
```

---

## ☁️ Google Drive Flow

### User Experience
```
Step 1: Connect to Google Drive
  ↓ (OAuth flow, user authorizes)
Step 2: API Configuration  
  ↓ (User selects service and enters API key)
Step 3: Choose Input Method
  ↓ (User pastes link OR browses folders)
Step 4: Select Drive Files
  ↓ (Files are shown with checkboxes)
Step 5: Translation Settings
  ↓ (User configures language and model)
Translation begins!
```

### Key Features
✅ **OAuth connection** - Secure Google Drive authorization
✅ **Two input methods** - Paste link OR browse folders
✅ **Session persistence** - Connection survives page refresh
✅ **Folder browsing** - List all Drive folders
✅ **Link parsing** - Extract file/folder ID from Drive links
✅ **File downloading** - Download files from Drive via backend

---

## 🎨 UI Components

### Step 1: Source Selection
**Visual Design:**
- Two side-by-side cards (responsive grid)
- **Left card**: Blue gradient, upload icon 📤
- **Right card**: Green gradient, cloud icon ☁️
- Both cards have hover effects and clear CTAs

### Source Status Card
Once a source is selected, shows:
- Source icon (📤 or ☁️)
- Source name
- Status (file count or "Connected")
- "Change Source" button

### File Selection Views

**Manual Upload:**
```
📄 Step 3: Uploaded Files
┌─────────────────────────────────┐
│ ☑️ document1.docx (125 KB)      │
│ ☑️ document2.docx (89 KB)       │
│ ☑️ document3.docx (203 KB)      │
└─────────────────────────────────┘
Selected 3 of 3 file(s)
```

**Google Drive:**
```
📄 Step 4: Select Drive Files
┌─────────────────────────────────┐
│ ☑️ Project Proposal (Google Doc)│
│ ☑️ Meeting Notes (Word Doc)     │
│ □  Budget 2024 (PDF)            │
└─────────────────────────────────┘
Selected 2 of 3 file(s)
```

---

## 🔄 State Management

### New State Variables
```javascript
const [sourceMethod, setSourceMethod] = useState('')  // 'upload' or 'drive'
const [uploadedFiles, setUploadedFiles] = useState([])  // Manual uploads
const [authenticated, setAuthenticated] = useState(false)  // Drive auth
const [files, setFiles] = useState([])  // Drive files
```

### Source Switching
Users can switch sources at any time:
```javascript
// Click "Change Source" button
// → Clears current source
// → Returns to Step 1 (source selection)
// → Resets file selections
```

---

## 🚀 Translation Process

### Unified Translation Flow
Both sources use the **same translation logic**:

```javascript
for (const fileId of selectedFiles) {
  // Get file from appropriate source
  const file = sourceMethod === 'upload' 
    ? uploadedFiles.find(f => f.id === fileId)
    : files.find(f => f.id === fileId)
  
  // Get file data
  let fileData
  if (sourceMethod === 'upload') {
    fileData = file.data  // Already base64
  } else {
    // Download from Drive
    fileData = await downloadFromDrive(fileId)
  }
  
  // Translate (same API call for both)
  const result = await translateAPI({
    fileData,
    fileName: file.name,
    language,
    model,
    apiKey
  })
}
```

---

## 📊 Comparison

| Feature | Manual Upload | Google Drive |
|---------|---------------|--------------|
| **Setup** | Instant | Requires OAuth |
| **File Source** | Local computer | Google Drive |
| **Steps** | 4 | 5 |
| **Backend Required** | No (only for translation) | Yes (for Drive API) |
| **Session Persistence** | No | Yes (localStorage) |
| **File Limit** | Browser memory | Drive API limits |
| **Supported Formats** | .docx only | .docx, Google Docs |
| **Privacy** | Files never leave browser | Downloaded temporarily |

---

## 💡 User Benefits

### Manual Upload
- ✅ **Fastest** - No authentication needed
- ✅ **Offline capable** - Works without internet (until translation)
- ✅ **Privacy** - Files stay in browser
- ✅ **Simple** - Just drag and drop

### Google Drive
- ✅ **Convenient** - No need to download files first
- ✅ **Organization** - Browse folders directly
- ✅ **Collaboration** - Access shared files
- ✅ **Integration** - Upload results back to Drive

---

## 🎯 Recommended Use Cases

### Use Manual Upload When:
- You have files on your local machine
- You want quick, one-time translations
- You don't want to connect external accounts
- You're working with sensitive documents

### Use Google Drive When:
- Files are already in Google Drive
- You're translating many files from the same location
- You want to upload results back to Drive
- You're working with Google Docs

---

## 🔧 Technical Details

### File Object Structure

**Manual Upload:**
```javascript
{
  id: "upload-1234567890-0.123",
  name: "document.docx",
  size: 102400,  // bytes
  mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  data: "UEsDBBQABgAIAAAAI..." // base64
}
```

**Google Drive:**
```javascript
{
  id: "1a2b3c4d5e6f7g8h9i0j",
  name: "document.docx",
  mimeType: "application/vnd.google-apps.document",
  size: "102400",
  modifiedTime: "2024-01-01T12:00:00.000Z"
  // data fetched separately via download API
}
```

### API Calls

**Manual Upload:**
- No Drive API calls needed
- Only translation API call

**Google Drive:**
- `/api/drive/auth` - Initiate OAuth
- `/api/drive/callback` - Handle OAuth response
- `/api/drive/folders` - List folders
- `/api/drive/files` - List files in folder/link
- `/api/drive/download` - Download file content
- Translation API call

---

## 🔐 Security

### Manual Upload
- Files processed entirely in browser until translation
- No file storage on servers
- Base64 sent to translation API (HTTPS)

### Google Drive
- OAuth 2.0 authentication
- Session tokens stored in localStorage
- Backend sessions stored in memory
- No permanent file storage

---

## 🎨 Design Philosophy

**Goal:** Give users choice without complexity

**Approach:**
1. **Clear separation** - Two distinct paths, not mixed
2. **Visual clarity** - Icons and colors differentiate sources
3. **Smart defaults** - Auto-select uploaded files
4. **Easy switching** - Can change source anytime
5. **Unified experience** - Same translation UI for both

**Result:** Users feel in control while the app handles complexity behind the scenes.

---

## 🚀 Future Enhancements

Possible additions:
- 📁 Drag & drop file upload
- 🌐 Dropbox/OneDrive integration
- 📎 URL-based document import
- 💾 Save translation history
- 🔗 Share translation links
- 📊 Batch upload progress indicator

---

## ✨ Summary

The dual-source flow provides:
- **Flexibility** - Upload or connect to Drive
- **Simplicity** - Clear 4-5 step process
- **Speed** - Manual upload is instant
- **Integration** - Drive connection for power users
- **Unified UX** - Same translation experience regardless of source

Perfect balance of convenience and power! 🎯

