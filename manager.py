
import random
from typing import Optional

import discord
from base import QueueItem
from downloader import Downloader

class Manager:
    def __init__(self, downloader: Downloader, vc: discord.VoiceClient):
        self.queue : list[QueueItem] = []
        self._downloader = downloader
        self._vc = vc
        
    def search_add(self, search: str, author: str) -> Optional[QueueItem]:
        return self._search_add(search, author, False)
    
    def search_add_next(self, search: str, author: str) -> Optional[QueueItem]:
        return self._search_add(search, author, True)
    
    def _search_add(self, search: str, author: str, next: bool) -> Optional[QueueItem]:
        queue_item = self._downloader.get_queue_item(search)
        queue_item.author = author
        if queue_item:
            random.shuffle(queue_item.medias)

            if not self.queue or not next:
                self.queue.append(queue_item)
            else:
                current = self.queue[0]
                if len(current.medias) > 1:
                    broke = QueueItem(
                        title=current.title,
                        medias=current.medias[1:],
                        author=current.author,
                    )
                    current.medias = current.medias[:1]
                    self.queue = [current, queue_item, broke, *self.queue[1:]]
                else:
                    self.queue = [current, queue_item, *self.queue[1:]]
            
        return queue_item
    
    def clear_queue(self):
        if self.queue:
            self.queue = self.queue[:1]
            if len(self.queue[0].medias) > 1:
                self.queue[0].medias = self.queue[0].medias[:1]
    
    def next_track(self, callback):
        if self._vc.is_playing():
            self._vc.stop()
            return

        if not self.queue:
            return

        if len(self.queue[0].medias) > 1:
            self.queue[0].medias = self.queue[0].medias[1:]
        else:
            self.queue = self.queue[1:]

        self.play(callback)
        
    def play(self, callback):
        if self._vc.is_playing():
            return

        if self.queue:
            queue_item = self.queue[0]
            media = queue_item.medias[0]
            callback(queue_item, media)

            current = media.url
            url = self._downloader.get_media_url(current)
            audio = discord.FFmpegOpusAudio(url)
            self._vc.play(audio, after=lambda _: self.next_track(callback))
