# media-extractor

A lightweight API that extracts direct video/audio download URLs from social media and video sites, powered by `yt-dlp`. Runs on AWS Lambda.

## API

**`POST /get-media`**

All requests must include an `x-api-key` header.

Request:
```json
{
  "url": "https://x.com/user/status/123456789"
}
```

Response:
```json
{
  "1280x720": "https://video.twimg.com/...",
  "640x360": "https://video.twimg.com/..."
}
```

Each key is a resolution (or `audio only`), each value is a direct download URL.

Error responses:

| Status | Body |
|--------|------|
| 400 | `{"error": "URL is required"}` |
| 400 | `{"error": "Invalid URL"}` |
| 400 | `{"error": "No suitable extractor found for this URL"}` |
| 403 | API key missing or invalid (returned by API Gateway) |
| 429 | Rate limit or daily quota exceeded (returned by API Gateway) |
| 500 | `{"error": "..."}` |

## Supported Sites

- **Twitter / X** — dedicated extractor with optimized format selection
- **1000+ other sites** — YouTube, Instagram, TikTok, Bilibili, Reddit, and more via `yt-dlp`

## Deployment

### Prerequisites

Add the following secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key |
| `AWS_REGION` | Target region, e.g. `ap-southeast-2` |

The IAM user needs permissions to create ECR, DynamoDB, IAM, Lambda, and API Gateway resources.

### First-time setup

Run the **Setup AWS Infrastructure** workflow once to provision all resources:

1. Go to **Actions** → **Setup AWS Infrastructure** → **Run workflow**
2. Fill in the inputs:

| Input | Default | Description |
|-------|---------|-------------|
| `aws_region` | `ap-southeast-2` | AWS region |
| `yt_dlp_verbose` | `false` | Enable verbose yt-dlp logging |
| `daily_quota` | `200` | Max API calls per day per user |
| `rate_limit` | `5` | Max requests per second per user |

3. Wait ~5 minutes. The job summary will show:
   - API endpoint URL
   - Your initial API key value
   - Two remaining GitHub Secrets to add

Add these to GitHub Secrets to enable ongoing deployments:
```
ECR_REPOSITORY       = media-extractor
LAMBDA_FUNCTION_NAME = media-extractor
```

> **Re-running the setup workflow is safe** — all steps are idempotent. If API Gateway was partially created, the workflow detects the incomplete state and automatically recreates it.

### Managing API keys

Use the **Manage API Keys** workflow (Actions → Manage API Keys → Run workflow):

| Action | Description |
|--------|-------------|
| `create` | Create a new key and add it to the usage plan |
| `disable` | Immediately block a user without deleting their key |
| `enable` | Re-enable a previously disabled key |
| `list` | Show all keys and their enabled status |

The key value is shown in the job summary on creation — it cannot be retrieved later.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DYNAMODB_TABLE` | `media-extractor-records` | DynamoDB table name |
| `YT_DLP_VERBOSE` | `false` | Set to `true` to enable verbose yt-dlp logging to CloudWatch |

Configurable in Lambda console (Configuration → Environment variables) without redeploying.

### Ongoing deploys

Every push to `main` automatically runs tests, builds a new container image, and deploys to Lambda.

### Local development

```bash
pip install -r requirements.txt
python run_local.py <url>
```

## iOS Shortcut

Import `media_extractor.shortcut` into the Shortcuts app. Share any video URL to the shortcut — it calls the API and presents download links for you to choose from.

After deploying, update the shortcut with your API Gateway endpoint and add an `x-api-key` header with your API key value.

> Make sure your API Gateway endpoint is accessible from your iPhone.
