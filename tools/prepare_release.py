#!/usr/bin/env python3
"""Prepare reviewed local APK and full source assets; never publish or push."""
import hashlib
import io
import json
import argparse
from pathlib import Path
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def git(*args: str, cwd: Path = ROOT) -> bytes:
    return subprocess.check_output(["git", "-C", str(cwd), *args])


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def main(openssl_source: Path | None = None) -> None:
    release = json.loads((ROOT / "website/release.json").read_text())
    apk = ROOT / "dist" / release["apk"]
    if digest(apk) != release["sha256"]:
        raise ValueError("APK differs from the reviewed website release fingerprint")
    if openssl_source is None:
        openssl_source = next(iter(sorted((ROOT / "app/.cxx").glob("**/openssl-3.4.4.tar.gz"))), None)
    if openssl_source is None:
        raise ValueError("Provide --openssl-source pointing to the original OpenSSL 3.4.4 source tarball")
    openssl_hash = "7bdf55ac20f2779e99e5eca306f824fad2b37dee5a06cc35ed5a8b85a6060010"
    if digest(openssl_source) != openssl_hash:
        raise ValueError("OpenSSL source differs from the tarball used for this APK")
    destination = ROOT / "dist" / f"github-{release['tag']}"
    destination.mkdir(parents=True, exist_ok=True)
    prefix = f"OpenTV-Cast-{release['version']}"
    # Top-level project sources only. Gitlinks are exported separately below.
    names = set(git("ls-files", "-z", "--cached", "--others", "--exclude-standard").decode().split("\0")) - {""}
    names -= set(git("ls-files", "--deleted", "-z").decode().split("\0"))
    modules = {}
    for row in git("ls-files", "--stage").decode().splitlines():
        metadata, path = row.split("\t", 1)
        mode, commit, _stage = metadata.split()
        if mode == "160000":
            modules[path] = commit
    names -= modules.keys()
    blocked = {"local.properties", ".env", "upload.jks"}
    for name in names:
        path = Path(name)
        if (path.parts[0] in {"work", "dist", ".git", ".gradle", "_site"}
                or path.name in blocked or path.suffix in {".jks", ".keystore", ".pem", ".key"}):
            raise ValueError(f"Local/private file unexpectedly selected: {name}")
        if not (ROOT / path).is_file() or (ROOT / path).is_symlink():
            raise ValueError(f"Expected a regular source file: {name}")
    manifest = []
    def normalize(info: tarfile.TarInfo) -> tarfile.TarInfo:
        info.uid = info.gid = 0
        info.uname = info.gname = ""
        return info

    with tempfile.TemporaryDirectory(prefix="opentv-source-") as temp:
        bundle = Path(temp) / release["source"]
        with tarfile.open(bundle, "w:gz") as archive:
            for name in sorted(names):
                path = ROOT / name
                archive.add(path, arcname=f"{prefix}/{name}", recursive=False, filter=normalize)
                manifest.append(f"{digest(path)}  {name}")
            for module, commit in sorted(modules.items()):
                # Export the pinned pristine dependency, not its generated patch worktree.
                data = git("archive", "--format=tar", commit, cwd=ROOT / module)
                with tarfile.open(fileobj=io.BytesIO(data)) as dependency:
                    for member in dependency:
                        original = member.name
                        content = dependency.extractfile(member) if member.isfile() else None
                        member.name = f"{prefix}/{module}/{original}"
                        archive.addfile(normalize(member), content)
                        if content:
                            content.close()
                manifest.append(f"git {commit}  {module} (pristine; tracked patches apply during build)")
            bundled = "bundled-sources/openssl-3.4.4.tar.gz"
            archive.add(openssl_source, arcname=f"{prefix}/{bundled}", recursive=False, filter=normalize)
            manifest.append(f"{openssl_hash}  {bundled}")
            note = f"""# Full source archive — {release['version']}

This archive contains a source working-tree snapshot, all pinned native submodule
sources, licenses, and build patches. It contains no Git metadata or signing keys.
SDK, JDK and managed dependencies are obtained using the build instructions.
The original OpenSSL 3.4.4 source tarball used by this APK is included under
bundled-sources/ with its license. The unmodified build scripts download that
version from upstream; they do not automatically use this local copy.

Before building, initialize ONLY UxPlay as a local Git repository, because the
Gradle patch task uses Git to restore and apply the tracked native patches:

    git init app/src/main/cpp/third_party/UxPlay
    git -C app/src/main/cpp/third_party/UxPlay add .
    git -C app/src/main/cpp/third_party/UxPlay -c user.name=SourceBuild -c user.email=source@example.invalid commit -m "Pristine source archive dependency"

Then follow README.md for SDK/JDK setup and the Gradle build. Do not run
submodule update in this source archive; its dependencies are already included.
See SOURCE_MANIFEST.txt for project fingerprints and dependency revisions.
This does not promise a bit-for-bit APK match or include a private signing key.
"""
            for name, text in {"SOURCE_ARCHIVE.md": note, "SOURCE_MANIFEST.txt": "\n".join(manifest) + "\n"}.items():
                content = text.encode()
                info = tarfile.TarInfo(f"{prefix}/{name}")
                info.size = len(content)
                info.mode = 0o644
                archive.addfile(info, io.BytesIO(content))
        source = destination / release["source"]
        import shutil
        shutil.copyfile(bundle, source)
    import shutil
    shutil.copyfile(apk, destination / apk.name)
    (destination / release["checksum_file"]).write_text(f"{release['sha256']}  {apk.name}\n")
    (destination / f"{prefix}-SOURCE-SHA256SUMS.txt").write_text(f"{digest(source)}  {source.name}\n")
    print(f"Prepared {len(names)} project files and {len(modules)} native dependencies in {destination}")
    print("Not published. Review assets and source manifest before uploading.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--openssl-source", type=Path)
    main(parser.parse_args().openssl_source)
