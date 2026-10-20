# Preparation status — October 19, 2026

Target: `aquaticmarinemammal15/project-n-preview`, default branch `main`, GitHub Pages project path `/project-n-preview/`.

The repository initially contained only its README and license. This preparation change adds deployment tooling and documentation. No app source, research documents, or app artifact is included. No Pages settings have been changed and no publication has been triggered.

## Verified locally

| Check | Result |
| --- | --- |
| Deployment tooling tests | 14 passed on Windows with Python 3.12 |
| Workflow YAML | Parsed successfully; manual deployment trigger and build/deploy dependency checked |
| Whitespace check | `git diff --check` passed |
| Current local Expo SDK 58 snapshot | Copied separately; original development files preserved |
| TypeScript baseline | `npx tsc --noEmit` passed |
| Web export baseline | Export completed with `/project-n-preview` base path in the build copy |
| Real artifact dry run | Staging and validation passed: 57 payload files, 2,834,350 total bytes including the manifest; retained outside this repository |
| Application lint baseline | Failed: 40 unresolved `@/…` import errors; reproduced with normal filesystem access |

The dry run proves the tooling accepts the current static export structure. It does not establish product approval or public-release readiness. Initial exploratory exports are not release artifacts. The final dry run used a fresh output directory without source maps.

## Before the first preview release

1. The development owner resolves the lint baseline and supplies an approved export with its source version and test results. Keep these fixes in development.
2. Review simulated sign-in, guest/role selection, fictional contact actions, and sample emergency controls before sharing the app. The current prototype opens phone/email links for sample data. No live dialing or email action was tested.
3. Complete browser, mobile, deep-link, accessibility, and privacy/content review using the release checklist. Those checks are currently unperformed.
4. Stage the approved artifact in a separate deployment pull request. Revalidate its manifest and review the actual generated files.
5. Enable GitHub Actions as the Pages publishing source, then manually deploy from `main` after review. Verify the successful deployment run, live site, and release manifest.

GitHub-hosted CI and Pages deployment are separate verification steps. Local test results do not imply either has run. Native Android/iOS packaging and store submission remain out of scope for this Pages preparation.
