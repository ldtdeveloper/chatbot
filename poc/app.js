/**
 * Voice Chat with OpenAI Realtime API
 * Connects via WebSocket proxy (handles authentication)
 * Sequential playback with noise reduction
 */

let websocket = null;
let isRecording = false;
let audioContext = null;
let stream = null;
let isPlayingAudio = false;
let audioBuffer = null; // Accumulate all audio chunks for current response
let currentSource = null; // Ensure only one source plays at a time
let audioPlaybackQueue = []; // Queue for sequential playback
let isPlayingFromQueue = false; // Track if we're currently playing from queue
let micBlockedUntil = 0; // Timestamp when microphone input will be re-enabled
let micBlockTimeout = null; // Timeout for re-enabling microphone

// Noise reduction settings - for filtering only, not for stopping mic
const NOISE_REDUCTION = {
    enableFiltering: true, // Enable noise filtering
    noiseReductionLevel: 0.3 // Noise reduction strength (0.0 to 1.0)
};

let recordingStartTime = 0;

// Update UI status
function updateStatus(status, message) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.className = 'status ' + status;
}

// Initialize connection on page load
window.addEventListener('load', function() {
    console.log('Page loaded, connecting to proxy...');
    connect();
});

// Connect to proxy server
function connect() {
    try {
        console.log('Connecting to WebSocket proxy...');
        websocket = new WebSocket('ws://localhost:8080');
        
        websocket.onopen = function(event) {
            console.log('✅ Connected to proxy, initializing...');
            updateStatus('connected', 'Connecting to OpenAI...');
            
            // Tell proxy to connect to OpenAI
            websocket.send(JSON.stringify({ action: 'connect' }));
        };
        
        websocket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            console.log('📨 Received message from proxy:', data);
            
            switch(data.type) {
                case 'connected':
                    console.log('✅ Connected to OpenAI');
                    updateStatus('connected', 'Initializing session...');
                    setTimeout(() => {
                        if (!document.getElementById('micBtn').disabled) return;
                        console.log('⏰ 3 seconds passed, enabling mic button anyway');
                        document.getElementById('micBtn').disabled = false;
                        updateStatus('connected', 'Ready to chat');
                    }, 3000);
                    break;
                case 'session_ready':
                    console.log('✅ Session ready, enabling mic button');
                    document.getElementById('micBtn').disabled = false;
                    updateStatus('connected', 'Ready to chat');
                    break;
                case 'transcript_user':
                    if (data.text) addMessage('user', data.text);
                    break;
                case 'transcript_assistant':
                    if (data.text) addMessage('assistant', data.text);
                    break;
                case 'audio_chunk':
                    console.log('📥 Received audio chunk from proxy, length:', data.audio?.length || 0);
                    if (data.audio) {
                        queueAudioChunk(data.audio);
                    }
                    break;
                case 'response.audio.done':
                    console.log('📥 All audio chunks received, queueing for sequential playback');
                    if (audioBuffer && audioBuffer.length > 0) {
                        queueResponseForPlayback(audioBuffer);
                        audioBuffer = null; // Clear for next response
                    }
                    break;
                case 'response_done':
                    updateStatus('connected', 'Ready to chat');
                    // Fallback: queue audio if response.audio.done didn't fire
                    if (audioBuffer && audioBuffer.length > 0) {
                        console.log('📥 Response done, queueing accumulated audio');
                        queueResponseForPlayback(audioBuffer);
                        audioBuffer = null;
                    }
                    break;
                case 'recording_started':
                    updateStatus('recording', 'Listening...');
                    const waveform1 = document.getElementById('waveform');
                    if (waveform1) waveform1.style.display = 'flex';
                    break;
                case 'recording_stopped':
                    updateStatus('connected', 'Ready to chat');
                    const waveform2 = document.getElementById('waveform');
                    if (waveform2) waveform2.style.display = 'none';
                    break;
                case 'error':
                    console.error('Error:', data.message);
                    alert('Error: ' + data.message);
                    updateStatus('disconnected', 'Error occurred');
                    break;
            }
        };
        
        websocket.onerror = function(error) {
            console.error('WebSocket error:', error);
            updateStatus('disconnected', 'Connection error');
        };
        
        websocket.onclose = function(event) {
            console.log('Disconnected from proxy');
            updateStatus('disconnected', 'Disconnected');
            document.getElementById('micBtn').disabled = true;
        };
        
    } catch (error) {
        console.error('Failed to connect:', error);
        alert('Failed to connect: ' + error.message);
    }
}

