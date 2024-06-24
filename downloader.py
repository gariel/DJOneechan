import yt_dlp
from base import QueueItem
import youtubeextractor

class Downloader:
    def get_queue_item(self, search: str) -> QueueItem:
        return youtubeextractor.extract(search)

    def get_media_url(self, url: str) -> str:
        with yt_dlp.YoutubeDL({
            'format': "worstaudio",
            'source_address': '0.0.0.0',
            'default_search': 'ytsearch',
            'outtmpl': '%(id)s.%(ext)s',
            'noplaylist': True,
            'allow_playlist_files': False,
            'paths': {'home': './dl/'}}) as ydl:
            info = ydl.extract_info(url, download=False)
            return info["url"]
