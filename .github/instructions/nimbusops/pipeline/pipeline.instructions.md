---
applyTo: "nimbusops/pipeline/**"
---

# Pipeline Challenge Authoring Rules

## Read Order (always)

1. pipeline.instructions.md (this file)
2. overview.instructions.md
3. structure.instructions.md
4. solution.instructions.md
5. cross-references.instructions.md

## Before Any Edit

- Read all *.instructions.md files in .github/instructions/nimbusops/pipeline.
- Understand the solution path and invariants.
- Check cross-references.instructions.md for dependencies.

## After Any Edit

- Update structure.instructions.md for file moves/additions/removals.
- Update cross-references.instructions.md for any link/path changes.
- Update solution.instructions.md if the solution path or flag changes.
- Update overview.instructions.md if the narrative changes.

## Invariants (never break)

- Flag: flag{l0g_m4sk1ng_1s_n0t_s3cur1ty}
- SHA-256 in .challenge.json must match the flag.
- CI runner masks literal secrets only, not base64.
- Step 7 debug dump is required to leak the base64 auth file.
- _ci-runner-src.js stays excluded via COMPILER: no_include.
- ci-runner.js stays base64-bundled.
- Intranet hostnames follow *.nimbusops.internal.

## Style Guidelines

- Dark theme, GitHub-like palette.
- favicon.ico lives at pipeline root; subdirectories use ../favicon.ico.
- GHES pages use ghes.css, status uses css/style.css, registry uses registry.css.
