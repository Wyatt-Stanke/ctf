---
applyTo: "nimbusops/pipeline/**"
---

# Pipeline Challenge Structure

Read pipeline.instructions.md first before using this file.
Update this file if you add, remove, rename, or move any files.

## Directory Layout

nimbusops/pipeline/
- .challenge.json
- .env.example
- index.html (intranet portal)
- favicon.ico
- Dockerfile
- nginx.conf
- challenge/index.html (COMPILER: challenge_page)
- .github/index.html (directory listing placeholder)
- .github/workflows/{build-test.yml,deploy-prod.yml,stale-cleanup.yml,index.html}
- status.nimbusops.internal/
  - index.html
  - status.json
  - robots.txt
  - css/{index.html,style.css}
  - js/{index.html,status.js}
- ghes.nimbusops.internal/
  - ghes.css
  - index.html, repo.html, actions.html, dispatch.html
  - commits.html, issues.html, issue-55.html, pulls.html
  - wiki.html, wiki-architecture.html, wiki-runbook.html
  - wiki-secrets.html, wiki-postmortem-nov.html
  - js/{index.html,_ci-runner-src.js,ci-runner.js}
- logs.nimbusops.internal/
  - index.html
  - latest.json
- registry.nimbusops.internal/
  - registry.css
  - index.html
  - repo-status-dash.html

## Challenge-Critical Files

- status.nimbusops.internal/index.html (HTML comment breadcrumbs)
- status.nimbusops.internal/robots.txt (logs breadcrumb)
- logs.nimbusops.internal/latest.json (workflow paths, failed run)
- ghes.nimbusops.internal/dispatch.html (exploit trigger)
- ghes.nimbusops.internal/js/_ci-runner-src.js (vulnerability)
- ghes.nimbusops.internal/js/ci-runner.js (bundled runner)
- ghes.nimbusops.internal/wiki-secrets.html (deploy key docs)
- ghes.nimbusops.internal/wiki-architecture.html (registry auth flow)
- ghes.nimbusops.internal/actions.html (workflow history)
- challenge/index.html (briefing + hints)

## Compiler Directives

- <!-- COMPILER: challenge_page --> (challenge/index.html)
- <!-- COMPILER: directory_listing --> (various index.html stubs)
- <!-- COMPILER: no_include --> (_ci-runner-src.js)
- <!-- COMPILER: base64_bundle ... --> (ci-runner.js)
- .challenge.json is excluded as metadata
