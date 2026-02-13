# expand

An **Actually Portable Executable** (APE) built with [Cosmopolitan Libc](https://justine.lol/cosmopolitan/) that ships a zip payload inside the binary and extracts it at runtime.

## How it works

1. The program is compiled with `cosmocc`, producing an APE `.com` binary.
2. At build time, the contents of the `payload/` directory are added to the binary using `zip` — APE binaries are simultaneously valid zip archives.
3. At runtime, Cosmopolitan's `/zip/` virtual filesystem exposes the embedded files. The program recursively walks `/zip/` and writes every file and directory to the specified output path.

## Quick start

```bash
# Put whatever you want to embed in payload/
cp -r ~/my-files/* payload/

# Build (downloads cosmocc automatically on first run)
just build

# Run — extracts to ./out/
./expand.com out
```

## Recipes

| Recipe | Description |
|--------|-------------|
| `just` / `just build` | Build `expand.com` with contents of `payload/` |
| `just toolchain` | Download cosmocc without building |
| `just clean` | Remove build artefacts and toolchain |

## Requirements

- `curl` or `wget` — to download the cosmocc toolchain
- `unzip` — to extract the toolchain archive
- `zip` — to embed the payload into the binary
- [just](https://github.com/casey/just) command runner

## Usage

```
./expand.com [OUTPUT_DIR]
```

- `OUTPUT_DIR` defaults to `.` (current directory) if omitted.
- Directories are created automatically.
- Output shows each extracted entry prefixed with `d` (directory) or `f` (file).

## File structure

```
expand/
├── expand.c          # C source — walks /zip/ and extracts to disk
├── justfile           # Build recipes (downloads cosmocc, compiles, embeds payload)
├── payload/           # Directory whose contents get embedded in the binary
│   └── README.txt     # Sample payload file
├── .gitignore
└── README.md
```