// Add message to transcript
function addMessage(type, text) {
    const transcript = document.getElementById('transcript');
    const existingMessage = transcript.querySelector('.message:last-child');
    
    if (existingMessage && existingMessage.classList.contains(type)) {
        existingMessage.innerHTML = `<strong>${type === 'user' ? 'You' : 'Assistant'}:</strong> ${text}`;
    } else {
        const message = document.createElement('div');
        message.className = 'message ' + type;
        message.innerHTML = `<strong>${type === 'user' ? 'You' : 'Assistant'}:</strong> ${text}`;
        transcript.appendChild(message);
    }
    
    transcript.scrollTop = transcript.scrollHeight;
}

// Calculate RMS (Root Mean Square) volume
function calculateRMS(audioData) {
    let sum = 0;
    for (let i = 0; i < audioData.length; i++) {
        sum += audioData[i] * audioData[i];
    }
    return Math.sqrt(sum / audioData.length);
}

// Apply noise reduction filter - reduces noise but never stops sending audio
function applyNoiseReduction(audioData) {
    if (!NOISE_REDUCTION.enableFiltering) {
        return audioData; // Return original if filtering disabled
    }
    
    // Apply noise reduction using spectral subtraction approach
    // This reduces background noise while preserving voice
    const filtered = new Float32Array(audioData.length);
    const noiseReductionLevel = NOISE_REDUCTION.noiseReductionLevel;
    
    // Estimate noise floor (assuming quiet parts are noise)
    let noiseFloor = 0;
    let sampleCount = 0;
    for (let i = 0; i < audioData.length; i++) {
        const abs = Math.abs(audioData[i]);
        if (abs < 0.01) { // Quiet parts likely noise
            noiseFloor += abs;
            sampleCount++;
        }
    }
    noiseFloor = sampleCount > 0 ? noiseFloor / sampleCount : 0;
    
    // Apply noise reduction while preserving voice
    for (let i = 0; i < audioData.length; i++) {
        const sample = audioData[i];
        const abs = Math.abs(sample);
        
        // Reduce noise proportionally, but always send the audio
        if (abs > noiseFloor) {
            // Voice signal - reduce noise component
            const noiseComponent = noiseFloor * noiseReductionLevel;
            filtered[i] = sample > 0 ? 
                Math.max(0, sample - noiseComponent) : 
                Math.min(0, sample + noiseComponent);
        } else {
            // Likely noise - reduce more aggressively but don't zero it
            filtered[i] = sample * (1 - noiseReductionLevel * 0.5);
        }
    }
    
    // Apply high-pass filter to reduce low-frequency rumble
    const highPassFiltered = new Float32Array(filtered.length);
    const alpha = 0.95; // High-pass filter coefficient
    
    highPassFiltered[0] = filtered[0];
    for (let i = 1; i < filtered.length; i++) {
        highPassFiltered[i] = alpha * (highPassFiltered[i-1] + filtered[i] - filtered[i-1]);
    }
    
    return highPassFiltered;
}

// Toggle recording
async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

// Start recording audio
async function startRecording() {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        alert('Not connected to OpenAI');
        return;
    }
    
    try {
        // Initialize audio context on first user interaction
        if (!audioContext) {
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            if (audioContext.state === 'suspended') {
                await audioContext.resume();
            }
        }
        
        // Request microphone access with noise reduction constraints
        stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true, // Browser's built-in noise suppression
                autoGainControl: true,
                sampleRate: 48000 // Request higher quality for better processing
            } 
        });
        
        const source = audioContext.createMediaStreamSource(stream);
        const processor = audioContext.createScriptProcessor(4096, 1, 1);
        processor.bufferSize = 16384;
        
        const sourceSampleRate = audioContext.sampleRate;
        const targetSampleRate = 24000;
        
        processor.onaudioprocess = function(e) {
            // Block microphone input during playback only
            const now = Date.now();
            if (now < micBlockedUntil || isPlayingAudio) {
                return;
            }
            
            // Continuous listening - always send audio if recording (like a phone call)
            if (isRecording && websocket && websocket.readyState === WebSocket.OPEN) {
                const inputData = e.inputBuffer.getChannelData(0);
                
                // Apply noise reduction (filters noise but always sends audio)
                let audioData = applyNoiseReduction(inputData);
                
                // Resample if needed
                if (sourceSampleRate !== targetSampleRate) {
                    audioData = resampleAudio(audioData, sourceSampleRate, targetSampleRate);
                }
                
                // Convert Float32 to PCM16
                const pcmData = convertFloat32ToPCM16(audioData);
                
                // Convert Int16Array to bytes (little-endian)
                const bytes = new Uint8Array(pcmData.length * 2);
                const dataView = new DataView(bytes.buffer);
                for (let i = 0; i < pcmData.length; i++) {
                    dataView.setInt16(i * 2, pcmData[i], true);
                }
                
                // Convert to base64
                const base64Audio = btoa(String.fromCharCode.apply(null, Array.from(bytes)));
                
                // Send audio data to proxy - continuous streaming (like a phone call)
                websocket.send(JSON.stringify({
                    action: 'audio',
                    audio: base64Audio
                }));
                // Removed verbose logging for cleaner console during continuous listening
            }
        };
        
        source.connect(processor);
        processor.connect(audioContext.destination);
        
        isRecording = true;
        recordingStartTime = Date.now(); // Track when recording started
        document.getElementById('micBtn').classList.add('recording');
        updateStatus('recording', 'Recording...');
        
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Could not access microphone: ' + error.message);
    }
}

