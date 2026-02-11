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
import sys
from pathlib import Path

# Directories at the repo root that are *not* challenge sources.
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


def _discover_challenges(root: Path) -> list[Path]:
    """Return sorted list of challenge source directories under *root*."""
    return sorted(
        p
        for p in root.iterdir()
        if p.is_dir() and p.name not in _IGNORE_DIRS and not p.name.startswith(".")
    )


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

    root = Path(".").resolve()
    out_root = Path(args.output).resolve()
    challenges = _discover_challenges(root)

    if not challenges:
        print("No challenge directories found.", file=sys.stderr)
        sys.exit(1)

    print(
        f"Found {len(challenges)} challenge(s): {', '.join(p.name for p in challenges)}"
    )
    for source in challenges:
        dest = out_root / source.name
        print(f"\nCompiling {source.name}/ -> {dest}")
        compile_site(source, dest)

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
