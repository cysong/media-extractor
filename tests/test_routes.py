import pytest
from flask import json
from app import create_app
from config import ERROR_MESSAGES

TWITTER_URL = 'https://x.com/AmiriTeran/status/1737693919775985997'

@pytest.fixture
def app():
    """
    创建和配置 Flask 测试客户端。
    """
    app = create_app()
    app.config.update({
        'TESTING': True,
    })
    yield app

@pytest.fixture
def client(app):
    """
    提供 Flask 测试客户端。
    """
    return app.test_client()

def test_valid_url(client):
    """
    测试有效 URL。
    """
    response = client.post('/get-media', json={'url': TWITTER_URL})
    # assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)  # 检查返回的是字典
    # 根据你的 `extractors` 实现，检查特定的解析结果
    # assert '1080p' in data  # 如果你的解析器返回的结果中有 `1080p` 清晰度

def test_invalid_url(client):
    """
    测试无效 URL。
    """
    response = client.post('/get-media', json={'url': 'invalid_url'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid URL'

def test_missing_url(client):
    """
    测试缺少 URL。
    """
    response = client.post('/get-media', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'URL is required'

def test_no_extractor_found(client):
    """
    测试不支持的 URL。
    """
    response = client.post('/get-media', json={'url': 'https://unsupportedsite.com/video'})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == ERROR_MESSAGES['no_extractor']

def test_twitter_video(client):
    """
    测试特定 Twitter 视频 URL。
    """
    response = client.post('/get-media', json={'url': TWITTER_URL})
    assert response.status_code == 200
    
    print(response.data)
    data = json.loads(response.data)
    assert isinstance(data, dict)  # 确保返回的是字典

    # 根据 `TwitterExtractor` 的实现来验证返回的内容
    # 这里的断言依赖于解析器的具体实现，可以根据实际返回的结果进行调整
    # assert '1080p' in data or '720p' in data or '480p' in data  # 检查是否有视频清晰度地址
    
    # 具体的断言可能需要根据实际情况调整，比如检查返回的 URL 是否符合预期
    for resolution, url in data.items():
        assert url.startswith('http')  # 确保每个 URL 都是有效的 HTTP URL

    
def test_youtube_video(client):
    """
    测试特定 Twitter 视频 URL。
    """
    response = client.post('/get-media', json={'url': 'https://www.youtube.com/watch?v=KWdhcOtGtcE'})
    assert response.status_code == 200
    
    print(response.data)
    data = json.loads(response.data)
    assert isinstance(data, dict)  # 确保返回的是字典

    # 根据 `TwitterExtractor` 的实现来验证返回的内容
    # 这里的断言依赖于解析器的具体实现，可以根据实际返回的结果进行调整
    # assert '1080p' in data or '720p' in data or '480p' in data  # 检查是否有视频清晰度地址
    
    # 具体的断言可能需要根据实际情况调整，比如检查返回的 URL 是否符合预期
    for resolution, url in data.items():
        assert url.startswith('http')  # 确保每个 URL 都是有效的 HTTP URL
