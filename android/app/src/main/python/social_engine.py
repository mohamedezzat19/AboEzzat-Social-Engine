import ipaddress
import json
import re
import socket
from urllib.parse import urlsplit

ALLOWED_HOSTS = {"youtube.com","youtu.be","youtube-nocookie.com","facebook.com","fb.watch","instagram.com","tiktok.com","x.com","twitter.com","threads.net"}
TIMEOUT_SECONDS = 25

def _allowed_host(host):
    host=(host or "").rstrip(".").lower()
    return any(host==domain or host.endswith("."+domain) for domain in ALLOWED_HOSTS)

def _validate_url(value):
    value=(value or "").strip()
    if len(value)>4096: raise ValueError("URL too long")
    parsed=urlsplit(value)
    if parsed.scheme not in ("http","https") or not parsed.hostname: raise ValueError("Only HTTP(S) URLs are supported")
    if parsed.username or parsed.password or not _allowed_host(parsed.hostname): raise ValueError("This platform is not allowed")
    host=parsed.hostname.rstrip(".").lower()
    try:
        addresses={item[4][0] for item in socket.getaddrinfo(host,parsed.port or (443 if parsed.scheme=="https" else 80),type=socket.SOCK_STREAM)}
    except (OSError,UnicodeError,ValueError): raise ValueError("The platform host could not be resolved")
    if not addresses: raise ValueError("The platform host could not be resolved")
    for address in addresses:
        if not ipaddress.ip_address(address).is_global: raise ValueError("Private network destinations are not allowed")
    return value

def _format_key(item):
    quality=str(item.get("quality") or "")
    match=re.search(r"(\d{3,4})\s*p",quality,re.I)
    height=int(match.group(1)) if match else 0
    return (-height,0 if item.get("type")=="mp4" else 1,quality)

def extract_json(url,cookies=""):
    try:
        safe_url=_validate_url(url)
        import yt_dlp
        options={"quiet":True,"no_warnings":True,"noplaylist":True,"skip_download":True,"cachedir":False,"socket_timeout":TIMEOUT_SECONDS,"ignoreerrors":False}
        if cookies:
            if "\r" in cookies or "\n" in cookies: raise ValueError("Invalid cookie header")
            options["http_headers"]={"Cookie":cookies.strip()}
        with yt_dlp.YoutubeDL(options) as ydl: info=ydl.extract_info(safe_url,download=False)
        if not info:
            return json.dumps({"success":False,"extractor":"yt_dlp","error_code":"NO_MEDIA","message":"The page did not return playable media.","formats":[]})
        raw=list(info.get("formats") or [])
        if info.get("url"): raw.append(info)
        formats=[]; seen=set()
        for item in raw:
            media_url=item.get("url")
            if not media_url or item.get("has_drm"): continue
            protocol=(item.get("protocol") or "").lower(); ext=(item.get("ext") or "").lower()
            if "m3u8" in protocol: kind="hls"
            elif "dash" in protocol or ext=="mpd": kind="dash"
            elif ext in ("mp4","m4v"): kind="mp4"
            elif ext in ("m4a","mp3","aac","opus"): kind="audio"
            else: kind="unknown"
            key=(media_url,kind)
            if key in seen: continue
            seen.add(key)
            headers={str(k):str(v) for k,v in (item.get("http_headers") or {}).items() if str(k).lower() not in ("cookie","authorization","proxy-authorization")}
            height=item.get("height"); quality=(str(height)+"p") if height else (item.get("format_note") or item.get("format_id"))
            formats.append({"url":media_url,"quality":str(quality) if quality else None,"type":kind,"headers":headers,"expires_at":None})
        formats.sort(key=_format_key)
        if not formats:
            return json.dumps({"success":False,"platform":urlsplit(safe_url).hostname,"extractor":"yt_dlp","error_code":"NO_PLAYABLE_FORMATS","message":"No non-DRM playable formats were returned.","requires_cookies":bool(info.get("login_required")),"formats":[]})
        return json.dumps({"success":True,"platform":info.get("extractor_key") or urlsplit(safe_url).hostname,"title":info.get("title"),"thumbnail":info.get("thumbnail"),"formats":formats[:12],"requires_cookies":False,"extractor":"yt_dlp","error_code":None,"message":None})
    except ValueError as error:
        return json.dumps({"success":False,"error_code":"INVALID_URL","message":str(error),"formats":[]})
    except Exception as error:
        return json.dumps({"success":False,"extractor":"yt_dlp","error_code":"PLATFORM_EXTRACTION_FAILED","message":"yt-dlp could not extract this page ("+type(error).__name__+").","formats":[]})
