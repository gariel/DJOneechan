import random
from io import BytesIO

import discord
from discord.errors import ClientException
from discord.voice_client import AudioPlayer
from models.queue_item import QueueItem
from downloader import Downloader
from gtts import gTTS

from repositories.history import HistoryRepository

RECONNECTING_FFMPEG_OPTIONS = "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 2"

class Manager:
    def __init__(self, downloader: Downloader, history_repo: HistoryRepository, vc: discord.VoiceClient):
        self.queue: list[QueueItem] = []
        self._downloader = downloader
        self._history_repo = history_repo
        self._vc = vc
        
    def search_add(self, search: str, author: str) -> list[QueueItem]:
        return self._search_add(search, author, False)
    
    def search_add_next(self, search: str, author: str) -> list[QueueItem]:
        return self._search_add(search, author, True)
    
    def _search_add(self, search: str, author: str, is_next: bool) -> list[QueueItem]:
        media_infos = self._downloader.get_queue_items(search)

        queue_items = [
            QueueItem(
                title=mi.title,
                url=mi.url,
                request=search,
                author=author
            )
            for mi in media_infos
        ]

        if not self.queue or not is_next:
            self.queue.extend(queue_items)
        else:
            self.queue = [self.queue[0], *queue_items, *self.queue[1:]]
            
        return queue_items
    
    def clear_queue(self):
        if self.queue:
            self.queue = self.queue[:1]
    
    def next(self, callback):
        if self._vc.is_playing():
            self._vc.stop()
            return

        if self._vc.is_paused():
            self._vc.resume()
            self._vc.stop()
            return

        if not self.queue:
            return

        self.queue = self.queue[1:]
        self.play(callback)

    def _internal_next(self, callback):
        self.next(callback)
        callback()
    
    def next_n(self, n: int, callback):
        if n > 1:
            self.queue = self.queue[n-1:]  # TODO: gambiarra
        self.next(callback)

    def play(self, callback, skip_history=False):
        if self._vc.is_playing():
            return

        if self._vc.is_paused():
            self._vc.resume()
            return

        if not self.queue:
            return

        queue_item = self.queue[0]

        current = queue_item.url
        url = self._downloader.get_media_url(current)
        audio = discord.FFmpegOpusAudio(url, before_options=RECONNECTING_FFMPEG_OPTIONS)
        try:
            self._vc.play(audio, after=lambda _: self._internal_next(callback))
            if not skip_history:
                self._history_repo.add_history(queue_item)
        except ClientException:
            pass

    def shuffle(self):
        if not self.queue:
            return

        head, *tail = self.queue
        random.shuffle(tail)
        self.queue = [head, *tail]

    def pause(self, callback):
        if not self._vc.is_playing() or self._vc.is_paused():
            return

        self._vc.pause()
        callback()

    @property
    def is_paused(self):
        return self._vc.is_paused()

    def interruption(self, message, callback):
        buffer = BytesIO()
        tts = gTTS(message, lang='pt-br', lang_check=False)
        tts.write_to_fp(buffer)
        buffer.seek(0)

        is_playing = self._vc.is_playing()

        def after(_):
            buffer.close()
            if is_playing:
                self._vc.resume()
            callback()

        if is_playing:
            self._vc.pause()
            player = AudioPlayer(
                discord.FFmpegOpusAudio(buffer, pipe=True),
                self._vc,
                after=after
            )
            player.start()
            return

        self._vc.play(
            discord.FFmpegOpusAudio(buffer, pipe=True),
            after=after
        )
