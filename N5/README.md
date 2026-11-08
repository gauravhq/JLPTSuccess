# JLPT N5 Tutor

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](../LICENSE)
[![Content: CC BY-SA 4.0](https://img.shields.io/badge/Content-CC%20BY--SA%204.0-lightgrey.svg)](CONTENT-LICENSE.md)
[![JLPT Level: N5](https://img.shields.io/badge/JLPT-N5-14452a.svg)](https://gauravaccentureproducts.github.io/JLPTSuccess/N5/)
[![PWA](https://img.shields.io/badge/PWA-installable-brightgreen.svg)](https://gauravaccentureproducts.github.io/JLPTSuccess/N5/)
[![Locales: EN · HI](https://img.shields.io/badge/locales-EN%20%C2%B7%20HI-blueviolet.svg)](docs/TRANSLATING.md)
[![Privacy: no telemetry](https://img.shields.io/badge/privacy-no%20telemetry-success.svg)](PRIVACY.md)

> **No login · No tracking · Works offline · Open source · 100% on-device · Free, no ads, no paywall.**

Browser-based static web app for studying JLPT N5: grammar, vocabulary, kanji, reading, and listening. **No server. No accounts. No third-party scripts.** Author-side build tools (Python) live under `/tools/`; the learner runs only the browser.

## Documentation

ISSUE-047 (audit round-5): the docs live in this directory. Quick map:

| Doc | Purpose |
|---|---|
| [`specifications/JLPT-N5-Current-Implementation-Spec.md`](specifications/JLPT-N5-Current-Implementation-Spec.md) | The authoritative living spec: what the app actually does today (**v1.12.50**). |
| [`CHANGELOG.md`](CHANGELOG.md) | User-visible release notes (currently at **v1.12.50**, post round-9). |
| [`AUDIO.md`](AUDIO.md) | Audio pipeline (multi-provider auto-fallback: VOICEVOX → edge-tts → gtts). |
| [`docs/SELF-HOST.md`](docs/SELF-HOST.md) / [`docs/SELF-HOST.hi.md`](docs/SELF-HOST.hi.md) | Fork → brand → deploy guide for institutional / school adopters (niche N3). |
| [`docs/TRANSLATING.md`](docs/TRANSLATING.md) | Translator-contributor on-ramp for Hindi (niche N1; corpus-wide Hindi review **complete** at LLM-persona-Q33 quality bar: see CHANGELOG v1.12.40-50). |
| [`docs/NATIVE-AUDIO-WORKFLOW.md`](docs/NATIVE-AUDIO-WORKFLOW.md) | How to swap synthesized audio for native-speaker recordings. |
| [`docs/UNIFIED-REVIEW-QUEUE-DESIGN.md`](docs/UNIFIED-REVIEW-QUEUE-DESIGN.md) | Cross-skill FSRS-4.5 review queue design (round-9 IMP-092). |
| [`prompts/N5Improvement.txt`](prompts/N5Improvement.txt) | Audit-only prompt that drives every audit round. Canonical strategic positioning + anti-items list. |
| [`feedback/n5-audit-2026-05-04.xlsx`](feedback/n5-audit-2026-05-04.xlsx) | Cumulative audit tracker (rounds 1-9). **219 Done / 3 Avoid / 0 Open / 0 Open Questions.** |
| [`feedback/audit-round9-2026-05-06.md`](feedback/audit-round9-2026-05-06.md) | Round-9 audit report (Sections 0-7, 27 findings registered). Historical snapshot. |
| [`PRIVACY.md`](PRIVACY.md) | Privacy contract: no telemetry, no third-party scripts, no PII. |
| [`CONTENT-LICENSE.md`](CONTENT-LICENSE.md) | CC BY-SA 4.0 for the educational content corpus. |
| [`NOTICES.md`](NOTICES.md) | Third-party content attributions (KanjiVG, Inter, Noto Sans JP, **VOICEVOX speakers**). |
| [`../LICENSE`](../LICENSE) | MIT for the source code. |
| [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | Contribution workflow + anti-features list. |

## Storage (privacy)

All learner state lives in browser **localStorage** under the namespace
`jlpt-n5-tutor:*` (e.g. `jlpt-n5-tutor:settings`, `jlpt-n5-tutor:history`).
No cookies, no IndexedDB, no third-party scripts, no remote API calls.
The only writable storage is the user's own browser. To audit, open
DevTools → Application → Storage → Local Storage. The CI invariant
**JA-37** enforces that `js/storage.js` and `PRIVACY.md` agree on the
namespace; doc-vs-code drift fails the release gate.

## Run locally

Open `index.html` in a modern browser (Chrome, Edge, Firefox).

> Some browsers block `file://` JSON fetches. If pages stay blank, serve over HTTP:
> ```
> python -m http.server 8000
> ```
> Then open http://localhost:8000.

## Deploy to GitHub Pages

1. Commit and push this folder (or its parent repo) to GitHub.
2. **Settings → Pages → Source** = `main` branch, root folder (or `/docs` if you nest the app under that).
3. After the first build (~30 seconds), visit `https://<your-user>.github.io/<repo>/N5/` (or wherever the app lives in your repo). The canonical deploy of this repo is at `https://gauravaccentureproducts.github.io/JLPTSuccess/N5/`.
4. Verify the four chapters load: Learn, Test, Drill, Summary. Take a quick test, miss something, and confirm the Drill badge updates and Chapter 3 / 4 reflect it.

The app uses **only relative paths** and **hash routing** (`#/learn`, `#/test`, …), so it works without any path-rewriting on GitHub Pages - no `404.html` fallback, no `gh-pages` action, nothing else needed.

A **service worker** (`sw.js`) is included and pre-caches the app shell + all data files. After your first online visit, the app continues to work offline. Bump `CACHE_VERSION` in `sw.js` when shipping a release so old caches get evicted.

## File map

```
/index.html                            entry point
/sw.js                                 service worker (offline cache)
/manifest.webmanifest                  PWA manifest
/css/main.css                          styling
/js/                                   app logic (one module per surface / mode)
  app.js storage.js furigana.js i18n.js shortcuts.js search.js pwa.js levels.js
  learn.js test.js papers.js review.js summary.js drill.js diagnostic.js
  reading.js listening.js kanji.js kanji-popover.js home.js feedback.js changelog.js
  kosoado.js wa-vs-ga.js verb-class.js te-form.js particle-pairs.js counters.js
  content-protect.js settings.js normalize.js
/data/                                 JSON consumed by the app
  grammar.json questions.json
  vocab.json kanji.json reading.json listening.json
  n5_kanji_whitelist.json n5_vocab_whitelist.json n5_kanji_readings.json
  dokkai_kanji_exception.json audio_manifest.json
  papers/manifest.json                   live counts: 29 papers, 426 questions
                                         (4 per-section + chokai virtual aggregator)
                                         + combined_sections + full_mock_papers
  papers/{moji,goi,bunpou,dokkai}/paper-{1..7}.json
                                         per-section layout: 6 full papers of 15 questions
                                         + 1 short paper of 10 questions = 100 Q (102 for dokkai).
                                         The short paper is intentional - it captures the residual
                                         items after the section's primary 6 papers are filled to
                                         15 each. Do not "rebalance" by redistributing.
  audio_manifest.json                    711 grammar/reading audio (gtts)
  audio_manifest_voice.json              47 listening audio (VOICEVOX multi-voice)
/audio/                                MP3 files (grammar examples, reading, listening)
/svg/kanji/                            stroke-order SVGs (one per N5 kanji)
/locales/                              UI translations: en, hi (closed set per JA-39)
/fonts/                                self-hosted woff2 (Inter, Noto Sans JP)
/tests/                                Playwright specs (p0-smoke, visual-regression with 76 baselines)
/tools/                                Python scripts run by the content author only
  check_content_integrity.py           release-blocker content-integrity invariants (script reports the live count)
  check_design_system.py               8 D-rules (Muji-flat spec compliance)
  lint_content.py
  build_audio.py
  build_listening_audio_multivoice_2026_05_07.py    multi-provider listening render
  fix_*.py                             versioned fixers (one per release)
/docs/N5-syllabus-methodology.md       N5 scope + source citations + authoring conventions
verification.md                        cross-source audit of N5 content
TASKS.md                               task list (mirrors session TodoWrite)
specifications/JLPT-N5-Current-Implementation-Spec.md   canonical functional + implementation spec (single source of truth)
```

## Content authoring workflow

1. Edit rich content directly in the JSON files (single source of truth):
   - `data/grammar.json` (178 patterns)
   - `data/vocab.json` (995 entries, post-BUG-018/019/024 dedup 2026-05-16/17)
   - `data/kanji.json` (106 entries)
   - `data/reading.json` / `data/listening.json` / `data/questions.json`
   - `data/papers/{moji,goi,bunpou,dokkai}/*.json` (paper questions)
2. Edit scope whitelists in `data/n5_*_whitelist.json` if adding to N5 scope.
3. Edit `docs/N5-syllabus-methodology.md` if changing methodology, source citations, or authoring conventions.
5. Lint for out-of-scope kanji + vocab tokens:
   ```
   python tools/lint_content.py
   ```
6. Run integrity + design checks (release blockers):
   ```
   python tools/check_content_integrity.py     # prints "PASS: all NN invariants green"
   python tools/check_design_system.py         # 8 D-rules
   ```
7. (Optional) Re-render listening audio with multi-voice VOICEVOX:
   ```
   # Prereq: VOICEVOX engine on :50021 + ffmpeg in PATH
   python tools/build_listening_audio_multivoice_2026_05_07.py
   ```
The learner never runs any of these scripts - they are author-side only.

## Authoring conventions

### Vocabulary whitelist exemptions

The `data/n5_vocab_whitelist.json` lookup is the source of truth for "what counts as N5 vocabulary." Two classes of items are intentionally excluded from the whitelist:

1. **Personal names** (e.g., マリア, ヤマダ, スズキ, たなか, アンナ) - universally exempted from textbook vocabulary lists. Names appear in passages and questions but never in the whitelist; CI does not flag this. If you add a new passage with a new personal name, do NOT add the name to the whitelist.
2. **Place names with no compound logic** (e.g., スペイン, アメリカ, メキシコ) - country names already in the whitelist are fine. Compound forms like スペイン人 / アメリカ人 are tracked since they're useful learner vocabulary. Don't bulk-add every conceivable place name.

Where to add: append the new term to `data/n5_vocab_whitelist.json` (sorted alphabetically) and run `python tools/check_content_integrity.py` to confirm the JA-13 / JA-15 / JA-16 invariants still pass.

### Spacing policy in passages

Insert a single space at every word boundary in `ja` text - particles, kanji compounds, demonstrative + noun, etc. The corpus is consistently spaced; new content must match.

- ✓ `わたしは とうきょうの 大学で 日本語を べんきょうしています。`
- ✗ `わたしは とうきょうの大学で 日本語を べんきょうしています。` (missing space before 大学)

Exceptions: spaces are NOT inserted within a single compound (e.g., `日本語` stays as one token; do not split as `日本 語`).

### N4 grammar leakage

N5 passages must use only N5 grammar markers. The two patterns most likely to slip through are:

- **〜と conditional** (`Verb-dict + と + comma + result-clause`) - this is N4 (Genki II L18, Minna I L23). Use te-form imperative or split into two sentences instead.
- **Potential form** (`Verb-stem + える/られる`) - this is N4 (Genki II L13). Use `Verb-dict + ことが できる` instead.

The `JA-21` content-integrity invariant catches both heuristically. Passages that intentionally include borderline late-N5 grammar should set `tier: "late_n5"` to opt out of the strict check.

### Kanji reading display convention

`data/n5_kanji_readings.json` stores both `on` and `kun` readings as **hiragana** (e.g., 高 → on `["こう"]`, kun `["たか"]`). This is a deliberate choice - the traditional pedagogical convention is on-yomi in katakana / kun in hiragana, but uniform-hiragana is simpler to render, easier to compare for invariant checks (JA-22 dedup, JA-24 i-adj-primary-kun), and the on/kun distinction is already conveyed via the labelled fields. UI surfaces that want the typographic split can apply it at render time. Closes OPEN-4 from `feedback/MASTER-TASK-LIST.md`.

### Counter-numeral display convention

The corpus standardises on **arabic numeral + counter** with the counter as kanji when it is in the N5 whitelist (e.g., `7時`, `5本`, `3人`, `100円`) and as kana when it is not (e.g., `1かい`, `8ふん`, `1ぱい` since 階 / 分 / 杯 are out-of-scope). Survey of the corpus 2026-05-01: 194 occurrences arabic+N5-kanji, 43 arabic+kana, 34 kanji+kanji (legacy), 29 kanji+kana (legacy). The arabic-first style dominates and is the going-forward convention. The remaining ~30 kanji+kanji occurrences (e.g., `二人`) appear inside passage prose where the kanji-form is natural reading-text style and don't need normalisation. Closes OPEN-5 from `feedback/MASTER-TASK-LIST.md`.

### Furigana mode

The app exposes a binary on/off furigana toggle (Settings panel). The `feedback/jlpt-n5-tutor-ux-developer-brief2.md` §4.1 originally called for a 3-mode toggle (always / known-only-hide / never), but Pass-13 native-teacher review concluded that auto-furigana produces wrong context-dependent readings (大学 = だいがく vs 大[おお]+学[がく]) and the feature was dropped. In-scope kanji render plain; out-of-scope words are authored in kana. The 3-mode requirement is formally dropped - see `js/settings.js` line 119 + `verification.md` Pass 13. Closes OPEN-8 from `feedback/MASTER-TASK-LIST.md`.

## Spec

See [`JLPT N5 Grammar Tutor – Functional Spec.docx`](JLPT%20N5%20Grammar%20Tutor%20%E2%80%93%20Functional%20Spec.docx) for the full functional specification, including content rules, UX requirements, data model, and acceptance criteria.

## Status

All Phase 1 features implemented and verified end-to-end in a browser preview:
- Chapter 1 Learn (TOC + 7-block detail + Mark-as-known)
- Chapter 2 Test (MCQ + dropdown + sentence-ordering, visible-but-disabled Submit, instant scoring, per-distractor explanations)
- Chapter 3 Review (weak-pattern cards driven by rolling-history threshold)
- Chapter 4 Summary (stats + category heatmap + reset)
- Drill mode (SRS engine with 1d / 3d / 7d / 14d boxes + immediate feedback + graduation)
- First-run Diagnostic (10 questions across categories, seeds SRS without affecting test history)
- Furigana toggle with N5-kanji ruby annotation (pragmatic single-pick readings)
- Service worker for offline capability

Content (current as of v1.17.1; counts auto-verified by JA-115 / JA-107 / JA-47): 178 grammar patterns across 5 super-categories (32 fine-grained categories) in `grammar.json` · 995 vocabulary entries in `vocab.json` (post-BUG-018/019/024 dedup 2026-05-16/17; original 1041 reduced to 995 over 4 dedup passes) · 106 N5 kanji in `kanji.json` (every entry has stroke order + 1-3 example compounds + 1-2 example sentences) · 54 reading passages in `reading.json` · 50 listening items in `listening.json` · 284 mock-test questions in `questions.json` · 28 audited papers (7 per section × 4 sections, 6 papers of 15 questions plus 1 short paper of 10 questions per section) totalling 402 questions across moji / goi / bunpou / dokkai. Counts drift over time - when in doubt, run `python tools/check_content_integrity.py` which derives them from the live data files. See `TASKS.md` for outstanding work.
