# ☁️ Upload to Drive Feature

## Overview

The application now supports **uploading translated documents directly to Google Drive**! After translating documents, you can save them to a new folder in your Drive with one click.

## How It Works

```
1. Translate Documents
   ↓
2. Click "Upload to Drive"
   ↓
3. Enter Folder Name (auto-suggested)
   ↓
4. Folder Created in Drive
   ↓
5. All Files Uploaded
   ↓
6. Success! Open Folder Link
```

## User Flow

### Step 1: Translate Documents
- Select and translate one or more documents as usual
- Wait for translation to complete

### Step 2: Upload to Drive
- After translation completes, you'll see two buttons:
  - **📥 Download All** - Downloads files to your computer
  - **☁️ Upload to Drive** - Uploads files to Google Drive

### Step 3: Create Folder
- Click "Upload to Drive"
- A dialog appears with a suggested folder name like:
  ```
  Translated_Spanish_2025-10-08
  ```
- Edit the name or press OK to continue

### Step 4: Files Upload
- A new folder is created in your Google Drive
- All translated files are uploaded to that folder
- Progress shown in console

### Step 5: Open Folder
- Success message shows:
  - Number of files uploaded
  - Folder name
  - Link to the folder
- Option to open folder in new tab

## API Endpoints

### Create Folder

**Endpoint**: `POST /api/drive/create-folder`

**Request Body**:
```json
{
  "state": "session_state_from_oauth",
  "folderName": "Translated Documents",
  "parentFolderId": "optional_parent_id"
}
```

**Response**:
```json
{
  "folderId": "new_folder_id",
  "folderName": "Translated Documents",
  "webViewLink": "https://drive.google.com/drive/folders/..."
}
```

### Upload File

**Endpoint**: `POST /api/drive/upload`

**Request Body**:
```json
{
  "state": "session_state_from_oauth",
  "folderId": "target_folder_id",
  "fileName": "document_spanish_translated.docx",
  "fileData": "base64_encoded_file_content",
  "mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
}
```

**Response**:
```json
{
  "fileId": "uploaded_file_id",
  "fileName": "document_spanish_translated.docx",
  "webViewLink": "https://docs.google.com/document/d/..."
}
```

## Technical Implementation

### Backend (FastAPI)

1. **OAuth Scopes Updated**:
   ```python
   SCOPES = [
       'https://www.googleapis.com/auth/drive.file',  # Create & modify
       'https://www.googleapis.com/auth/drive.readonly',  # Read files
       'https://www.googleapis.com/auth/drive.metadata.readonly'  # Read metadata
   ]
   ```

2. **Folder Creation**:
   - Uses `service.files().create()` with `mimeType: 'application/vnd.google-apps.folder'`
   - Returns folder ID and web view link
   - Optional parent folder support

3. **File Upload**:
   - Decodes base64 file data
   - Uses `MediaIoBaseUpload` for memory-based upload
   - Resumable uploads for reliability
   - Returns file ID and direct link

### Frontend (Next.js/React)

1. **Upload Handler**:
   ```javascript
   const handleUploadAllToDrive = async () => {
     // 1. Prompt for folder name
     // 2. Create folder via API
     // 3. Upload each file
     // 4. Show success with link
     // 5. Optional: open folder
   }
   ```

2. **UI Components**:
   - "Upload to Drive" button in results header
   - Progress feedback during upload
   - Success notification with link
   - Option to open folder in new tab

## Security & Permissions

### Required OAuth Scopes

- `drive.file` - Create and modify files/folders created by the app
- `drive.readonly` - Read existing files
- `drive.metadata.readonly` - Read file metadata

### Permission Model

- App can only modify files/folders it creates
- Cannot modify or delete existing Drive files
- Read-only access to browse and download files
- Secure token-based authentication

## Usage Examples

### Example 1: Single File Translation & Upload

```
1. Select "document.docx" from Drive
2. Translate to Spanish
3. Click "Upload to Drive"
4. Enter folder name: "Spanish Translations"
5. File uploaded as "document_spanish_translated.docx"
6. Open folder to view
```

