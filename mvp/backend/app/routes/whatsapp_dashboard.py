from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.whatsapp_configs import WhatsappConfig


router = APIRouter(prefix="/api", tags=["dashboard"])

@router.get("/human-agent/owner-info/{slug}")
def get_owner_info(slug: str, db: Session = Depends(get_db)):

    # Step 1: find config
    config = db.query(WhatsappConfig).filter(
        WhatsappConfig.dashboard_slug == slug
    ).first()

    if not config:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    # Step 2: find agent
    agent = db.query(TextAgent).filter(
        TextAgent.id == config.text_agent_id
    ).first()

    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Step 3: find owner
    owner = db.query(User).filter(
        User.id == TextAgent.user_id
    ).first()

    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    # Return a simple professional HTML page (can be enhanced)
    html_content =  """
    <!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Agent Dashboard</title>
  <script>
    const API_BASE = "http://localhost:8000";
    const WS_BASE = "ws://localhost:8000/ws/dashboard";
    let ws;
    let agentName = prompt("Enter your name:");

    const handoffs = {};
    let activeUser = null;

    function connectWS() {
      ws = new WebSocket(WS_BASE);
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("WS Received:", data);

        if (data.type === "new_message" && activeUser && activeUser.whatsapp_number === data.whatsapp_number) {
          addMessage(data.content, true);
        }

        if (data.type === "handoff_alert") {
          handoffs[data.whatsapp_number] = data;
          renderQueue();
        }

        if (data.type === "agent_assigned") {
          if (handoffs[data.whatsapp_number]) {
            handoffs[data.whatsapp_number].assigned_agent = data.agent_name;
          }
          renderQueue();
        }
      };
      ws.onclose = () => setTimeout(connectWS, 3000);
    }

    function addMessage(msg, fromUser) {
      const chat = document.getElementById("chat-log");
      const bubble = document.createElement("div");
      bubble.className = fromUser ? "bubble incoming" : "bubble outgoing";
      bubble.innerText = msg;
      chat.appendChild(bubble);
      chat.scrollTop = chat.scrollHeight;
    }

    function claimUser(number) {
      if (!activeUser) return;
      ws.send(JSON.stringify({ type: "claim", whatsapp_number: number, agent_name: agentName }));
      activeUser = handoffs[number];
      renderQueue();
    }

    function sendMessage() {
      const input = document.getElementById("agent-input");
      const msg = input.value.trim();
      if (!msg || !activeUser) return;
      ws.send(JSON.stringify({ type: "message", to: activeUser.whatsapp_number, text: msg }));
      addMessage(msg, false);
      input.value = "";
    }

    function selectUser(number) {
      activeUser = handoffs[number];
      document.getElementById("chat-log").innerHTML = "";
    }

    function renderQueue() {
      const queue = document.getElementById("handoff-queue");
      queue.innerHTML = "";
      Object.values(handoffs).forEach(h => {
        const item = document.createElement("div");
        item.className = "queue-item";
        item.innerText = `+${h.whatsapp_number} ${h.summary || ""} ${h.assigned_agent ? "(Booked by "+h.assigned_agent+")" : "(Unclaimed)"}`;
        item.onclick = () => selectUser(h.whatsapp_number);
        queue.appendChild(item);
      });
    }

    window.onload = () => {
      connectWS();
    };
  </script>
  <style>
    body { margin:0; font-family: Arial, sans-serif; background:#0c1317; color:#e9edef; display:flex; height:100vh; }
    .sidebar { width:300px; background:#202c33; overflow-y:auto; padding:10px; }
    .queue-item { padding:8px; border-bottom:1px solid #222d34; cursor:pointer; }
    .queue-item:hover { background:#2a3942; }
    .main { flex:1; display:flex; flex-direction:column; }
    header { background:#202c33; padding:10px; font-weight:bold; display:flex; justify-content:space-between; }
    #chat-log { flex:1; padding:10px; overflow-y:auto; background:#0b141a; }
    .bubble { padding:8px 12px; border-radius:12px; margin:5px 0; max-width:70%; }
    .incoming { background:#2a3942; align-self:flex-start; }
    .outgoing { background:#00a884; align-self:flex-end; color:#0b141a; }
    footer { padding:10px; background:#202c33; display:flex; gap:10px; }
    input { flex:1; padding:8px; border-radius:8px; border:none; outline:none; }
    button { padding:8px 12px; background:#00a884; border:none; border-radius:8px; color:#0b141a; font-weight:bold; cursor:pointer; }
  </style>
</head>
<body>
  <div class="sidebar">
    <h3>Handoff Queue</h3>
    <div id="handoff-queue"></div>
  </div>
  <div class="main">
    <header>
      <span>Agent: <strong id="agent-name"></strong></span>
      <span>Status: Online</span>
    </header>
    <div id="chat-log"></div>
    <footer>
      <input type="text" id="agent-input" placeholder="Type a message..."/>
      <button onclick="sendMessage()">Send</button>
    </footer>
  </div>
  <script>
    document.getElementById("agent-name").innerText = agentName;
  </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)