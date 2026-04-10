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

> **Re-running the setup workflow is safe** — each step checks whether the resource already exists and skips creation if so. Exception: if the workflow fails mid-way through API Gateway creation, delete the partially created API in the AWS console before re-running.

### Ongoing deploys

Every push to `main` automatically runs tests, builds a new container image, and deploys to Lambda.

### Local development

```bash
pip install -r requirements.txt
python run_local.py <url>
```

## iOS Shortcut

Import `media_extractor.shortcut` into the Shortcuts app. Share any video URL to the shortcut — it calls the API and presents download links for you to choose from.

> Make sure your server is reachable from your iPhone (local network or public URL).
