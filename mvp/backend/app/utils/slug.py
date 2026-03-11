import secrets

def generate_dashboard_slug(agent_name: str, agent_id: int):
    # Use a secure, random token instead of readable names for security
    print(f"yes it reach here{secrets.token_urlsafe(12)}")
    return secrets.token_urlsafe(12)