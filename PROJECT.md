# OpenTV-Cast — project context

## Goal
Build an installable AirPlay receiver for Android TV / Google TV and Android TV boxes, independent of the TV brand. An iPhone should discover it through its existing AirPlay / Screen Mirroring controls on the same local network.

## Foundation and licensing
This is a downstream adaptation of https://github.com/jqssun/android-airplay-server at commit a46cca0a6a1274e9e33c0e750f0f1c1eb1d881ea. Preserve its GPL-3.0 license, credits, and the licenses of bundled dependencies. Keep the existing Kotlin package and JNI names together; the installable application ID may differ.

## Compatibility target
- One APK containing arm64-v8a, armeabi-v7a, and x86_64 native libraries.
- The current manifest/build declares minimum Android API 23. This is an installation constraint, not proof of device compatibility.
- Android TV launcher and remote navigation are inherited from upstream.
- Samsung Tizen and LG webOS require separate platform applications.
- Sender and receiver must share a local subnet allowing multicast discovery and direct connections.
- DRM-protected content is unsupported by the upstream receiver.
- Do not advertise universal compatibility until tested on representative physical TVs/boxes and iOS versions.

## Verification required
Build and inspect all packaged ABIs, the merged manifest, and APK signature. Smoke-test startup where an emulator is available. Physical acceptance still requires a real iPhone and TV: discovery, PIN connection if enabled, portrait/landscape mirroring with audio, disconnect/reconnect, remote navigation, and background/foreground transitions. Emulator startup alone does not prove AirPlay works.

## Local build setup
Use JDK 21. The first build downloads dependencies. Install Android SDK 37, NDK 27.0.12077973 and CMake 3.22.1 in your own Android SDK directory. These are local tools; do not commit SDKs, caches, signing keys, or local.properties.

Build from the project root with `./gradlew :app:assembleDebug`, with JAVA_HOME and ANDROID_HOME set appropriately. A successful debug APK is for device testing; distribution signing is a separate step.

## Version 0.2.0 scope
New OpenTV-Cast branding and icon. Mirror decoder output drains independently of incoming packets, with dedicated SurfaceTexture callbacks. Official Cast Connect activity is implemented but requires the external setup in CAST_SETUP.md and hardware acceptance. Android whole-screen/third-party app Cast still uses the box system receiver. Preserve package ID and stored preferences when upgrading.
