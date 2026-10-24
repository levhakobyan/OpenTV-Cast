# Google Cast / Cast Connect

## What is implemented
OpenTV-Cast has an isolated official Cast Connect video receiver activity, `io.github.jqssun.airplay.cast.CastPlaybackActivity`. It handles Google Cast LAUNCH/LOAD intents, supported direct HTTP(S) video/HLS loads, start position, autoplay and playback rate, and exposes play/pause/seek/stop through its media session. Invalid URLs, local file/content locations, embedded credentials, unsupported media types, queues and load credentials are rejected. DRM, custom app-specific entities and queue handling are outside this implementation.

An accepted Cast load stops the AirPlay receiver before playback so its native audio/video cannot continue underneath Cast. Opening the Cast setup screen alone does not stop AirPlay. Returning to the main screen requests AirPlay restart only if Cast actually preempted a running receiver. Explicit user Stop is otherwise preserved.

## Setup required before device acceptance
1. Use a TV/box that already supports Google's Cast infrastructure and Google Play services. Installing this APK alone does not turn every Android box into a certified Chromecast.
2. Register a receiver application in the Google Cast SDK Developer Console and associate its Android TV package with `local.airplaytv.receiver`.
3. For this sideloaded debug APK, register the TV's **Google Cast software serial number** in that same Console. This is not the serial number printed on the box. Follow Google's registration/wait/restart instructions.
4. Use a compatible Cast sender configured with the matching receiver app ID and Cast Connect support. No app ID or sender registration has been created automatically.
5. Send a supported direct video URL. Confirm launch, media playback, pause, seek, stop, second load, error handling, remote control, background/return, and AirPlay/Cast switching on hardware.

Official references:
- https://developers.google.com/cast/codelabs/cast-connect-atv
- https://developers.google.com/cast/docs/android_tv_receiver/core_features
- https://developers.google.com/cast/docs/android_tv_receiver/troubleshooting

## Android screen mirroring and third-party apps
Google Home whole-screen mirroring and apps such as YouTube use the TV's existing system Google Cast receivers. Those apps do not automatically launch OpenTV-Cast's custom receiver. Cast Connect is an integration for compatible senders, not a generic replacement for all receiver application IDs. Use the TV's system Cast name for those flows.

## Library compatibility
`play-services-cast-tv:21.1.1` is combined with `play-services-cast:22.3.1` to retain the application's API 23 minimum. The newer Cast 23 library declares minimum API 24 and was rejected by the manifest merger. No unsafe manifest override is used. The APK retains ARM32, ARM64 and x86_64 builds; this is not proof of hardware Cast availability.

## Independent receiver investigation (2026-10-25)
The user requested compatibility on boxes without system Google Cast, without paid registration, and allowed omitting this feature if that requirement could not be met. No registration or payment was completed. Existing Cast Connect code is retained, but it is not a universal Cast receiver.

Source review of Chromium Open Screen and `yukarikaname/openchromecast` did not establish a receiver that works with unchanged Android Cast apps and normally launched Chrome on arbitrary boxes. Chromium validates the receiver's certificate chain. Open Screen documents a developer receiver workflow requiring Chrome to be launched with `--cast-developer-certificate-path` pointing at its generated root certificate. This is a possible Chrome-only experiment, not evidence of stock Android sender compatibility. The standalone receiver also needs Android playback/platform integration; it was not built or tested here.

No independent receiver was added to the APK, no browser trust settings were changed, and no device credentials were extracted. The current APK and its hardware verification gaps remain as documented in `VERIFICATION-0.2.0.md`.

Primary evidence:
- [Open Screen developer receiver instructions](https://chromium.googlesource.com/openscreen/+/refs/heads/main/cast/docs/USING.md)
- [Chromium Cast certificate trust store](https://chromium.googlesource.com/chromium/src/+/refs/heads/main/components/media_router/common/providers/cast/certificate/cast_trust_store.cc)
- [Open Screen standalone mirroring application](https://chromium.googlesource.com/openscreen/+/refs/heads/main/cast/standalone_receiver/mirroring_application.cc)
- [OpenChromecast source and limitations](https://github.com/yukarikaname/openchromecast)