### Example 2: Batch Translation & Upload

```
1. Select 10 files from folder
2. Translate all to German
3. Click "Upload to Drive"
4. Enter folder name: "German_Batch_2025-10-08"
5. All 10 files uploaded
6. Open folder to access all files
```

## UI Features

### Results Section

After translation completes, you'll see:

```
📊 Translation Results            [📥 Download All] [☁️ Upload to Drive]

💡 Tip: Use "Upload to Drive" to save all translated files 
directly to your Google Drive in a new folder.

┌────────────────────────────────────────────────┐
│ ✅ document.docx                               │
│   Paragraphs: 45                               │
│   Total Tokens: 12,345                         │
│   Est. Cost: $0.0123                [Download] │
│                                                 │
│ 📖 Translated Content Preview                  │
│ ┌────────────────────────────────────────────┐ │
│ │ Translated paragraph 1...                  │ │
│ │ Translated paragraph 2...                  │ │
│ │ (scrollable)                               │ │
│ └────────────────────────────────────────────┘ │
│ 💬 2,345 words • 📄 45 paragraphs              │
│                                                 │
│ 🔍 View Processing Logs ▶                      │
└────────────────────────────────────────────────┘
```

## Benefits

### For Users

- ✅ **No Manual Uploads** - Skip downloading then re-uploading
- ✅ **Organized Storage** - Files saved in dated folders
- ✅ **Direct Access** - Open folder immediately in Drive
- ✅ **Backup** - Files automatically backed up to cloud
- ✅ **Sharing** - Easy to share folder with others

### For Developers

- ✅ **Clean API** - RESTful endpoints
- ✅ **Memory Efficient** - No temporary files on server
- ✅ **Error Handling** - Robust retry logic
- ✅ **Session Based** - Secure OAuth state management
- ✅ **Type Safe** - Pydantic models for validation

## Folder Naming Convention

Default folder names follow this pattern:
```
Translated_{language}_{date}

Examples:
- Translated_Spanish_2025-10-08
- Translated_German_2025-10-08
- Translated_Dutch_2025-10-08
```

You can customize the folder name when prompted!

## Limitations & Notes

### Current Limitations

- Folders created at Drive root (not in specific parent folders by default)
- Sequential upload (one file at a time)
- No progress bar during upload (console logs only)

### Future Enhancements

- [ ] Choose parent folder for new folder
- [ ] Parallel file uploads
- [ ] Upload progress bar
- [ ] Upload to existing folder option
- [ ] Batch folder organization
- [ ] Custom folder structure

## Troubleshooting

### "Not authenticated" error

**Issue**: Session expired or not connected to Drive

**Solution**: 
- Reconnect to Google Drive
- Check that authentication was successful
- Verify session state is valid

### "Failed to create folder" error

**Issue**: Missing permissions or network issue

**Solution**:
- Re-authenticate with Google Drive
- Check that OAuth scopes include `drive.file`
- Verify internet connection

### "Upload failed" error

**Issue**: File too large or network timeout

**Solution**:
- Check file size (recommended < 10MB)
- Try uploading files individually
- Check backend logs for detailed error

### Files uploaded but can't see them

**Issue**: Folder permissions or Drive sync delay

**Solution**:
- Wait a few seconds and refresh Drive
- Check the folder link provided
- Verify uploads in Drive activity log

## Testing

### Test Upload Flow

1. **Setup**:
   ```bash
   # Backend running on :8000
   # Frontend running on :3000
   # Connected to Google Drive
   ```

2. **Translate a test document**
3. **Click "Upload to Drive"**
4. **Enter folder name**: `Test_Upload_Folder`
5. **Verify**:
   - Folder created in Drive
   - File appears in folder
   - Can open and view file

### Verify Permissions

Check that your OAuth consent screen includes:
- View and manage Google Drive files created by this app
- View files in your Google Drive

## Support

For issues with uploads:
1. Check backend terminal logs
2. Verify OAuth scopes in Google Cloud Console
3. Test creating folder manually in Drive
4. Check network connectivity

---

**Happy Translating & Uploading! 🌐☁️**
