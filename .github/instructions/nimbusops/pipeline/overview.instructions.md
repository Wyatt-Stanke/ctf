---
applyTo: "nimbusops/pipeline/**"
---

# Pipeline Challenge Overview

Read pipeline.instructions.md first before using this file.

## Concept

"Pipeline" is a medium-difficulty CTF challenge themed around CI/CD security.
The player has access to NimbusOps' internal intranet and must find a container
registry deploy key by exploiting a flaw in the GitHub Actions pipeline.

## Narrative

NimbusOps is a fictional cloud infrastructure company. During a real outage in
November 2025, DevOps lead Marina Santiago built a status page and deployed it
via GitHub Actions on their self-hosted GitHub Enterprise Server instance.

The deploy pipeline authenticates to a private Harbor-based container registry
using a static deploy key stored as a GitHub Actions secret. The company is
confident their secrets are safe because GitHub Actions automatically masks
secrets in log output.

The flaw: GitHub Actions only masks exact string matches. The pipeline writes
base64(flag{DEPLOY_KEY}) to an auth file. When a deploy fails, a debug step
(Step 7, if: failure()) dumps that file's contents. The base64-encoded value is
not masked because masking only replaces the literal secret string, not
transformed versions of it.

## Characters

- Marina Santiago (msantiago) - DevOps Lead, owns secrets
- James Park (jpark) - Senior Backend, trusts masking
- Alex Kovacs (akovacs) - Junior Dev, raised secret safety concerns
- Jess Kim (jkim) - Platform Eng
- Dev Patel (dpatel) - Backend
- Taylor Lin (tlin) - Security

## Design Philosophy

- Discoverable breadcrumbs: status page -> robots.txt / HTML comments -> GHES ->
  wiki / actions -> dispatch -> failure -> base64 debug dump.
- Realistic simulation: GHES, status, registry, and logs look like real tools.
- No source reading required: CI runner is bundled and obfuscated.
- Progressive hints: three hints on the challenge page.

## Flag

flag{l0g_m4sk1ng_1s_n0t_s3cur1ty}
SHA-256: f026394fb297674616ec30dc91ab3bc095981a1eccbefcd81d4eede1bdc02c1e
