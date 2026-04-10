import json
import os
from urllib.parse import urlparse

from app.extractors import get_extractor

ERROR_NO_URL = 'URL is required'
ERROR_INVALID_URL = 'Invalid URL'
ERROR_NO_EXTRACTOR = 'No suitable extractor found for this URL'

_API_KEY = os.environ.get('API_KEY')


def _is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False


def _response(status_code: int, body: dict) -> dict:
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body),
    }


def lambda_handler(event, context):
    if _API_KEY:
        headers = event.get('headers') or {}
        if headers.get('x-api-key') != _API_KEY:
            return _response(401, {'error': 'Unauthorized'})

    try:
        body = json.loads(event.get('body') or '{}')
    except (json.JSONDecodeError, TypeError):
        return _response(400, {'error': ERROR_NO_URL})

    url = body.get('url')
    if not url:
        return _response(400, {'error': ERROR_NO_URL})

    if not _is_valid_url(url):
        return _response(400, {'error': ERROR_INVALID_URL})

    extractor = get_extractor(url)
    if not extractor:
        return _response(400, {'error': ERROR_NO_EXTRACTOR})

    result = extractor.extract(url)
    status = 500 if 'error' in result else 200
    return _response(status, result)
