# Deployment and artifact handoff

## Separation from development

The development team owns app source, design, sample data, dependencies, lint/type checks, and product changes. This repository owns staging an approved export, checking its integrity, publishing it, and restoring a previous release. Do not copy the app's source tree, research files, directory PDFs, `.env` files, dependencies, or machine-specific work notes here.

The first preparation change contains tooling only. It neither publishes a placeholder nor claims a live app exists.

## Export contract

The handoff is a directory containing `index.html` and its static assets. Supply the source commit (preferred) or a clearly identified approved snapshot label, product test results, known limitations, and release approval. `release-manifest.json` records the supplied version label; it is not a signature or proof of approval.

For the currently inspected Expo SDK 58 app, create the web export in a separate deployment/build copy. Set `expo.experiments.baseUrl` to `/project-n-preview` in that copy's app configuration. Preserve its other configuration. Run its required lint/type checks, then:

```sh
npm ci
npm run lint
npx tsc --noEmit
npx expo export --platform web
```

Deliver the generated `dist/`, without source maps. Do not publish the development server. For `web.output: "single"`, stage with `--spa`; for a static pre-rendered export, omit it and verify every route has its own HTML. GitHub Pages cannot host server rendering, server routes, authentication backends, or private secrets. Put no private keys or real participant data into client bundles.

The configured project path is significant: `/assets/...` points at the account's domain root and will fail; generated resources must use `/project-n-preview/assets/...` or valid relative paths. The validator checks HTML resource links and CSS `url()` references. It cannot prove JavaScript-generated URLs, interactive behavior, accessibility, third-party availability, or absence of all sensitive data. Browser checks and human review remain required.

`--spa` supplies `404.html` by copying the entrypoint. GitHub Pages will return an HTTP 404 for a direct visit to a client-side route while the app loads; this is a static-host fallback, not a server rewrite. Test deep-link refresh under the project prefix. Prefer pre-rendered routes when HTTP 200 for direct links is needed. Do not add a custom domain without updating and retesting the base path.

## Stage and review

From this repository root:

```sh
python scripts/stage_site.py /absolute/path/to/dist --source-version SOURCE_COMMIT --spa
python scripts/validate_site.py site
python -m unittest discover -s tests -v
```

The stager validates before replacing anything. Prior staged artifacts are retained locally in ignored `.deployment-backups/` directories. Git history is the shared rollback record. No source files are changed. Staging rejects links, hidden files, source maps, source file extensions, and several common credential formats. This is a targeted screening check, not a comprehensive secrets or privacy audit.

Review `git diff --stat` and every staged file before committing. Confirm the manifest's source version matches the intended handoff. Keep the release checklist results in the deployment pull request. Never copy credentials into a workflow: deployment uses GitHub's built-in token and OIDC.

## One-time GitHub setup

1. Merge the preparation pull request when ready. This does not publish the site.
2. In **Settings → Pages → Build and deployment**, select **GitHub Actions** as Source.
3. In **Settings → Environments → github-pages**, allow deployment from `main`. Add a required reviewer if supported and desired. The workflow itself also restricts publication to a manual run on `main`.
4. Stage an approved preview in a separate pull request and merge after checks and review.
5. In **Actions → Preview deployment preparation → Run workflow**, select `main` and run it.

The `check` job tests deployment tooling and validates a staged site if present. For manual runs on `main`, `artifact` requires a valid site and uploads only `site/`. `deploy` publishes that artifact to the `github-pages` environment. Pull requests receive no Pages write or OIDC permissions. There is no automatic deployment on merge.

## Verify a deployment

Wait for the workflow's deployment job to succeed. Use its environment URL; do not infer success from the repository existing or the checks job passing. Follow the release checklist, including the root page, built assets, route refresh, mobile navigation, and external links. Read `/project-n-preview/release-manifest.json` and match `source_version` and file hashes to the reviewed artifact. Record the workflow run and deployed commit in the release pull request.

## Roll back

1. Identify the last good deployment's commit and workflow run.
2. Revert the artifact-changing commit through a pull request; keep subsequent valid deployment tooling. Review the restored manifest and file set, then merge to `main`.
3. Run the deployment workflow manually on `main` and verify the environment URL and manifest again.

Avoid force-pushing or rewriting app development history. If the failure is sensitive-data exposure, remove public access using the repository's Pages settings while addressing it; restoring an older deployment does not remove data from public Git history or caches.

## References checked for this preparation

- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Expo SDK 58 baseUrl configuration](https://docs.expo.dev/versions/v58.0.0/config/app/#baseurl)
- [Expo web export and GitHub Pages hosting](https://docs.expo.dev/guides/publishing-websites/#github-pages)
