---
applyTo: "compiler/**"
---

# Compiler Cross-References

Update this file when changing template placeholders or directive names.

## Template Placeholders

- challenge.html uses {{TITLE}}, {{DIFFICULTY}}, {{DIFF_COLOR}}, {{SLUG}},
  {{FLAG_HASH}}, {{BODY}}, {{SHARED_CSS}}, {{SHARED_JS}}
- homepage.html uses {{GROUPS}}, {{HASHES}}, {{COUNT}}, {{GROUP_MAP}},
  {{SHARED_CSS}}, {{SHARED_JS}}

## Directive Mappings

- directives.KNOWN_DIRECTIVES must include any new directive name.
- builder.compile_site and server._CompilerHandler both call detect_directive
  and apply_directive; keep their logic in sync.

