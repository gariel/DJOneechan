from datetime import datetime
from typing import Optional

from pymongo.synchronous.database import Database

from models.queue_item import QueueItem, Sumary
from repositories import BaseRepository


class HistoryRepository(BaseRepository):
    COLLECTION_NAME = "music_history"

    def __init__(self, client: Optional[Database]):
        super().__init__(client)
        self._collection = self._is_valid and client[self.COLLECTION_NAME]

    def add_history(self, queue_item: QueueItem):
        if self._is_valid:
            self._collection.insert_one(self._convert(queue_item))

    def summarize_top(self, n: int, date: datetime) -> list[Sumary]:
        if not self._is_valid:
            return []

        data = self._collection.aggregate([
            {"$match": {"at": {"$gt": date}}},
            {"$group": {"_id": {"title":"$title", "url":"$url"}, "times": {"$sum": 1}}},
            {"$project": {"title": "$_id.title", "url": "$_id.url", "times": 1, "_id": 0}},
            {"$sort": {"times": -1}},
            {"$limit": n},
        ])
        return self._unconvert_n(Sumary, list(data))