import json
import logging


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            'time': self.formatTime(record, '%Y-%m-%dT%H:%M:%S'),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }
        if record.exc_info:
            entry['exception'] = self.formatException(record.exc_info)
        return json.dumps(entry)


def _build_logger() -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(_JsonFormatter())
    log = logging.getLogger('media-extractor')
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)
    log.propagate = False
    return log


logger = _build_logger()


def progress_hook(d):
    if d['status'] == 'finished':
        logger.info("Download finished, now post-processing ...")
