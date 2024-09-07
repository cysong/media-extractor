from app.log import logger, progress_hook


YT_DLP_OPTS = {
    'quiet': False,
    'verbose': True,
    'noplaylist': True,
    'skip_download': True,
    'check_formats': False,
    'format_sort': ['res', 'br', 'size'],  # Sort by resolution, bitrate, and size
    'noplaylist': True,  # Download the video instead of the playlist
    'hls_use_mpegts': True,  # Use MPEG-TS format for HLS streams
    'postprocessors': [{
        'key': 'FFmpegVideoConvertor',
        'preferedformat': 'mp4',  # Convert to MP4 format if needed
    }],
    'format': 'bestvideo+bestaudio/best',  # Download best video and audio combination
    'logger': logger,
    'progress_hooks': [progress_hook],
}

ERROR_MESSAGES = {
    'no_extractor': 'No suitable extractor found for this URL'
}
