# Noise Reduction Features in Backend

## Overview

The backend implements noise reduction features through OpenAI's Realtime API configuration. These features help improve voice recognition accuracy by filtering background noise and optimizing speech detection.

---

## Noise Reduction Components

### 1. **Noise Reduction Mode** (`noise_reduction_mode`)

**Location**: `mvp/backend/app/models/agent.py`

**Available Modes**:
- **`NEAR_FIELD`** (`"near_field"`): Optimized for close-range microphones (e.g., headset, phone)
- **`FAR_FIELD`** (`"far_field"`): Optimized for distant microphones (e.g., room microphones, conference calls)

**Default**: `NEAR_FIELD`

**Implementation**:
```python
class NoiseReductionMode(str, enum.Enum):
    NEAR_FIELD = "near_field"
    FAR_FIELD = "far_field"
```

**Usage in OpenAI Realtime API**:
```python
session_payload["session"]["input_audio_noise_reduction"] = {
    "type": noise_reduction_type  # "near_field" or "far_field"
}
```

---

### 2. **Voice Activity Detection (VAD) Threshold** (`noise_reduction_threshold`)

**Purpose**: Controls sensitivity of speech detection. Higher values = less sensitive (fewer false starts), lower values = more sensitive (catches quieter speech).

**Type**: String (stored as decimal, e.g., "0.5", "0.6", "0.75")

**Default**: `"0.5"`

**Current Implementation**: `0.6` (in widget.py line 590)

**Range**: Typically 0.0 to 1.0

**Usage in OpenAI Realtime API**:
```python
"turn_detection": {
    "type": "server_vad",
    "threshold": float(agent.noise_reduction_threshold)  # e.g., 0.6
}
```

---

### 3. **Prefix Padding** (`noise_reduction_prefix_padding_ms`)

**Purpose**: How many milliseconds of audio before detected speech to include. Captures the beginning of speech that might be cut off.

**Type**: Integer (milliseconds)

**Default**: `300` ms (model default)
**Current Implementation**: `200` ms (in widget.py line 591 - reduced for faster response)

**Usage in OpenAI Realtime API**:
```python
"turn_detection": {
    "prefix_padding_ms": agent.noise_reduction_prefix_padding_ms or 200
}
```

---

### 4. **Silence Duration** (`noise_reduction_silence_duration_ms`)

**Purpose**: How long to wait in silence (milliseconds) before considering the user has finished speaking and the bot should respond.

**Type**: Integer (milliseconds)

**Default**: `500` ms (model default)
**Current Implementation**: `700` ms (in widget.py line 592 - increased to wait longer before responding)

**Usage in OpenAI Realtime API**:
```python
"turn_detection": {
    "silence_duration_ms": agent.noise_reduction_silence_duration_ms or 700
}
```

---

## Database Schema

### Agent Model (`agents` table)

```python
# Noise reduction settings (for turn_detection in Realtime API)
noise_reduction_mode = Column(String, default=NoiseReductionMode.NEAR_FIELD.value)
noise_reduction_threshold = Column(String, default="0.5")  # VAD threshold
noise_reduction_prefix_padding_ms = Column(Integer, default=300)
noise_reduction_silence_duration_ms = Column(Integer, default=500)
```

---

## Implementation in Widget Route

**File**: `mvp/backend/app/routes/widget.py`

### Configuration (Lines 588-593)

```python
"turn_detection": {
    "type": "server_vad",
    "threshold": float(agent.noise_reduction_threshold) if agent.noise_reduction_threshold else 0.6,
    "prefix_padding_ms": agent.noise_reduction_prefix_padding_ms or 200,
    "silence_duration_ms": agent.noise_reduction_silence_duration_ms or 700
}
```

### Noise Reduction Mode (Lines 674-680)

```python
# Add noise reduction mode if specified
if agent.noise_reduction_mode:
    noise_reduction_type = agent.noise_reduction_mode.value if hasattr(agent.noise_reduction_mode, 'value') else str(agent.noise_reduction_mode)
    session_payload["session"]["input_audio_noise_reduction"] = {
        "type": noise_reduction_type
    }
```

---

## API Schema

### AgentCreate Schema

```python
noise_reduction_mode: Optional[str] = "near_field"
noise_reduction_threshold: Optional[str] = "0.5"
noise_reduction_prefix_padding_ms: Optional[int] = 300
noise_reduction_silence_duration_ms: Optional[int] = 500
```

### AgentUpdate Schema

```python
noise_reduction_mode: Optional[str] = None
noise_reduction_threshold: Optional[str] = None
noise_reduction_prefix_padding_ms: Optional[int] = None
noise_reduction_silence_duration_ms: Optional[int] = None
```

---

## How It Works

1. **Backend Configuration**: When an agent is created/updated, noise reduction settings are stored in the database.

2. **WebSocket Connection**: When a widget connects via WebSocket (`/api/widget/ws`), the backend:
   - Retrieves the agent's noise reduction settings
   - Configures OpenAI Realtime API session with these settings
   - Sends `session.update` message to OpenAI with:
     - `input_audio_noise_reduction.type` (near_field/far_field)
     - `turn_detection.threshold` (VAD sensitivity)
     - `turn_detection.prefix_padding_ms` (audio capture before speech)
     - `turn_detection.silence_duration_ms` (wait time before response)

3. **OpenAI Processing**: OpenAI's Realtime API applies these settings to:
   - Filter background noise based on mode (near/far field)
   - Detect speech activity using the threshold
   - Capture audio with prefix padding
   - Wait for silence duration before responding

---

## Current Default Values (in widget.py)

- **Threshold**: `0.6` (less sensitive than model default 0.5)
- **Prefix Padding**: `200` ms (faster than model default 300ms)
- **Silence Duration**: `700` ms (longer than model default 500ms)

**Note**: These are hardcoded defaults in `widget.py` and override the database defaults if not set.

---

## Recommendations

### For Close-Range Microphones (Headset, Phone)
- **Mode**: `NEAR_FIELD`
- **Threshold**: `0.5` - `0.6`
- **Prefix Padding**: `200` - `300` ms
- **Silence Duration**: `500` - `700` ms

### For Far-Range Microphones (Room, Conference)
- **Mode**: `FAR_FIELD`
- **Threshold**: `0.6` - `0.75` (higher to reduce false positives)
- **Prefix Padding**: `300` - `400` ms
- **Silence Duration**: `700` - `1000` ms

---

## Files Involved

1. **Models**: `mvp/backend/app/models/agent.py`
2. **Routes**: `mvp/backend/app/routes/widget.py` (lines 588-593, 674-680)
3. **Schemas**: `mvp/backend/app/schemas.py`
4. **Legacy Widget**: `mvp/backend/widget/main.py` (lines 333-361)

