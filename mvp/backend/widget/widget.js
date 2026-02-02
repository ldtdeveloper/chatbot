(function() {
    // Get configuration from script tag data attributes
    const scriptTag = document.currentScript || document.querySelector('script[data-agent-id]');
    const agentId = scriptTag ? parseInt(scriptTag.getAttribute('data-agent-id')) : null;
    const apiBaseUrl = scriptTag ? scriptTag.getAttribute('data-api-url') : null;
    const agentName = scriptTag ? scriptTag.getAttribute('data-agent-name') : 'Voice Assistant';
    
    if (!agentId || !apiBaseUrl) {
        console.error('[Widget] Missing required configuration: agentId or apiBaseUrl');
        return;
    }
    
    // Inject CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = apiBaseUrl.replace(/\/$/, '') + '/api/widget/widget.css';
    document.head.appendChild(link);
    
    // Create widget HTML
    const widgetHTML = `
        <div id="voice-widget-container">
            <div id="voice-widget-panel">
                <div id="voice-widget-header">${agentName}</div>
                <div id="voice-widget-transcript"></div>
                <div id="voice-widget-status">Ready</div>
            </div>
            <button id="voice-widget-button" title="${agentName}">
                <svg id="mic-icon" viewBox="0 0 24 24">
                    <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
                    <path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
                </svg>
                <svg id="stop-icon" viewBox="0 0 24 24" style="display: none;">
                    <path d="M6 6h12v12H6z"/>
                </svg>
            </button>
        </div>
    `;
    
    // Inject widget HTML
    const container = document.createElement('div');
    container.innerHTML = widgetHTML;
    document.body.appendChild(container);
    
    // Widget JavaScript
    const button = document.getElementById('voice-widget-button');
    const panel = document.getElementById('voice-widget-panel');
    const transcript = document.getElementById('voice-widget-transcript');
    const status = document.getElementById('voice-widget-status');
    const micIcon = document.getElementById('mic-icon');
    const stopIcon = document.getElementById('stop-icon');
    
    let ws = null;
    let audioContext = null;
    let processor = null;
    let source = null;
    let stream = null;
    let isRecording = false;
    let isConnected = false;
    let audioQueue = [];
    let isPlaying = false;
    let currentAudioSource = null;
    let currentPlaybackContext = null;
    
    // Advanced speech detection state for better noise filtering
    let speechDetectionState = {
        consecutiveSpeechFrames: 0,
        lastSpeechTime: 0,
        speechStartTime: 0, // Track when continuous speech started (client-side)
        openaiSpeechStartTime: 0, // Track when OpenAI detected speech started
        minSpeechFrames: 3, // Require 3 consecutive frames to confirm speech detection
        minContinuousSpeechMs: 1500, // Require 1500ms (1.5 seconds) of continuous speech before interrupting
        openaiSpeechDebounceMs: 500, // Wait 500ms after OpenAI speech_started before stopping (filters false positives)
        speechThreshold: 0.02, // Base RMS threshold
        energyHistory: [], // Track recent energy levels to detect variation
        zcrHistory: [], // Track zero crossing rate history
        historySize: 5, // Keep last 5 frames for variance calculation
        minVariance: 0.0002, // Minimum variance to distinguish speech from continuous noise/music
        minZCR: 0.1, // Minimum zero crossing rate for speech (speech has higher ZCR than noise)
        maxZCR: 0.5, // Maximum zero crossing rate (filters out high-frequency noise)
        adaptiveThreshold: 0.02, // Adaptive threshold that adjusts to background noise
        noiseFloor: 0.01, // Estimated background noise level
        noiseFloorAlpha: 0.95, // Smoothing factor for noise floor estimation
        speechScore: 0, // Combined speech likelihood score (0-1)
        openaiSpeechPending: false // Track if we're waiting to stop after OpenAI speech_started
    };
    
    // Determine WebSocket URL
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = apiBaseUrl.replace(/^https?:/, '').replace(/^\/\//, '');
    const wsUrl = `${wsProtocol}//${wsHost}/api/widget/ws?agent_id=${agentId}`;
    
    // Function to update button icon
    function updateButtonIcon(showStop) {
        if (showStop) {
            micIcon.style.display = 'none';
            stopIcon.style.display = 'block';
            button.title = 'Stop Conversation';
        } else {
            micIcon.style.display = 'block';
            stopIcon.style.display = 'none';
            button.title = agentName;
        }
    }
    
    // Show recharge popup
    function showRechargePopup(message) {
        // Create popup overlay
        const overlay = document.createElement('div');
        overlay.id = 'recharge-popup-overlay';
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            animation: fadeIn 0.3s ease;
        `;
        
        // Create popup content
        const popup = document.createElement('div');
        popup.style.cssText = `
            background: white;
            border-radius: 12px;
            padding: 0;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: slideUp 0.3s ease;
        `;
        
        popup.innerHTML = `
            <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 1.5rem; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center;">
                <h2 style="margin: 0; font-size: 1.5rem; font-weight: 600;">⚠️ Insufficient Balance</h2>
                <button id="close-recharge-popup" style="background: rgba(255, 255, 255, 0.2); border: none; color: white; font-size: 1.5rem; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: background 0.2s; padding: 0; line-height: 1;">×</button>
            </div>
            <div style="padding: 2rem;">
                <p style="margin: 0.75rem 0; color: #555; line-height: 1.6; font-size: 1rem;">${message}</p>
                <p style="margin: 0.75rem 0; color: #555; line-height: 1.6; font-size: 1rem;">Please recharge your wallet to continue using the service.</p>
            </div>
            <div style="padding: 0 2rem 2rem; display: flex; justify-content: flex-end; gap: 1rem;">
                <button id="recharge-popup-ok" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem 2rem; border-radius: 6px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s; width: auto;">I Understand</button>
            </div>
        `;
        
        overlay.appendChild(popup);
        document.body.appendChild(overlay);
        
        // Add animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
        
        // Close handlers
        const closePopup = () => {
            overlay.remove();
            style.remove();
        };
        
        document.getElementById('close-recharge-popup').addEventListener('click', closePopup);
        document.getElementById('recharge-popup-ok').addEventListener('click', closePopup);
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                closePopup();
            }
        });
    }
    
    // Toggle panel or stop conversation
    button.addEventListener('click', function() {
        if (isConnected || isRecording) {
            // Stop conversation
            stopConversation();
        } else {
            // Open panel and connect
            panel.classList.toggle('open');
            if (panel.classList.contains('open')) {
                connect();
            }
        }
    });
    
    // WebSocket connection
    async function connect() {
        try {
            status.textContent = 'Connecting...';
            ws = new WebSocket(wsUrl);
            
            
            ws.onopen = function() {
                console.log('[Widget] Connected to backend');
                isConnected = true;
                button.classList.add('connected');
                updateButtonIcon(true);
                status.textContent = 'Connected - Ready';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };
            
            ws.onerror = function(error) {
                console.error('[Widget] WebSocket error:', error);
                status.textContent = 'Connection error';
            };
            
            ws.onclose = function() {
                console.log('[Widget] Disconnected');
                isConnected = false;
                button.classList.remove('connected', 'recording');
                updateButtonIcon(false);
                status.textContent = 'Disconnected';
                cleanup();
            };
        } catch (error) {
            console.error('[Widget] Connection failed:', error);
            status.textContent = 'Failed to connect';
        }
    }
    
    // Stop conversation
    function stopConversation() {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close();
        }
        cleanup();
        panel.classList.remove('open');
        updateButtonIcon(false);
        status.textContent = 'Stopped';
    }
    
    // Handle messages
    function handleMessage(data) {
        console.log(data?.type);
        switch (data.type) {
            case 'connected':
                status.textContent = 'Connected - Ready';
                startRecording();
                // Startup message is now handled by the backend automatically
                break;
            case 'transcript_user':
                addTranscript('user', data.text);
                break;
            case 'transcript_assistant':
                addTranscript('assistant', data.text);
                break;
            case 'audio_chunk':
                if (data.audio) {
                    // If this is a new response (queue was cleared), start fresh
                    queueAudio(data.audio);
                }
                break;
            case 'speech_started':
                // OpenAI detected user speech - use debounced approach to filter false positives
                const currentTime = Date.now();
                speechDetectionState.openaiSpeechStartTime = currentTime;
                speechDetectionState.openaiSpeechPending = true;
                
                // Set a timeout to actually stop playback after debounce period
                // This allows us to verify speech is continuing
                setTimeout(() => {
                    // Only stop if speech is still detected (not a false positive)
                    if (speechDetectionState.openaiSpeechPending && 
                        (Date.now() - speechDetectionState.openaiSpeechStartTime) >= speechDetectionState.openaiSpeechDebounceMs) {
                        stopAllPlayback();
                        speechDetectionState.openaiSpeechPending = false;
                    }
                }, speechDetectionState.openaiSpeechDebounceMs);
                
                status.textContent = 'Listening...';
                button.classList.add('recording');
                break;
            case 'speech_stopped':
                status.textContent = 'Processing...';
                button.classList.remove('recording');
                break;
            case 'response_done':
                status.textContent = 'Ready';
                break;
            case 'error':
                status.textContent = 'Error: ' + data.error;
                console.error('[Widget] Error:', data.error);
                
                // Handle insufficient balance error
                if (data.error === 'insufficient_balance') {
                    showRechargePopup(data.message || 'Your wallet balance is insufficient. Please recharge to continue using the service.');
                    // Stop recording if active
                    if (isRecording) {
                        stopRecording();
                    }
                    // Close connection
                    if (ws) {
                        ws.close();
                        ws = null;
                        isConnected = false;
                    }
                }
                break;
        }
    }
    
    // Audio recording
    async function startRecording() {
        if (isRecording) return;
        
        // Check if getUserMedia is available (requires HTTPS or localhost)
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            const isHttp = window.location.protocol === 'http:';
            const isLocalhost = window.location.hostname.includes('localhost') || 
                               window.location.hostname === '127.0.0.1';
            
            let errorMsg;
            if (isHttp && !isLocalhost) {
                const httpsUrl = window.location.href.replace('http://', 'https://');
                errorMsg = 'Microphone access requires HTTPS';
                console.error('[Widget]', errorMsg + '. Please use:', httpsUrl);
                status.textContent = errorMsg + ' - Use HTTPS';
                alert(errorMsg + '\n\nFor security reasons, microphone access requires a secure connection (HTTPS).\n\nPlease access this page via:\n' + httpsUrl);
            } else {
                errorMsg = 'Microphone access is not available in this browser';
                console.error('[Widget]', errorMsg);
                status.textContent = errorMsg;
                alert(errorMsg);
            }
            return;
        }
        
        try {
            stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 24000,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                    suppressLocalAudioPlayback: true
                }
            });
            
            // Use browser's default sample rate to avoid conflicts
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            source = audioContext.createMediaStreamSource(stream);
            const bufferSize = 4096;
            processor = audioContext.createScriptProcessor(bufferSize, 1, 1);
            
            // Create a silent gain node instead of connecting to destination
            // This avoids sample rate mismatch issues
            const gainNode = audioContext.createGain();
            gainNode.gain.value = 0; // Silent output
            
            source.connect(processor);
            processor.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            processor.onaudioprocess = function(e) {
                if (!isConnected || !isRecording) return;
                
                const inputData = e.inputBuffer.getChannelData(0);
                
                // Advanced multi-feature speech detection
                // Uses RMS energy, energy variance, and zero crossing rate (ZCR)
                
                // 1. Calculate RMS Energy
                const rms = Math.sqrt(inputData.reduce((sum, val) => sum + val * val, 0) / inputData.length);
                
                // 2. Calculate Zero Crossing Rate (ZCR) - speech has characteristic ZCR patterns
                let zcr = 0;
                for (let i = 1; i < inputData.length; i++) {
                    if ((inputData[i] >= 0 && inputData[i-1] < 0) || (inputData[i] < 0 && inputData[i-1] >= 0)) {
                        zcr++;
                    }
                }
                const normalizedZCR = zcr / inputData.length; // Normalize by frame length
                
                // 3. Update adaptive noise floor (estimate background noise level)
                if (rms < speechDetectionState.adaptiveThreshold) {
                    // Likely noise - update noise floor estimate
                    speechDetectionState.noiseFloor = 
                        speechDetectionState.noiseFloorAlpha * speechDetectionState.noiseFloor + 
                        (1 - speechDetectionState.noiseFloorAlpha) * rms;
                }
                
                // 4. Track energy history for variance calculation
                speechDetectionState.energyHistory.push(rms);
                if (speechDetectionState.energyHistory.length > speechDetectionState.historySize) {
                    speechDetectionState.energyHistory.shift();
                }
                
                // 5. Track ZCR history
                speechDetectionState.zcrHistory.push(normalizedZCR);
                if (speechDetectionState.zcrHistory.length > speechDetectionState.historySize) {
                    speechDetectionState.zcrHistory.shift();
                }
                
                // 6. Calculate energy variance (speech has more variation than continuous noise/music)
                let energyVariance = 0;
                if (speechDetectionState.energyHistory.length >= 3) {
                    const mean = speechDetectionState.energyHistory.reduce((a, b) => a + b, 0) / speechDetectionState.energyHistory.length;
                    const variance = speechDetectionState.energyHistory.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / speechDetectionState.energyHistory.length;
                    energyVariance = variance;
                }
                
                // 7. Calculate adaptive threshold (adjusts to background noise level)
                speechDetectionState.adaptiveThreshold = Math.max(
                    speechDetectionState.speechThreshold,
                    speechDetectionState.noiseFloor * 2.5 // Threshold is 2.5x the noise floor
                );
                
                // 8. Multi-feature speech detection scoring
                // Feature 1: Energy above adaptive threshold
                const energyScore = rms > speechDetectionState.adaptiveThreshold ? 1 : 0;
                
                // Feature 2: Energy variance (speech has variation, continuous noise doesn't)
                const varianceScore = energyVariance >= speechDetectionState.minVariance ? 1 : 0;
                
                // Feature 3: Zero Crossing Rate (speech has characteristic ZCR range)
                const zcrScore = (normalizedZCR >= speechDetectionState.minZCR && 
                                 normalizedZCR <= speechDetectionState.maxZCR) ? 1 : 0;
                
                // Feature 4: Signal-to-noise ratio (SNR)
                const snr = speechDetectionState.noiseFloor > 0 ? 
                    (rms / speechDetectionState.noiseFloor) : 0;
                const snrScore = snr > 2.0 ? 1 : 0; // Require at least 2:1 SNR
                
                // Combined speech likelihood score (weighted combination)
                // Require at least 3 out of 4 features to indicate speech
                const featureCount = energyScore + varianceScore + zcrScore + snrScore;
                const isSpeechDetected = featureCount >= 3;
                
                // Store speech score for debugging (optional)
                speechDetectionState.speechScore = featureCount / 4;
                
                // Track consecutive speech frames to distinguish real speech from noise
                const currentTime = Date.now();
                if (isSpeechDetected) {
                    speechDetectionState.consecutiveSpeechFrames++;
                    speechDetectionState.lastSpeechTime = currentTime;
                    
                    // Track when continuous speech started
                    if (speechDetectionState.speechStartTime === 0) {
                        speechDetectionState.speechStartTime = currentTime;
                    }
                } else {
                    // Reset counter if no speech detected (allows brief pauses in speech)
                    // Only reset if we haven't had speech for a while
                    if (currentTime - speechDetectionState.lastSpeechTime > 200) {
                        speechDetectionState.consecutiveSpeechFrames = 0;
                        speechDetectionState.speechStartTime = 0; // Reset speech start time
                    }
                }
                
                // Client-side backup detection: Only interrupt if we have sustained speech for the minimum duration
                // This is a backup in case OpenAI's detection misses something
                // Require both: sufficient frames AND continuous speech for 1000ms
                if (isPlaying && 
                    speechDetectionState.consecutiveSpeechFrames >= speechDetectionState.minSpeechFrames &&
                    speechDetectionState.speechStartTime > 0) {
                    
                    const continuousSpeechDuration = currentTime - speechDetectionState.speechStartTime;
                    
                    // Only stop playback if user has been speaking continuously for at least 1000ms
                    // This ensures we don't interrupt on brief sounds
                    if (continuousSpeechDuration >= speechDetectionState.minContinuousSpeechMs) {
                        stopAllPlayback();
                        // Reset after interrupting to avoid immediate re-triggering
                        speechDetectionState.consecutiveSpeechFrames = 0;
                        speechDetectionState.speechStartTime = 0;
                        speechDetectionState.openaiSpeechPending = false; // Cancel OpenAI pending if client-side triggered
                    }
                }
                
                // If OpenAI speech_started was detected, verify it's still ongoing
                // Reset pending flag if speech stops (false positive detection)
                if (speechDetectionState.openaiSpeechPending && !isSpeechDetected) {
                    // If no speech detected for a while, cancel the pending stop
                    if (currentTime - speechDetectionState.openaiSpeechStartTime > 300) {
                        speechDetectionState.openaiSpeechPending = false;
                    }
                }
                
                const inputSampleRate = audioContext.sampleRate;
                
                // Resample to 24kHz if needed (matches OpenAI's output format)
                let audioData = inputData;
                if (inputSampleRate !== 24000) {
                    audioData = resampleAudio(inputData, inputSampleRate, 24000);
                }
                
                const pcm16 = float32ToPCM16(audioData);
                const base64Audio = arrayBufferToBase64(pcm16.buffer);
                
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        action: 'audio_chunk',
                        audio: base64Audio
                    }));
                }
            };
            
            isRecording = true;
            status.textContent = 'Recording...';
        } catch (err) {
            console.error('[Widget] Recording error:', err);
            status.textContent = 'Microphone access denied';
        }
    }
    
    function stopRecording() {
        if (!isRecording) return;
        
        if (processor) {
            processor.disconnect();
            processor = null;
        }
        if (source) {
            source.disconnect();
            source = null;
        }
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        if (audioContext && audioContext.state !== 'closed') {
            audioContext.close();
            audioContext = null;
        }
        
        isRecording = false;
    }
    
    // Stop all audio playback and clear queue
    function stopAllPlayback() {
        // Stop current audio source if playing
        if (currentAudioSource) {
            try {
                // Remove onended handler to prevent callback after stop
                currentAudioSource.onended = null;
                currentAudioSource.stop();
                currentAudioSource.disconnect();
            } catch (err) {
                // Source may already be stopped
            }
            currentAudioSource = null;
        }
        
        // Close playback context if exists
        if (currentPlaybackContext && currentPlaybackContext.state !== 'closed') {
            try {
                currentPlaybackContext.close();
            } catch (err) {
                // Context may already be closed
            }
            currentPlaybackContext = null;
        }
        
        // Clear the audio queue
        audioQueue = [];
        isPlaying = false;
        
        // Reset speech detection state after stopping playback
        speechDetectionState.consecutiveSpeechFrames = 0;
        speechDetectionState.lastSpeechTime = 0;
        speechDetectionState.speechStartTime = 0;
        speechDetectionState.openaiSpeechStartTime = 0;
        speechDetectionState.openaiSpeechPending = false;
        speechDetectionState.energyHistory = [];
        speechDetectionState.zcrHistory = [];
        speechDetectionState.speechScore = 0;
    }
    
    // Audio playback
    function queueAudio(base64Audio) {
        audioQueue.push(base64Audio);
        if (!isPlaying) {
            playNextAudio();
        }
    }
    
    async function playNextAudio() {
        if (audioQueue.length === 0) {
            isPlaying = false;
            return;
        }
        
        isPlaying = true;
        const base64Audio = audioQueue.shift();
        
        try {
            const binaryString = atob(base64Audio);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            
            // OpenAI sends audio at 24kHz, so playback must match
            const playbackContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 24000
            });
            currentPlaybackContext = playbackContext;
            
            const pcm16 = new Int16Array(bytes.buffer);
            const float32 = new Float32Array(pcm16.length);
            for (let i = 0; i < pcm16.length; i++) {
                float32[i] = pcm16[i] / 32768.0;
            }
            
            const audioBuffer = playbackContext.createBuffer(1, float32.length, 24000);
            audioBuffer.getChannelData(0).set(float32);
            
            const bufferSource = playbackContext.createBufferSource();
            currentAudioSource = bufferSource;
            bufferSource.buffer = audioBuffer;
            bufferSource.connect(playbackContext.destination);
            
            bufferSource.onended = function() {
                if (currentAudioSource === bufferSource) {
                    currentAudioSource = null;
                }
                if (currentPlaybackContext === playbackContext) {
                    currentPlaybackContext = null;
                }
                // Only close if context is not already closed
                if (playbackContext.state !== 'closed') {
                    try {
                        playbackContext.close();
                    } catch (err) {
                        // Context may already be closing/closed
                    }
                }
                playNextAudio();
            };
            
            bufferSource.start(0);
        } catch (err) {
            console.error('[Widget] Playback error:', err);
            playNextAudio();
        }
    }
    
    // Helper functions
    function resampleAudio(inputData, inputSampleRate, outputSampleRate) {
        if (inputSampleRate === outputSampleRate) {
            return inputData;
        }
        
        const ratio = inputSampleRate / outputSampleRate;
        const outputLength = Math.round(inputData.length / ratio);
        const output = new Float32Array(outputLength);
        
        for (let i = 0; i < outputLength; i++) {
            const index = i * ratio;
            const indexFloor = Math.floor(index);
            const indexCeil = Math.min(indexFloor + 1, inputData.length - 1);
            const fraction = index - indexFloor;
            
            // Linear interpolation
            output[i] = inputData[indexFloor] * (1 - fraction) + inputData[indexCeil] * fraction;
        }
        
        return output;
    }
    
    function float32ToPCM16(float32Array) {
        const pcm16 = new Int16Array(float32Array.length);
        for (let i = 0; i < float32Array.length; i++) {
            let s = Math.max(-1, Math.min(1, float32Array[i]));
            pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
        }
        return pcm16;
    }
    
    function arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }
    
    function addTranscript(role, text) {
        const div = document.createElement('div');
        div.className = 'transcript-' + role;
        
        if (role === 'assistant') {
            // Add AI icon for assistant messages
            const icon = document.createElement('span');
            icon.className = 'ai-icon';
            icon.innerHTML = '🗩';
            div.appendChild(icon);
            
            const textSpan = document.createElement('span');
            textSpan.textContent = text;
            div.appendChild(textSpan);
        } else {
            div.textContent = 'You: ' + text;
        }
        
        transcript.appendChild(div);
        transcript.scrollTop = transcript.scrollHeight;
    }
    
    function cleanup() {
        stopRecording();
        if (ws) {
            ws.close();
            ws = null;
        }
        audioQueue = [];
        isPlaying = false;
    }
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', cleanup);
})();

