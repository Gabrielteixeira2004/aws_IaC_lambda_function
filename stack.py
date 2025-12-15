from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_apigatewayv2 as apigw,
    aws_apigatewayv2_integrations as integrations,
    aws_apigatewayv2_authorizers as authorizers,
    aws_s3 as s3,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct
from app import config 

class MyStepFunctionsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # =================================================================================
        # WALKTHROUGH: AWS Step Functions & Lambda Stack
        # =================================================================================
        # This stack creates a complete serverless workflow:
        # 1. An S3 bucket for data storage.
        # 2. A Worker Lambda that processes data and writes to S3.
        # 3. An Auth Lambda for securing the API.
        # 4. A Step Function that orchestrates the Worker Lambda.
        # 5. An HTTP API Gateway to expose the workflow to the world.
        # =================================================================================

        # --- 1. Handle Roles (Restricted Env Support) ---
        # existing_lambda_role_arn and existing_sfn_role_arn are checked from config.
        # If they exist, we import them. This is useful for environments where
        # IAM role creation is restricted (e.g., corporate sandboxes).
        if config.EXISTING_LAMBDA_ROLE_ARN:
            lambda_role = iam.Role.from_role_arn(
                self, "ImportedLambdaRole", 
                role_arn=config.EXISTING_LAMBDA_ROLE_ARN, 
                mutable=False
            )
        else:
            lambda_role = None

        if config.EXISTING_SFN_ROLE_ARN:
            sfn_role = iam.Role.from_role_arn(
                self, "ImportedSFNRole", 
                role_arn=config.EXISTING_SFN_ROLE_ARN, 
                mutable=False
            )
        else:
            sfn_role = None

        # --- 2. S3 Bucket ---
        # Create a bucket to store our processed data logs.
        # RemovalPolicy.RETAIN ensures the bucket is NOT deleted when the stack is destroyed.
        bucket = s3.Bucket(
            self, "DataBucket",
            bucket_name=config.BUCKET_NAME, 
            removal_policy=RemovalPolicy.RETAIN,
        )

        # --- 3. Worker Lambda ---
        # This function does the actual work (writing to S3).
        # We explicitly exclude unrelated files from the zip to keep it small and secure.
        worker_lambda = _lambda.Function(
            self, "WorkerLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            # Zip root, exclude junk
            code=_lambda.Code.from_asset(
                ".", 
                exclude=["cdk.out", ".git", ".uv", ".venv", "**/__pycache__"]
            ),
            handler="app.tasks.lambda_handler", 
            timeout=Duration.seconds(10),
            role=lambda_role,
            environment={
                "BUCKET_NAME": bucket.bucket_name
            }
        )

        # Grant permissions if we created the role (if it's not imported)
        if not config.EXISTING_LAMBDA_ROLE_ARN:
            bucket.grant_read_write(worker_lambda)

        # --- 4. Auth Lambda (The Bouncer) ---
        # This lambda checks requests before they reach our API.
        # It verifies if the request contains the correct secret header.
        auth_lambda = _lambda.Function(
            self, "AuthLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(
                ".", 
                exclude=["cdk.out", ".git", ".uv", ".venv", "**/__pycache__"]
            ),
            handler="app.auth.handler",
            role=lambda_role
        )

        # --- 5. Authorizer Configuration ---
        # Connects the Auth Lambda to API Gateway.
        # It's configured to look at the header specified in our config.
        authorizer = authorizers.HttpLambdaAuthorizer(
            "MyCustomAuthorizer",
            auth_lambda,
            response_types=[authorizers.HttpLambdaResponseType.SIMPLE],
            identity_source=[f"$request.header.{config.API_SECRET_HEADER}"],
        )

        # --- 6. Step Function ---
        # A simple state machine that runs our Worker Lambda.
        # In a real scenario, this could be a complex chain of multiple tasks.
        process_task = tasks.LambdaInvoke(
            self, "ProcessData",
            lambda_function=worker_lambda,
            output_path="$.Payload"
        )

        state_machine = sfn.StateMachine(
            self, "HelloWorldStateMachine",
            definition_body=sfn.DefinitionBody.from_chainable(process_task),
            state_machine_type=sfn.StateMachineType.STANDARD,
            role=sfn_role
        )

        # --- 7. API Gateway V2 ---
        # Exposes the Lambda/Step Function via HTTP.
        # Protected by our Custom Authorizer.
        api = apigw.HttpApi(
            self, "SimpleApi",
            default_authorizer=authorizer
        )

        # Define the route: POST /run triggers the Worker Lambda directly
        # (Could also trigger the Step Function if we used AwsIntegration)
        api.add_routes(
            path="/run",
            methods=[apigw.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration(
                "LambdaIntegration", worker_lambda
            )
        )

        # --- 8. THROTTLING PROTECTION (Save Money) ---
        # We access the low-level CloudFormation Stage resource to apply limits.
        # This limits the API to 10 requests per second.
        # If an attacker sends 1,000,000 requests, 999,990 are blocked for FREE.
        if api.default_stage and api.default_stage.node.default_child:
            cfn_stage = api.default_stage.node.default_child
            cfn_stage.default_route_settings = apigw.CfnStage.RouteSettingsProperty(
                throttling_burst_limit=20,  # Allow short spikes
                throttling_rate_limit=10    # Max steady requests/sec
            )

        # --- 9. Outputs ---
        # Useful info printed to the terminal after deployment.
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "BucketName", value=bucket.bucket_name)
