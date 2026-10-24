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

## Pending publication

Per the user's request, no repository was created, no commit/tag/push was made, and neither the release nor Pages was published. Remote download links therefore cannot be validated yet. GitHub Actions execution, public APK transfer and installation from the public page require checks after publication. The proposed repository is `levhakobyan/OpenTV-Cast`; change README links if a different name is used. `PUBLISHING.md` gives the exact next steps.

Real-device smoothness and broad TV/sender compatibility remain unverified. The APK remains a debug-signed preview; future production signing needs a separate plan.
