"""
HubSpot service for syncing conversation data to HubSpot CRM
"""
import requests
import re
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


def extract_contact_info(transcript: str) -> Dict[str, Optional[str]]:
    """
    Extract contact information from conversation transcript using regex patterns.
    
    Returns:
        Dictionary with extracted contact information:
        - email: Email address
        - first_name: First name
        - last_name: Last name
        - phone: Phone number
        - company: Company name
        - notes: Conversation notes
    """
    contact_info = {
        "email": None,
        "first_name": None,
        "last_name": None,
        "phone": None,
        "company": None,
        "notes": transcript[:5000] if transcript else None  # Limit notes to 5000 chars
    }
    
    if not transcript:
        logger.warning("Empty transcript provided for contact extraction")
        return contact_info
    
    logger.info(f"Extracting contact info from transcript ({len(transcript)} chars)")
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, transcript)
    if emails:
        contact_info["email"] = emails[0].lower()
    
    # Extract phone number (various formats)
    phone_patterns = [
        r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
        r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
        r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Simple format
        r'\d{5}\s+\d{5}',  # 5 digits space 5 digits (e.g., "79862 45118")
        r'\d{4}\s+\d{4}',  # 4 digits space 4 digits
        r'\d{6}\s+\d{4}',  # 6 digits space 4 digits
        r'\d{10}',  # 10 consecutive digits
        r'phone\s*(?:number|no|#)?\s*(?:is|:)?\s*([\d\s\-\(\)\+]{10,})',  # "phone number is X"
        r'number\s*(?:is|:)?\s*([\d\s\-\(\)\+]{10,})',  # "number is X"
    ]
    for pattern in phone_patterns:
        phones = re.findall(pattern, transcript, re.IGNORECASE)
        if phones:
            # Get the first match (or the captured group if pattern has groups)
            phone_match = phones[0] if isinstance(phones[0], str) else phones[0]
            # Clean up phone number - remove spaces, dashes, dots, parentheses, but keep + and digits
            phone = re.sub(r'[-.\s()]', '', phone_match)
            # Remove leading + if followed by country code 1 (US)
            if phone.startswith('1') and len(phone) == 11:
                phone = phone[1:]
            if len(phone) >= 10:
                contact_info["phone"] = phone
                break
    
    # Extract names (look for "my name is", "I'm", "call me", etc.)
    name_patterns = [
        r'(?:my name is|i\'?m|i am|call me|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
    ]
    for pattern in name_patterns:
        matches = re.findall(pattern, transcript, re.IGNORECASE)
        if matches:
            full_name = matches[0].strip()
            # Clean up name - remove "and" if it's part of the match
            full_name = re.sub(r'\s+and\s+', ' ', full_name, flags=re.IGNORECASE)
            name_parts = full_name.split()
            # Filter out common words that might be captured
            name_parts = [p for p in name_parts if p.lower() not in ['and', 'is', 'the', 'a', 'an']]
            if len(name_parts) >= 2:
                contact_info["first_name"] = name_parts[0]
                contact_info["last_name"] = " ".join(name_parts[1:])
            elif len(name_parts) == 1:
                contact_info["first_name"] = name_parts[0]
            break
    
    # Extract company name
    company_patterns = [
        r'(?:company|work for|work at|from)\s+([A-Z][A-Za-z0-9\s&]+)',
        r'([A-Z][A-Za-z0-9\s&]+)\s+(?:inc|llc|ltd|corp|corporation)',
    ]
    for pattern in company_patterns:
        matches = re.findall(pattern, transcript, re.IGNORECASE)
        if matches:
            contact_info["company"] = matches[0].strip()
            break
    
    # Log extraction results
    logger.info(f"Extracted contact info: name={contact_info.get('first_name')} {contact_info.get('last_name')}, "
                f"email={contact_info.get('email')}, phone={contact_info.get('phone')}, company={contact_info.get('company')}")
    
    return contact_info


