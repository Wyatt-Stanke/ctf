"""
CLI entry point for the CTF site compiler.

Usage
-----
    python -m compiler compile <source_dir> [--output dist]
    python -m compiler serve  <source_dir> [--port 8000]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _cmd_compile(args: argparse.Namespace) -> None:
    from compiler.builder import compile_site

    source = Path(args.source).resolve()
    output = Path(args.output).resolve()

    if not source.is_dir():
        print(f"Error: source directory {source} does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Compiling {source} -> {output}")
    compile_site(source, output)
    print("Done.")


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
        help="Apply directives and output a static site.",
    )
    p_compile.add_argument(
        "source",
        help="Path to the challenge source directory (e.g. pipeline/).",
    )
    p_compile.add_argument(
        "-o",
        "--output",
        default="dist",
        help="Output directory (default: dist/).",
    )
    p_compile.set_defaults(func=_cmd_compile)

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
