---
applyTo: "compiler/**"
---

# Compiler Overview

The compiler builds and serves static challenge sites by copying files and
applying inline directives. It is used for both one-off builds and a full
site compile that generates a homepage listing all challenges.

## Key Capabilities

- Compile a single challenge directory into dist/<challenge>/.
- Compile all challenges and generate a grouped homepage.
- Serve a challenge locally with live directive processing.

## Core Concepts

- Challenges live at the repo root and include .challenge.json metadata.
- Groups are directories containing .group.json and one or more challenges.
- Directives are detected from the first line of a file and applied during
  compile or serve.

