import random
from io import BytesIO

import discord
from discord.errors import ClientException
from discord.voice_client import AudioPlayer
from base import QueueItem
from downloader import Downloader
from gtts import gTTS


class Manager:
    def __init__(self, downloader: Downloader, vc: discord.VoiceClient):
        self.queue: list[QueueItem] = []
        self._downloader = downloader
        self._vc = vc
        
    def search_add(self, search: str, author: str) -> list[QueueItem]:
        return self._search_add(search, author, False)
    
    def search_add_next(self, search: str, author: str) -> list[QueueItem]:
        return self._search_add(search, author, True)
    
    def _search_add(self, search: str, author: str, next: bool) -> list[QueueItem]:
        queue_items = self._downloader.get_queue_items(search)

        for qi in queue_items:
            qi.author = author

        if not self.queue or not next:
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

    def play(self, callback):
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
        audio = discord.FFmpegOpusAudio(url)
        try:
            self._vc.play(audio, after=lambda _: self._internal_next(callback))
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
        tts = gTTS(message, lang='pt-br', slow=False)
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
