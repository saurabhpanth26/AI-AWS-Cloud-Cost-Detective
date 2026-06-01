import json
import os
import anthropic


def analyze_costs(resources: list[dict]) -> dict:
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    resource_summary = json.dumps(resources, indent=2)

    prompt = f"""You are an AWS cloud cost optimization expert. Analyze the following AWS resources and identify cost issues.

Resources:
{resource_summary}

Analyze for:
1. Over-provisioned resources (oversized EC2 instances, RDS, Lambda with too much memory)
2. Unused/idle resources (unassociated Elastic IPs, unattached EBS volumes, stopped EC2 instances)
3. Misconfigurations (wrong instance families, missing auto-scaling, no reserved instances)
4. Storage cost issues (large EBS volumes, S3 buckets without lifecycle policies)
5. Load balancer waste (idle or underutilized ELBs)

Respond with a JSON object in exactly this structure:
{{
  "summary": "Brief overall summary of findings",
  "total_resources": <number>,
  "issues_found": <number>,
  "estimated_monthly_savings": "$X - $Y",
  "issues": [
    {{
      "resource_id": "id or name of the resource",
      "resource_type": "type of resource",
      "issue_type": "over-provisioned | unused | misconfigured | storage | other",
      "severity": "high | medium | low",
      "explanation": "Clear explanation of the problem and why it costs money",
      "fix_command": "AWS CLI command or step to fix it"
    }}
  ]
}}

Return only valid JSON, no markdown fences."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)
