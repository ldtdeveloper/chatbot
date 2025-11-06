# Website Voice Assistant

A simple voice-powered AI assistant that connects directly to OpenAI's Realtime API.

## Quick Start

```bash
php -S localhost:8000
```

Open: `http://localhost:8000`

## How It Works

- **index.php** - UI with microphone button
- **app.js** - Direct WebSocket connection to OpenAI Realtime API
- Auto-connects on page load
- Click mic to speak
- Receives audio responses in real-time

## Features

✅ Direct browser connection to OpenAI  
✅ Voice input/output  
✅ Live transcription  
✅ Real-time audio streaming  
✅ Server VAD (Voice Activity Detection)  

## Configuration

Update API key in `app.js` (line 5)
