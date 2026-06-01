# Prompt 1: FastAPI Backend + AWS CLI / boto3

Create a Python FastAPI backend in a `backend/` folder for the AI Cloud Cost Detective project.

## What to build

- A FastAPI server with a `POST /api/analyze` endpoint that accepts `{ "resource_group": "<account_or_region>" }`.
- A `GET /api/resource-groups` endpoint that returns the list of AWS regions (or accounts) available.
- Use `boto3` to fetch AWS resources:
  - Use `boto3` with `ResourceGroupsTaggingAPI` (`get_resources`) or per-service clients to list all resources in the selected region.
  - Collect EC2 instances, RDS instances, S3 buckets, Lambda functions, ELBs, EBS volumes, and Elastic IPs.
- Parse the boto3 response and return a structured list with resource type, name/id, region, instance type / SKU, and tags.
- Use AWS CLI (`aws sts get-caller-identity`) or boto3 to confirm credentials are configured.
- Add error handling for missing AWS credentials, invalid region, or boto3 exceptions.
- Enable CORS for `http://localhost:5173`.
- Include a `requirements.txt` with `fastapi`, `uvicorn`, `boto3`.

## Project structure

```
backend/
├── main.py
├── aws_scanner.py
├── requirements.txt
```

Refer to `Architecture.MD` and `RequestFlow.MD`. This covers step ③ of the request flow.
