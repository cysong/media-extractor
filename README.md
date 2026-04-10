# media-extractor

A lightweight Flask API that extracts direct video/audio download URLs from social media and video sites, powered by `yt-dlp`.

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

## Installation

```bash
pip install -r requirements.txt
python run.py
```

Server runs on port `80` by default.

## iOS Shortcut

Import `media_extractor.shortcut` into the Shortcuts app. Share any video URL to the shortcut — it calls the API and presents download links for you to choose from.

> Make sure your server is reachable from your iPhone (local network or public URL).
