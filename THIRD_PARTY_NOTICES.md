# Attribution and third-party source

OpenTV-Cast is derived from [jqssun/android-airplay-server](https://github.com/jqssun/android-airplay-server), starting at `a46cca0a6a1274e9e33c0e750f0f1c1eb1d881ea`. Its GPL-3.0 license is retained in `LICENSE`, as are source notices. The Android media player includes work credited upstream to [Next Player](https://github.com/anilbeesetti/nextplayer).

Native components are pinned by Git submodule references. Clone with `--recurse-submodules`; GitHub's automatically generated source ZIP does **not** embed submodules. Distribute the accompanying complete source archive with preview APKs, including the submodule sources and tracked build patches.

| Component | Source / license location |
| --- | --- |
| UxPlay | `app/src/main/cpp/third_party/UxPlay`, GPL-3.0; `LICENSE` |
| Playfair | Bundled in UxPlay; `lib/playfair/LICENSE.md` |
| llhttp | Bundled in UxPlay; `lib/llhttp/LICENSE-MIT` |
| FFmpeg | `app/src/main/cpp/third_party/ffmpeg`; `LICENSE.md`, `COPYING.*`; this build enables minimal audio decoders |
| libplist | `app/src/main/cpp/third_party/libplist`; `COPYING*` and source notices |
| openssl-cmake | `app/src/main/cpp/third_party/openssl-cmake`; `LICENSE` |
| OpenSSL | Version 3.4.4, fetched by openssl-cmake; original source tarball and Apache-2.0 license included in release source archives under `bundled-sources/` |
| Oboe | Google Oboe, Apache-2.0; dependency declared in Gradle |
| AndroidX, Kotlin, Compose, Media3 and other managed dependencies | Versions declared in `gradle/libs.versions.toml` and `app/build.gradle.kts`; retain upstream notices |
| Google Play services Cast libraries | Governed by Google's SDK terms; the integration does not grant Google Cast certification |

Changes in this fork include branding, mirroring frame handling/lifecycle fixes, regression checks, experimental Cast Connect integration and distribution documentation. Third-party names identify compatibility or attribution and do not imply endorsement.
