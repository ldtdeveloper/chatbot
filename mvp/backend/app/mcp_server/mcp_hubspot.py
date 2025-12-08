# HubSpot MCP Server with Conversation Logging
import os
from mcp.server.fastmcp import FastMCP
import httpx
import asyncio
import sys
from datetime import datetime
from pathlib import Path

mcp = FastMCP("hubspot")
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY")
HUBSPOT_BASE = "https://api.hubapi.com"

def log(*args):
    """Safe debug logger -> only writes to stderr"""
    import sys
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"[{timestamp}] " + " ".join(str(a) for a in args) + "\n"
    sys.stderr.write(message)
    sys.stderr.flush()
    
    # Also write to file for debugging
    try:
        log_file = Path(__file__).parent.parent / "logs" / "mcp_hubspot.log"
        log_file.parent.mkdir(exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(message)
    except:
        pass

async def hubspot_request(endpoint: str, method="GET", data=None):
    """Make requests to HubSpot API safely"""
    url = f"{HUBSPOT_BASE}{endpoint}"
    headers = {
        "Authorization": f"Bearer {HUBSPOT_API_KEY}",
        "Content-Type": "application/json"
    }
    log(f"[MCP] HubSpot API Request → {method} {url}")

    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                resp = await asyncio.shield(client.get(url, headers=headers, timeout=15.0))
            elif method == "POST":
                resp = await asyncio.shield(client.post(url, json=data, headers=headers, timeout=15.0))
            elif method == "PATCH":
                resp = await asyncio.shield(client.patch(url, json=data, headers=headers, timeout=15.0))
            
            log(f"[MCP] HubSpot Response: {resp.status_code}")
            resp.raise_for_status()
            return resp.json()
        except asyncio.CancelledError:
            log("[MCP] ❗ HubSpot request cancelled")
            return {"error": "Request cancelled"}
        except Exception as e:
            log("[MCP] ❗ HubSpot API Error:", e)
            return {"error": str(e)}


# ---------------- CONVERSATION LOGGING ---------------- #

@mcp.tool()
async def log_conversation_message(
    user_message: str,
    assistant_message: str,
    contact_email: str = None,
    contact_name: str = None,
    session_id: str = None
) -> dict:
    """
    REQUIRED: Log every conversation exchange to HubSpot.
    Call this after EVERY user-assistant interaction.
    
    Args:
        user_message: What the user said
        assistant_message: Your response to the user
        contact_email: User's email (optional, but preferred)
        contact_name: User's name (optional)
        session_id: Unique session identifier (optional)
    
    Returns:
        Success confirmation with note_id and contact_id
    """
    log(f"[MCP] log_conversation_message() - Contact: {contact_email or contact_name or 'Anonymous'}")
    
    contact_id = None
    
    # Step 1: Find or create contact
    if contact_email:
        # Try to find existing contact by email
        result = await hubspot_request(
            f"/crm/v3/objects/contacts/{contact_email}?idProperty=email&properties=firstname,lastname,email"
        )
        
        if "error" not in result:
            contact_id = result.get("id")
            log(f"[MCP] Found existing contact: {contact_id}")
        else:
            # Create new contact
            properties = {"email": contact_email}
            if contact_name:
                name_parts = contact_name.split(" ", 1)
                properties["firstname"] = name_parts[0]
                if len(name_parts) > 1:
                    properties["lastname"] = name_parts[1]
            
            create_result = await hubspot_request(
                "/crm/v3/objects/contacts",
                method="POST",
                data={"properties": properties}
            )
            
            if "error" not in create_result:
                contact_id = create_result.get("id")
                log(f"[MCP] Created new contact: {contact_id}")
    
    # Step 2: Create engagement (note) with the conversation
    timestamp = datetime.now().isoformat()
    note_body = f"""Conversation Log
Time: {timestamp}
Session: {session_id or 'N/A'}
Contact: {contact_email or contact_name or 'Anonymous'}

USER: {user_message}

ASSISTANT: {assistant_message}
"""
    
    engagement_data = {
        "properties": {
            "hs_timestamp": datetime.now().strftime("%s000"),  # Unix timestamp in milliseconds
            "hs_note_body": note_body,
            "hubspot_owner_id": None  # You can set an owner ID if needed
        }
    }
    
    # Associate with contact if we have one
    if contact_id:
        engagement_data["associations"] = [
            {
                "to": {"id": contact_id},
                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 202}]
            }
        ]
    
    note_result = await hubspot_request(
        "/crm/v3/objects/notes",
        method="POST",
        data=engagement_data
    )
    
    if "error" in note_result:
        return {
            "success": False,
            "error": note_result["error"],
            "message": "Failed to log conversation to HubSpot"
        }
    
    log(f"[MCP] Conversation logged successfully - Note ID: {note_result.get('id')}")
    
    return {
        "success": True,
        "note_id": note_result.get("id"),
        "contact_id": contact_id,
        "message": "Conversation logged to HubSpot successfully",
        "logged_at": timestamp
    }


