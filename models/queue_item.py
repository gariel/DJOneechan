from dataclasses import dataclass


@dataclass
class MediaInfo:
    title: str
    url: str


@dataclass
class QueueItem:
    title: str
    url: str
    request: str
    author: str

@dataclass
class Sumary:
    title: str
    url: str
    times: int