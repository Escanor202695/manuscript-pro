# Migration Guide: @google/generative-ai → @google/genai

## Overview

This project has been updated to use the new `@google/genai` package (v1.22.0) instead of the older `@google/generative-ai` package.

## What Changed

### 1. Package Update

**Before:**
```json
"@google/generative-ai": "^0.1.3"
```

**After:**
```json
"@google/genai": "^1.22.0"
```

### 2. Import Statement

**Before:**
```javascript
import { GoogleGenerativeAI } from '@google/generative-ai';
```

**After:**
```javascript
import { GoogleGenAI } from '@google/genai';
```

### 3. Client Initialization

**Before:**
```javascript
const genAI = new GoogleGenerativeAI(apiKey);
```

**After:**
```javascript
const genAI = new GoogleGenAI({ apiKey: apiKey });
```

### 4. API Call Structure

**Before:**
```javascript
const geminiModel = genAI.getGenerativeModel({ 
  model,
  generationConfig: {
    temperature: 0.0,
    responseMimeType: "application/json"
  }
});

const result = await geminiModel.generateContent(prompt);
const response = await result.response;
const text = response.text();
```

**After:**
```javascript
const response = await genAI.models.generateContent({
  model: model,
  contents: prompt,
  config: {
    temperature: 0.0,
    responseMimeType: "application/json"
  }
});

const text = response.text;
```

### 5. Response Access

**Before:**
```javascript
const result = await geminiModel.generateContent(prompt);
const response = await result.response;
const text = response.text();  // Method call
```

**After:**
```javascript
const response = await genAI.models.generateContent({...});
const text = response.text;  // Property access
```

### 6. Usage Metadata

**Before:**
```javascript
const usage = response.usageMetadata;
const inputTokens = usage.promptTokenCount;
const outputTokens = usage.candidatesTokenCount;
const totalTokens = usage.totalTokenCount;
```

**After:**
```javascript
const usage = response.usageMetadata || {};
const inputTokens = usage.promptTokenCount || 0;
const outputTokens = usage.candidatesTokenCount || 0;
const totalTokens = usage.totalTokenCount || 0;
```

## Benefits of New API

1. **Simplified Structure** - Fewer nested objects
2. **Direct Response Access** - No need to await multiple times
3. **More Intuitive** - Property access instead of method calls
4. **Better Performance** - Streamlined API calls
5. **Future-Proof** - Latest official SDK

## Migration Steps for Your Project

If you're updating your own code:

1. **Update package.json**
   ```bash
   npm uninstall @google/generative-ai
   npm install @google/genai
   ```

2. **Update imports** in all files
   ```javascript
   // Change this:
   import { GoogleGenerativeAI } from '@google/generative-ai';
   
   // To this:
   import { GoogleGenAI } from '@google/genai';
   ```

3. **Update initialization**
   ```javascript
   // Change this:
   const genAI = new GoogleGenerativeAI(apiKey);
   
   // To this:
   const genAI = new GoogleGenAI({ apiKey: apiKey });
   ```

4. **Update API calls**
   - Replace `getGenerativeModel()` with direct `models.generateContent()`
   - Move model name into the generateContent call
   - Pass config directly as object
   - Access response.text as property, not method

5. **Test thoroughly**
   - Test all translation features
   - Verify token counting works
   - Check error handling

## Files Modified

- `src/lib/translator.js` - Main translation logic
- `package.json` - Dependency update

## Compatibility

- **Node.js**: 18+
- **Next.js**: 14+
- **@google/genai**: 1.22.0+

## Troubleshooting

### Issue: "Cannot find module '@google/genai'"

**Solution:**
```bash
npm install
```

### Issue: "genAI.models is not a function"

**Solution:** Make sure you're using the correct initialization:
```javascript
const genAI = new GoogleGenAI({ apiKey: apiKey });
```

### Issue: "response.text is undefined"

**Solution:** The new API returns `.text` as a property, not a method:
```javascript
const text = response.text;  // Not response.text()
```

### Issue: API returns error about responseMimeType

**Solution:** Ensure config is passed correctly:
```javascript
config: {
  temperature: 0.0,
  responseMimeType: "application/json"
}
```

## API Reference

### GoogleGenAI Constructor

```javascript
new GoogleGenAI({ apiKey: string })
```

### generateContent Method

```javascript
genAI.models.generateContent({
  model: string,           // e.g., "gemini-2.5-flash"
  contents: string,        // Your prompt
  config: {
    temperature: number,   // 0.0 to 1.0
    responseMimeType: string // "application/json" or "text/plain"
  }
})
```

### Response Object

```javascript
{
  text: string,
  usageMetadata: {
    promptTokenCount: number,
    candidatesTokenCount: number,
    totalTokenCount: number
  }
}
```

## Need Help?

- Check the main [README.md](README.md) for setup instructions
- Review [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Open an issue on GitHub if you encounter problems

## Version History

- **v1.0.0** - Initial release with @google/generative-ai
- **v1.1.0** - Migrated to @google/genai (current)

---

Last updated: 2025-01-08
