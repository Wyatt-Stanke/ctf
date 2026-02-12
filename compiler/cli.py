"""
CLI entry point for the CTF site compiler.

Usage
-----
    python -m compiler compile <source_dir> [--output dist]
    python -m compiler compile-all [--output dist]
    python -m compiler serve  <source_dir> [--port 8000]
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

# Directories at the repo root that are *not* challenge or group sources.
_IGNORE_DIRS = {
    ".git",
    ".github",
    ".mypy_cache",
    ".venv",
    "compiler",
    "dist",
    "node_modules",
    "__pycache__",
}


@dataclass
class ChallengeGroup:
    """A named group of challenges (e.g. from a ``.group.json`` directory)."""

    name: str
    description: str
    slug: str
    challenges: list[Path] = field(default_factory=list)


def _discover_groups(root: Path) -> list[ChallengeGroup]:
    """Walk *root* and return grouped challenge directories.

    A **group directory** contains a ``.group.json`` file and one or more
    challenge sub-directories (each optionally containing ``.challenge.json``).

    A **standalone challenge** at the top level (no ``.group.json`` in its
    parent) is placed into an implicit "Ungrouped" group.
    """
    groups: list[ChallengeGroup] = []
    ungrouped: list[Path] = []

    for entry in sorted(root.iterdir()):
        if not entry.is_dir() or entry.name in _IGNORE_DIRS or entry.name.startswith("."):
            continue

        group_meta_file = entry / ".group.json"
        if group_meta_file.exists():
            # This is a group directory — discover challenges inside it
            try:
                meta = json.loads(group_meta_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                meta = {}

            challenges = sorted(
                p for p in entry.iterdir()
                if p.is_dir() and not p.name.startswith(".")
            )
            if challenges:
                groups.append(ChallengeGroup(
                    name=meta.get("name", entry.name.replace("-", " ").replace("_", " ").title()),
                    description=meta.get("description", ""),
                    slug=entry.name,
                    challenges=challenges,
                ))
        elif (entry / ".challenge.json").exists():
            # Top-level standalone challenge
            ungrouped.append(entry)

    if ungrouped:
        groups.append(ChallengeGroup(
            name="Ungrouped",
            description="",
            slug="_ungrouped",
            challenges=ungrouped,
        ))

    return groups


def _all_challenges(groups: list[ChallengeGroup]) -> list[Path]:
    """Flatten groups into a single list of challenge paths."""
    return [c for g in groups for c in g.challenges]


def _cmd_compile(args: argparse.Namespace) -> None:
    from compiler.builder import compile_site

    source = Path(args.source).resolve()
    out_root = Path(args.output).resolve()
    dest = out_root / source.name

    if not source.is_dir():
        print(f"Error: source directory {source} does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Compiling {source} -> {dest}")
    compile_site(source, dest)
    print("Done.")


def _cmd_compile_all(args: argparse.Namespace) -> None:
    from compiler.builder import compile_site
    from compiler.homepage import generate_homepage

    root = Path(".").resolve()
    out_root = Path(args.output).resolve()
    groups = _discover_groups(root)
    challenges = _all_challenges(groups)

    if not challenges:
        print("No challenge directories found.", file=sys.stderr)
        sys.exit(1)

    print(
        f"Found {len(challenges)} challenge(s) in {len(groups)} group(s): "
        + ", ".join(
            f"{g.name} ({', '.join(c.name for c in g.challenges)})"
            for g in groups
        )
    )
    for source in challenges:
        # Output is always flat: dist/<challenge_name>/
        dest = out_root / source.name
        print(f"\nCompiling {source.relative_to(root)}/ -> {dest}")
        compile_site(source, dest)

    # Generate the root homepage listing all challenges, grouped
    print("\nGenerating homepage...")
    generate_homepage(groups, dest=out_root)

    print("\nAll done.")


def _cmd_serve(args: argparse.Namespace) -> None:
    from compiler.server import serve

    source = Path(args.source).resolve()

    if not source.is_dir():
        print(f"Error: source directory {source} does not exist.", file=sys.stderr)
        sys.exit(1)

    serve(source, port=args.port)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="compiler",
        description="CTF site compiler — build & serve with directive processing.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # -- compile -----------------------------------------------------------
    p_compile = sub.add_parser(
        "compile",
        help="Apply directives and output a single challenge.",
    )
    p_compile.add_argument(
        "source",
        help="Path to the challenge source directory (e.g. pipeline/).",
    )
    p_compile.add_argument(
        "-o",
        "--output",
        default="dist",
        help="Output root directory (default: dist/). Challenge is written to dist/<name>/.",
    )
    p_compile.set_defaults(func=_cmd_compile)

    # -- compile-all -------------------------------------------------------
    p_all = sub.add_parser(
        "compile-all",
        help="Discover and compile every challenge directory.",
    )
    p_all.add_argument(
        "-o",
        "--output",
        default="dist",
        help="Output root directory (default: dist/).",
    )
    p_all.set_defaults(func=_cmd_compile_all)

    # -- serve -------------------------------------------------------------
    p_serve = sub.add_parser(
        "serve",
        help="Serve a challenge with live directive processing.",
    )
    p_serve.add_argument(
        "source",
        help="Path to the challenge source directory (e.g. pipeline/).",
    )
    p_serve.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000).",
    )
    p_serve.set_defaults(func=_cmd_serve)

    # -- dispatch ----------------------------------------------------------
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
