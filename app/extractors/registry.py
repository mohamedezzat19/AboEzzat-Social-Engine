from app.config import settings
from app.extractors.base import BaseExtractor
from app.extractors.http_direct import HttpDirectExtractor
from app.extractors.ytdlp_adapter import YtDlpExtractor
from app.security import is_allowed_platform_host
from app.schemas import ExtractResponse


class ExtractorRegistry:
    def __init__(self) -> None:
        self._direct = HttpDirectExtractor()
        self._platform = YtDlpExtractor() if settings.enable_ytdlp else None

    async def extract(self, url: str) -> ExtractResponse:
        direct = await self._direct.extract(url)
        if direct.success:
            return direct

        from urllib.parse import urlsplit
        host = (urlsplit(url).hostname or "").lower()
        if self._platform and is_allowed_platform_host(host):
            return await self._platform.extract(url)

        return ExtractResponse(
            success=False,
            extractor="registry",
            error_code="UNSUPPORTED_URL",
            message="No enabled extractor supports this URL. Supported platform adapters are limited to the configured public-site allowlist.",
        )


registry = ExtractorRegistry()
