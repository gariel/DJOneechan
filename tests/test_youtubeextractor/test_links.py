
import pytest

from downloader import youtubeextractor

@pytest.mark.parametrize(
    "description,link",
    [
        ("Video Music", "https://www.youtube.com/watch?v=V9PVRfjEBTI"),
        ("Query", "apt"),
        ("Music", "https://music.youtube.com/watch?v=WKZO-CWeOVA"),
        ("Playlist Premiere", "https://www.youtube.com/watch?v=WBzJjzpyp8I&list=PLa6vAiDb1x3uJIuiNBMig_U4iji4uy3Wq"),
        ("Shortened Video", "https://youtu.be/watch?v=V9PVRfjEBTI"),
        ("Mobile Video", "https://m.youtube.com/watch?v=V9PVRfjEBTI"),
    ],
)
def test_should_be_able_to_find_youtube_links(description: str, link: str):
    medias = youtubeextractor.extract(link)
    assert len(medias) == 1


@pytest.mark.parametrize(
    "description,link",
    [
        ("Video Playlist", "https://www.youtube.com/watch?v=z_b4tucWzSw&list=PLa6vAiDb1x3svD9LX_atO--y2zDUTjeZt"),
        ("Radio with Premiere", "https://www.youtube.com/watch?v=WBzJjzpyp8I&list=RDWBzJjzpyp8I&start_radio=1&rv=WBzJjzpyp8I"),
        ("Music Playlist", "https://music.youtube.com/watch?v=WKZO-CWeOVA&list=RDAMVMWKZO-CWeOVA"),
    ],
)
def test_should_be_able_to_find_youtube_links_for_playlists(description: str, link: str):
    medias = youtubeextractor.extract(link)
    assert len(medias) > 10


@pytest.mark.parametrize(
    "description,link",
    [
        ("Soundcloud", "https://soundcloud.com/delilahsaxena/need-to-breathe"),
        ("Spotify", "https://open.spotify.com/intl-pt/track/14WYmNQWvR2TTWoRp8t9Ml?si=7ec97a0e671f4768"),
        ("Random - Google", "https://google.com"),
    ]
)
def test_should_not_break_for_other_links(description: str, link: str):
    medias = youtubeextractor.extract(link)
    assert len(medias) == 0