/**
 * Minimal WebSocket Proxy for OpenAI Realtime API
 * Handles authentication that browsers cannot send
 */

const WebSocket = require('ws');
const https = require('https');
require('dotenv').config();

const API_KEY = process.env.OPENAI_API_KEY;

if (!API_KEY) {
    console.error('ERROR: OPENAI_API_KEY environment variable is not set');
    console.error('Please create a .env file with: OPENAI_API_KEY=your-api-key-here');
    process.exit(1);
}

const wss = new WebSocket.Server({ port: 8080 });
const clients = new Map();

wss.on('connection', (clientWs) => {
    console.log('Client connected');

    clientWs.on('message', async (message) => {
        try {
            const data = JSON.parse(message);
            
            if (data.action === 'connect') {
                // Fetch prompt details first (for visibility)
                await fetchPromptById('pmpt_68ff62ef52788194a734057269518ef201ba99ea44967ea9');
                await connectToOpenAI(clientWs);
            } else if (data.action === 'audio' && clients.has(clientWs)) {
                console.log('📤 Forwarding audio to OpenAI, length:', data.audio?.length || 0);
                const openaiWs = clients.get(clientWs);
                if (openaiWs && openaiWs.readyState === WebSocket.OPEN) {
                    openaiWs.send(JSON.stringify({
                        type: 'input_audio_buffer.append',
                        audio: data.audio
                    }));
                } else {
                    console.warn('⚠️ Cannot forward audio: OpenAI connection not open');
                }
            } else if (data.action === 'commit' && clients.has(clientWs)) {
                console.log('📤 Committing audio buffer to OpenAI');
                const openaiWs = clients.get(clientWs);
                if (openaiWs && openaiWs.readyState === WebSocket.OPEN) {
                    openaiWs.send(JSON.stringify({
                        type: 'input_audio_buffer.commit'
                    }));
                } else {
                    console.warn('⚠️ Cannot commit audio: OpenAI connection not open');
                }
            }
        } catch (error) {
            console.error('Error:', error);
        }
    });

    clientWs.on('close', () => {
        console.log('Client disconnected');
        if (clients.has(clientWs)) {
            const openaiWs = clients.get(clientWs);
            if (openaiWs) openaiWs.close();
            clients.delete(clientWs);
        }
    });
});

async function connectToOpenAI(clientWs) {
    const wsUrl = 'wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17';
    
    const openaiWs = new WebSocket(wsUrl, {
        headers: {
            'Authorization': `Bearer ${API_KEY}`,
            'OpenAI-Beta': 'realtime=v1'
        }
    });

    clients.set(clientWs, openaiWs);
    let assistantText = '';

    openaiWs.on('open', () => {
        console.log('✅ Connected to OpenAI');
        
        // Send session update with custom prompt
        console.log('📤 Sending session.update to OpenAI with custom prompt...');
        openaiWs.send(JSON.stringify({
            type: 'session.update',
            session: {
                modalities: ['audio', 'text'],
                prompt: {
                    id: 'pmpt_68ff62ef52788194a734057269518ef201ba99ea44967ea9',
                    version: '8'
                },
                input_audio_format: 'pcm16',
                output_audio_format: 'pcm16',
                turn_detection: {
                    type: 'server_vad',
                    threshold: 0.5,
                    prefix_padding_ms: 300,
                    silence_duration_ms: 500
                }
            }
        }));
        
        clientWs.send(JSON.stringify({ type: 'connected' }));
    });

    openaiWs.on('message', (data) => {
        const msg = JSON.parse(data.toString());
        const eventType = msg.type || msg.event;
        
        // Log all response events for debugging
        if (eventType && eventType.includes('response')) {
            console.log('📥 Response event from OpenAI:', eventType, JSON.stringify(msg).substring(0, 300));
        } else if (eventType === 'response.audio.delta' || eventType === 'response.audio.done' || eventType === 'error') {
            console.log('📥 Received from OpenAI:', JSON.stringify(msg, null, 2));
        } else {
            console.log('📥 Event type:', eventType);
        }
        
        switch(eventType) {
            case 'session.created':
                console.log('✅ Session created, notifying client...');
                clientWs.send(JSON.stringify({ type: 'session_ready' }));
                break;
            case 'conversation.item.input_audio_transcription.completed':
                if (msg.transcript) {
                    clientWs.send(JSON.stringify({
                        type: 'transcript_user',
                        text: msg.transcript
                    }));
                }
                break;
            case 'response.audio_transcript.delta':
                if (msg.delta) assistantText += msg.delta;
                break;
            case 'response.audio_transcript.done':
                if (assistantText) {
                    clientWs.send(JSON.stringify({
                        type: 'transcript_assistant',
                        text: assistantText
                    }));
                    assistantText = '';
                }
                break;
            case 'response.audio.delta':
                if (msg.delta) {
                    console.log('📥 Received audio chunk from OpenAI, length:', msg.delta?.length || 0, 'forwarding to client');
                    clientWs.send(JSON.stringify({
                        type: 'audio_chunk',
                        audio: msg.delta
                    }));
                } else {
                    console.warn('⚠️ response.audio.delta received but delta is empty');
                }
                break;
            case 'response.audio.done':
                console.log('📥 Audio transmission complete from OpenAI');
                clientWs.send(JSON.stringify({ type: 'response.audio.done' }));
                break;
            case 'input_audio_buffer.speech_started':
                clientWs.send(JSON.stringify({ type: 'recording_started' }));
                break;
            case 'input_audio_buffer.speech_stopped':
                clientWs.send(JSON.stringify({ type: 'recording_stopped' }));
                break;
            case 'response.done':
                console.log('📥 Response done from OpenAI');
                clientWs.send(JSON.stringify({ type: 'response_done' }));
                break;
            default:
                // Log any unhandled events for debugging
                if (eventType && !eventType.startsWith('response.') && eventType !== 'session.created') {
                    console.log('⚠️ Unhandled event from OpenAI:', eventType, JSON.stringify(msg).substring(0, 200));
                }
                break;
        }
    });

    openaiWs.on('error', (err) => {
        console.error('OpenAI error:', err);
        clientWs.send(JSON.stringify({ type: 'error', message: err.message }));
    });

    openaiWs.on('close', () => {
        clients.delete(clientWs);
    });
}

// Fetch a prompt by id via REST and log its instructions/content
function fetchPromptById(promptId) {
    return new Promise((resolve) => {
        const options = {
            hostname: 'api.openai.com',
            path: `/v1/prompts/${promptId}`,
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${API_KEY}`,
                'Content-Type': 'application/json'
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => (data += chunk));
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    console.log('🧾 Prompt Fetch Response:', JSON.stringify(json, null, 2));
                } catch (e) {
                    console.error('Failed to parse prompt response:', e.message);
                }
                resolve();
            });
        });
        req.on('error', (e) => {
            console.error('Prompt fetch error:', e.message);
            resolve();
        });
        req.end();
    });
}

console.log('WebSocket proxy running on ws://localhost:8080');

