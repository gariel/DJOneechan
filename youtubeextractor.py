import json
from json import JSONDecodeError
from typing import Iterable

import requests
import urllib
from base import QueueItem


def _search(data):
    for contents in data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]:
        for video in contents["itemSectionRenderer"]["contents"]:
            if "videoRenderer" in video.keys():
                video_data = video.get("videoRenderer", {})

                id = video_data["videoId"]
                url = f"https://www.youtube.com/watch?v={id}"
                title = video_data.get("title", {}).get("runs", [[{}]])[0].get("text", None)

                return QueueItem(
                    title=title,
                    url=url,
                )
    return None


def _video(url: str, data: dict) -> QueueItem:
    title = "unknown"
    for content in data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"]:
        if "videoPrimaryInfoRenderer" in content:
            video = content["videoPrimaryInfoRenderer"]
            title = video["title"]["runs"][0]["text"]
            break
    
    return QueueItem(
        title=title,
        url=url,
    )


def _playlist(data: dict) -> list[QueueItem]:
    playlist = data["contents"]["twoColumnWatchNextResults"]["playlist"]["playlist"]

    items : list[QueueItem] = []
    for video in playlist["contents"]:
        if "playlistPanelVideoRenderer" in video.keys():
            video_data = video.get("playlistPanelVideoRenderer", {})
            id = video_data["videoId"]

            title = str(video_data.get("title", {}).get("simpleText", id))
            url=f"https://www.youtube.com/watch?v={id}"

            items.append(QueueItem(
                title=title,
                url=url,
            ))

    return items


def _parse(url: str, is_search: bool) -> Iterable[QueueItem]:
    if "music.youtube" in url:
        url = url.replace("music.youtube", "youtube")

    response = requests.get(url).text
    while "ytInitialData" not in response:
        response = requests.get(url).text

    start = (
        response.index("ytInitialData")
        + len("ytInitialData")
        + 3
    )
    end = response.index("};", start) + 1
    json_str = response[start:end]
    try:
        data = json.loads(json_str)
    except JSONDecodeError:
        print("================ JSONDecodeError,", json_str)
        return

    if is_search:
        yield _search(data)

    elif "&list=" in url:
        for video in _playlist(data):
            yield video
    else:
        yield _video(url, data)


def extract(text: str) -> list[QueueItem]:
    is_search = not urllib.parse.urlparse(text).scheme

    if is_search:
        encoded_search = urllib.parse.quote_plus(text)
        text = f"https://youtube.com/results?search_query={encoded_search}"

    return list(item for item in _parse(text, is_search) if item)
