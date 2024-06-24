import json
import requests
import urllib
from base import MediaItem, QueueItem


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
                    medias=[
                        MediaItem(
                            title=title,
                            url=url,
                        ),
                    ],
                )
    return None


def _video(url: str, data: dict) -> QueueItem:
    title = "unknown"
    for content in data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"]:
        if "videoPrimaryInfoRenderer" in content:
            video = content["videoPrimaryInfoRenderer"]
            title = video["title"]["runs"][0]["text"]
    
    return QueueItem(
        title=title,
        medias=[
            MediaItem(
                title=title,
                url=url,
            ),
        ],
    )


def _playlist(data: dict) -> QueueItem:
    playlist = data["contents"]["twoColumnWatchNextResults"]["playlist"]["playlist"]
    title = playlist["title"]

    medias = []
    for video in playlist["contents"]:
        if "playlistPanelVideoRenderer" in video.keys():
            video_data = video.get("playlistPanelVideoRenderer", {})
            id = video_data["videoId"]
            medias.append(MediaItem(
                url=f"https://www.youtube.com/watch?v={id}",
                title=video_data.get("title", {}).get("simpleText", id),
            ))

    return QueueItem(
        title=title,
        medias=medias
    )


def _parse(url: str, is_search: bool) -> QueueItem:
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
    data = json.loads(json_str)

    if is_search:
        return _search(data)

    if "&list=" in url:
        return _playlist(data)
    return _video(url, data)


def extract(text: str) -> QueueItem:
    is_search = not urllib.parse.urlparse(text).scheme

    if is_search:
        encoded_search = urllib.parse.quote_plus(text)
        text = f"https://youtube.com/results?search_query={encoded_search}"

    return _parse(text, is_search)