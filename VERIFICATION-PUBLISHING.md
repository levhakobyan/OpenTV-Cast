# Publication preparation — 2026-10-25

## Ready locally

- Rewritten README, installation/build instructions, changelog, contributing guide, issue/PR templates, GPL license and third-party attribution.
- Static download site, self-hosted SVG illustrations and responsive CSS; no JavaScript, analytics or remote fonts.
- Repository-aware Pages build workflow and a separate Android verification workflow. Removed the inherited automatic upstream release workflow that assumed private signing secrets.
- Release notes and local packaging tool for the unchanged 0.2.1 APK, checksums, pinned native dependency source and the original OpenSSL 3.4.4 source tarball.

## Checks performed

- Website rendered and screenshots inspected at desktop 1440px and mobile 390px. Layout geometry/image loading checked at 320px, 768px and 1920px: no horizontal overflow or broken images.
- FAQ and checksum disclosures open; keyboard skip navigation and visible focus work. Reduced-motion mode disables smooth scrolling/transitions. No browser page errors observed.
- Generated page has no unresolved template fields. Download, source, release and checksum links resolve to the intended explicit `v0.2.1` filenames (not a `/latest` alias).
- Pages/build workflow and issue-template YAML parsed successfully; Python helpers compiled and executed; shell syntax and `git diff --check` passed.
- Pristine pinned UxPlay plus all nine tracked patches matches all six modified native working-tree files byte for byte. Generated native changes do not require publishing a private submodule commit.
- Existing APK fingerprint matches release metadata and the current local build output. No Android runtime source was changed during publication preparation; prior Android verification is recorded in `VERIFICATION-0.2.0.md`.
- Limited credential-pattern audit of selected project text files and 62 local history commits found no supported token/private-key patterns; publication candidates contain no personal home-directory paths. Gitleaks is not installed, so this is **not** a complete Gitleaks audit. Ignored local SDK/cache/signing files and submodule contents were outside that pattern scan.

## Status at the preparation checkpoint

At that checkpoint, per the user's request, no repository had been created, no commit/tag/push had been made, and neither the release nor Pages had been published. Remote download links therefore cannot be validated yet. GitHub Actions execution, public APK transfer and installation from the public page require checks after publication. The proposed repository is `levhakobyan/OpenTV-Cast`; change README links if a different name is used. `PUBLISHING.md` gives the exact next steps.

Real-device smoothness and broad TV/sender compatibility remain unverified. The APK remains a debug-signed preview; future production signing needs a separate plan.

## Published and verified — 2026-10-25

The user subsequently created the public repository and authorized push, release publication and Pages enablement.

- Source pushed to `levhakobyan/OpenTV-Cast`, `main`, commit `c1f2b2a0cd75f378bc695bba62de07488f16caa2`, preserving upstream history and submodule references. The original remote is retained as `upstream`.
- Public pre-release `v0.2.1` published at that source commit with the unchanged APK, APK checksum, full source archive and source checksum. All four assets are reported uploaded by GitHub's public API.
- GitHub Pages configured to use Actions. The initial push ran before Pages was enabled and failed in configure-pages; after enabling Pages, the same workflow's second attempt passed both build and deploy in 26 seconds. No source workaround or broader permissions were needed.
- Live site: https://levhakobyan.github.io/OpenTV-Cast/
- Release: https://github.com/levhakobyan/OpenTV-Cast/releases/tag/v0.2.1
- Anonymous full APK download completed (51,892,162 bytes); SHA-256 matches `1440a481ab9316772203e52f28c2015f85b2ac53575d863a276e0ce195b3a964`. Both public checksum files match their local release assets.
- Live HTML, CSS and SVG assets returned HTTP 200. Live HTML has the correct APK link and no template placeholders; the rendered public page was inspected in Chrome.
- No Android runtime code or APK was changed for publication. Installation on the user's TV from the public page and physical playback remain manual acceptance steps.