// Stop recording
function stopRecording() {
    isRecording = false;
    recordingStartTime = 0; // Reset recording start time
    if (processor) {
        processor.disconnect();
        processor = null;
    }
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    document.getElementById('micBtn').classList.remove('recording');
    updateStatus('connected', 'Processing...');
    const waveform = document.getElementById('waveform');
    if (waveform) waveform.style.display = 'none';
    
    // Send commit action after a delay to ensure all chunks are sent
    setTimeout(() => {
        if (websocket && websocket.readyState === WebSocket.OPEN) {
            websocket.send(JSON.stringify({ action: 'commit' }));
            console.log('📤 Sent commit action');
        }
    }, 300); // Reduced from 500ms to 300ms for faster response
}

let processor = null;

// Convert Float32 to PCM16
function convertFloat32ToPCM16(float32Array) {
    const pcm16 = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i++) {
        const sample = Math.max(-1, Math.min(1, float32Array[i]));
        pcm16[i] = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
    }
    return pcm16;
}

// Resample audio data
function resampleAudio(input, inputSampleRate, outputSampleRate) {
    if (inputSampleRate === outputSampleRate) {
        return input;
    }
    
    const ratio = inputSampleRate / outputSampleRate;
    const outputLength = Math.round(input.length / ratio);
    const output = new Float32Array(outputLength);
    
    for (let i = 0; i < outputLength; i++) {
        const index = Math.floor(i * ratio);
        output[i] = input[index] || 0;
    }
    
    return output;
}

// Queue audio chunk for later combination
function queueAudioChunk(base64Audio) {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    try {
        const binaryString = atob(base64Audio);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }
        
        if (!audioBuffer) {
            audioBuffer = [];
        }
        audioBuffer.push(bytes);
        console.log('📥 Queued audio chunk, buffer size:', audioBuffer.length);
        
    } catch (error) {
        console.error('Error queueing audio:', error);
    }
}

// Queue a response for sequential playback
function queueResponseForPlayback(bufferArray) {
    if (!bufferArray || bufferArray.length === 0) {
        console.warn('⚠️ Cannot queue empty audio buffer');
        return;
    }
    
    // Calculate total size and combine chunks
    let totalLength = 0;
    for (let i = 0; i < bufferArray.length; i++) {
        totalLength += bufferArray[i].length;
    }
    
    const combinedBytes = new Uint8Array(totalLength);
    let offset = 0;
    for (let i = 0; i < bufferArray.length; i++) {
        combinedBytes.set(bufferArray[i], offset);
        offset += bufferArray[i].length;
    }
    
    // Add to queue
    audioPlaybackQueue.push(combinedBytes);
    console.log('📋 Queued response for sequential playback. Queue size:', audioPlaybackQueue.length);
    
    // Start playing if not already playing
    if (!isPlayingFromQueue) {
        playNextInQueue();
    }
}

// Play the next item in the queue sequentially
async function playNextInQueue() {
    if (audioPlaybackQueue.length === 0) {
        console.log('📋 Playback queue empty');
        isPlayingFromQueue = false;
        return;
    }
    
    if (isPlayingFromQueue) {
        console.log('⏸️ Already playing from queue, waiting...');
        return;
    }
    
    isPlayingFromQueue = true;
    const audioData = audioPlaybackQueue.shift();
    console.log('🎵 Playing from queue. Remaining:', audioPlaybackQueue.length);
    
    // Block microphone 1 second BEFORE playback starts
    const now = Date.now();
    micBlockedUntil = now + 1000;
    console.log('🎤 Microphone input blocked 1 second before playback starts');
    
    // Wait 1 second before starting playback
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    try {
        await decodeAndPlayAudio(audioData);
    } catch (error) {
        console.error('Error playing from queue:', error);
        isPlayingFromQueue = false;
        playNextInQueue(); // Continue with next item
    }
}

