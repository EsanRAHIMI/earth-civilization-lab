# Maintainer checklist for public GitHub research software

This file documents **administrative settings requiring repository-owner authority**. Creating this checklist does not itself change GitHub settings.

## Repository About

GitHub repository page → About gear / Edit repository details:

- **Description:** `Open Earth-system observatory and reproducible research benchmarks for climate, water and food — physically grounded, evidence-first.`
- **Website:** `https://esanrahimi.github.io/earth-civilization-lab/`
- **Topics:** `earth-system-science`, `climate-science`, `hydrology`, `crop-yield`, `geospatial`, `research-software`, `open-science`, `reproducibility`, `python`, `digital-twin`.
- Enable **Issues** and **Discussions** if desired; discussion prompts should invite replication, scientific critique and newcomer questions. Topics must not be misrepresented as demonstrated operational capability.

## Main-branch protections

GitHub Settings → Rules → Rulesets (or Branches → Branch protection):
- Restrict force pushes and deletion of `main`.
- Require Pull Requests and at least one approving review from a maintainer/reviewer.
- Require the passing **offline** checks `Python source, governance and offline science contract (3.11)`, `Python source, governance and offline science contract (3.12)`, and `Dashboard syntax and source safety` (choose exact names as they appear in the GitHub Checks UI).
- Require resolution of conversations and prevent bypass where supported.
- Do **not** make provider-download, scheduled data retrieval or GRACE credential workflows required for ordinary contributions; those are network- and credential-dependent.
- Review CODEOWNERS file and ensure at least one available owner can approve reviews.

## Security and external data access

- Enable repository Secret Scanning and private vulnerability reporting where supported.
- Set minimum required GitHub Actions permissions; do not allow untrusted PR code into workflows holding provider credentials.
- NASA Earthdata auth requires `EARTHDATA_TOKEN` configured under Settings → Secrets and variables → Actions for protected GRACE runs; protect this secret, never publish it in an issue or source file.
- Verify repository Pages environment restrictions and every data-source redistribution right.
- Keep dependency updates/release publication under reviewer control.

## Scholarly identity and sustainable citation

- Consider a public Zenodo integration after checking source-data licences; tag a reproducible version, then publish an immutable release.
- Populate the real archived release DOI in `CITATION.cff` and `codemeta.json`; **never publish an unassigned DOI**.
- Avoid representing GitHub stars, forks or workflow success as independent scientific review. Publish reproducibility, data lineage and negative results.

## What is still manual

Changing About/Topics/Discussions, configuring branch rules and project-wide security options require administrative GitHub permissions. These settings are not changed by adding files to the repository.
