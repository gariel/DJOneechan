import yt_dlp
from downloader import youtubeextractor
from models.queue_item import MediaInfo


class Downloader:
    def get_queue_items(self, search: str) -> list[MediaInfo]:
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
