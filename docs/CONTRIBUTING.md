# Contributing to JLPTSuccess

Thanks for considering a contribution. This project is a static, no-
account, privacy-respecting JLPT N5 prep app deployed as a PWA. The
canonical strategic positioning is in `N5/prompts/N5Improvement.txt`
- audit-driven, niche-fit-aware. Read that first if you're proposing
a feature.

## Quick links

| What you want to do | Where to look |
|---|---|
| **Help translate UI / content** into Hindi (the only non-EN locale post-2026-05-06; see CHANGELOG v1.12.40) | [`N5/docs/TRANSLATING.md`](N5/docs/TRANSLATING.md) |
| **Self-host or fork** for an institution / school | [`N5/docs/SELF-HOST.md`](N5/docs/SELF-HOST.md) |
| **Recommend native audio recordings** | [`N5/docs/NATIVE-AUDIO-WORKFLOW.md`](N5/docs/NATIVE-AUDIO-WORKFLOW.md) |
| **File a bug** | [GitHub issue templates](https://github.com/gauravaccentureproducts/JLPTSuccess/issues/new/choose) |
| **Read the spec** | [`N5/specifications/JLPT-N5-Current-Implementation-Spec.md`](N5/specifications/JLPT-N5-Current-Implementation-Spec.md) |
| **Read the audit history** | [`N5/feedback/n5-audit-2026-05-04.xlsx`](N5/feedback/n5-audit-2026-05-04.xlsx) |

## Code of Conduct

This project follows the [Contributor Covenant 2.1](CODE_OF_CONDUCT.md).
Be respectful. Don't be a jerk. Reports go to the email in the CoC.

## License

By contributing you agree that:

- **Code contributions** are licensed under the MIT License (`LICENSE`
  at repo root).
- **Content contributions** (grammar entries, vocab, translations,
  reading/listening passages) are licensed under CC BY-SA 4.0
  (`N5/CONTENT-LICENSE.md`).

If you're unsure which bucket your contribution falls into, ask in the
PR. Most pure-data work is content; most JS/CSS/Python work is code.

## How to contribute

### Reporting a bug

1. Check [open issues](https://github.com/gauravaccentureproducts/JLPTSuccess/issues)
   for duplicates.
2. Open a new issue using the **bug report** template.
3. Include steps to reproduce + your browser/OS + a screenshot if
   visual.

### Proposing a feature

1. Check the audit tracker (`N5/feedback/n5-audit-2026-05-04.xlsx`)
   to see if it's already considered. Many features were
   intentionally excluded - see Section 7 of `N5/prompts/N5Improvement.txt`
   ("Anti-Items") for the canonical "do not build this" list.
2. Open a feature-request issue. If your feature aligns with a niche
   already on the roadmap (N1 multilingual / N2 privacy / N3 self-
   host / N4 all-in-one), say so explicitly - it accelerates review.

### Submitting a code change

1. Fork the repo + create a topic branch.
2. Make your change. Match existing code style - vanilla JS/CSS/Python,
   no framework dependencies. Keep PRs focused on one logical change.
3. **Run the integrity gate before pushing:**
   ```bash
   python N5/tools/check_content_integrity.py
   node N5/tests/footer-regex.test.js
   ```
   Both must pass.
4. **Run the full build before pushing if your change touches
   `data/`, `css/`, or `sw.js`:**
   ```bash
   cd N5/
   npm run build       # version.json + min CSS + cache version bump
   ```
5. Open a PR using the **pull request** template.

### Submitting a content correction

If you spot a grammar / kanji / vocab / reading / listening error,
either:

- Open a content-correction issue (template available), OR
- File a PR directly editing the relevant `N5/data/*.json` file.

The 44 release-blocker invariants in `tools/check_content_integrity.py`
will catch the most common authoring mistakes; if your PR fails an
invariant, that's the bot telling you the schema needs adjusting too.

### Submitting a translation

See [`N5/docs/TRANSLATING.md`](N5/docs/TRANSLATING.md) for the full
workflow. TL;DR:

1. The supported locales are **EN and HI** (Hindi). The 2026-05-06
   transition narrowed the app from a 5-locale shell (en/vi/id/ne/zh)
   to en+hi after market research found Hindi is the unique
   high-demand-low-competition gap (top-5 JLPT country, ~50K
   applicants/year, no dedicated Hindi-medium prep app).
2. Edit `N5/locales/hi.json` to upgrade machine-translated strings
   tagged `_meta.review_status: "llm_curated"` to native-quality.
3. PR titled `i18n(hi): native review of NN/<total> keys`.

## Development

```bash
# Local dev server
cd N5/
python -m http.server 8000
# Open http://localhost:8000/

# Run tests
node tests/footer-regex.test.js          # unit
npm run test:smoke                       # Playwright smoke (needs npm i first)
python tools/check_content_integrity.py  # release gate

# Regenerate build artefacts
npm run build                            # all of: version + min CSS + sw cache bump
```

## Anti-features (we will close PRs that add these)

Per the canonical anti-items list in `prompts/N5Improvement.txt` §7:

- **No accounts.** No login, no cloud sync, no leaderboards. Breaks
  niche N2.
- **No telemetry / analytics.** No page-view tracking, no error
  reporting to a third party. Breaks niche N2.
- **No third-party scripts.** CSP is same-origin. Breaks niche N2.
- **No ads.** Breaks niche N2.
- **No paid tier or donate-to-unlock.** Breaks niche N2 + N3.
- **No gamification (streaks/XP/push notifications).** Adult learners
  disengage from Duolingo-style nags.
- **No JS framework rewrite.** Vanilla baseline is part of the self-
  host story. Adding React/Vue/Svelte breaks niche N3.

If you're not sure whether your feature falls into one of these, ask
in an issue before writing code.

## Questions

Open a discussion or an issue. We'd rather answer questions than
review a PR that doesn't fit the project's scope.

- JLPTSuccess maintainers
