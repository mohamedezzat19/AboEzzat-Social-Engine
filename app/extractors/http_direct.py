from urllib.parse import urlsplit

from app.extractors.base import BaseExtractor
from app.schemas import ExtractResponse, MediaFormat


class HttpDirectExtractor(BaseExtractor):
    name = "http_direct"
    extensions = {
        ".mp4": "mp4",
        ".m3u8": "hls",
        ".mpd": "dash",
        ".m4a": "audio",
        ".mp3": "audio",
        ".aac": "audio",
        ".webm": "unknown",
    }

    async def extract(self, url: str) -> ExtractResponse:
        path = urlsplit(url).path.lower()
        media_type = next((kind for suffix, kind in self.extensions.items() if path.endswith(suffix)), None)
        if not media_type:
            return ExtractResponse(
                success=False,
                extractor=self.name,
                error_code="NO_DIRECT_MEDIA",
                message="The supplied URL does not look like a direct media file. No platform adapter has matched it yet.",
            )
        return ExtractResponse(
            success=True,
            platform=urlsplit(url).hostname,
            title=None,
            formats=[MediaFormat(url=url, type=media_type)],
            extractor=self.name,
        )
