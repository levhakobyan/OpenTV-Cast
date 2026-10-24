# Changelog

## 0.2.1 — public preview

- Rename the application and default receiver to OpenTV-Cast; add the TV/signal launcher icon and banner.
- Keep the installation ID and signing identity of the existing local test build, preserving upgrades and saved receiver names.
- Include the 0.2 playback changes below.

## 0.2.0 — development preview

- Drain mirrored-video decoder output independently of network input.
- Deliver frame notifications on a dedicated thread and improve renderer teardown/reconnect behavior.
- Add deterministic renderer lifecycle regression checks.
- Add experimental official Cast Connect direct-video/HLS playback, gated by device support and external registration. This does not provide generic Android/Chrome casting on arbitrary boxes.
- Correct foreground-service lifecycle and Media3/API annotations identified by lint.

## 0.1.0 — initial local preview

- Adapt android-airplay-server for a sideloadable Android TV receiver under `local.airplaytv.receiver`.
- Package ARM64, ARM32 and x86_64 native libraries.

Physical TV smoothness and compatibility remain subject to device testing. Public preview APKs are debug-signed.
