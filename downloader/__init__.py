import yt_dlp
from downloader import youtubeextractor
from models.queue_item import MediaInfo


class Downloader:
    def __init__(self, cookie_file: str):
        self.cookie_file = cookie_file

    def get_queue_items(self, search: str) -> list[MediaInfo]:
        return youtubeextractor.extract(search)

    def get_media_url(self, url: str) -> str | None:
        options = {
            'default_search': 'ytsearch',
            'outtmpl': '%(id)s.%(ext)s',
            'noplaylist': True,
            'allow_playlist_files': False,
            'paths': {'home': './dl/'},
            'extractor_args': {'youtube': {'player_client': ['web_music']}},
            'js_runtimes': {'deno': {'path': None}},
            'remote_components': ['ejs:github'],
        }

        if self.cookie_file:
            options['cookiefile'] = self.cookie_file

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'url' in info:
                return info["url"]

            if 'requested_formats' in info and info['requested_formats']:
                return info['requested_formats'][0]['url']


            if 'entries' in info:
                for entry in info['entries']:
                    if 'url' in entry:
                        return entry['url']
                    
                    if 'formats' in entry:
                        for fmt in entry['formats']:
                            if fmt.get('video_ext', "none") != "none" or fmt.get("audio_ext", "none") != "none":
                                return fmt["url"]

            return None
