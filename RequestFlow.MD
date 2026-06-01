## AI Cloud Cost Detective - Request Flow

```
①  User ─·─·─► React ─·─·─► FastAPI Auth ─·─·─► JWT (AWS RDS PostgreSQL)

②  User selects AWS Region ─·─·─► Python Backend

③  Python ─·─·─► boto3 ─·─·─► Fetches all resources in region

④  Python ─·─·─► FastAPI WebSocket ─·─·─► React (live progress)

⑤  Python ─·─·─► Anthropic Claude API ─·─·─► Cost analysis

⑥  Python ─·─·─► AWS RDS PostgreSQL ─·─·─► Stores analysis history

⑦  React ◄·─·─·─ Final report with suggestions & fixes
```
