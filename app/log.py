import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger('media-extractor')


def progress_hook(d):
    if d['status'] == 'finished':
        logger.info("Download finished, now post-processing ...")
