"""Live browser regression + timing run; requires the ingested 640-patent sample."""
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[2]
session = f"thinkstruct-tests-{os.getpid()}"
url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4173"


def browser(*args, source=None):
    result = subprocess.run(
        ["agent-browser", "--session", session, "--json", *args],
        input=source, text=True, capture_output=True, timeout=180,
    )
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    payload = json.loads(result.stdout)
    if not payload.get("success"):
        raise RuntimeError(payload)
    return payload.get("data")


try:
    browser("open", url)
    browser("wait", "--fn", "!!document.querySelector('[data-total]')")
    results = browser("eval", "--stdin", source=(Path(__file__).parent / "exploration.browser.js").read_text())["result"]
    report = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "platform": platform.platform(), "machine": platform.machine(),
        "url": url, "results": results,
    }
    output = root / "artifacts" / "frontend-exploration.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    print(f"Saved {output}")
finally:
    browser("close")
