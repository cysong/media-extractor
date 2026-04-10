# Lambda Migration Plan

## Overview

Refactor the Flask-based media extractor into a native AWS Lambda handler,
removing the Flask dependency and replacing SQLite with DynamoDB.

## Architecture

```
Before
──────────────────────────────────────────
Client → Flask (port 80)
           └── routes.py
                 └── extractors → yt-dlp
                 └── models.py  → SQLite

After
──────────────────────────────────────────
Client → API Gateway → Lambda (handler.py)
                           └── extractors → yt-dlp
                           └── models.py  → DynamoDB
```

## File Changes

| File | Action | Reason |
|------|--------|--------|
| `handler.py` | Create | Lambda entry point, replaces Flask routes |
| `app/routes.py` | Delete | Replaced by handler.py |
| `app/__init__.py` | Delete | Flask app factory no longer needed |
| `app/models.py` | Rewrite | SQLite → DynamoDB via boto3 |
| `database.py` | Delete | SQLite init logic no longer needed |
| `requirements.txt` | Update | Remove Flask, add boto3 |
| `run.py` | Delete | Flask dev server no longer used |
| `Dockerfile` | Create | Container image for Lambda deployment |
| `config.py` | Update | Remove Flask/SQLite config, add DynamoDB table name |

## handler.py Design

```python
def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    url  = body.get('url')

    # validate → get_extractor → extract → return
```

Single function, no routing library needed. API Gateway handles the HTTP layer.

## DynamoDB Table Design

Table name: `media-extractor-records`

| Attribute | Type | Role |
|-----------|------|------|
| `id` | String (UUID) | Partition key |
| `url` | String | Source URL |
| `response` | String (JSON) | Extracted URLs |
| `success` | Boolean | Extraction result |
| `created_at` | String (ISO 8601) | Timestamp |

> `media` (full yt-dlp info) is omitted — it can be hundreds of KB and is rarely queried.

## Deployment

```
ECR container image (not zip) — required for ffmpeg binary

Build:
  docker build -t media-extractor .
  docker tag media-extractor:latest <account>.dkr.ecr.<region>.amazonaws.com/media-extractor:latest
  docker push ...

Lambda config:
  Runtime : Container image
  Handler : handler.lambda_handler
  Timeout : 60s
  Memory  : 512 MB
  Env     : DYNAMODB_TABLE=media-extractor-records
```

## Dockerfile Design

```dockerfile
FROM public.ecr.aws/lambda/python:3.12
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN yum install -y ffmpeg          # or copy static binary
COPY . .
CMD ["handler.lambda_handler"]
```

## Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| 60s timeout | Slow sites may fail | Return 504, client retries |
| Cold start ~2-3s | First request latency | Acceptable for iOS shortcut use |
| ffmpeg availability | Format merging may fail without it | Include static ffmpeg binary in image |
| DynamoDB cost | Near zero at low volume | Free tier covers ~25GB storage |

## Local Development

Without Flask, local testing uses a thin wrapper:

```python
# run_local.py
import json
from handler import lambda_handler

event = {'body': json.dumps({'url': 'https://x.com/...'})}
print(lambda_handler(event, None))
```
