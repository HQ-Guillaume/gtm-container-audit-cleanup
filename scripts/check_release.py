#!/usr/bin/env python3
"""Run dependency-free release checks for the GTM audit cleanup skill."""

from __future__ import annotations

import argparse
import py_compile
import re
import subprocess
import sys
from pathlib import Path


MAX_SKILL_LINES = 500
LONG_REFERENCE_LINES = 100
BLOCKLIST_FILE = "scripts/release_blocklist.txt"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def text_files(root: Path) -> list[Path]:
    paths = [root / "SKILL.md", root / "README.md", root / "agents" / "openai.yaml"]
    paths.extend(sorted((root / "references").glob("*.md")))
    paths.extend(sorted((root / "scripts").glob("*.py")))
    return [path for path in paths if path.exists()]


def parse_frontmatter(skill_path: Path) -> tuple[dict[str, str], list[str]]:
    text = skill_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, ["SKILL.md frontmatter is missing"]
    try:
        _, raw, _ = text.split("---", 2)
    except ValueError:
        return {}, ["SKILL.md frontmatter is not closed"]

    values: dict[str, str] = {}
    errors = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"Invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')

    keys = list(values)
    if keys != ["name", "description"]:
        errors.append(f"Frontmatter keys must be name, description; found {keys}")
    if values.get("name") != "gtm-container-audit-cleanup":
        errors.append("Skill name must be gtm-container-audit-cleanup")
    if not values.get("description"):
        errors.append("Skill description is empty")
    return values, errors


def referenced_resources(root: Path) -> tuple[set[str], list[str]]:
    refs: set[str] = set()
    missing: list[str] = []
    pattern = re.compile(r"`((?:references|scripts)/[^`]+?)`", re.S)
    for path in text_files(root):
        content = path.read_text(encoding="utf-8")
        for match in pattern.finditer(content):
            raw = " ".join(match.group(1).split())
            rel = raw.split()[0].strip().rstrip(".,;:)")
            if "*" in rel:
                continue
            refs.add(rel)
            if not (root / rel).exists():
                missing.append(f"{path.relative_to(root)} references missing {rel}")
    return refs, missing


def imported_scripts(root: Path) -> set[str]:
    imports: set[str] = set()
    pattern = re.compile(r"^\s*(?:from|import)\s+([A-Za-z_][A-Za-z0-9_]*)")
    for path in sorted((root / "scripts").glob("*.py")):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = pattern.match(line)
            if not match:
                continue
            candidate = root / "scripts" / f"{match.group(1)}.py"
            if candidate.exists():
                imports.add(candidate.relative_to(root).as_posix())
    return imports


def release_blocklist(root: Path) -> list[str]:
    path = root / BLOCKLIST_FILE
    if not path.exists():
        return []
    patterns = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if value and not value.startswith("#"):
            patterns.append(value)
    return patterns


def check_orphan_resources(root: Path, referenced: set[str]) -> list[str]:
    errors = []
    imported = imported_scripts(root)
    exempt = {
        "scripts/check_release.py",
        "scripts/gtm_self_test.py",
    }
    routed = referenced | imported | exempt

    for folder, suffix in (("references", "*.md"), ("scripts", "*.py")):
        for path in sorted((root / folder).glob(suffix)):
            rel = path.relative_to(root).as_posix()
            if rel not in routed:
                errors.append(f"{rel} is not referenced, imported, or explicitly exempted")
    return errors


def git_ls_files(root: Path) -> set[str]:
    try:
        output = subprocess.check_output(["git", "ls-files"], cwd=root, text=True)
    except Exception:
        return set()
    return set(output.splitlines())


def check_reference_navigation(root: Path) -> list[str]:
    errors = []
    for path in sorted((root / "references").glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > LONG_REFERENCE_LINES and "## Contents" not in lines[:25]:
            errors.append(
                f"{path.relative_to(root)} has {len(lines)} lines and no ## Contents"
            )
    return errors


def check_patterns(root: Path, name: str, patterns: list[str]) -> list[str]:
    errors = []
    compiled = [(pattern, re.compile(pattern, re.I)) for pattern in patterns]
    for path in text_files(root):
        if path.relative_to(root).as_posix() == BLOCKLIST_FILE:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for label, pattern in compiled:
                if pattern.search(line):
                    errors.append(f"{name}: {path.relative_to(root)}:{lineno}: {label}")
    return errors


def check_py_compile(root: Path) -> list[str]:
    errors = []
    for path in sorted((root / "scripts").glob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(f"py_compile failed for {path.relative_to(root)}: {exc.msg}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--allow-untracked",
        action="store_true",
        help="Do not fail when referenced resources are not tracked by git.",
    )
    args = parser.parse_args()

    root = repo_root()
    errors: list[str] = []

    _, frontmatter_errors = parse_frontmatter(root / "SKILL.md")
    errors.extend(frontmatter_errors)

    skill_lines = (root / "SKILL.md").read_text(encoding="utf-8").splitlines()
    if len(skill_lines) > MAX_SKILL_LINES:
        errors.append(f"SKILL.md has {len(skill_lines)} lines; max is {MAX_SKILL_LINES}")

    refs, missing_refs = referenced_resources(root)
    errors.extend(missing_refs)
    errors.extend(check_orphan_resources(root, refs))

    tracked = git_ls_files(root)
    if tracked and not args.allow_untracked:
        untracked_refs = sorted(ref for ref in refs if ref not in tracked)
        if untracked_refs:
            errors.append("Referenced resources are untracked: " + ", ".join(untracked_refs))

    errors.extend(check_reference_navigation(root))
    errors.extend(check_patterns(root, "blocklist", release_blocklist(root)))
    errors.extend(check_py_compile(root))

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Release check: FAIL ({len(errors)} error(s))")
        return 1

    print(
        "Release check: PASS "
        f"({len(refs)} referenced resources, SKILL.md {len(skill_lines)} lines)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
