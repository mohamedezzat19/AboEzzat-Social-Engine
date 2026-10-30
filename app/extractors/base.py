from abc import ABC, abstractmethod

from app.schemas import ExtractResponse


class BaseExtractor(ABC):
    name = "base"

    @abstractmethod
    async def extract(self, url: str) -> ExtractResponse:
        raise NotImplementedError
