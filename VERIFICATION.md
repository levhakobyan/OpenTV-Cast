# TV Bridge 0.1.0 — verification

## Passed
- Unmodified upstream baseline: `:app:assembleDebug` (5m21s).
- Downstream TV Bridge: `:app:assembleDebug` (17s).
- APK signature verification: valid v1 and v2 signatures. This is a debug-signed local test build.
- Packaged native libraries: arm64-v8a, armeabi-v7a, x86_64.
- APK metadata: local.airplaytv.receiver, version 0.1.0, min API 23, target API 37, TV launcher entry, touchscreen optional.
- Android API 34 ARM64 phone emulator: baseline and downstream installation and cold launch succeeded.
- Baseline and downstream RTSP OPTIONS and GET /info returned 200 OK.
- Downstream /info name: TV Bridge.
- Android NSD callbacks confirmed _airplay._tcp and _raop._tcp registered with TV Bridge.
- Downstream process stop and relaunch: receiver /info responded again with TV Bridge.
- Screenshot inspected: waiting-for-connection UI and TV Bridge receiver name visible.
- `git diff --check` passed.

## Not yet verified
Physical Xiaomi/other Android TV hardware, iPhone discovery across a real LAN, pairing/PIN, video/audio streaming, portrait/landscape transitions during mirroring, remote control navigation, background connections, boot behavior, and old Android releases. No real Apple sender completed an AirPlay handshake in these checks. NSD registration is not proof that an iPhone can discover the device across a particular router.

Upstream emits existing Kotlin/CMake/C compiler warnings. The default Android API 23 installation threshold does not prove runtime support on every Android 6+ device. Samsung Tizen and LG webOS are outside this APK's platform support.

## Source and changes
Full source checkout: project root (clone with submodules).
Upstream: https://github.com/jqssun/android-airplay-server
Pinned upstream commit: a46cca0a6a1274e9e33c0e750f0f1c1eb1d881ea
Preserved GPL-3.0 licensing and upstream credits. Changes are limited to app ID, app/receiver name, version, documentation, project name, and dist ignore rule. Native AirPlay, media, and security behavior remain upstream implementations. The native build reapplies the repository's existing UxPlay patches, leaving that submodule modified as expected.
