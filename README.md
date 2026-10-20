# Project N preview deployment

Deployment preparation and static preview artifacts for NovusPal. Application development stays in its own workspace. This repository does not build or sign native apps.

Expected Pages address after the first successful deployment: **https://aquaticmarinemammal15.github.io/project-n-preview/**. Preparation alone does not make that address live.

## What belongs here

- `scripts/` and `tests/`: staging, integrity checks, and deployment tooling.
- `.github/workflows/pages.yml`: pull request checks and a manually triggered Pages deployment from `main`.
- `site/`: an approved static web export, added at handoff time. Only this directory is uploaded to Pages.
- `docs/`: release checklist and deployment/rollback instructions.

No preview is bundled with the initial preparation change. The workflow reports that state explicitly and refuses deployment until a valid export is staged. A passing tooling check does not certify the app for release.

## Prepare a preview

Use Python 3.12 or newer; no Python packages, npm packages, tokens, or paid services are needed for these deployment tools.

```sh
python -m unittest discover -s tests -v
python scripts/stage_site.py /path/to/approved/web-export --source-version DEVELOPMENT_COMMIT_OR_APPROVED_SNAPSHOT --spa
python scripts/validate_site.py site
```

For Expo exports, read the [handoff requirements](docs/DEPLOYMENT.md). `--spa` is for a single-page export only; omit it for pre-rendered routes. Staging validates the export first, preserves the previous local site in `.deployment-backups/`, and records a source version plus SHA-256 file hashes. This records what was staged; review and approval still happen through the pull request and release checklist.

Review and commit the `site/` diff in a deployment branch, run the [release checklist](docs/RELEASE_CHECKLIST.md), and merge after review. Enable Pages with **GitHub Actions** as the source, then run **Preview deployment preparation** manually on `main`. Pushes and pull requests run checks; they do not publish the site.

Read [deployment and rollback instructions](docs/DEPLOYMENT.md) before the first release. APK, iOS signing, native builds, and app store submissions remain future work.
