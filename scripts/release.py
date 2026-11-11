#!/usr/bin/env python3
"""Check or build the explicit public package; never run task executors."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import zipfile

PUBLIC_FILES = (
    "README.md", "README.zh-CN.md", "LICENSE", "VERSION", ".gitignore",
    "CONTRIBUTING.md", "CHANGELOG.md", "research/sources.json",
)
PUBLIC_DIRS = ("skills", "docs", "evals", "scripts", "tests", "workflow_runtime", ".github")
TEXT_SUFFIXES = {".md", ".json", ".py", ".yaml", ".yml", ".txt"}
RULES = (
    ("email-address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("personal-absolute-path", re.compile(
        r"/(?:home|Users)/[A-Za-z0-9_.-]+(?:/|\b)|"
        r"[A-Za-z]:[\\/](?:Users|Documents and Settings)[\\/][^\s\"']+")),
    ("private-key", re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----")),
    ("credential-token", re.compile(
        r"\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,})\b")),
)


def within(path, root):
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def public_files(root):
    """An allowlist, not .gitignore, determines release membership."""
    root = Path(root).resolve()
    result = []
    for name in PUBLIC_FILES:
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Missing or unsafe public file: " + name)
        result.append(path)
    for name in PUBLIC_DIRS:
        directory = root / name
        if directory.is_symlink():
            raise ValueError("Symlink public directory: " + name)
        if not directory.exists():
            continue
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise ValueError("Symlink in public tree: " + path.relative_to(root).as_posix())
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path.is_file():
                result.append(path)
    return sorted(set(result))


def check(root, private_terms=()):
    root = Path(root).resolve()
    paths = public_files(root)
    members = {path.relative_to(root).as_posix() for path in paths}
    errors = []
    contents = {path.relative_to(root).as_posix(): path.read_bytes() for path in paths}
    for path in paths:
        rel = path.relative_to(root).as_posix()
        if any(pattern.search(rel) for _, pattern in RULES) or any(
            term.casefold() in rel.casefold() for term in private_terms
        ):
            errors.append("Public member name contains a private pattern; name withheld")
            continue
        if path.name.startswith(".env") or path.name in {"credentials.json", "id_rsa"}:
            errors.append(rel + ": forbidden credential file")
        if path.suffix not in TEXT_SUFFIXES and rel not in PUBLIC_FILES:
            errors.append(rel + ": unsupported public file type")
        raw = contents[rel]
        if len(raw) > 1024 * 1024:
            errors.append(rel + ": file exceeds 1 MiB review bound")
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(rel + ": not UTF-8 text")
            continue
        for rule, pattern in RULES:
            match = pattern.search(text)
            if match:
                line = text.count("\n", 0, match.start()) + 1
                errors.append("{}:{}: {}".format(rel, line, rule))
        for index, term in enumerate(private_terms):
            if term.casefold() in text.casefold():
                # Do not echo the private term into logs or public reports.
                errors.append(rel + ": custom-private-term-" + str(index + 1))
        if path.suffix == ".json":
            try:
                json.loads(text)
            except ValueError:
                errors.append(rel + ": invalid JSON")
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                target_path = (path.parent / target.split("#")[0]).resolve()
                if not within(target_path, root) or target_path.relative_to(root).as_posix() not in members:
                    errors.append(rel + ": link outside public package or missing target")
    return contents, errors


def build(root, output, private_terms=()):
    root = Path(root).resolve()
    output = Path(output).resolve()
    if within(output, root):
        raise ValueError("Write release archives outside the source directory")
    contents, errors = check(root, private_terms)
    if errors:
        raise ValueError("Release checks failed:\n" + "\n".join(errors))
    # Package exactly the byte snapshot that passed inspection.
    manifest = {
        "version": contents["VERSION"].decode().strip(),
        "files": {rel: hashlib.sha256(raw).hexdigest() for rel, raw in sorted(contents.items())},
    }
    contents["RELEASE-MANIFEST.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix="workflow-release-", suffix=".zip", dir=output.parent)
    try:
        os.close(handle)
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
            for rel, raw in sorted(contents.items()):
                info = zipfile.ZipInfo("agent-workflow-kit/" + rel, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, raw)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--private-terms", type=Path, help="Local file: one private literal per line; never bundled")
    parser.add_argument("--output", type=Path, help="Build a ZIP outside the source tree after checks")
    args = parser.parse_args()
    terms = []
    if args.private_terms:
        if within(args.private_terms.resolve(), args.root.resolve()):
            parser.error("Keep the private-terms file outside the public source directory")
        terms = [line.strip() for line in args.private_terms.read_text(encoding="utf-8").splitlines() if line.strip()]
    if args.output:
        manifest = build(args.root, args.output, terms)
        print(json.dumps({"version": manifest["version"], "files": len(manifest["files"]), "built": True}))
    else:
        paths, errors = check(args.root, terms)
        print(json.dumps({"files": len(paths), "errors": errors}, indent=2))
        return int(bool(errors))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
