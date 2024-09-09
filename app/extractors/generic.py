import yt_dlp

from config import YT_DLP_OPTS
from .base import BaseExtractor
from typing import List, Dict, Optional


class GenericExtractor(BaseExtractor):
    """
    通用视频解析器，适用于未指定的站点。
    """

    def supports(self, url):
        return 'unsupportedsite.com' not in url  # 默认支持所有站点，该不存在的站点只是做测试用

    def extract_info(self, url):
        with yt_dlp.YoutubeDL(YT_DLP_OPTS) as ydl:
            return ydl.extract_info(url, download=False)

    def filter_formats(self, formats: List[Dict]) -> Dict[str, str]:
        """
        选择最佳的媒体格式（音频或视频），根据以下规则：
        - 排除播放列表格式（如 m3u8）。
        - 对音频格式，选择质量最高的。
        - 对视频格式，选择包含音频的视频格式，在相同分辨率下选择质量最好的，并优先选择常见格式（如 mp4）。
        - 最终输出字典，key 为分辨率，value 为下载 URL。

        Args:
            formats (List[Dict]): yt-dlp 提取的媒体格式列表，每个字典包含格式的信息。

        Returns:
            Dict[str, str]: 选择出的最佳格式，key 为分辨率，value 为下载 URL。
        """
        best_formats = {}

        # 排除 m3u8 等不直接下载的格式
        valid_formats = [f for f in formats if f.get(
            "protocol", "") in ("http", "https")]

        # 分类为音频和视频格式
        audio_formats = [f for f in valid_formats if f.get(
            'acodec') != 'none' and f.get('vcodec') == 'none']
        video_formats = [f for f in valid_formats if f.get(
            'vcodec') != 'none' and f.get('acodec') != 'none']

        # 选择最高质量的音频格式
        if audio_formats:
            best_audio = max(audio_formats, key=lambda f: f.get("abr", 0))
            best_formats[best_audio['resolution']] = best_audio['url']

        # 对视频格式进行筛选
        video_by_resolution = {}
        for video in video_formats:
            resolution = video.get('resolution', 'unknown')
            if resolution not in video_by_resolution:
                video_by_resolution[resolution] = video
            else:
                # 比较同分辨率的质量，选择文件大小最大、格式最好的
                current_best = video_by_resolution[resolution]
                if (
                    video.get('tbr', 0) > current_best.get('tbr', 0) or
                    (video.get('tbr', 0) == current_best.get(
                        'tbr', 0) and video.get('ext') == 'mp4')
                ):
                    video_by_resolution[resolution] = video

        # 将最佳视频格式按分辨率加入输出字典
        for resolution, video_format in video_by_resolution.items():
            best_formats[resolution] = video_format['url']

        return best_formats
