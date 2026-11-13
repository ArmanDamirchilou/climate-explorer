"""Package the clean tracked source and frozen demonstration for review."""

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from build_demo import build
from climate import CODE_SHA256, ROOT


def git(*arguments):
    return subprocess.check_output(["git", "-C", str(ROOT), *arguments])


def package(output):
    if git("status", "--porcelain").strip():
        raise ValueError("Commit the reviewed changes before creating the handoff archive.")
    output = output.resolve()
    if output.suffix != ".zip" or not output.is_relative_to(ROOT / "release-build"):
        raise ValueError("Choose a .zip path inside the ignored release-build directory.")
    if output.exists():
        raise ValueError("Choose a new archive filename so an earlier handoff is preserved.")
    build(ROOT / "dist")
    files = {}
    for encoded in git("ls-files", "-z").split(b"\0"):
        if not encoded:
            continue
        relative = encoded.decode()
        path = ROOT / relative
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f"Unsupported tracked source path: {relative}")
        files[f"source/{relative}"] = path.read_bytes()
    for path in sorted((ROOT / "dist").rglob("*")):
        if path.is_file() and not path.name.startswith("."):
            files[f"demo/{path.relative_to(ROOT / 'dist')}"] = path.read_bytes()
    files["START_HERE.md"] = b"""# Climate Explorer 1.0.0 review package

Read source/submission/FARHAD_HANDOFF.md first. The video and seven-slide PDF are in demo/.

To open the frozen application without installing scientific packages, run Python from this extracted folder:

    python3 -m http.server 8767 --bind 127.0.0.1 --directory demo

Then open http://127.0.0.1:8767/ in your browser. Keep the terminal open. The demo uses local frozen NASA responses and requires no NASA account or network access after download. Selecting an external source or repository link still needs the internet. Opening index.html directly may block data loading, so use the local server.

For the full Python application, tests and replay, follow source/README.md using Python 3.14 and the locked dependencies. Source development began 11 November 2026. AI assistance and unresolved competition eligibility are documented. No competition entry has been submitted. User feedback and student contributions must be real and separately recorded.

RELEASE_MANIFEST.json records the source commit and every included file's SHA-256. It detects changes relative to this manifest; it is not a digital signature or proof of scientific validity.
"""
    record = {"release": "1.0.0", "created_utc": datetime.now(timezone.utc).isoformat(),
              "source_commit": git("rev-parse", "HEAD").decode().strip(), "code_sha256": CODE_SHA256,
              "files": {name: hashlib.sha256(body).hexdigest() for name, body in sorted(files.items())}}
    files["RELEASE_MANIFEST.json"] = (json.dumps(record, indent=2)+"\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
            for name, body in sorted(files.items()):
                archive.writestr(name, body)
        with ZipFile(output) as archive:
            if archive.testzip() is not None:
                raise ValueError("Archive integrity check failed.")
            manifest = json.loads(archive.read("RELEASE_MANIFEST.json"))
            if set(archive.namelist()) != set(manifest["files"]) | {"RELEASE_MANIFEST.json"}:
                raise ValueError("Archive file coverage differs from its manifest.")
            for name, digest in manifest["files"].items():
                if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                    raise ValueError(f"Archive checksum differs: {name}")
    except Exception:
        output.unlink(missing_ok=True)
        raise
    return {"artifact": output.name, "bytes": output.stat().st_size,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "source_commit": record["source_commit"], "code_sha256": CODE_SHA256,
            "files_verified": len(record["files"])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "release-build/climate-explorer-1.0.0-handoff.zip")
    args = parser.parse_args()
    result = package(args.output)
    args.output.with_suffix(".verification.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
