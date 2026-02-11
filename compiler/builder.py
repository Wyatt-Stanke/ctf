"""
Static site builder — ``compile`` subcommand.

Walks the source directory, copies every file into ``dist/``, and applies
compiler directives where found.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from compiler.directives import apply_directive, detect_directive


def compile_site(source: Path, dest: Path) -> None:
    """Build the static site from *source* into *dest*.

    *dest* is wiped clean before every build so the output is always a
    faithful snapshot of the source with directives applied.
    """
    source = source.resolve()
    dest = dest.resolve()

    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)

    for src_file in sorted(source.rglob("*")):
        rel = src_file.relative_to(source)
        dst_file = dest / rel

        if src_file.is_dir():
            dst_file.mkdir(parents=True, exist_ok=True)
            continue

        dst_file.parent.mkdir(parents=True, exist_ok=True)

        directive = detect_directive(src_file)
        if directive == "no_include":
            print(f"  skip   {rel}")
            continue

        if directive is None:
            # No directive — straight copy (preserves binary files too)
            shutil.copy2(src_file, dst_file)
            print(f"  copy  {rel}")
        else:
            # Compute the URL prefix for directory listings
            url_prefix = "/" + rel.parent.as_posix()
            if not url_prefix.endswith("/"):
                url_prefix += "/"

            transformed = apply_directive(src_file, directive, url_prefix)
            dst_file.write_text(transformed, encoding="utf-8")
            print(f"  {directive:20s} {rel}")
