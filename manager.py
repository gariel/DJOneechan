
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
        queue_item = self._downloader.get_queue_item(search)
        queue_item.author = author
        if queue_item:
            random.shuffle(queue_item.medias)
            self.queue.append(queue_item)
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
