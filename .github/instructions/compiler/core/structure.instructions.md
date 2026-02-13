---
applyTo: "compiler/**"
---

# Compiler Structure

Update this file if you add, remove, rename, or move any files.

compiler/
- __init__.py
- __main__.py (python -m compiler entry point)
- cli.py (argparse CLI, group discovery, compile entry points)
- builder.py (compile logic, file copy, directive application)
- directives.py (directive detection + implementations)
- assets.py (shared CSS/JS caching and placeholders)
- homepage.py (homepage generator for compile-all)
- server.py (dev server with live directives)
- challenge.html (challenge page template)
- homepage.html (root homepage template)
- shared.css (shared styles for templates)
- shared.js (shared scripts for templates)
- requirements.txt

