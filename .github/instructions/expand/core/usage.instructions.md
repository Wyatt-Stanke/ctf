---
applyTo: "expand/**"
---

# Expand — Build & Usage

## Building

```bash
cd expand/
just build        # downloads cosmocc, compiles expand.c, embeds payload/
```

The justfile:
1. Downloads cosmocc (Cosmopolitan C compiler) to `.cosmocc/` if not present.
2. Compiles `expand.c` to `expand.com` using `cosmocc`.
3. Runs `cd payload && zip -qr ../expand.com .` to append payload files into the APE binary's zip directory.

## Running

```bash
./expand.com [OUTPUT_DIR]
```

- Walks the `/zip/` virtual filesystem exposed by Cosmopolitan Libc.
- Recreates the directory tree and copies all files to `OUTPUT_DIR` (defaults to `.`).

## Customising the payload

Replace or add files under `payload/` before building. Every file and subdirectory in `payload/` becomes part of the binary.

## Configuration

Variables are set at the top of the justfile:

| Variable | Default | Purpose |
|----------|---------|--------|
| `cosmocc_version` | `4.0.2` | cosmocc release to download |
| `payload_dir` | `payload` | Directory to embed |
| `cflags` | `-Os -Wall -Wextra -Wpedantic` | Compiler flags |
