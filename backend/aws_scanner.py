import boto3
from botocore.exceptions import NoCredentialsError, ClientError


def get_aws_regions() -> list[str]:
    ec2 = boto3.client("ec2", region_name="us-east-1")
    response = ec2.describe_regions(Filters=[{"Name": "opt-in-status", "Values": ["opt-in-not-required", "opted-in"]}])
    return sorted([r["RegionName"] for r in response["Regions"]])


def verify_credentials() -> dict:
    sts = boto3.client("sts")
    return sts.get_caller_identity()


def scan_resources(region: str) -> list[dict]:
    resources = []

    # EC2 instances
    try:
        ec2 = boto3.client("ec2", region_name=region)
        paginator = ec2.get_paginator("describe_instances")
        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                for inst in reservation["Instances"]:
                    name = next((t["Value"] for t in inst.get("Tags", []) if t["Key"] == "Name"), inst["InstanceId"])
                    resources.append({
                        "type": "EC2 Instance",
                        "id": inst["InstanceId"],
                        "name": name,
                        "region": region,
                        "sku": inst.get("InstanceType", "unknown"),
                        "state": inst["State"]["Name"],
                        "tags": {t["Key"]: t["Value"] for t in inst.get("Tags", [])},
                    })
    except ClientError:
        pass

    # EBS volumes
    try:
        paginator = ec2.get_paginator("describe_volumes")
        for page in paginator.paginate():
            for vol in page["Volumes"]:
                name = next((t["Value"] for t in vol.get("Tags", []) if t["Key"] == "Name"), vol["VolumeId"])
                resources.append({
                    "type": "EBS Volume",
                    "id": vol["VolumeId"],
                    "name": name,
                    "region": region,
                    "sku": f"{vol['VolumeType']} {vol['Size']}GB",
                    "state": vol["State"],
                    "tags": {t["Key"]: t["Value"] for t in vol.get("Tags", [])},
                })
    except ClientError:
        pass

    # Elastic IPs
    try:
        eips = ec2.describe_addresses()
        for eip in eips["Addresses"]:
            resources.append({
                "type": "Elastic IP",
                "id": eip.get("AllocationId", eip.get("PublicIp")),
                "name": eip.get("PublicIp", ""),
                "region": region,
                "sku": "Elastic IP",
                "state": "associated" if "AssociationId" in eip else "unassociated",
                "tags": {t["Key"]: t["Value"] for t in eip.get("Tags", [])},
            })
    except ClientError:
        pass

    # RDS instances
    try:
        rds = boto3.client("rds", region_name=region)
        paginator = rds.get_paginator("describe_db_instances")
        for page in paginator.paginate():
            for db in page["DBInstances"]:
                resources.append({
                    "type": "RDS Instance",
                    "id": db["DBInstanceIdentifier"],
                    "name": db["DBInstanceIdentifier"],
                    "region": region,
                    "sku": db["DBInstanceClass"],
                    "state": db["DBInstanceStatus"],
                    "tags": {},
                })
    except ClientError:
        pass

    # S3 buckets (global but include for completeness)
    try:
        s3 = boto3.client("s3", region_name=region)
        buckets = s3.list_buckets().get("Buckets", [])
        for bucket in buckets:
            resources.append({
                "type": "S3 Bucket",
                "id": bucket["Name"],
                "name": bucket["Name"],
                "region": "global",
                "sku": "S3",
                "state": "active",
                "tags": {},
            })
    except ClientError:
        pass

    # Lambda functions
    try:
        lam = boto3.client("lambda", region_name=region)
        paginator = lam.get_paginator("list_functions")
        for page in paginator.paginate():
            for fn in page["Functions"]:
                resources.append({
                    "type": "Lambda Function",
                    "id": fn["FunctionArn"],
                    "name": fn["FunctionName"],
                    "region": region,
                    "sku": f"{fn['Runtime']} {fn['MemorySize']}MB",
                    "state": "active",
                    "tags": {},
                })
    except ClientError:
        pass

    # Elastic Load Balancers (v2)
    try:
        elb = boto3.client("elbv2", region_name=region)
        paginator = elb.get_paginator("describe_load_balancers")
        for page in paginator.paginate():
            for lb in page["LoadBalancers"]:
                resources.append({
                    "type": "Load Balancer",
                    "id": lb["LoadBalancerArn"],
                    "name": lb["LoadBalancerName"],
                    "region": region,
                    "sku": lb["Type"],
                    "state": lb["State"]["Code"],
                    "tags": {},
                })
    except ClientError:
        pass

    return resources