def create_or_update_hubspot_contact(
    access_token: str,
    contact_info: Dict[str, Optional[str]],
    conversation_notes: Optional[str] = None
) -> tuple:
    """
    Create or update a contact in HubSpot CRM.
    
    Args:
        access_token: HubSpot OAuth access token
        contact_info: Dictionary with contact information (email, first_name, last_name, phone, company)
        conversation_notes: Optional conversation transcript/notes
    
    Returns:
        HubSpot contact ID if successful, None otherwise
    """
    if not access_token:
        error_msg = "HubSpot access token is missing"
        logger.error(error_msg)
        return None, error_msg
    
    # Check if we have at least email or phone to identify/create contact
    if not contact_info.get("email") and not contact_info.get("phone"):
        error_msg = "Cannot create HubSpot contact: no email or phone provided"
        logger.warning(error_msg)
        return None, error_msg
    
    try:
        # Prepare contact properties
        properties = {}
        
        if contact_info.get("email"):
            properties["email"] = contact_info["email"]
        if contact_info.get("first_name"):
            properties["firstname"] = contact_info["first_name"]
        if contact_info.get("last_name"):
            properties["lastname"] = contact_info["last_name"]
        if contact_info.get("phone"):
            properties["phone"] = contact_info["phone"]
        if contact_info.get("company"):
            properties["company"] = contact_info["company"]
        
        # Note: HubSpot doesn't have a default "notes" property on contacts
        # We'll store conversation notes using HubSpot's Notes API after contact creation
        # DO NOT add "notes" to properties - it will cause "Property doesn't exist" error
        
        # HubSpot API endpoint for creating/updating contacts
        # Using email as unique identifier
        url = "https://api.hubapi.com/crm/v3/objects/contacts"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # First, try to find existing contact by email
        contact_id = None
        if contact_info.get("email"):
            search_url = f"https://api.hubapi.com/crm/v3/objects/contacts/search"
            search_payload = {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "email",
                                "operator": "EQ",
                                "value": contact_info["email"]
                            }
                        ]
                    }
                ],
                "properties": ["id", "email"]
            }
            
            search_response = requests.post(search_url, json=search_payload, headers=headers)
            if search_response.status_code == 200:
                results = search_response.json().get("results", [])
                if results:
                    contact_id = results[0]["id"]
                    logger.info(f"Found existing HubSpot contact: {contact_id}")
        
        # Create or update contact
        if contact_id:
            # Update existing contact
            update_url = f"{url}/{contact_id}"
            payload = {"properties": properties}
            response = requests.patch(update_url, json=payload, headers=headers)
        else:
            # Create new contact
            payload = {"properties": properties}
            response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            if not contact_id:
                # Extract contact ID from create response
                contact_data = response.json()
                contact_id = contact_data.get("id")
            
            # Optionally create a note with conversation details using HubSpot Notes API
            if conversation_notes and contact_id:
                try:
                    # Create a note associated with this contact
                    notes_url = "https://api.hubapi.com/crm/v3/objects/notes"
                    note_payload = {
                        "properties": {
                            "hs_note_body": conversation_notes[:10000],  # HubSpot note body limit
                            "hs_timestamp": int(datetime.now().timestamp() * 1000)  # Current timestamp in milliseconds
                        },
                        "associations": [
                            {
                                "to": {"id": str(contact_id)},  # Convert to string
                                "types": [{"associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 214}]
                            }
                        ]
                    }
                    # Note: Association format - "to" should be an object with "id" as string
                    # Association type 214 = note-to-contact association
                    # If association fails, we'll skip it - contact creation is more important
                    note_response = requests.post(notes_url, json=note_payload, headers=headers)
                    if note_response.status_code in [200, 201]:
                        logger.info(f"✅ Created note for contact {contact_id}")
                    else:
                        # Note creation failure is non-fatal - contact was already created
                        error_text = note_response.text[:200] if note_response.text else "Unknown error"
                        logger.warning(f"⚠️ Failed to create note for contact {contact_id}: {note_response.status_code} - {error_text}")
                        # Don't fail the whole sync if note creation fails
                except Exception as note_error:
                    # Don't fail the whole sync if note creation fails
                    logger.warning(f"⚠️ Error creating note (non-fatal): {str(note_error)}")
            
            logger.info(f"✅ Successfully synced contact to HubSpot: {contact_id}")
            return contact_id, None  # Return tuple: (contact_id, error_message)
        else:
            # Try to parse error message from response
            try:
                error_data = response.json()
                error_msg = error_data.get("message", response.text)
            except:
                error_msg = response.text
            
            full_error = f"HTTP {response.status_code}: {error_msg}"
            logger.error(f"❌ Failed to sync contact to HubSpot: {full_error}")
            
            # Check if it's an authentication error
            if response.status_code == 401:
                return None, f"Authentication failed. Please reconnect HubSpot OAuth. Error: {error_msg}"
            
            return None, full_error
            
    except Exception as e:
        error_msg = f"Error syncing to HubSpot: {str(e)}"
        logger.error(f"❌ {error_msg}")
        import traceback
        traceback.print_exc()
        return None, error_msg


def sync_conversation_to_hubspot(
    access_token: str,
    transcript: str,
    agent_name: Optional[str] = None
) -> tuple:
    """
    Sync conversation transcript to HubSpot CRM.
    
    Args:
        access_token: HubSpot OAuth access token
        transcript: Full conversation transcript
        agent_name: Optional agent name for notes
    
    Returns:
        Tuple of (contact_id, error_message)
        - contact_id: HubSpot contact ID if successful, None otherwise
        - error_message: Error message if failed, None if successful
    """
    if not access_token:
        return None, "HubSpot access token is missing"
    
    if not transcript or len(transcript.strip()) < 10:
        return None, "Transcript is too short or empty"
    
    try:
        # Extract contact information from transcript
        contact_info = extract_contact_info(transcript)
        
        # Prepare conversation notes
        notes = transcript
        if agent_name:
            notes = f"Conversation with {agent_name}:\n\n{transcript}"
        
        # Create or update contact in HubSpot
        contact_id, error = create_or_update_hubspot_contact(
            access_token=access_token,
            contact_info=contact_info,
            conversation_notes=notes
        )
        
        if contact_id:
            return contact_id, None
        else:
            # Return the detailed error from create_or_update function
            return None, error if error else "Failed to create/update contact in HubSpot"
            
    except Exception as e:
        error_msg = f"Error syncing to HubSpot: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return None, error_msg

