
(async () => {
  console.info("[Voice Bot] Initializing...");

  const WS_URL = "ws://your address/ws";
  let ws = null;
  let audioContext = null;
  let processor = null;
  let source = null;
  let stream = null;
  let isRecording = false;
  let isConnected = false;
  
  // Audio playback queue
  let audioQueue = [];
  let isPlaying = false;


  // WebSocket Setup

  async function initWebSocket() {
    return new Promise((resolve, reject) => {
      ws = new WebSocket(WS_URL);

      ws.onopen = () => {
        console.info("[WS] Connected to server");
        isConnected = true;
        
        // Establish OpenAI session
        ws.send(JSON.stringify({ action: "connect" }));
        resolve();
      };

      ws.onmessage = handleServerMessage;

      ws.onclose = () => {
        console.info("[WS] Connection closed");
        isConnected = false;
        cleanup();
      };

      ws.onerror = (err) => {
        console.error("[WS] Error:", err);
        isConnected = false;
        reject(err);
      };
    });
  }


  // Message Handler

  function handleServerMessage(event) {
    try {
      const data = JSON.parse(event.data);
      const type = data.type;

      switch (type) {
        case "connected":
          console.info("[WS] OpenAI session established");
          updateStatus("Connected - Ready to chat");
          break;

        case "transcript_user":
          console.log(" You:", data.text);
          displayTranscript("user", data.text);
          break;

        case "transcript_assistant":
          console.log(" Assistant:", data.text);
          displayTranscript("assistant", data.text);
          break;

        case "audio_chunk":
          // Queue audio for playback
          if (data.audio) {
            queueAudio(data.audio);
          }
          break;

        case "response_done":
          console.info("[Response] Complete");
          break;

        case "speech_started":
          console.info("[VAD] User started speaking");
          updateStatus("Listening...");
          break;

        case "speech_stopped":
          console.info("[VAD] User stopped speaking");
          updateStatus("Processing...");
          break;

        case "agent_set":
          console.info(`[Agent] Set to: ${data.name}`);
          updateStatus(`Agent: ${data.name}`);
          break;

        case "prompt_set":
          console.info("[Prompt] Updated");
          break;

        case "error":
          console.error("[Error]", data.error);
          updateStatus(`Error: ${data.error}`);
          break;

        default:
          console.log("[WS] Unknown message type:", type);
      }
    } catch (err) {
      console.error("[WS] Parse error:", err);
    }
  }

  // Audio Recording

  async function startRecording() {
    if (isRecording) {
      console.warn("[Audio] Already recording");
      return;
    }

    try {
      // Request microphone access
      stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 24000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        } 
      });

      audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 24000
      });
      
      source = audioContext.createMediaStreamSource(stream);

      // Use ScriptProcessor for audio processing
      const bufferSize = 4096;
      processor = audioContext.createScriptProcessor(bufferSize, 1, 1);
      
      source.connect(processor);
      processor.connect(audioContext.destination);

      processor.onaudioprocess = (e) => {
        if (!isConnected || !isRecording) return;

        const inputData = e.inputBuffer.getChannelData(0);
        
        // Convert Float32Array to 16-bit PCM
        const pcm16 = float32ToPCM16(inputData);
        
        // Convert to base64
        const base64Audio = arrayBufferToBase64(pcm16.buffer);
        
        // Send to server
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            action: "audio_chunk",
            audio: base64Audio
          }));
        }
      };

      isRecording = true;
      console.info("[Audio] Recording started");
      updateStatus("Recording...");
      
    } catch (err) {
      console.error("[Audio] Recording error:", err);
      updateStatus("Microphone access denied");
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
    console.info("[Audio] Recording stopped");
    updateStatus("Ready");
  }


  // Audio Playback
 
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
      // Decode base64 to PCM16
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }

      // Create audio context for playback
      const playbackContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 24000
      });

      // Convert PCM16 to Float32
      const pcm16 = new Int16Array(bytes.buffer);
      const float32 = new Float32Array(pcm16.length);
      for (let i = 0; i < pcm16.length; i++) {
        float32[i] = pcm16[i] / 32768.0;
      }

      // Create audio buffer
      const audioBuffer = playbackContext.createBuffer(1, float32.length, 24000);
      audioBuffer.getChannelData(0).set(float32);

      // Play audio
      const bufferSource = playbackContext.createBufferSource();
      bufferSource.buffer = audioBuffer;
      bufferSource.connect(playbackContext.destination);
      
      bufferSource.onended = () => {
        playbackContext.close();
        playNextAudio();
      };

      bufferSource.start(0);
      
    } catch (err) {
      console.error("[Audio] Playback error:", err);
      playNextAudio(); // Try next audio
    }
  }

 
  // Helper Functions
  
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

  function updateStatus(message) {
    const statusEl = document.getElementById("voice-bot-status");
    if (statusEl) {
      statusEl.textContent = message;
    }
    console.info(`[Status] ${message}`);
  }

  function displayTranscript(role, text) {
    const transcriptEl = document.getElementById("voice-bot-transcript");
    if (transcriptEl) {
      const msgDiv = document.createElement("div");
      msgDiv.className = `transcript-${role}`;
      msgDiv.textContent = `${role === 'user' ? '🎤' : '🤖'} ${text}`;
      transcriptEl.appendChild(msgDiv);
      transcriptEl.scrollTop = transcriptEl.scrollHeight;
    }
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

  
  // Public API

  window.voiceBot = {
    start: startRecording,
    stop: stopRecording,
    setAgent: (agentId) => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "set_agent", agent_id: agentId }));
      }
    },
    setPrompt: (prompt) => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "prompt", prompt: prompt }));
      }
    },
    commit: () => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "commit" }));
      }
    }
  };

 
  // Initialize

  try {
    await initWebSocket();
    await startRecording();
    console.info("[Voice Bot] Ready!");
  } catch (err) {
    console.error("[Voice Bot] Initialization failed:", err);
    updateStatus("Failed to initialize");
  }

  // Cleanup on page unload
  window.addEventListener("beforeunload", cleanup);

})();