// Decode audio bytes and play
async function decodeAndPlayAudio(bytes) {
    console.log('🎵 decodeAndPlayAudio called with', bytes.length, 'bytes');
    
    // Ensure audioContext exists - create it if it doesn't exist
    if (!audioContext) {
        console.log('🎵 Creating new audio context for playback');
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    console.log('🎵 Audio context state:', audioContext.state);
    
    // Resume audio context if suspended (required by browsers)
    if (audioContext.state === 'suspended') {
        console.log('🎵 Resuming suspended audio context...');
        await audioContext.resume();
        console.log('🎵 Audio context resumed, new state:', audioContext.state);
    }
    
    try {
        const sampleCount = bytes.length / 2;
        console.log('🎵 Processing', sampleCount, 'samples from', bytes.length, 'bytes');
        
        if (sampleCount === 0) {
            console.warn('⚠️ No samples to play');
            isPlayingFromQueue = false;
            playNextInQueue();
            return;
        }
        
        if (bytes.length % 2 !== 0) {
            console.warn('⚠️ Odd number of bytes, truncating');
            bytes = bytes.slice(0, bytes.length - 1);
        }
        
        // Ensure we have a proper ArrayBuffer
        let buffer = bytes.buffer;
        if (bytes.byteOffset !== 0 || bytes.byteLength !== bytes.buffer.byteLength) {
            buffer = bytes.slice().buffer;
        }
        const dataView = new DataView(buffer);
        
        // Convert to Int16Array
        const int16Array = new Int16Array(sampleCount);
        for (let i = 0; i < sampleCount; i++) {
            int16Array[i] = dataView.getInt16(i * 2, true);
        }
        
        // Convert to Float32
        const float32Array = new Float32Array(sampleCount);
        for (let i = 0; i < sampleCount; i++) {
            float32Array[i] = int16Array[i] / 32768.0;
        }
        
        console.log('🎵 Decoding', sampleCount, 'samples');
        
        // Resample if needed
        const inputSampleRate = 24000;
        const outputSampleRate = audioContext.sampleRate;
        console.log('🎵 Sample rates - input:', inputSampleRate, 'output:', outputSampleRate);
        
        let audioData = float32Array;
        if (outputSampleRate !== inputSampleRate) {
            console.log('🎵 Resampling from', inputSampleRate, 'to', outputSampleRate);
            audioData = resampleAudio(float32Array, inputSampleRate, outputSampleRate);
            console.log('🎵 Resampled to', audioData.length, 'samples');
        }
        
        // Create and play audio
        const audioBufferObj = audioContext.createBuffer(1, audioData.length, outputSampleRate);
        audioBufferObj.getChannelData(0).set(audioData);
        
        const source = audioContext.createBufferSource();
        currentSource = source;
        source.buffer = audioBufferObj;
        source.connect(audioContext.destination);
        
        source.onended = () => {
            console.log('🎵 ✅ Audio playback complete');
            isPlayingAudio = false;
            currentSource = null;
            isPlayingFromQueue = false;
            
            // Block microphone for 1 second AFTER playback ends
            const now = Date.now();
            micBlockedUntil = now + 1000;
            console.log('🎤 Microphone input blocked for 1 second after playback');
            
            // Re-enable microphone after 1 second
            if (micBlockTimeout) {
                clearTimeout(micBlockTimeout);
            }
            micBlockTimeout = setTimeout(() => {
                micBlockedUntil = 0;
                console.log('🎤 Microphone input re-enabled (ready for user input)');
                
                // Automatically play next item in queue if available
                if (audioPlaybackQueue.length > 0) {
                    console.log('▶️ Playing next response in queue...');
                    setTimeout(() => playNextInQueue(), 100);
                }
            }, 1000);
        };
        
        // Update blocking timestamp to cover full playback duration + 1 second after
        const playbackDurationMs = audioBufferObj.duration * 1000;
        const now = Date.now();
        micBlockedUntil = now + playbackDurationMs + 1000;
        
        // Ensure audio context is running before starting
        if (audioContext.state === 'suspended') {
            await audioContext.resume();
        }
        
        source.start(0);
        isPlayingAudio = true;
        console.log('🎵 ✅ Audio source started! Duration:', audioBufferObj.duration.toFixed(2), 'seconds');
        console.log('🎵 ✅ Playback should be audible now');
        
        // Verify it's actually playing
        setTimeout(() => {
            if (audioContext.state === 'running' && isPlayingAudio) {
                console.log('🎵 ✅ Verified: Audio context running and isPlayingAudio is true');
            } else {
                console.warn('⚠️ Audio may not be playing. State:', audioContext.state, 'isPlaying:', isPlayingAudio);
            }
        }, 100);
        
    } catch (error) {
        console.error('❌ Error decoding/playing audio:', error);
        console.error('Error stack:', error.stack);
        isPlayingAudio = false;
        currentSource = null;
        isPlayingFromQueue = false;
        playNextInQueue(); // Continue with next item even if this one failed
    }
}
