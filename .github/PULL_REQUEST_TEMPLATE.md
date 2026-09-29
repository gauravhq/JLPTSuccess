<!-- Thanks for contributing to JLPTSuccess. Filling this template out makes review faster. -->

## What this PR does

<!-- One-paragraph summary. What changed, why, and what user-visible behavior is affected. -->

## Type of change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] Content correction (grammar example, vocab entry, kanji reading, question, rationale)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Localization / translation update (vi / id / ne / zh)
- [ ] Documentation only
- [ ] Refactor / internal cleanup (no functional change)
- [ ] Build / tooling / CI
- [ ] Breaking change (requires a coordinated rollout - see "Breaking change" section below)

## Linked issue(s)

<!-- e.g. "Closes #42", "Refs #17", "Part of IMP-057". -->

## Scope of files touched

<!-- Quick sanity check - which level subdir does this touch? -->

- [ ] Top-level (JLPTSuccess root: index.html, css, manifest, etc.)
- [ ] N5
- [ ] N4 - ⚠️ **WORK-BLOCKED**, requires explicit unblock from the maintainer (see [.claude/CLAUDE.md](../.claude/CLAUDE.md))
- [ ] N3 / N2 / N1 (placeholder updates only)
- [ ] Cross-repo / shared assets

## Verification

<!-- How was this tested? -->

- [ ] `python tools/check_content_integrity.py` runs clean (for content / data changes)
- [ ] Playwright P0 smoke suite passes (`npx playwright test`)
- [ ] Manually verified on the live preview / local server
- [ ] Tested in dark mode + light mode (for UI changes)
- [ ] Tested at mobile (≤768px) + desktop (for UI changes)
- [ ] Tested with screen reader / keyboard-only nav (for accessibility changes)

## Screenshots / before-after (for UI changes)

<!-- Drag-drop into this textarea. -->

## Locale impact

<!-- Did you add/change strings? -->

- [ ] No new user-visible strings
- [ ] Added new English strings → corresponding keys updated in `locales/{vi,id,ne,zh}.json` (or marked `// TODO: translate`)
- [ ] Locale-only update (translation refresh)

## Breaking change details

<!-- Only fill in if "Breaking change" was ticked above. -->

- **What breaks:**
- **Migration path for existing users / progress data:**
- **Cache version bump required?** Yes / No (and the new value)

## Privacy posture review

<!-- The app has a hard "no remote calls / no telemetry / no third-party scripts" contract. -->

- [ ] No new external network requests at runtime
- [ ] No new third-party scripts / fonts / images
- [ ] No localStorage keys added outside the `jlpt-n5-tutor:*` namespace (or whichever level)
- [ ] No new permissions requested in the manifest

## Self-review checklist

- [ ] Read the [Code of Conduct](../docs/CODE_OF_CONDUCT.md) and agree
- [ ] Followed existing code conventions in this repo (vanilla ES modules, no frameworks; CSS variables for theming)
- [ ] Comments added for non-obvious logic (the "why", not the "what")
- [ ] No commented-out code blocks left in the diff
- [ ] No `console.log` debug output left behind
- [ ] CHANGELOG.md updated if user-visible behavior changed
- [ ] CACHE_VERSION in `sw.js` bumped if shell files changed
- [ ] `?v=` query string on script/stylesheet bumped in `index.html` if those files changed
