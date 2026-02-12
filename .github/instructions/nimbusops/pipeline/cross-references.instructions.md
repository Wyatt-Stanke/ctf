---
applyTo: "nimbusops/pipeline/**"
---

# Pipeline Challenge Cross-References

Read pipeline.instructions.md first before using this file.
Update this file when changing any href, src, fetch(), or path reference.

## Asset References

- index.html -> favicon.ico
- status.nimbusops.internal/index.html -> css/style.css, ../favicon.ico, js/status.js
- status.nimbusops.internal/js/status.js -> fetch("status.json")
- ghes.nimbusops.internal/*.html -> ghes.css, ../favicon.ico, lucide CDN
- ghes.nimbusops.internal/dispatch.html -> js/ci-runner.js
- registry.nimbusops.internal/index.html -> registry.css, ../favicon.ico
- registry.nimbusops.internal/repo-status-dash.html -> registry.css, ../favicon.ico

## Navigation Links

- Portal index.html -> status.nimbusops.internal/, ghes.nimbusops.internal/, logs.nimbusops.internal/, registry.nimbusops.internal/
- challenge/index.html -> ../status.nimbusops.internal/
- status page HTML comments -> ../logs.nimbusops.internal/, ghes.nimbusops.internal/NimbusOps/status-dash
- GHES pages link to siblings in ghes.nimbusops.internal/
- Registry pages link within registry.nimbusops.internal/

## Breadcrumbs (solution-critical)

- status.nimbusops.internal/robots.txt disallows /logs.nimbusops.internal/
- logs.nimbusops.internal/latest.json -> workflow paths + failed run
- ghes.nimbusops.internal/actions.html -> dispatch.html
- wiki-secrets + wiki-architecture describe registry auth flow

## Config References

- Dockerfile ARG REGISTRY=registry.nimbusops.internal
- Dockerfile healthcheck -> /status.nimbusops.internal/status.json
- nginx.conf server_name *.nimbusops.internal
- nginx.conf status.json location -> /status.nimbusops.internal/status.json
- deploy-prod.yml comments mention ghes.nimbusops.internal

## CI Runner Internals

- DEFAULT_REGISTRY = registry.nimbusops.internal
- canResolve() checks endsWith(".nimbusops.internal")
- registry_override validation requires substring "nimbusops"
- Image path: {registry}/nimbusops/status-dash:{sha}
