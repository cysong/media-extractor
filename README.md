# media-extractor

A lightweight API that extracts direct video/audio download URLs from social media and video sites, powered by `yt-dlp`. Runs on AWS Lambda.

## API

**`POST /get-media`**

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

Error response:
```json
{
  "error": "No suitable extractor found for this URL"
}
```

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
2. Select your AWS region and click **Run workflow**
3. Wait ~5 minutes. The job summary will show the API endpoint and two remaining secrets to add:

```
ECR_REPOSITORY       = media-extractor
LAMBDA_FUNCTION_NAME = media-extractor
```

Add those to GitHub Secrets to enable ongoing deployments.

> **Re-running the setup workflow is safe** — all steps are idempotent. If API Gateway was partially created, the workflow detects the missing route and automatically deletes and recreates it.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DYNAMODB_TABLE` | `media-extractor-records` | DynamoDB table name |
| `API_KEY` | _(empty)_ | When set, all requests must include `x-api-key: <value>` header. Leave empty to disable auth. |
| `YT_DLP_VERBOSE` | `false` | Set to `true` to enable verbose yt-dlp logging to CloudWatch. Useful for debugging extraction failures. |

These are configured during the setup workflow and can be updated anytime in the Lambda console (Configuration → Environment variables) without redeploying.

### Ongoing deploys

Every push to `main` automatically runs tests, builds a new container image, and deploys to Lambda.

### Local development

```bash
pip install -r requirements.txt
python run_local.py <url>
```

## iOS Shortcut

Import `media_extractor.shortcut` into the Shortcuts app. Share any video URL to the shortcut — it calls the API and presents download links for you to choose from.

After deploying, update the shortcut with your API Gateway endpoint. If you set an `API_KEY`, add an `x-api-key` header to the request in the shortcut.

> Make sure your API Gateway endpoint is accessible from your iPhone.
