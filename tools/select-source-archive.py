#!/usr/bin/env python3
"""Select a versioned Prics Play source archive deterministically for CI.

If one or more `Prics-Play-X.Y.Z-Android.zip` archives exist in the repository root,
each is validated against its internal package.json version and expected top-level
folder. The highest valid semantic version is extracted. If no matching archive is
present, the checked-out repository root is used. No archive is selected by mtime or
filesystem order.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path, PurePosixPath

WORKSPACE = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
RUNNER_TEMP = Path(os.environ.get("RUNNER_TEMP", WORKSPACE / ".runner-temp")).resolve()
VERSIONED_ARCHIVE = re.compile(r"^Prics-Play-(\d+)\.(\d+)\.(\d+)-Android\.zip$")


def fail(message: str) -> "NoReturn":
    print(f"::error::{message}", file=sys.stderr)
    raise SystemExit(1)


def validate_archive(archive: Path, version: str) -> tuple[tuple[int, int, int], str]:
    expected_root = f"prics-play-{version}"
    expected_package = f"{expected_root}/package.json"
    with zipfile.ZipFile(archive) as zf:
        names = zf.namelist()
        for name in names:
            path = PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts:
                fail(f"Unsafe path in source archive {archive.name}: {name}")
        if expected_package not in names:
            fail(f"{archive.name} must contain {expected_package}")
        try:
            package = json.loads(zf.read(expected_package).decode("utf-8"))
        except Exception as exc:
            fail(f"Cannot read package.json in {archive.name}: {exc}")
        if str(package.get("version", "")) != version:
            fail(f"{archive.name} filename version {version} does not match package.json version {package.get('version')}")
        if f"{expected_root}/implementation.md" not in names:
            fail(f"{archive.name} is missing {expected_root}/implementation.md")
    return tuple(int(part) for part in version.split(".")), expected_root


def main() -> None:
    matches = []
    invalid = []
    for archive in WORKSPACE.glob("Prics-Play-*-Android.zip"):
        match = VERSIONED_ARCHIVE.fullmatch(archive.name)
        if not match:
            continue
        version = ".".join(match.groups())
        try:
            version_key, expected_root = validate_archive(archive, version)
            matches.append((version_key, archive, expected_root))
        except SystemExit:
            raise
        except Exception as exc:
            invalid.append((archive.name, str(exc)))

    if invalid:
        fail("Invalid versioned source archive(s): " + "; ".join(f"{name}: {error}" for name, error in invalid))

    root_version_key = None
    root_version = ""
    root_package = WORKSPACE / "package.json"
    if root_package.is_file():
        try:
            root_version = str(json.loads(root_package.read_text(encoding="utf-8")).get("version", ""))
            if re.fullmatch(r"\\d+\\.\\d+\\.\\d+", root_version):
                root_version_key = tuple(int(part) for part in root_version.split("."))
        except Exception:
            root_version_key = None

    latest_archive = max(matches, key=lambda item: item[0]) if matches else None
    # If the checked-out source itself is newer than every archived ZIP, use the checkout.
    # On an equal version, prefer the validated archive because it is the explicit release input.
    if latest_archive is None or (root_version_key is not None and root_version_key > latest_archive[0]):
        source_dir = WORKSPACE
        if latest_archive is None:
            print("No versioned Prics Play source ZIP found; using checked-out repository source.")
        else:
            print(f"Repository source {root_version} is newer than archived ZIP {latest_archive[2]}; using checkout.")
    else:
        _, archive, expected_root = latest_archive
        extract_parent = RUNNER_TEMP / "prics-play-source"
        if extract_parent.exists():
            shutil.rmtree(extract_parent)
        extract_parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(extract_parent)
        source_dir = (extract_parent / expected_root).resolve()
        if not source_dir.is_dir():
            fail(f"Expected extracted source folder is missing: {source_dir}")
        print(f"Selected validated source archive: {archive.name}")

    env_file = os.environ.get("GITHUB_ENV")
    if env_file:
        with open(env_file, "a", encoding="utf-8") as handle:
            handle.write(f"PRICS_SOURCE_DIR={source_dir}\n")
    else:
        print(f"PRICS_SOURCE_DIR={source_dir}")


if __name__ == "__main__":
    main()
