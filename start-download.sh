#!/bin/bash
# Temporary, APK-only public download link. Stop with Ctrl+C.
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
for dependency in python3 cloudflared; do
    if ! command -v "$dependency" >/dev/null 2>&1; then
        echo "Missing dependency: $dependency" >&2
        echo "Install Python 3 and cloudflared first (Homebrew: brew install cloudflared)." >&2
        exit 1
    fi
done

apk_path="${APK_PATH:-$project_dir/app/build/outputs/apk/debug/app-debug.apk}"
if [[ ! -f "$apk_path" && -z "${APK_PATH:-}" ]]; then
    apk_path="$project_dir/dist/OpenTV-Cast-0.2.1-debug-universal.apk"
fi
if [[ ! -f "$apk_path" ]]; then
    echo "APK not found: $apk_path" >&2
    echo "Build the app first, or set APK_PATH to the APK you want to share." >&2
    exit 1
fi

mkdir -p "$project_dir/work"
run_dir="$(mktemp -d "$project_dir/work/apk-share.XXXXXX")"
public_dir="$run_dir/public"
mkdir "$public_dir"
server_pid=""
tunnel_pid=""
cleanup() {
    trap - EXIT INT TERM
    if [[ -n "$tunnel_pid" ]]; then
        kill "$tunnel_pid" 2>/dev/null || true
        wait "$tunnel_pid" 2>/dev/null || true
    fi
    if [[ -n "$server_pid" ]]; then
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
    fi
    echo "Download server and tunnel stopped. Logs: $run_dir"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

# A fresh directory contains only the selected APK, page and checksum.
cp "$apk_path" "$public_dir/tv-bridge.apk"
python3 - "$public_dir" <<'PY'
import hashlib
import sys
from pathlib import Path
directory = Path(sys.argv[1])
digest = hashlib.sha256((directory / 'tv-bridge.apk').read_bytes()).hexdigest()
(directory / 'SHA256SUMS.txt').write_text(digest + '  tv-bridge.apk\n')
PY
cat > "$public_dir/index.html" <<'HTML'
<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenTV-Cast download</title>
<style>
body{background:#111827;color:#fff;font:24px/1.6 system-ui,sans-serif;margin:6vh 7vw}
main{max-width:850px;margin:auto}h1{font-size:52px}a{color:#bdd7ff}
.button{display:inline-block;padding:22px 36px;background:#e0edff;color:#10213d;border-radius:14px;font-size:30px;font-weight:bold;text-decoration:none}
a:focus{outline:5px solid #fbbf24;outline-offset:8px}li{margin:14px 0}small{font-size:18px}
</style><main><h1>OpenTV-Cast</h1><p>Android TV / Google TV test build</p>
<a class="button" href="/tv-bridge.apk" download="OpenTV-Cast.apk" autofocus>Download APK</a>
<ol><li>Download the APK, then open it from your browser downloads.</li>
<li>If asked, allow this browser to install unknown apps. Choose Install, then Open.</li>
<li>Keep OpenTV-Cast open. On your iPhone select Screen Mirroring &rarr; OpenTV-Cast. Connect both devices to the same local network.</li></ol>
<p><small>This is a debug test build. Protected video is unsupported. Android will ask you to confirm installation.</small></p>
<p><small><a href="/SHA256SUMS.txt">APK checksum</a></small></p></main></html>
HTML

python3 "$project_dir/tools/serve_apk.py" --port 0 --directory "$public_dir" > "$run_dir/server.log" 2>&1 &
server_pid=$!
origin=""
for ((attempt=0; attempt<100; attempt++)); do
    if ! kill -0 "$server_pid" 2>/dev/null; then
        cat "$run_dir/server.log" >&2
        exit 1
    fi
    origin="$(sed -n 's/^OpenTV-Cast downloads: //p' "$run_dir/server.log" | head -n 1)"
    [[ -n "$origin" ]] && break
    sleep 0.1
done
if [[ -z "$origin" ]]; then
    echo "Local download server did not become ready. See $run_dir/server.log" >&2
    exit 1
fi

echo "Starting Cloudflare for the APK download page..."
echo "Anyone with the generated link can download this APK."
echo "Keep this Terminal window open. Press Ctrl+C when finished."
cloudflared tunnel --no-autoupdate --url "$origin" --protocol http2 > "$run_dir/cloudflared.log" 2>&1 &
tunnel_pid=$!
public_url=""
for ((attempt=0; attempt<120; attempt++)); do
    if ! kill -0 "$tunnel_pid" 2>/dev/null; then
        cat "$run_dir/cloudflared.log" >&2
        exit 1
    fi
    public_url="$(grep -Eo 'https://[a-z0-9-]+\.trycloudflare\.com' "$run_dir/cloudflared.log" | head -n 1 || true)"
    [[ -n "$public_url" ]] && break
    sleep 1
done
if [[ -z "$public_url" ]]; then
    echo "Cloudflare did not return a URL. See $run_dir/cloudflared.log" >&2
    exit 1
fi
echo
echo "Open this address in the TV browser:"
echo "$public_url"
echo
echo "Direct APK: $public_url/tv-bridge.apk"
echo "If the link is not ready immediately, retry in a few seconds."
echo "Logs: $run_dir"
while kill -0 "$server_pid" 2>/dev/null && kill -0 "$tunnel_pid" 2>/dev/null; do
    sleep 1
done
echo "A download process stopped unexpectedly. Check the logs above." >&2
exit 1
