(function() {
    // Get configuration from script tag data attributes
    const scriptTag = document.currentScript || document.querySelector('script[data-agent-id]');
    const agentId = scriptTag ? parseInt(scriptTag.getAttribute('data-agent-id')) : null;
    const apiBaseUrl = scriptTag ? scriptTag.getAttribute('data-api-url') : null;
    const agentName = scriptTag ? scriptTag.getAttribute('data-agent-name') : 'Voice Assistant';
    const targetDivId = scriptTag ? scriptTag.getAttribute('data-target-id') : 'chatbot';
    
    if (!agentId || !apiBaseUrl) {
        console.error('[Widget] Missing required configuration: agentId or apiBaseUrl');
        return;
    }
    
    // Inject CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = apiBaseUrl.replace(/\/$/, '') + '/api/widget/widget-static.css';
    document.head.appendChild(link);
    
    // HTML
    const widgetHTML = `
        <div id="voice-widget-panel-wrapper">
            <div id="voice-widget-header">${agentName}</div>
            <div id="voice-widget-transcript"></div>
            <div id="voice-widget-status">Ready</div>
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

    const targetDiv = document.getElementById(targetDivId);
    if (!targetDiv) {
        console.error('[Widget] Target div not found:', targetDivId);
        return;
    }
    
    // Make sure target div has proper positioning
    const targetStyle = window.getComputedStyle(targetDiv);
    if (targetStyle.position === 'static') {
        targetDiv.style.position = 'relative';
    }
    
    // Wrap in outer container that inherits parent dimensions
    targetDiv.innerHTML = `<div id="voice-widget-container">${widgetHTML}</div>`;
    
    // JS logic
    const button = document.getElementById('voice-widget-button');
    const panel = document.getElementById('voice-widget-panel-wrapper');
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
    
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsHost = apiBaseUrl.replace(/^https?:/, '').replace(/^\/\//, '');
    const wsUrl = `${wsProtocol}//${wsHost}/api/widget/ws?agent_id=${agentId}`;
    
    function updateButtonIcon(showStop) {
        micIcon.style.display = showStop ? 'none' : 'block';
        stopIcon.style.display = showStop ? 'block' : 'none';
        button.title = showStop ? 'Stop Conversation' : agentName;
    }
    
    button.addEventListener('click', function() {
        if (isConnected || isRecording) {
            stopConversation();
        } else {
            if (!isConnected) connect();
        }
    });
    
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
    
    function stopConversation() {
        if (ws && ws.readyState === WebSocket.OPEN) ws.close();
        cleanup();
        updateButtonIcon(false);
        status.textContent = 'Stopped';
    }
    
    function handleMessage(data) {
        switch (data.type) {
            case 'connected': status.textContent = 'Connected - Ready'; startRecording(); break;
            case 'transcript_user': addTranscript('user', data.text); break;
            case 'transcript_assistant': addTranscript('assistant', data.text); break;
            case 'audio_chunk': if (data.audio) queueAudio(data.audio); break;
            case 'speech_started': status.textContent = 'Listening...'; button.classList.add('recording'); break;
            case 'speech_stopped': status.textContent = 'Processing...'; button.classList.remove('recording'); break;
            case 'response_done': status.textContent = 'Ready'; break;
            case 'error': status.textContent = 'Error: ' + data.error; console.error('[Widget] Error:', data.error); break;
        }
    }
    
    async function startRecording() {
        if (isRecording) return;
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            const isHttp = window.location.protocol === 'http:';
            const isLocalhost = window.location.hostname.includes('localhost') || window.location.hostname === '127.0.0.1';
            let errorMsg = isHttp && !isLocalhost ? 'Microphone access requires HTTPS' : 'Microphone access is not available in this browser';
            console.error('[Widget]', errorMsg);
            status.textContent = errorMsg;
            alert(errorMsg);
            return;
        }
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, sampleRate: 24000, echoCancellation: true, noiseSuppression: true, autoGainControl: true } });
            audioContext = new (window.AudioContext || window.webkitAudioContext)();
            source = audioContext.createMediaStreamSource(stream);
            processor = audioContext.createScriptProcessor(4096, 1, 1);
            const gainNode = audioContext.createGain();
            gainNode.gain.value = 0;
            source.connect(processor); processor.connect(gainNode); gainNode.connect(audioContext.destination);
            processor.onaudioprocess = function(e) {
                if (!isConnected || !isRecording) return;
                let audioData = e.inputBuffer.getChannelData(0);
                if (audioContext.sampleRate !== 24000) audioData = resampleAudio(audioData, audioContext.sampleRate, 24000);
                const pcm16 = float32ToPCM16(audioData);
                const base64Audio = arrayBufferToBase64(pcm16.buffer);
                if (ws && ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ action: 'audio_chunk', audio: base64Audio }));
            };
            isRecording = true; status.textContent = 'Recording...';
        } catch (err) { console.error('[Widget] Recording error:', err); status.textContent = 'Microphone access denied'; }
    }
    
    function stopRecording() {
        if (!isRecording) return;
        if (processor) { processor.disconnect(); processor = null; }
        if (source) { source.disconnect(); source = null; }
        if (stream) { stream.getTracks().forEach(track => track.stop()); stream = null; }
        if (audioContext && audioContext.state !== 'closed') { audioContext.close(); audioContext = null; }
        isRecording = false;
    }
    
    function queueAudio(base64Audio) { audioQueue.push(base64Audio); if (!isPlaying) playNextAudio(); }
    async function playNextAudio() {
        if (audioQueue.length === 0) { isPlaying = false; return; }
        isPlaying = true;
        const base64Audio = audioQueue.shift();
        try {
            const binaryString = atob(base64Audio);
            const bytes = new Uint8Array(binaryString.length);
            for (let i = 0; i < binaryString.length; i++) bytes[i] = binaryString.charCodeAt(i);
            const playbackContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
            const pcm16 = new Int16Array(bytes.buffer);
            const float32 = new Float32Array(pcm16.length);
            for (let i = 0; i < pcm16.length; i++) float32[i] = pcm16[i] / 32768.0;
            const audioBuffer = playbackContext.createBuffer(1, float32.length, 24000);
            audioBuffer.getChannelData(0).set(float32);
            const bufferSource = playbackContext.createBufferSource();
            bufferSource.buffer = audioBuffer;
            bufferSource.connect(playbackContext.destination);
            bufferSource.onended = function() { playbackContext.close(); playNextAudio(); };
            bufferSource.start(0);
        } catch (err) { console.error('[Widget] Playback error:', err); playNextAudio(); }
    }
    
    function resampleAudio(inputData, inputSampleRate, outputSampleRate) {
        if (inputSampleRate === outputSampleRate) return inputData;
        const ratio = inputSampleRate / outputSampleRate;
        const outputLength = Math.round(inputData.length / ratio);
        const output = new Float32Array(outputLength);
        for (let i = 0; i < outputLength; i++) {
            const index = i * ratio;
            const indexFloor = Math.floor(index);
            const indexCeil = Math.min(indexFloor + 1, inputData.length - 1);
            const fraction = index - indexFloor;
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
        for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
        return btoa(binary);
    }
    
    function addTranscript(role, text) {
        const div = document.createElement('div');
        div.className = 'transcript-' + role;
        if (role === 'assistant') {
            const icon = document.createElement('span');
            icon.className = 'ai-icon'; icon.innerHTML = '🗩'; div.appendChild(icon);
            const textSpan = document.createElement('span'); textSpan.textContent = text; div.appendChild(textSpan);
        } else div.textContent = 'You: ' + text;
        transcript.appendChild(div);
        transcript.scrollTop = transcript.scrollHeight;
    }
    
    function cleanup() { stopRecording(); if (ws) { ws.close(); ws = null; } audioQueue = []; isPlaying = false; }
    window.addEventListener('beforeunload', cleanup);
})();