---
applyTo: "compiler/**"
---

# Compiler Usage

## CLI Commands

- python -m compiler compile <source_dir> [--output dist]
- python -m compiler compile-all [--output dist]
- python -m compiler serve <source_dir> [--port 8000]

## Output Behavior

- compile: writes to dist/<challenge>/ and clears any existing output first.
- compile-all: outputs every challenge to dist/<challenge>/ and writes
  dist/index.html for the homepage.

## Directives (first line only)

- <!-- COMPILER: directory_listing -->
- <!-- COMPILER: html_minify -->
- <!-- COMPILER: challenge_page -->
- // COMPILER: json_minify
- // COMPILER: no_include
- // COMPILER: base64_bundle <file>

## Directive Notes

- directory_listing generates an nginx-style index page for that directory.
- html_minify removes comments and collapses whitespace (preserves pre/script/style).
- json_minify parses and re-serializes JSON with compact separators.
- no_include excludes the file from build output and dev server.
- base64_bundle appends eval(atob("...")) for the referenced file.
- challenge_page wraps content with the shared template and reads .challenge.json.

