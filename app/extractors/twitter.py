import yt_dlp

from app.extractors.generic import GenericExtractor

class TwitterExtractor(GenericExtractor):
    """
    Twitter 视频解析器。
    """
    def supports(self, url):
        return "twitter.com" in url or "x.com" in url
