from app.extractors.base import BaseExtractor
from app.extractors.http_direct import HttpDirectExtractor


class ExtractorRegistry:
    def __init__(self) -> None:
        self._extractors: list[BaseExtractor] = [HttpDirectExtractor()]

    async def extract(self, url: str):
        last_result = None
        for extractor in self._extractors:
            result = await extractor.extract(url)
            if result.success and result.formats:
                return result
            last_result = result
        return last_result


registry = ExtractorRegistry()
