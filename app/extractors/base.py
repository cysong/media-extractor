from abc import abstractmethod
from typing import Dict, List, final
from venv import logger

from app.models import MediaData


class BaseExtractor:
    """
    解析器基类，定义接口。
    所有特定站点的解析器应继承此类。
    """

    @abstractmethod
    def supports(self, url: str) -> bool:
        """
        检查此解析器是否支持该URL。
        """
        raise NotImplementedError

    @final
    def extract(self, url) -> Dict[str, str]:
        """
        提取视频下载地址。
        """
        response = None
        media_info = None
        try:
            media_info = self.extract_info(url)
        except Exception as e:
            response = {'error': str(e)}
            logger.error(e)

        if media_info is not None:
            formats = media_info.get('formats', [])
            response = self.filter_formats(formats)
        else:
            response = {'error', 'No media info found'}

        self.log(url, media_info, response)
        return response

    @abstractmethod
    def extract_info(self, url: str) -> Dict[str, any]:
        """
        提取视频信息
        """
        raise NotImplementedError

    @abstractmethod
    def filter_formats(self, formats: List[Dict]) -> Dict[str, str]:
        """
        Fileter all the formats return 
        """
        raise NotImplementedError

    @final
    def log(self, url, media=None, response: Dict[str, str] = None):
        """
        Log media info and response to database
        """
        MediaData(url, media, response, 'error' in response).save()
