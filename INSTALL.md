# OpenTV-Cast — install and test

The debug APK is a local test build of an open-source AirPlay receiver. It is not an Apple-certified receiver and has not yet been validated on physical TV models.

## On the TV
1. Copy `OpenTV-Cast-0.2.1-debug-universal.apk` to the TV or box (for example with a USB drive or an existing file transfer app).
2. Open it using the TV file manager. If Android asks, allow installation from that file manager, then install.
3. Open **OpenTV-Cast** from the apps screen. Grant notification access if requested. Start the receiver if it is stopped.
4. Change the receiver name in Settings if you have multiple TVs. Optionally enable a PIN. Overlay access is only needed for bringing the receiver to the front automatically; use the app open in the foreground for the first test.

## On the iPhone
1. Connect to the same local network as the TV. Avoid a guest network that isolates devices.
2. Open Control Center, then **Screen Mirroring** and choose **OpenTV-Cast** (or the receiver name you chose).
3. If a PIN is enabled, enter the code shown on the TV.
4. For supported media apps, use their AirPlay control. Whole-screen mirroring and an app-specific AirPlay stream are separate paths; test the one you need.

## Acceptance checklist
- TV appears in the iPhone list; connection succeeds.
- Portrait and landscape pictures render with sound.
- Stop mirroring and reconnect.
- Navigate Settings using the TV remote.
- Repeat after leaving/reopening the app and after a TV restart.

Protected video may show a black screen or fail; upstream does not support DRM-protected content. If ordinary mirroring stutters, try 1280x720 and 30 FPS in Settings. Device compatibility must be established through testing, not the TV brand alone.

## Developer installation
With an authorized device already connected to adb:

```sh
adb install -r OpenTV-Cast-0.2.1-debug-universal.apk
adb shell am start -n local.airplaytv.receiver/io.github.jqssun.airplay.MainActivity
```

This fork uses application ID `local.airplaytv.receiver`, so it can be installed beside the upstream app. Stop the other receiver before testing: both may attempt to use the same listening port.

## Upgrade from TV Bridge
Install OpenTV-Cast over the existing build; application ID and debug signing identity are unchanged. Custom receiver names and settings remain. The default receiver name becomes OpenTV-Cast only when no custom name was saved. See CAST_SETUP.md before expecting Cast Connect playback.
