import os

from app.log import logger

_verbose = os.environ.get('YT_DLP_VERBOSE', 'false').lower() == 'true'


def _progress_hook(d):
    if d['status'] == 'finished':
        logger.info("Download finished, now post-processing ...")


YT_DLP_OPTS = {
    'quiet': not _verbose,
    'verbose': _verbose,
    'noplaylist': True,
    'skip_download': True,
    'check_formats': False,
    'format_sort': ['res', 'br', 'size'],
    'hls_use_mpegts': True,
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',
    }],
    'format': 'bestvideo[ext!=m3u8]+bestaudio[ext!=m3u8]/best[ext!=m3u8]',
    'logger': logger,
    'progress_hooks': [_progress_hook],
}
