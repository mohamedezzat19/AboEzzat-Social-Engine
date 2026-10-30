# AboEzzat Social Engine for Android

This Android app embeds yt-dlp with Chaquopy and exposes a loopback-only API for AboEzzat Share New.

## First milestone
- Foreground service keeps the local API alive after the user starts it.
- API binds only to 127.0.0.1:8765 (not exposed to Wi-Fi).
- GET /health and POST /api/v1/extract use the existing service contract.
- A random 256-bit bearer token is generated and stored in private app preferences.
- Cookies and bearer tokens are not logged or forwarded to the TV.
- yt-dlp is embedded in the APK; no Termux or laptop is required at runtime.

## Connect Share New
1. Install and open this app.
2. Tap تشغيل المحرك.
3. Tap نسخ إعدادات Share New.
4. In Share New > Social Engine settings, set base URL to http://127.0.0.1:8765 and paste the generated bearer token.
5. Enable the Social Engine extractor.

The phone needs internet access for public websites. The local app-to-app connection does not need a router or external internet.

## Build
From this directory run gradle assembleDebug. The APK is app/build/outputs/apk/debug/app-debug.apk.

## Limitations
This milestone embeds yt-dlp as the first engine. Additional extractors and controls follow after Android build and device runtime validation. Some platforms may require cookies or JavaScript challenge support and may change frequently. A successful build does not prove extraction works on every site. Android battery management may stop background work; exempt this app from battery optimization if necessary.
