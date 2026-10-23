# Security Policy

## Scope

This repository contains public observation dashboards, Python research pipelines, GitHub workflows, data-source connectors and scripts that may authenticate to upstream scientific data providers.

**Do not post vulnerabilities, secrets or private tokens in public issues.** For security-sensitive reports, use GitHub's **Report a vulnerability** / private vulnerability reporting feature if enabled; otherwise contact the repository maintainer privately through their GitHub profile. Do not assume an unaudited security mailbox or private reporting feature exists.

Provide affected commit or workflow, a minimal reproduction, impact and suggested remediation. Avoid uploading access tokens, private datasets, or exploiting deployed systems without authorization.

## Safeguards expected of contributions

- Never include `EARTHDATA_TOKEN`, API keys, service credentials, cookies or `.netrc` in source, test fixtures, logs, Issues, or Pages assets.
- GitHub Actions must use minimum necessary permissions. Untrusted PR code must not access write tokens or scientific provider secrets.
- Pin dependency versions in independent research environments. Review third-party Actions and commit-sha pin them for sensitive jobs when feasible.
- Treat external GeoJSON/CSV/NetCDF/ZIP content as untrusted; cap downloads, check MIME/schema, validate dimensions and stop on corrupt or anomalous source data.
- Do not serve protected raw NASA Earthdata files through public Pages or artifacts unless explicitly permitted by the provider terms.
- The scientific release gate must remain fail-closed.

This is research software with **no guaranteed security support SLA** and no guarantee of suitability for safety-critical decisions.
