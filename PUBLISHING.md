# Publishing OpenTV-Cast

This guide describes the release and website workflow for the **public** GitHub repository `levhakobyan/OpenTV-Cast`, with `main` as its branch. If a different name is chosen, update README links; Pages automatically uses the actual GitHub repository for download/source links.

## Before the first push

- Review the source diff and the release notes. Keep `local.properties`, signing keys, `work/`, `dist/` and caches out of Git.
- Preserve the upstream Git history, GPL license, source notices and pinned submodules. The dirty UxPlay working tree is generated from tracked patches; do not commit a private submodule reference.
- Commit the reviewed source to `main` when ready. Keep the original repository as `upstream`, then add your empty public repository as `origin`; do not push this fork to jqssun's repository.
- Run the checks in README.md and build the website with `python3 tools/build_site.py`.

No command here automatically creates a repository, pushes, publishes a release or changes account settings.

## Prepare release assets

Run `python3 tools/prepare_release.py` after the final source review. It verifies the existing APK against `website/release.json`, copies it and its checksum into `dist/github-v0.2.1/`, and creates a source archive including the pinned submodules, build patches and original OpenSSL 3.4.4 source tarball. It finds the latter in the native build cache, or accepts `--openssl-source /path/to/openssl-3.4.4.tar.gz`, and verifies its fingerprint against the source used for this preview. It uses Git's source file list, excludes ignored/local files, and does not include `.git` directories or private keys. Review the archive manifest before uploading.

Use the existing APK for this preview so installed local test builds can upgrade with the same debug signer. A CI-generated debug APK will have a different key. Do not publish private signing material. A stable production signing plan is still needed for future public upgrades.

## Publish the APK release

After pushing the reviewed source, create a GitHub release tagged **`v0.2.1`** at that source commit. Mark it as a **pre-release** and use `release-notes/v0.2.1.md` for the description. Attach all files from `dist/github-v0.2.1/` together:

- `OpenTV-Cast-0.2.1-debug-universal.apk`
- `OpenTV-Cast-0.2.1-SHA256SUMS.txt`
- `OpenTV-Cast-0.2.1-source.tar.gz`
- `OpenTV-Cast-0.2.1-SOURCE-SHA256SUMS.txt`

The site links to this explicit tag, because preview releases do not reliably resolve through GitHub's `/releases/latest` URL. Keep the filenames exactly as listed. GitHub's default source ZIP alone omits submodules.

## Enable GitHub Pages

In the public repository, open **Settings → Pages → Build and deployment → Source → GitHub Actions**. Run **Actions → Publish download website → Run workflow**, on `main`. Later changes to the website on `main` deploy automatically.

The expected URL for the proposed repository is `https://levhakobyan.github.io/OpenTV-Cast/`. Publish the APK release before sharing this page so its download links work. Pages hosts only the static website; the APK and full source archive are served by GitHub Releases. A download does not silently install an Android app.

## After publishing

Open the live page on desktop, phone and the TV browser. Verify the APK download completes, its SHA-256 matches, the release/source links work, and Android shows installation confirmation. GitHub may be inaccessible from some networks, and a browser's broken download manager is not fixed by hosting alone.

Official references: [GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages), [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).
