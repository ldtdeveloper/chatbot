
import os
import json
import asyncio
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3
from typing import Optional, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database
DB_PATH = os.path.abspath(Path(__file__).parent.parent / "voice_assistant.db")

def get_agent(agent_id: int) -> Optional[Dict]:
    """
    Fetch agent by id from the voice_assistant.db.
    Returns None if not found, else a dict with keys from DB columns.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None

        columns = [col[0] for col in cursor.description]
        agent = dict(zip(columns, row))

        # Parse JSON config if exists
        if agent.get("agent_config"):
            try:
                agent["agent_config"] = json.loads(agent["agent_config"])
            except json.JSONDecodeError:
                agent["agent_config"] = {}
        else:
            agent["agent_config"] = {}

        conn.close()
        print(f"[DB] Loaded agent #{agent_id}: {agent.get('name', 'Unknown')}")
        print(f"[DB] Instructions: {agent.get('instructions', 'None')[:100]}...")
        return agent
    except Exception as e:
        print(f"[DB] Error fetching agent {agent_id}: {e}")
        return None


# FastAPI Setup
app = FastAPI(title="Realtime Voice Agent Proxy")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).resolve().parent
WIDGET_DIR = BASE_DIR / "widget-files"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable. Please set it in your .env file")

# Client tracking
clients: Dict[WebSocket, websockets.WebSocketClientProtocol] = {}
client_agent: Dict[WebSocket, Optional[Dict]] = {}

# Endpoints
@app.get("/get-widget")
async def get_widget():
    """Serve widget files to the frontend"""
    try:
        html = (WIDGET_DIR / "chatbot.html").read_text(encoding="utf-8")
        css = (WIDGET_DIR / "chatbot.css").read_text(encoding="utf-8")
        js = (WIDGET_DIR / "chatbot.js").read_text(encoding="utf-8")
        return JSONResponse({"html": html, "css": css, "js": js})
    except FileNotFoundError as e:
        return JSONResponse({"error": f"Widget file not found: {e}"}, status_code=404)
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)

# Serve static files
app.mount("/static", StaticFiles(directory=WIDGET_DIR), name="static")

# WebSocket Handler
@app.websocket("/ws")
async def websocket_proxy(ws: WebSocket):
    """Main WebSocket endpoint for browser widget"""
    await ws.accept()
    print("[WS] Client connected")
    openai_ws = None
    assigned_agent = None

    try:
        while True:
            text = await ws.receive_text()
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "error": "Invalid JSON"})
                continue

            action = data.get("action")
            print(f"[WS] Action: {action}")

            if action == "set_agent":
                agent_id = data.get("agent_id")
                if agent_id is None:
                    await ws.send_json({"type": "error", "error": "missing agent_id"})
                    continue
                
                agent = get_agent(agent_id)
                if not agent:
                    await ws.send_json({"type": "error", "error": f"Agent {agent_id} not found in database"})
                    continue
                
                client_agent[ws] = agent
                assigned_agent = agent
                
                await ws.send_json({
                    "type": "agent_set", 
                    "agent_id": agent_id, 
                    "name": agent.get("name", "Unknown"),
                    "instructions_preview": agent.get("instructions", "")[:100] + "..."
                })
                print(f"[WS] Agent #{agent_id} '{agent.get('name')}' assigned to client")

                if ws in clients:
                    openai_ws = clients[ws]
                    if openai_ws.open:
                        instructions = get_agent_instructions(agent)
                        if instructions:
                            await openai_ws.send(json.dumps({
                                "type": "session.update",
                                "session": {"instructions": instructions}
                            }))
                            print("[WS] Updated OpenAI session with agent instructions")

            elif action == "connect":
                assigned_agent = client_agent.get(ws)
                if assigned_agent:
                    print(f"[WS] Connecting with agent: {assigned_agent.get('name', 'Unknown')}")
                else:
                    print("[WS] Connecting without specific agent")
                
                openai_ws = await connect_openai(ws, assigned_agent)
                clients[ws] = openai_ws
                print("[WS] OpenAI session established")

            elif action == "prompt":
                prompt = data.get("prompt", "").strip()
                if not prompt:
                    await ws.send_json({"type": "error", "error": "empty prompt"})
                    continue
                
                print(f"[WS] Custom prompt received: {prompt[:100]}...")
                
                if ws in clients:
                    openai_ws = clients[ws]
                    if openai_ws.open:
                        await openai_ws.send(json.dumps({
                            "type": "session.update",
                            "session": {"instructions": prompt}
                        }))
                        await ws.send_json({"type": "prompt_set", "text": prompt})
                        print("[WS] Updated OpenAI session with custom prompt")
                        continue
                
                client_agent[ws] = {"instructions": prompt, "name": "Custom Prompt"}
                await ws.send_json({"type": "prompt_set", "text": prompt})

            elif action == "audio_chunk":
                if ws not in clients:
                    continue
                
                openai_ws = clients[ws]
                if openai_ws.open:
                    audio_data = data.get("audio")
                    if audio_data:
                        await openai_ws.send(json.dumps({
                            "type": "input_audio_buffer.append",
                            "audio": audio_data
                        }))

            elif action == "commit":
                if ws not in clients:
                    print("[WS] Commit received but no OpenAI session")
                    continue
                
                openai_ws = clients[ws]
                if openai_ws.open:
                    await openai_ws.send(json.dumps({
                        "type": "input_audio_buffer.commit"
                    }))
                    await openai_ws.send(json.dumps({
                        "type": "response.create"
                    }))
                    print("[WS] Committed audio & requested response")

            else:
                print(f"[WS] Unknown action: {action}")

    except WebSocketDisconnect:
        print("[WS] Client disconnected")
    except Exception as e:
        print(f"[WS] Exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if ws in clients:
            openai_ws = clients.pop(ws)
            try:
                await openai_ws.close()
                print("[WS] Closed OpenAI connection")
            except:
                pass
        client_agent.pop(ws, None)
        try:
            await ws.close()
        except:
            pass


# Helper to get instructions
def get_agent_instructions(agent: Dict) -> Optional[str]:
    """Extract instructions from agent dict"""
    if not agent:
        return None
    
    instructions = agent.get("instructions")
    if instructions:
        return instructions
    
    config = agent.get("agent_config", {})
    if isinstance(config, dict):
        instructions = config.get("instructions")
        if instructions:
            return instructions
    
    instructions = agent.get("system_prompt")
    if instructions:
        return instructions
    
    return None


# OpenAI Connection
async def connect_openai(client_ws: WebSocket, agent: Optional[Dict] = None):
    """Connect to OpenAI Realtime API and configure session with agent instructions"""
    ws_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }
    
    try:
        openai_ws = await websockets.connect(ws_url, extra_headers=headers)
        print("[OpenAI] Connected to Realtime API")
    except Exception as e:
        print(f"[OpenAI] Connection failed: {e}")
        await client_ws.send_json({"type": "error", "error": "Failed to connect to OpenAI"})
        raise

    instructions = get_agent_instructions(agent)

    session_payload = {
        "type": "session.update",
        "session": {
            "modalities": ["audio", "text"],
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {"model": "whisper-1"},
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500
            }
        }
    }
    
    if instructions:
        session_payload["session"]["instructions"] = instructions
        agent_name = agent.get("name", "Unknown") if agent else "Custom"
        print(f"[OpenAI] Applying agent instructions from '{agent_name}'")
        print(f"[OpenAI] Preview: {instructions[:200]}...")
    else:
        print("[OpenAI] No agent instructions - using default behavior")

    await openai_ws.send(json.dumps(session_payload))
    print("[OpenAI] Session configured")

    asyncio.create_task(handle_openai_messages(openai_ws, client_ws))
    
    await client_ws.send_json({"type": "connected"})
    return openai_ws


# OpenAI Message Handler
async def handle_openai_messages(openai_ws, client_ws):
    """Receive messages from OpenAI and forward to browser client"""
    assistant_text = ""
    
    try:
        async for msg in openai_ws:
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                continue

            event_type = data.get("type", "")
            
            if event_type == "conversation.item.input_audio_transcription.completed":
                transcript = data.get("transcript", "")
                if transcript:
                    await client_ws.send_json({"type": "transcript_user", "text": transcript})
                    print(f"[OpenAI] User: {transcript}")

            elif event_type == "response.audio_transcript.delta":
                assistant_text += data.get("delta", "")

            elif event_type == "response.audio_transcript.done":
                if assistant_text:
                    await client_ws.send_json({"type": "transcript_assistant", "text": assistant_text})
                    print(f"[OpenAI] Assistant: {assistant_text}")
                    assistant_text = ""

            elif event_type == "response.audio.delta":
                delta = data.get("delta")
                if delta:
                    await client_ws.send_json({"type": "audio_chunk", "audio": delta})

            elif event_type == "response.done":
                await client_ws.send_json({"type": "response_done"})
                print("[OpenAI] Response complete")

            elif event_type == "input_audio_buffer.speech_started":
                await client_ws.send_json({"type": "speech_started"})
                print("[OpenAI] User started speaking")

            elif event_type == "input_audio_buffer.speech_stopped":
                await client_ws.send_json({"type": "speech_stopped"})
                print("[OpenAI] User stopped speaking")

            elif event_type == "error":
                error_msg = data.get("error", {}).get("message", "Unknown error")
                await client_ws.send_json({"type": "error", "error": error_msg})
                print(f"[OpenAI] Error: {error_msg}")

    except Exception as e:
        print(f"[OpenAI] Message handler error: {e}")
    finally:
        try:
            await openai_ws.close()
        except:
            pass

print("=" * 60)
print(" Voice Bot Backend Server Ready!")
print("=" * 60)
print(f" Database: {DB_PATH}")
print(f" OpenAI Key: {'Set' if OPENAI_API_KEY else 'Missing'}")
print("=" * 60)
