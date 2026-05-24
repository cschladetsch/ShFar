#!/usr/bin/env python3

from __future__ import annotations

import difflib
import json
import os
import shlex
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


HOST = os.environ.get("FAR_PLAYGROUND_HOST", "127.0.0.1")
PORT = int(os.environ.get("FAR_PLAYGROUND_PORT", "8765"))
SCRIPT_DIR = Path(__file__).resolve().parent
PLAYGROUND_PATH = SCRIPT_DIR / "playground.html"
FAR_PATH = SCRIPT_DIR / "far"
DEMO_ROOT = SCRIPT_DIR / "demo"
MAX_SAMPLED_DIFFS = 5
MAX_DIFF_LINES = 80


PRESETS = [
    {
        "id": "rename-class",
        "label": "Rename a class",
        "description": "Turn OldClass into NewClass across C++ sources.",
        "glob": "*.cpp",
        "find": "OldClass",
        "replace": "NewClass",
        "dry_run": False,
        "backup": False,
    },
    {
        "id": "banner-comments",
        "label": "Normalize banner comments",
        "description": "Collapse // -- Text ----- into // Text.",
        "glob": "*.{cpp,hpp,h}",
        "find": "// -- (.*) -+$",
        "replace": "// \\1",
        "dry_run": False,
        "backup": False,
    },
    {
        "id": "fix-typo",
        "label": "Fix a typo",
        "description": "Change recieve to receive in Markdown and shell files.",
        "glob": "*.{md,sh}",
        "find": "recieve",
        "replace": "receive",
        "dry_run": False,
        "backup": False,
    },
    {
        "id": "cmake-target",
        "label": "Rename a CMake target",
        "description": "Rename mylib_static to mylib.",
        "glob": "CMakeLists.txt",
        "find": "mylib_static",
        "replace": "mylib",
        "dry_run": False,
        "backup": False,
    },
]


@dataclass
class PreviewRequest:
    root: Path
    glob: str
    find: str
    replace: str
    dry_run: bool
    auto_yes: bool
    backup: bool


def shell_quote(arg: str) -> str:
    return shlex.quote(arg)


def build_command(req: PreviewRequest) -> str:
    args = ["far"]
    if req.dry_run:
        args.append("-n")
    if req.auto_yes:
        args.append("-y")
    if req.backup:
        args.append("-b")
    args.extend([str(req.root), req.glob, req.find, req.replace])
    return " ".join(shell_quote(arg) for arg in args)


def parse_request(payload: dict[str, Any]) -> PreviewRequest:
    root_value = str(payload.get("root", "")).strip()
    glob = str(payload.get("glob", "")).strip() or "*"
    find = str(payload.get("find", ""))
    replace = str(payload.get("replace", ""))
    dry_run = bool(payload.get("dry_run", False))
    auto_yes = bool(payload.get("auto_yes", False))
    backup = bool(payload.get("backup", False))

    if not root_value:
        raise ValueError("Root is required.")
    root = Path(root_value).expanduser().resolve()
    if not root.exists():
        raise ValueError(f"Root does not exist: {root}")
    if not root.is_dir():
        raise ValueError(f"Root is not a directory: {root}")
    if not find:
        raise ValueError("Find pattern is required.")

    return PreviewRequest(
        root=root,
        glob=glob,
        find=find,
        replace=replace,
        dry_run=dry_run,
        auto_yes=auto_yes,
        backup=backup,
    )


def run_far(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(FAR_PATH), *args],
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )


def parse_far_listing(stdout: str) -> list[str]:
    files: list[str] = []
    for line in stdout.splitlines():
        if line.startswith("  "):
            files.append(line.strip())
    return files


def match_files(req: PreviewRequest) -> tuple[list[Path], list[str]]:
    result = run_far(["-n", str(req.root), req.glob, req.find], SCRIPT_DIR)
    stderr_messages = [line for line in result.stderr.splitlines() if line.strip()]
    if result.returncode == 0:
        files = [Path(path).resolve() for path in parse_far_listing(result.stdout)]
        return files, stderr_messages
    if result.returncode == 2:
        return [], stderr_messages
    message = result.stderr.strip() or result.stdout.strip() or "Preview failed."
    raise RuntimeError(message)


def copy_matched_files(root: Path, files: list[Path], temp_root: Path) -> None:
    for source in files:
        relative = source.relative_to(root)
        target = temp_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def apply_preview_replacement(req: PreviewRequest, matched_files: list[Path], temp_root: Path) -> None:
    if not matched_files:
        return
    result = run_far(["-y", str(temp_root), req.glob, req.find, req.replace], SCRIPT_DIR)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Preview replacement failed."
        raise RuntimeError(message)


def unified_diff(original: str, updated: str, path_label: str) -> str:
    lines = list(
        difflib.unified_diff(
            original.splitlines(),
            updated.splitlines(),
            fromfile=f"{path_label} (before)",
            tofile=f"{path_label} (after)",
            lineterm="",
        )
    )
    if len(lines) > MAX_DIFF_LINES:
        head = lines[:MAX_DIFF_LINES]
        head.append(f"... diff truncated after {MAX_DIFF_LINES} lines ...")
        lines = head
    return "\n".join(lines)


def preview_changes(req: PreviewRequest) -> dict[str, Any]:
    matched_files, warnings = match_files(req)
    relative_matches = [str(path.relative_to(req.root)) for path in matched_files]
    if not matched_files:
        return {
            "command": build_command(req),
            "root": str(req.root),
            "matched_files": [],
            "changed_files": [],
            "sample_diffs": [],
            "truncated": False,
            "warnings": warnings,
            "error": None,
        }

    changed_files: list[str] = []
    sampled_diffs: list[dict[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="far-playground-") as temp_dir:
        temp_root = Path(temp_dir)
        copy_matched_files(req.root, matched_files, temp_root)
        apply_preview_replacement(req, matched_files, temp_root)

        for source in matched_files:
            relative = source.relative_to(req.root)
            candidate = temp_root / relative
            before_text = source.read_text(encoding="utf-8")
            after_text = candidate.read_text(encoding="utf-8")
            if before_text == after_text:
                continue
            path_label = str(relative)
            changed_files.append(path_label)
            if len(sampled_diffs) < MAX_SAMPLED_DIFFS:
                sampled_diffs.append(
                    {
                        "path": path_label,
                        "diff": unified_diff(before_text, after_text, path_label),
                    }
                )

    return {
        "command": build_command(req),
        "root": str(req.root),
        "matched_files": relative_matches,
        "changed_files": changed_files,
        "sample_diffs": sampled_diffs,
        "truncated": len(changed_files) > len(sampled_diffs),
        "warnings": warnings,
        "error": None,
    }


class PlaygroundHandler(BaseHTTPRequestHandler):
    server_version = "FarPlayground/1.0"

    def do_GET(self) -> None:
        if self.path in {"/", "/playground.html"}:
            self._serve_html()
            return
        if self.path == "/api/config":
            self._send_json(
                {
                    "demo_root": str(DEMO_ROOT),
                    "presets": PRESETS,
                    "max_sample_diffs": MAX_SAMPLED_DIFFS,
                }
            )
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        if self.path != "/api/preview":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length)
            payload = json.loads(raw.decode("utf-8"))
            req = parse_request(payload)
            response = preview_changes(req)
            self._send_json(response)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except RuntimeError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:  # pragma: no cover
            self._send_json({"error": f"Unexpected server error: {exc}"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _serve_html(self) -> None:
        content = PLAYGROUND_PATH.read_text(encoding="utf-8")
        body = content.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), PlaygroundHandler)
    print(f"far playground: http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
