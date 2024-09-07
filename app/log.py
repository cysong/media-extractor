import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIRECTORY = 'logs'
if not os.path.exists(LOG_DIRECTORY):
    os.makedirs(LOG_DIRECTORY)


class MyLogger:
    def __init__(self):
        # 创建 Logger
        self.logger = logging.getLogger('media-extractor')
        self.logger.setLevel(logging.DEBUG)

        # 创建 RotatingFileHandler 处理程序
        handler = RotatingFileHandler(
            os.path.join(LOG_DIRECTORY, 'app.log'),  # 日志文件名
            maxBytes=10 * 1024 * 1024,  # 最大文件大小 10MB
            backupCount=10  # 保留 10 个备份文件
        )

        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # 将处理程序添加到 Logger
        self.logger.addHandler(handler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)


logger = MyLogger()


def progress_hook(d):
    if d['status'] == 'finished':
        logger.info("Download finished, now post-processing ...")
