from yt_dlp import YoutubeDL

def fetch_view_count(video_url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'no_warnings': True,
        'simulate': True,
        'force_generic_extractor': False,
        'extract_flat': True,
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info.get('view_count', 'N/A')
    except Exception as e:
        return f"Error: {str(e)}"
