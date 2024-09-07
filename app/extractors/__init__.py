from .twitter import TwitterExtractor
from .generic import GenericExtractor

# 定义所有解析器
EXTRACTORS = [
    TwitterExtractor(),
    GenericExtractor()  # 通用解析器作为回退
]

def get_extractor(url):
    """
    根据URL返回合适的解析器。
    """
    for extractor in EXTRACTORS:
        if extractor.supports(url):
            return extractor
    return None
