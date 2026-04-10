import json
import pytest
from unittest.mock import patch

from handler import lambda_handler

TWITTER_URL = 'https://x.com/AmiriTeran/status/1737693919775985997'
YOUTUBE_URL = 'https://www.youtube.com/watch?v=KWdhcOtGtcE'
INSTAGRAM_URL = 'https://www.instagram.com/reel/C_jZKM4Ij3t/?utm_source=ig_web_copy_link'

MOCK_FORMATS = [
    {'vcodec': 'h264', 'acodec': 'aac', 'resolution': '1280x720', 'protocol': 'https', 'tbr': 2000, 'ext': 'mp4', 'url': 'https://example.com/720.mp4'},
    {'vcodec': 'h264', 'acodec': 'aac', 'resolution': '640x360',  'protocol': 'https', 'tbr': 800,  'ext': 'mp4', 'url': 'https://example.com/360.mp4'},
]

MOCK_MEDIA_INFO = {'formats': MOCK_FORMATS}


def _event(body: dict, api_key: str = None) -> dict:
    event = {'body': json.dumps(body)}
    if api_key is not None:
        event['headers'] = {'x-api-key': api_key}
    return event


def _body(response: dict) -> dict:
    return json.loads(response['body'])


# ── Unit tests (mocked extractor) ────────────────────────────────────────────

@patch('handler._API_KEY', 'test-secret')
def test_unauthorized_missing_key():
    res = lambda_handler(_event({}), None)
    assert res['statusCode'] == 401

@patch('handler._API_KEY', 'test-secret')
def test_unauthorized_wrong_key():
    res = lambda_handler(_event({}, api_key='wrong'), None)
    assert res['statusCode'] == 401

@patch('handler._API_KEY', 'test-secret')
@patch('handler.get_extractor')
def test_authorized_with_correct_key(mock_get_extractor):
    res = lambda_handler(_event({}, api_key='test-secret'), None)
    assert res['statusCode'] != 401

@patch('handler.get_extractor')
def test_missing_url(mock_get_extractor):
    res = lambda_handler(_event({}), None)
    assert res['statusCode'] == 400
    assert _body(res)['error'] == 'URL is required'
    mock_get_extractor.assert_not_called()


@patch('handler.get_extractor')
def test_invalid_url(mock_get_extractor):
    res = lambda_handler(_event({'url': 'not_a_url'}), None)
    assert res['statusCode'] == 400
    assert _body(res)['error'] == 'Invalid URL'
    mock_get_extractor.assert_not_called()


@patch('handler.get_extractor', return_value=None)
def test_no_extractor_found(mock_get_extractor):
    res = lambda_handler(_event({'url': 'https://unsupportedsite.com/video'}), None)
    assert res['statusCode'] == 400
    assert 'error' in _body(res)


@patch('app.models.MediaData.save')
@patch('app.extractors.generic.GenericExtractor.extract_info', return_value=MOCK_MEDIA_INFO)
def test_successful_extraction(mock_extract, mock_save):
    res = lambda_handler(_event({'url': 'https://example.com/video'}), None)
    assert res['statusCode'] == 200
    data = _body(res)
    assert isinstance(data, dict)
    for url in data.values():
        assert url.startswith('http')


@patch('app.models.MediaData.save')
@patch('app.extractors.generic.GenericExtractor.extract_info', side_effect=Exception('site error'))
def test_extractor_error(mock_extract, mock_save):
    res = lambda_handler(_event({'url': 'https://example.com/video'}), None)
    assert res['statusCode'] == 500
    assert 'error' in _body(res)


def test_malformed_body():
    event = {'body': 'not-json'}
    res = lambda_handler(event, None)
    assert res['statusCode'] == 400


# ── Integration tests (real yt-dlp, skipped in CI) ───────────────────────────

@pytest.mark.integration
@patch('app.models.MediaData.save')
def test_twitter_video(mock_save):
    res = lambda_handler(_event({'url': TWITTER_URL}), None)
    assert res['statusCode'] == 200
    data = _body(res)
    assert isinstance(data, dict)
    for url in data.values():
        assert url.startswith('http')


@pytest.mark.integration
@patch('app.models.MediaData.save')
def test_youtube_video(mock_save):
    res = lambda_handler(_event({'url': YOUTUBE_URL}), None)
    assert res['statusCode'] == 200
    data = _body(res)
    assert isinstance(data, dict)
    for url in data.values():
        assert url.startswith('http')


@pytest.mark.integration
@patch('app.models.MediaData.save')
def test_instagram_video(mock_save):
    res = lambda_handler(_event({'url': INSTAGRAM_URL}), None)
    assert res['statusCode'] == 200
    data = _body(res)
    assert isinstance(data, dict)
    for url in data.values():
        assert url.startswith('http')
