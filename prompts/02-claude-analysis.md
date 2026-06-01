# Prompt 2: Claude API Integration for Cost Analysis

Build on top of the existing FastAPI backend. Add AI-powered cost analysis using the Anthropic Claude API.

## What to build

- Create an `ai_analyzer.py` module in `backend/` that:
  - Takes the list of AWS resources (from `aws_scanner.py`) as input.
  - Builds a prompt asking Claude to analyze the resources for: over-provisioning, unused/idle resources, misconfigurations, wrong pricing tiers, and cost optimization opportunities.
  - Calls the Anthropic Claude API (`claude-sonnet-4-6`) using the `anthropic` Python SDK and returns the structured analysis.
- The AI response should include: a summary, list of issues found (with severity: high/medium/low), estimated savings, and actionable fix commands (AWS CLI commands or Terraform snippets the user can run).
- Update `POST /api/analyze` to call `aws_scanner` first, then pass results to `ai_analyzer`, and return the final analysis.
- Store the Anthropic API key in environment variables. Add a `.env.example` file.
- Update `requirements.txt` — add `anthropic`, `python-dotenv`.

## Anthropic SDK usage

```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": prompt}
    ]
)
result = message.content[0].text
```

## Project structure update

```
backend/
├── main.py          (updated)
├── aws_scanner.py   (no change)
├── ai_analyzer.py   (new)
├── requirements.txt (updated)
├── .env.example     (new — ANTHROPIC_API_KEY)
```

Refer to `Architecture.MD` and `RequestFlow.MD`. This covers step ⑤ of the request flow.