#  ORIGINAL TOOLS  #

@mcp.tool()
async def get_contact_by_email(email: str) -> dict:
    """Get contact information from HubSpot by email"""
    log(f"[MCP] get_contact_by_email(): {email}")
    result = await hubspot_request(
        f"/crm/v3/objects/contacts/{email}?idProperty=email&properties=firstname,lastname,email,phone,company,jobtitle"
    )

    if "error" in result:
        return {
            "found": False,
            "error": result["error"],
            "message": f"Contact with email {email} not found in HubSpot"
        }

    props = result.get("properties", {})
    contact_info = {
        "found": True,
        "hubspot_id": result.get("id"),
        "email": props.get("email"),
        "firstname": props.get("firstname"),
        "lastname": props.get("lastname"),
        "phone": props.get("phone"),
        "company": props.get("company"),
        "jobtitle": props.get("jobtitle"),
        "full_name": f"{props.get('firstname', '')} {props.get('lastname', '')}".strip()
    }

    log(f"[MCP] Contact Found → {contact_info['full_name']} (ID: {contact_info['hubspot_id']})")
    return contact_info


@mcp.tool()
async def create_contact(
    email: str, 
    firstname: str, 
    lastname: str, 
    phone: str = None, 
    company: str = None
) -> dict:
    """Create a new contact in HubSpot"""
    log(f"[MCP] create_contact(): {firstname} {lastname} ({email})")

    properties = {"email": email, "firstname": firstname, "lastname": lastname}
    if phone: 
        properties["phone"] = phone
    if company: 
        properties["company"] = company

    data = {"properties": properties}
    result = await hubspot_request("/crm/v3/objects/contacts", method="POST", data=data)

    if "error" in result:
        return {"success": False, "error": result["error"]}

    props = result.get("properties", {})
    contact_info = {
        "success": True,
        "hubspot_id": result.get("id"),
        "email": props.get("email"),
        "firstname": props.get("firstname"),
        "lastname": props.get("lastname"),
        "phone": props.get("phone"),
        "company": props.get("company"),
        "message": f"Contact created successfully with ID: {result.get('id')}"
    }

    log(f"[MCP] Contact Created → ID {contact_info['hubspot_id']}")
    return contact_info


@mcp.tool()
async def capture_request_hubspot(
    name: str = None,
    email: str = None,
    products_requested: list = None,
    services_requested: list = None
) -> dict:
    """Capture a product/service request in HubSpot"""
    log(f"[MCP] capture_request_hubspot(): {email}")
    products_requested = products_requested or []
    services_requested = services_requested or []
    contact = None
    is_returning = False

    if email:
        result = await hubspot_request(
            f"/crm/v3/objects/contacts/{email}?idProperty=email&properties=firstname,lastname,email,last_requested_product,last_requested_service"
        )
        if "error" not in result:
            contact = result
            is_returning = True

    properties = {
        "firstname": name.split()[0] if name else None,
        "lastname": " ".join(name.split()[1:]) if name and len(name.split()) > 1 else None,
        "email": email,
        "last_requested_product": ", ".join(products_requested) if products_requested else None,
        "last_requested_service": ", ".join(services_requested) if services_requested else None,
    }
    properties = {k: v for k, v in properties.items() if v is not None}

    if contact:
        hubspot_id = contact.get("id")
        await hubspot_request(
            f"/crm/v3/objects/contacts/{hubspot_id}", 
            method="PATCH", 
            data={"properties": properties}
        )
        message = f"Welcome back {name}! Your new request has been recorded."
    else:
        result = await hubspot_request(
            "/crm/v3/objects/contacts", 
            method="POST", 
            data={"properties": properties}
        )
        hubspot_id = result.get("id")
        message = f"Thank you {name}! Your request has been saved."

    log(f"[MCP] capture_request complete → {email}")
    return {
        "success": True,
        "is_returning": is_returning,
        "hubspot_id": hubspot_id,
        "message": message,
        "products_requested": products_requested,
        "services_requested": services_requested
    }



if __name__ == "__main__":
    log("Initializing HubSpot MCP server with conversation logging...")
    log("HubSpot MCP Server Running - Ready to log conversations!")
    mcp.run(transport="stdio")