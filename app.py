import aws_cdk as cdk
from stack import MyStepFunctionsStack

# --- 1. App Entry Point ---
# This is the main entry point for the CDK application.
# It initializes the CDK App and defines the Stack we want to deploy.

print("--- 1. Starting App ---") 

app = cdk.App()

# --- 2. Define the Stack ---
# We instantiate our custom stack defined in 'stack.py'.
# The 'env' parameter specifies the AWS region where this stack will be deployed.
MyStepFunctionsStack(
    app, 
    "HelloStepFunctionsStack", 
    env=cdk.Environment(region="us-east-2")
)

print("--- 2. App Defined, Synthesizing... ---")
# --- 3. Synthesize ---
# likely the most important step. It converts our Python code into 
# a CloudFormation template (JSON/YAML) that AWS understands.
app.synth()
print("--- 3. Done ---")
