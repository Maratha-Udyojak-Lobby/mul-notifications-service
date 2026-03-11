# MUL Notifications Service

Async email, SMS, and push notifications via Celery + Redis.

## Development

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8006
```

Server runs on http://127.0.0.1:8006
