# 🌐 Next.js Drive Document Translator

A modern web application built with Next.js that translates documents from Google Drive using Google's Gemini AI. Process multiple documents at once with real-time progress tracking, all in memory with no server-side storage.

## ✨ Features

- 🔐 **Secure Google Drive OAuth** - Connect to your Google Drive securely
- 📁 **Flexible File Selection** - Browse folders or paste Drive links
- 🔄 **Batch Translation** - Translate multiple documents at once
- 🌍 **Multi-Language Support** - Translate to Spanish, German, Dutch, French, Italian, Portuguese, and more
- 📊 **Real-Time Analytics** - Track token usage and translation progress
- 💾 **Memory-Based Processing** - All processing done in memory, no files saved to disk
- 🎯 **Smart Batching** - Efficient API usage with intelligent paragraph batching
- ☁️ **Upload to Drive** - Save translated documents directly to Google Drive
- 📖 **Content Preview** - View translated text in the UI before downloading

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm 9+
- Google Cloud Project with Drive API enabled
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   cd nextjs-drive-translator
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   
   Create a `.env.local` file in the root directory:
   
   ```env
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_PROJECT_ID=your_google_project_id
   NEXT_PUBLIC_BASE_URL=http://localhost:3000
   SESSION_SECRET=your_random_secret_string
   ```

4. **Run the development server**
   ```bash
   npm run dev
   ```

5. **Open your browser**
   
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🔧 Configuration

### Google Cloud Setup

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Drive API**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Drive API"
   - Click "Enable"

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - For local development: `http://localhost:3000/api/drive/callback`
     - For production: `https://yourdomain.com/api/drive/callback`
   - Copy the Client ID and Client Secret

4. **Get Gemini API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/apikey)
   - Sign in with your Google account
   - Create or copy your API key

### Supported File Types

- Google Docs (`.gdoc`)
- Microsoft Word (`.docx`)
- PDF (`.pdf`)

## 📖 Usage

1. **Enter API Key**
   - Paste your Gemini API key in the configuration section
   - Your key is only used locally and never stored

2. **Connect to Google Drive**
   - Click "Connect to Google Drive"
   - Authorize the application in the popup window
   - Return to the application

3. **Select Files**
   - **Option A**: Paste a Google Drive folder or file link
   - **Option B**: Browse your Drive folders and select files
   - Select one or multiple files to translate

4. **Configure Translation**
   - Choose target language
   - Select Gemini model (Flash for speed, Pro for quality)
   - Click "Start Translation"

5. **Download Results**
   - Download individual translated documents
   - Or download all as a batch

## 🏗️ Project Structure

```
nextjs-drive-translator/
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   ├── drive/
│   │   │   │   ├── auth/route.js       # OAuth initiation
│   │   │   │   ├── callback/route.js   # OAuth callback
│   │   │   │   ├── folders/route.js    # List folders
│   │   │   │   ├── files/route.js      # List files
│   │   │   │   ├── download/route.js   # Download files
│   │   │   │   └── logout/route.js     # Disconnect
│   │   │   └── translate/route.js      # Translation endpoint
│   │   ├── globals.css
│   │   ├── layout.js
│   │   └── page.js                     # Main UI
│   └── lib/
│       ├── driveClient.js              # Drive API utilities
│       └── translator.js               # Translation logic
├── next.config.js
├── package.json
├── tailwind.config.js
└── README.md
```

## 🔒 Security & Privacy

- **OAuth 2.0**: Secure authentication with Google
- **No Server Storage**: Documents processed entirely in memory
- **Session Cookies**: Temporary authentication tokens (7-day expiry)
- **Client-Side API Key**: Gemini API key never sent to the server
- **HTTPS Ready**: Production deployment uses secure connections

## 🎨 Customization

### Adding More Languages

Edit the language options in `src/app/page.js`:

```javascript
<select value={language} onChange={(e) => setLanguage(e.target.value)}>
  <option>Spanish</option>
  <option>Your Language</option>
</select>
```

### Adjusting Batch Size

Modify the `BATCH_SIZE` constant in `src/lib/translator.js`:

```javascript
const BATCH_SIZE = 10; // Number of paragraphs per API request
```

### Changing Models

Add more Gemini models in `src/app/page.js`:

```javascript
<select value={model} onChange={(e) => setModel(e.target.value)}>
  <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
  <option value="your-model">Your Model</option>
</select>
```

## 🚀 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project in [Vercel](https://vercel.com)
3. Add environment variables in project settings
4. Deploy!

### Docker

```bash
# Build image
docker build -t nextjs-drive-translator .

# Run container
docker run -p 3000:3000 \
  -e GOOGLE_CLIENT_ID=your_id \
  -e GOOGLE_CLIENT_SECRET=your_secret \
  -e GOOGLE_PROJECT_ID=your_project \
  -e NEXT_PUBLIC_BASE_URL=http://localhost:3000 \
  nextjs-drive-translator
```

## 🐛 Troubleshooting

### "Not authenticated" error
- Ensure cookies are enabled in your browser
- Check that OAuth redirect URI matches exactly in Google Cloud Console

### "Failed to download file" error
- Verify the file is not corrupted
- Ensure you have read permissions for the file
- Check that the file type is supported

### Translation fails
- Verify your Gemini API key is valid
- Check your API quota hasn't been exceeded
- Ensure the document contains translatable text

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions

## 🙏 Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Powered by [Google Gemini AI](https://ai.google.dev/)
- Uses [Google Drive API](https://developers.google.com/drive)

---

Made with ❤️ using Next.js and Google AI
