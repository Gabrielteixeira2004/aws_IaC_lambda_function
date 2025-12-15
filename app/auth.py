# app/auth.py
from app import config  # <--- ABSOLUTE IMPORT

# --- Auth Handler ---
# This function is triggered by the API Gateway Authorizer.
# It determines if a request is allowed to proceed to our backend.
def handler(event, context):
    headers = event.get("headers", {})
    # Normalize headers to lowercase to ensure case-insensitive matching
    headers_lower = {k.lower(): v for k, v in headers.items()}
    
    # Read from Config
    expected_header = config.API_SECRET_HEADER.lower()
    token = headers_lower.get(expected_header, "")
    
    # Simple check: Does the header value match our secret?
    # returns a policy document structure expected by HTTP API simple authorizers.
    return {
        "isAuthorized": (token == config.API_SECRET_VALUE)
    }
