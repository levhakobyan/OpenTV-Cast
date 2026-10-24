# Castora 0.2.0 — verification

## Implemented
- Castora app label, default AirPlay receiver name, adaptive/legacy launcher icons and TV banner. Existing package and signing key retained.
- Mirroring decoder output drains independently of input packets. SurfaceTexture notifications use a dedicated callback thread. Idle/reconnect/teardown paths retain bounded worker counts.
- Official Cast Connect direct-video/HLS receiver activity with validated HTTP(S) URL loads, autoplay/position/rate and play/pause/seek/stop media session control. Unsupported devices show setup information. Accepted Cast loads preempt AirPlay; setup alone does not.
- Media3 opt-in/API requirements declared and LifecycleService.onStartCommand super call restored after lint findings. No lint suppression or unsafe manifest minimum-SDK override.

## Passed
- Final command: `:app:testDebugUnitTest :app:assembleDebug :app:lintDebug` — BUILD SUCCESSFUL (31s). Lint has no errors; existing warnings remain.
- Three JUnit tests cover accepted network URLs/media types and invalid/local/credential-bearing locations.
- Actual Kotlin renderer sources pass the JVM platform-boundary regression harness: delayed final-frame drain, callbacks without main-loop pumping, display-surface replacement, resolution/keyframe changes, reconnect, output errors, concurrent release, ten restart cycles and GL initialization failure cleanup. The agent also showed each targeted test failing against its original source file. This does not measure physical MediaCodec performance.
- APK signature valid; signing certificate matches TV Bridge 0.1.0. Packaged native AirPlay libraries include arm64-v8a, armeabi-v7a and x86_64; min API 23 retained.
- API 34 phone emulator upgraded from version 0.1.0 to 0.2.0 without uninstall; a saved custom receiver name survived. Native AirPlay OPTIONS and /info responded after upgrade.
- Opening the unsupported-device Cast setup screen did not interrupt the active AirPlay receiver. Setup UI inspected.
- Final APK after lifecycle correction installed/launched successfully; native /info responded with Castora after test-name change.
- Bash download script syntax and `git diff --check` passed. Download uses fresh APK-only staging directory and retains /tv-bridge.apk route.

## Required physical acceptance / external setup
The Xiaomi motion symptom has not been remeasured on hardware. Compare the same numbered 30/60 FPS clip before/after using the same sender, network, resolution, codec and TV picture settings; include UI load, portrait/landscape, fullscreen and reconnect transitions. MacBook and iPhone real AirPlay playback still require acceptance; the upstream receiver supports both platforms.

Actual Google Cast playback remains unverified and needs the registration and compatible sender described in CAST_SETUP.md. No Console registration or app ID was created. This APK does not replace the TV's system Google Cast for whole-screen Android casting or arbitrary third-party apps/YouTube; unsupported boxes do not become certified Chromecast devices. Cast queues/credentials/DRM are not implemented. It remains a debug test build, not a signed production release.

The active Cloudflare session stages an old copy. Restart start-download.sh to serve this new APK; use its new URL. Do not publish the private source archive through that script.

Final icon safe-area adjustment: `:app:assembleDebug :app:lintDebug` passed (14s). Final APK signature verified and matches 0.1.0 certificate; packaged dist APK/checksum refreshed.
