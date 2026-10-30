from app.extractors.ytdlp_adapter import _format_sort_key
from app.schemas import MediaFormat


def test_highest_resolution_is_ranked_first():
    formats = [
        MediaFormat(url="https://cdn.example/720.mp4", type="mp4", quality="720p"),
        MediaFormat(url="https://cdn.example/1080.m3u8", type="hls", quality="1080p"),
        MediaFormat(url="https://cdn.example/480.mp4", type="mp4", quality="480p"),
    ]
    ranked = sorted(formats, key=_format_sort_key)
    assert [item.quality for item in ranked] == ["1080p", "720p", "480p"]


def test_progressive_mp4_wins_resolution_tie():
    formats = [
        MediaFormat(url="https://cdn.example/1080.m3u8", type="hls", quality="1080p"),
        MediaFormat(url="https://cdn.example/1080.mp4", type="mp4", quality="1080p"),
    ]
    ranked = sorted(formats, key=_format_sort_key)
    assert ranked[0].type == "mp4"
