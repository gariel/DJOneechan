import json
from json import JSONDecodeError
from typing import Iterable

import requests
import urllib

from models.queue_item import MediaInfo


def _search(data):
    for contents in data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"]:
        for video in contents["itemSectionRenderer"]["contents"]:
            if "videoRenderer" in video.keys():
                video_data = video.get("videoRenderer", {})

                id = video_data["videoId"]
                url = f"https://www.youtube.com/watch?v={id}"
                title = video_data.get("title", {}).get("runs", [[{}]])[0].get("text", None)

                return MediaInfo(
                    title=title,
                    url=url,
                )
    return None


def _video(url: str, results: dict) -> MediaInfo:
    title = "unknown"
    for content in results["contents"]:
        if "videoPrimaryInfoRenderer" in content:
            video = content["videoPrimaryInfoRenderer"]
            title = video["title"]["runs"][0]["text"]
            break
    
    return MediaInfo(
        title=title,
        url=url,
    )


def _playlist(playlist: dict) -> list[MediaInfo]:
    items : list[MediaInfo] = []
    for video in playlist["contents"]:
        if "playlistPanelVideoRenderer" in video.keys():
            video_data = video.get("playlistPanelVideoRenderer", {})
            id = video_data["videoId"]

            title = str(video_data.get("title", {}).get("simpleText", id))
            url=f"https://www.youtube.com/watch?v={id}"

            items.append(MediaInfo(
                title=title,
                url=url,
            ))

    return items


def _parse(url: str, is_search: bool) -> Iterable[MediaInfo]:
    if "youtube" not in url and "youtu.be" not in url:
        return

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

    else:
        next_results = data["contents"]["twoColumnWatchNextResults"]
        if "playlist" in next_results:
            playlist = next_results["playlist"]["playlist"]
            yield from _playlist(playlist)
        else:
            results = next_results["results"]["results"]
            yield _video(url, results)


def extract(text: str) -> list[MediaInfo]:
    is_search = not urllib.parse.urlparse(text).scheme

    if is_search:
        encoded_search = urllib.parse.quote_plus(text)
        text = f"https://youtube.com/results?search_query={encoded_search}"

    return list(item for item in _parse(text, is_search) if item)
