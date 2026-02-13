---
applyTo: "expand/**"
---

# Expand — Structure

Update this file if you add, remove, rename, or move any files.

expand/
- expand.c (C source — walks /zip/ and extracts every entry to disk)
- justfile (downloads cosmocc, compiles, embeds payload via zip)
- payload/ (directory whose contents are embedded in the binary at build time)
  - README.txt (sample payload file)
- .gitignore (ignores build artefacts and .cosmocc/)
- README.md (project documentation)
