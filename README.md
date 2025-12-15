# AWS Step Functions & Lambda Demo with CDK

This project demonstrates a serverless workflow on AWS using **AWS Step Functions**, **Lambda**, **API Gateway**, and **S3**, defined with **AWS CDK**.

It is designed to be deployed using `uv` for dependency management.

## 🚀 Overview

The stack creates:
1.  **API Gateway**: The entry point for HTTP requests.
2.  **Auth Lambda**: A "bouncer" that protects the API using a secret header.
3.  **Step Function**: Orchestrates the workflow.
4.  **Worker Lambda**: Processes data and saves it to S3.
5.  **S3 Bucket**: Stores the processed data (logs).

## 🛠️ Prerequisites

-   **Python 3.12+**
-   **uv**: An extremely fast Python package installer and resolver.
-   **AWS CLI**: Configured with your credentials (`aws configure`).
-   **Node.js**: Required for AWS CDK.

## 📦 Setup & Installation (The `uv` Way)

This project uses `uv` to manage dependencies, which is significantly faster than pip.

1.  **Install `uv`** (if you haven't already):
    ```bash
    pip install uv
    ```

2.  **Install Dependencies**:
    `uv` creates a virtual environment and installs packages from `pyproject.toml`.
    ```bash
    uv sync
    ```

3.  **Activate Virtual Environment** (Optional manually, `uv run` handles this):
    -   Windows: `.venv\Scripts\activate`
    -   Mac/Linux: `source .venv/bin/activate`

## ⚙️ Configuration

Check `app/config.py` to customize:
-   `BUCKET_NAME`: **Must be globally unique**. Change the default!
-   `API_SECRET_VALUE`: The token used to authenticate requests.

## 🚀 Deployment

1.  **Synthesize the CloudFormation Template**:
    Checks your code and generates the CloudFormation template.
    ```bash
    uv run cdk synth
    ```

2.  **Deploy to AWS**:
    Provisions the resources in your AWS account.
    ```bash
    uv run cdk deploy
    ```

## 🧪 Usage

Once deployed, you will see an **ApiUrl** in the outputs.

**Send a POST request** (e.g., using curl or Postman):

```bash
curl -X POST https://<your-api-url>/run \
  -H "my-secret: supersecret123" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Step Functions!"}'
```

-   **Success**: Returns 200 OK.
-   **Check S3**: Go to the S3 console and check the bucket specified in `config.py`. You should see a new JSON file.

## 🧹 Cleanup

To avoid incurring future charges, destroy the stack:

```bash
uv run cdk destroy
```

Note: The S3 bucket is configured with `RemovalPolicy.RETAIN`, so it will NOT be deleted automatically. You must delete it manually if desired.
