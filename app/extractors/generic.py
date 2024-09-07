import yt_dlp

from config import YT_DLP_OPTS
from .base import BaseExtractor

class GenericExtractor(BaseExtractor):
    """
    通用视频解析器，适用于未指定的站点。
    """
    def supports(self, url):
        return 'unsupportedsite.com' not in url  # 默认支持所有站点，该不存在的站点只是做测试用

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
