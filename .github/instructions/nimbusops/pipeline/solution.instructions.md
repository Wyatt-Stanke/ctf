---
applyTo: "nimbusops/pipeline/**"
---

# Pipeline Challenge Solution (Spoilers)

Read pipeline.instructions.md first before using this file.

## Flag

flag{l0g_m4sk1ng_1s_n0t_s3cur1ty}
Base64: ZmxhZ3tsMGdfbTRzazFuZ18xc19uMHRfczNjdXIxdHl9

## Vulnerability

GitHub Actions masks secrets by exact string replacement only. Transformed
values (like base64) are not masked. The pipeline writes btoa(FLAG) to
/tmp/.registry-auth before attempting registry auth. When auth fails, Step 7
(debug dump, if: failure()) prints the auth file unmasked.

## Intended Solution Path

1. Start at status.nimbusops.internal/.
2. Check robots.txt -> reveals logs.nimbusops.internal/.
3. View page source -> HTML comments reveal GHES repo path.
4. Visit logs.nimbusops.internal/ -> latest.json shows workflow files and run
   history (includes failure #116).
5. Visit ghes.nimbusops.internal/ -> repo -> Actions -> dispatch page.
6. Read wiki (secrets + architecture) to understand registry auth flow.
7. Use dispatch.html with hidden query params:
   - environment
   - registry_override (not shown in UI)
   - skip_preflight (not shown in UI)
8. Craft a URL that passes Step 1 validation (contains "nimbusops"), skips
   preflight, and fails DNS in Step 4:

   dispatch.html?environment=production&registry_override=nimbusops.example.com&skip_preflight=true

9. Step 4 writes the auth file, then fails auth. Step 7 dumps the base64 value.
10. Base64-decode to get the flag.

## Constraints

- registry_override must contain "nimbusops" (Step 1 validation).
- registry_override must NOT end with .nimbusops.internal (so canResolve() fails).
- skip_preflight must be true to reach Step 4.

## Anti-Solutions

- Normal deploys succeed, so Step 7 never runs.
- Only reading logs directory reveals run metadata, not full output.
- Reading ci-runner.js is possible but called out as cheating.
- Registry override without skip_preflight fails before Step 4.
