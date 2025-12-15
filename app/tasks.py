# app/tasks.py
import json
import os
import boto3
import datetime
from app import config  # <--- ABSOLUTE IMPORT

# Initialize S3 Client outside the handler for connection reuse (Cold Start optimization)
s3 = boto3.client("s3")

# --- Worker Lambda Handler ---
# This function is executed by Step Functions or API Gateway.
# It simply logs the event it received to an S3 bucket.
def lambda_handler(event, context):
    print(f"📥 Event: {json.dumps(event)}")
    
    # Determine the bucket name.
    # Cloud: Uses Env Var (defaults to None, handled by config logic if needed)
    # Local: Uses config.BUCKET_NAME directly via import because Lambda env vars aren't present
    bucket_name = os.environ.get("BUCKET_NAME", config.BUCKET_NAME)
    
    timestamp = datetime.datetime.now().isoformat()
    file_name = f"log-{timestamp}.json"
    
    data = {
        "timestamp": timestamp,
        "input": event
    }

    try:
        # Write the JSON file to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        return {"status": "success", "file": file_name}
    except Exception as e:
        print(f"❌ Error writing to {bucket_name}: {e}")
        raise e

# --- LOCAL DEBUGGING ---
# allows you to run `python app/tasks.py` to test the logic 
# on your machine without deploying to AWS.
if __name__ == "__main__":
    print(f"🐛 Debugging Locally using bucket: {config.BUCKET_NAME}")
    
    # Ensure env var matches config for local run
    os.environ["BUCKET_NAME"] = config.BUCKET_NAME

    test_event = {"input": "Hello from Absolute Import!"}
    
    try:
        # We need to simulate the Lambda Context being None
        response = lambda_handler(test_event, None)
        print(json.dumps(response, indent=2))
    except Exception as e:
        print(f"❌ Failed: {e}")
