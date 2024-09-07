from flask import Blueprint, request, jsonify
from urllib.parse import urlparse

from config import ERROR_MESSAGES
from .extractors import get_extractor

main = Blueprint('main', __name__)


def is_valid_url(url):
    """
    验证 URL 的合法性。
    """
    try:
        parsed_url = urlparse(url)
        # 确保 URL 具有有效的方案 (例如 http, https) 和网络位置 (例如 domain)
        return all([parsed_url.scheme, parsed_url.netloc])
    except Exception:
        return False


@main.route('/get-media', methods=['POST'])
def get_media():
    """
    API接口：根据URL获取视频下载地址。
    """
    data = request.get_json()
    url = data.get('url')
    return extract_media(url)


def extract_media(url):
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if not is_valid_url(url):
        return jsonify({'error': 'Invalid URL'}), 400

    extractor = get_extractor(url)
    if not extractor:
        return jsonify({'error': ERROR_MESSAGES['no_extractor']}), 400

    media_urls = extractor.extract(url)

    if 'error' in media_urls:
        return jsonify({'error': media_urls['error']}), 500

    return jsonify(media_urls), 200
