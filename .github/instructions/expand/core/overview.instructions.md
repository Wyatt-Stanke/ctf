---
applyTo: "expand/**"
---

# Expand — Overview

`expand/` contains an Actually Portable Executable (APE) built with Cosmopolitan Libc.

The binary embeds a zip payload at build time (from the `payload/` directory) and extracts it to a user-specified output directory at runtime using Cosmopolitan's `/zip/` virtual filesystem.

## Key concepts

- **APE binary**: a single executable that runs natively on Linux, macOS, Windows, FreeBSD, OpenBSD, and NetBSD without modification.
- **Cosmopolitan `/zip/` VFS**: any files added to the binary's zip central directory via `zip` are accessible at runtime under the `/zip/` mount point.
- **cosmocc**: the Cosmopolitan C compiler toolchain, downloaded automatically by the Makefile.
