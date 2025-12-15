# app/config.py

# =================================================================================
# CONFIGURATION
# =================================================================================
# Centralized configuration for the application.
# PRO TIP: In a real production app, 'API_SECRET_VALUE' should be stored 
# in AWS Secrets Manager or Parameter Store, NOT in plain text.

# --- 1. AWS RESOURCES ---
# CRITICAL: This must be GLOBALLY unique. 
# Change "12345" to your name or random numbers.
BUCKET_NAME = "stepfunctions-demo-bucket-change-me-12345" 

# --- 2. SECURITY ---
# The header name and value we expect for authentication.
API_SECRET_HEADER = "my-secret"
API_SECRET_VALUE = "supersecret123"

# --- 3. IAM ROLES (For Restricted Environments) ---
# If you have Admin access, keep these as None.
# If restricted, paste the ARNs your admin gave you.
EXISTING_LAMBDA_ROLE_ARN = None
EXISTING_SFN_ROLE_ARN = None
