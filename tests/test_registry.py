from app.extractors.registry import ExtractorRegistry


def test_registry_has_direct_and_platform_adapters():
    registry = ExtractorRegistry()
    assert registry._direct.name == "http_direct"
    assert registry._platform is None or registry._platform.name == "yt_dlp"
