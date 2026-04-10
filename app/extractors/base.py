from abc import abstractmethod
from typing import Any, Dict, List, final

from app.log import logger
from app.models import MediaData


class BaseExtractor:
    """
    Base class for all extractors. Subclasses must implement
    supports(), extract_info(), and filter_formats().
    """

    @abstractmethod
    def supports(self, url: str) -> bool:
        raise NotImplementedError

    @final
    def extract(self, url: str) -> Dict[str, str]:
        response: Dict[str, str]
        try:
            media_info = self.extract_info(url)
            formats = media_info.get('formats', [])
            response = self.filter_formats(formats)
        except Exception as e:
            logger.error(f"Extraction failed for {url}: {e}")
            response = {'error': str(e)}

        self.log(url, response)
        return response

    @abstractmethod
    def extract_info(self, url: str) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def filter_formats(self, formats: List[Dict]) -> Dict[str, str]:
        raise NotImplementedError

    @final
    def log(self, url: str, response: Dict[str, str]) -> None:
        try:
            MediaData(url, response, 'error' not in response).save()
        except Exception as e:
            logger.error(f"Failed to log to DynamoDB: {e}")
