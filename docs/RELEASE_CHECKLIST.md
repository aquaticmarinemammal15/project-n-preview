# Preview release checklist

Copy this checklist into the artifact handoff pull request. Record actual results, device/browser versions, source version, tester, and date. Untested items stay unchecked.

## Artifact and product review

- [ ] Development commit or approved snapshot and artifact owner identified.
- [ ] Development lint and type checks pass; test results attached.
- [ ] Only reviewed static export files in `site/`; no source maps, credentials, raw research, private directory data, or participant details.
- [ ] Sample people, numbers, and simulated sign-in are visibly identified. No real credentials are requested for the demo.
- [ ] Mock Google/SSO sign-in and any guest/role bypass are reviewed as preview behavior; no protected data is exposed.
- [ ] Sample contact actions and emergency controls cannot mislead testers into contacting fictional or unverified numbers. Do not test-call emergency services.
- [ ] University branding, attribution, images, and externally sourced map data have appropriate approval/credits.
- [ ] `python scripts/validate_site.py site` passes; release manifest identifies the intended source version.
- [ ] Tool tests pass; pull request diff and release scope reviewed.

## Browser and accessibility checks

- [ ] Test the published project prefix `/project-n-preview/`, not only a development server at `/`.
- [ ] First load and hard refresh show the app, icons, fonts, and images without missing-resource or uncaught JavaScript errors.
- [ ] Search, filters, contact details, place navigation, missing-location handling, and Back preserve intended state.
- [ ] Direct links and refresh work for home, contacts, a contact detail, places, and an unknown route; document SPA fallback HTTP 404 behavior if applicable.
- [ ] Narrow mobile portrait, landscape, desktop, zoom, and long text remain usable without clipped controls or unwanted horizontal scrolling.
- [ ] Keyboard navigation, visible focus, screen headings, accessible names, screen reader announcements, contrast, and touch targets checked.
- [ ] Current mobile Safari and Android Chrome checked, plus desktop browser; record actual devices and versions.
- [ ] External campus links open the intended sites; error and offline behavior are understandable.

## Publication and recovery

- [ ] Pages uses GitHub Actions; deployment limited to `main` and manually triggered.
- [ ] Release owner approves publication of this artifact; native app release is out of scope.
- [ ] Last good deployment commit identified, or explicitly record that this is the first release.
- [ ] Deployment job succeeds; record run URL, deployed commit, and environment URL.
- [ ] Live manifest matches the approved artifact; repeat first-load, asset, mobile, and deep-link checks at the live URL.
- [ ] Known limitations and any failed checks recorded; no unverified production-readiness claim.
