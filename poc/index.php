<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Website Assistant - Voice Chat</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 600px;
            padding: 40px;
        }

        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
            text-align: center;
        }

        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
            text-align: center;
        }

        .status {
            background: #f5f5f5;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 30px;
            font-size: 14px;
            color: #555;
            text-align: center;
            font-weight: 600;
        }

        .status.disconnected {
            background: #fee;
            color: #c33;
        }

        .status.connected {
            background: #efe;
            color: #3c3;
        }

        .status.recording {
            background: #ffe;
            color: #cc3;
        }

        .mic-container {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
        }

        .mic-button {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: none;
            background: #e91e63;
            color: white;
            font-size: 40px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(233, 30, 99, 0.4);
        }

        .mic-button:hover:not(:disabled) {
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(233, 30, 99, 0.5);
        }

        .mic-button:active:not(:disabled) {
            transform: scale(0.95);
        }

        .mic-button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .mic-button.recording {
            background: #f44336;
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0%, 100% {
                box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.7);
            }
            50% {
                box-shadow: 0 0 0 20px rgba(244, 67, 54, 0);
            }
        }

        .transcript-container {
            background: #f9f9f9;
            border-radius: 10px;
            padding: 20px;
            min-height: 300px;
            max-height: 500px;
            overflow-y: auto;
        }

        .transcript-label {
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .transcript {
            color: #666;
            line-height: 1.8;
            font-size: 15px;
        }

        .message {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 8px;
        }

        .message.user {
            background: #e3f2fd;
            border-left: 3px solid #2196F3;
        }

        .message.assistant {
            background: #f1f8e9;
            border-left: 3px solid #4CAF50;
        }

        .hidden {
            display: none;
        }

        .instructions {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }

        .instructions h3 {
            color: #2e7d32;
            margin-bottom: 8px;
            font-size: 14px;
        }

        .instructions p {
            color: #555;
            font-size: 13px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎙️ Website Assistant</h1>
        <p class="subtitle">Voice-powered AI assistant for your website</p>

        <div class="instructions">
            <h3>📋 How to use:</h3>
            <p>Click the microphone button below to start talking. The assistant is ready to help you navigate the website, answer questions, and provide assistance.</p>
        </div>

        <div class="status connected" id="status">Connecting to OpenAI...</div>

        <div class="mic-container">
            <button class="mic-button" id="micBtn" onclick="toggleRecording()" disabled>
                🎤
            </button>
        </div>

        <div class="waveform hidden" id="waveform" style="display: none;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 4px; height: 60px;">
                <div style="width: 4px; background: #667eea; border-radius: 2px; animation: wave 1s infinite; animation-delay: 0s;"></div>
                <div style="width: 4px; background: #667eea; border-radius: 2px; animation: wave 1s infinite; animation-delay: 0.1s;"></div>
                <div style="width: 4px; background: #667eea; border-radius: 2px; animation: wave 1s infinite; animation-delay: 0.2s;"></div>
                <div style="width: 4px; background: #667eea; border-radius: 2px; animation: wave 1s infinite; animation-delay: 0.3s;"></div>
                <div style="width: 4px; background: #667eea; border-radius: 2px; animation: wave 1s infinite; animation-delay: 0.4s;"></div>
            </div>
        </div>

        <div class="transcript-container">
            <div class="transcript-label">Conversation</div>
            <div class="transcript" id="transcript">
                <div class="message assistant">Hello! I'm your website assistant. How can I help you today?</div>
            </div>
        </div>
    </div>

    <script src="app.js"></script>
</body>
</html>
