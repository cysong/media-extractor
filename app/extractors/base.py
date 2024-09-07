class BaseExtractor:
    """
    解析器基类，定义接口。
    所有特定站点的解析器应继承此类。
    """
    def supports(self, url):
        """
        检查此解析器是否支持该URL。
        """
        raise NotImplementedError

    def extract(self, url):
        """
        提取视频下载地址。
        """
        raise NotImplementedError
