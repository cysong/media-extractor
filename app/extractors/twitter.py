import yt_dlp

from config import YT_DLP_OPTS
from .base import BaseExtractor

class TwitterExtractor(BaseExtractor):
    """
    Twitter 视频解析器。
    """
    def supports(self, url):
        return "twitter.com" in url or "x.com" in url

    def extract(self, url):
        with yt_dlp.YoutubeDL(YT_DLP_OPTS) as ydl:
            try:
                video_info = ydl.extract_info(url, download=False)
                formats = video_info.get('formats', [])
                return self._get_video_resolutions(formats)
            except yt_dlp.utils.DownloadError as e:
                return {'error': str(e)}

    def _get_video_resolutions(self, formats):
        """
        提取不同清晰度的视频地址。
        """
        video_urls = {}
        for format in formats:
            resolution = format.get('format_note', 'Unknown')
            url = format.get('url')
            if url:
                video_urls[resolution] = url
        return video_urls
