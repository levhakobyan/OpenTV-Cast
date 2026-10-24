# Contributing to OpenTV-Cast

Bug reports, device compatibility reports, documentation and focused fixes are welcome. Please search existing issues first.

For a playback issue, include the app version, TV/box model, Android version, sender device/OS, Wi-Fi or Ethernet, mirroring versus media streaming, resolution/FPS, and steps to reproduce. Say whether sound, video, or both are affected. Use a non-protected clip you can share. Remove personal information from logs and screenshots.

For code changes, describe the problem and resulting behavior, keep the diff focused, and run the checks in README.md. Changes to asynchronous playback should cover disconnect/reconnect, surface recreation and teardown. JVM tests cannot replace hardware playback tests; state what you tested and what remains unverified.

Keep the install ID and preference compatibility unless a change explicitly requires otherwise. Keep native modifications as ordered patches under `app/src/main/cpp/patches/UxPlay`; Gradle restores and applies these files during native configuration.

Contributions are distributed under the project's GPL-3.0 license. Preserve attribution and third-party notices. Do not include credentials, signing keys, device identifiers, local SDK paths, generated builds or private captures in a pull request.
