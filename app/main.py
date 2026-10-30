from fastapi import Depends, FastAPI

from app.config import settings
from app.extractors.registry import registry
from app.schemas import ExtractRequest, ExtractResponse
from app.security import require_bearer_token, validate_public_http_url

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name, "version": "0.1.0"}


@app.post(
    "/api/v1/extract",
    response_model=ExtractResponse,
    dependencies=[Depends(require_bearer_token)],
)
async def extract_media(payload: ExtractRequest):
    safe_url = validate_public_http_url(payload.url)
    result = await registry.extract(safe_url, cookies=payload.cookies)
    return result or ExtractResponse(
        success=False,
        error_code="NO_EXTRACTOR",
        message="No enabled extractor could process this URL.",
    )
