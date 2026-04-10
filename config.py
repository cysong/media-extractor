import os

from app.log import logger, progress_hook

_verbose = os.environ.get('YT_DLP_VERBOSE', 'false').lower() == 'true'

YT_DLP_OPTS = {
    'quiet': not _verbose,
    'verbose': _verbose,
    'noplaylist': True,
    'skip_download': True,
    'check_formats': False,
    'format_sort': ['res', 'br', 'size'],  # Sort by resolution, bitrate, and size
    'hls_use_mpegts': True,  # Use MPEG-TS format for HLS streams
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',  # Convert to MP4 format if needed
    }],
    'format': 'bestvideo[ext!=m3u8]+bestaudio[ext!=m3u8]/best[ext!=m3u8]',  # Download best video and audio combination
    'logger': logger,
    'progress_hooks': [progress_hook],
}

