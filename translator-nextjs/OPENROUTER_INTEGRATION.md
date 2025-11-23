# 🌐 OpenRouter Integration

## Overview

The application now supports **two AI services** for translation:
1. **Google Gemini** - Google's native AI models
2. **OpenRouter** - Access to Claude, GPT-4, Llama, and 100+ other models

## Features

### Service Selection
Users can switch between services with a single click in the UI.

### Supported Models

#### Google Gemini
- Gemini 2.5 Flash (Recommended - Fast & Cheap)
- Gemini 2.0 Flash
- Gemini 1.5 Flash
- Gemini 1.5 Pro (Best Quality)

#### OpenRouter
- **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus
- **OpenAI**: GPT-4 Turbo, GPT-4o
- **Meta**: Llama 3.1 70B Instruct
- **Google**: Gemini Pro 1.5

## How to Use

### Step 1: Choose Service

In the **API Configuration** section:
- Click **🤖 Google Gemini** for Gemini models
- Click **🌐 OpenRouter** for OpenRouter models

### Step 2: Enter API Key

**For Gemini:**
1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Create API key
3. Paste in the application

**For OpenRouter:**
1. Visit [OpenRouter Dashboard](https://openrouter.ai/keys)
2. Sign up/login
3. Create API key
4. Paste in the application

### Step 3: Select Model

The model dropdown automatically updates based on your service choice:
- **Gemini**: Shows Gemini models
- **OpenRouter**: Shows Claude, GPT-4, Llama, etc.

### Step 4: Translate

Click "Start Translation" - the backend automatically routes to the correct service!

## Technical Implementation

### Backend (`main.py`)

#### Dual Service Support

```python
@app.post("/api/translate")
async def translate_document(request: TranslateRequest):
    if request.service == "openrouter":
        result = await translate_document_openrouter(...)
    else:  # gemini
        result = await translate_document_gemini(...)
    return result
```

#### OpenRouter API Call

```python
async def call_openrouter_batch_api(session, prompt, model, api_key, logs):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("OPENROUTER_REFERER"),
        "X-Title": "DriveTranslator"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }
    
    async with session.post(url, headers=headers, json=payload) as resp:
        data = await resp.json()
        return parse_response(data)
```

#### Gemini API Call

```python
def call_gemini_batch_api(client, prompt, model, logs):
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            response_mime_type="application/json"
        )
    )
    return parse_response(response)
```

### Frontend (`page.js`)

#### Service State

```javascript
const [service, setService] = useState('gemini')  // 'gemini' or 'openrouter'
const [model, setModel] = useState('gemini-2.5-flash')
```

#### Auto Model Update

```javascript
useEffect(() => {
  if (service === 'gemini') {
    setModel('gemini-2.5-flash')
  } else {
    setModel('anthropic/claude-3.5-sonnet')
  }
}, [service])
```

#### Service Selector UI

```jsx
<div className="grid grid-cols-2 gap-3">
  <button onClick={() => setService('gemini')}>
    🤖 Google Gemini
  </button>
  <button onClick={() => setService('openrouter')}>
    🌐 OpenRouter
  </button>
</div>
```

#### Dynamic Model Selection

```jsx
<select value={model} onChange={(e) => setModel(e.target.value)}>
  {service === 'gemini' ? (
    // Gemini models
  ) : (
    // OpenRouter models
  )}
</select>
```

## API Comparison

| Feature | Google Gemini | OpenRouter |
|---------|--------------|------------|
| **Models** | Gemini family | 100+ models |
| **Pricing** | ~$0.000001/token | Varies by model |
| **Speed** | Very fast | Model-dependent |
| **API Key** | Free tier available | Credits required |
| **Best For** | Quick translations | Model flexibility |

## Model Recommendations

### For Speed
- **Gemini 2.5 Flash** (Gemini)
- **Claude 3.5 Sonnet** (OpenRouter)
- **GPT-4o** (OpenRouter)

### For Quality
- **Gemini 1.5 Pro** (Gemini)
- **Claude 3 Opus** (OpenRouter)
- **GPT-4 Turbo** (OpenRouter)

### For Cost
- **Gemini 2.5 Flash** (Cheapest)
- **Llama 3.1 70B** (OpenRouter - Open source)

## Benefits of OpenRouter

### Model Diversity
- Access Claude, GPT-4, Llama, and more
- Switch models without changing API keys
- Compare results across different models

### Flexibility
- Choose best model for your use case
- Balance cost vs. quality
- Access latest models quickly

### Unified Billing
- One API key for all models
- Transparent pricing
- Usage tracking dashboard

## Configuration

### Backend Environment

Add to `backend/.env`:
```env
OPENROUTER_REFERER=https://yourdomain.com
```

### Headers Required

OpenRouter requires:
- `Authorization: Bearer {api_key}`
- `HTTP-Referer` - Your domain (for analytics)
- `X-Title` - App name (optional)

## Usage Statistics

Both services provide token usage:
- **Input tokens** - Prompt size
- **Output tokens** - Generated text
- **Total tokens** - Sum of both
- **Cost estimation** - Calculated automatically

## Error Handling

### Retry Logic
- 3 attempts for each batch
- 2-second delay between retries
- Fallback content on complete failure

### Service-Specific Errors

**Gemini**:
- Rate limiting
- Quota exceeded
- Invalid API key

**OpenRouter**:
- Insufficient credits
- Model unavailable
- Rate limiting

## Testing

### Test Gemini
1. Select "Google Gemini"
2. Enter Gemini API key
3. Choose any Gemini model
4. Translate

### Test OpenRouter
1. Select "OpenRouter"
2. Enter OpenRouter API key
3. Choose any available model
4. Translate

## Logging

Service type is logged in translation:
```
[START] Batch translation started for language: Spanish
[INFO] Service: Gemini AI  (or OpenRouter AI)
[INFO] Using model: gemini-2.5-flash (or anthropic/claude-3.5-sonnet)
```

## Future Enhancements

- [ ] Add more OpenRouter models
- [ ] Model comparison mode
- [ ] Cost comparison tool
- [ ] A/B testing between services
- [ ] Automatic failover
- [ ] Best model recommendation

## Get Started

1. **Choose your service** in the UI
2. **Get API key** from the respective platform
3. **Select a model** from the dropdown
4. **Start translating!**

Both services use the same translation logic and produce identical output quality! 🎉

---

**Supported By:**
- Google Gemini API
- OpenRouter API
- aiohttp for async HTTP requests

