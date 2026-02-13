---
applyTo: "compiler/**"
---

# Compiler Authoring Rules

## Read Order (always)

1. compiler.instructions.md (this file)
2. overview.instructions.md
3. structure.instructions.md
4. usage.instructions.md

## Before Any Edit

- Scan usage.instructions.md to confirm CLI expectations.
- Keep directive syntax on the very first line of files.
- Verify any new compiler metadata uses dotfiles (e.g. .challenge.json).

## After Any Edit

- Update structure.instructions.md for file moves/additions/removals.
- Update usage.instructions.md if CLI flags or directive behavior changes.

## Invariants (do not break)

- Hidden markdown (.*.md) never ships in build output or dev server.
- .challenge.json and .group.json are excluded from build output.
- Directive comments must be the first line of the file.
- The dev server must not serve no_include or hidden markdown files.

