from typing import Literal
from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    url: str = Field(min_length=8, max_length=4096)


class MediaFormat(BaseModel):
    url: str
    quality: str | None = None
    type: Literal["mp4", "hls", "dash", "audio", "unknown"] = "unknown"
    headers: dict[str, str] = Field(default_factory=dict)
    expires_at: str | None = None


class ExtractResponse(BaseModel):
    success: bool
    platform: str | None = None
    title: str | None = None
    thumbnail: str | None = None
    formats: list[MediaFormat] = Field(default_factory=list)
    requires_cookies: bool = False
    extractor: str | None = None
    error_code: str | None = None
    message: str | None = None
