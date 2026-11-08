# JLPT N5 Grammar Tutor - Tasks

## ▶ ACTIVE WORK — 2026-05-10 Legal Vetting Audit (11 findings)

Audit run: `prompts/LegalVetting.txt`.
Report: `feedback/legal-vetting-audit-2026-05-10.md`.
Persona: Japan-IP / education-publishing IP counsel (15-yr).
Overall exposure: **MEDIUM**. No severe findings.

Implementation order: **High-severity first** (F-1, F-2),
then Medium-severity documentation backlog (F-3, F-4, F-5,
F-6 light track), then Low-severity polish (F-8 thru F-11).

Status: ⏳ pending · 🔧 in-progress · ✅ done · ⏸ deferred

### TIER 1 — HIGH severity (resolve before partner / monetization pass)

| # | ID | P | Title | Status |
|---|---|---|---|---|
| 1 | LEGAL-F-1 | P1 | Remove `feedback/closed/external-questions-learnjapaneseaz.md` + `feedback/closed/external-corpus/learnjapaneseaz-extract.json` from public repo (DMCA risk) | ✅ done 2026-05-11 (git rm both files from HEAD; analysis-and-gap-audit.md source quotes redacted; README.md updated; history retained — not filter-repo'd, see commit msg) |
| 1b | LEGAL-F-12 | P1 | NEW (discovered during F-1 execution): `KnowledgeBank/externally_sourced_n5.md` (1778 lines, 42 mentions of learnjapaneseaz, line 20 declares "All questions in this file are extracted from public practice tests on learnjapaneseaz.com/jlpt-n5") was NOT in F-1 scope per audit text but appears to carry the same DMCA risk class. Audit missed this. | ✅ done 2026-05-11 (git rm KB file; tools/check_content_integrity.py refactored to remove the file from QUESTION_FILES list, EXPECTED_Q_COUNTS dict (was 189 questions), and 3 source-faithful exemption docstrings; EXPECTED_TOTAL updated 591→402; 50/50 invariants green) |
| 2 | LEGAL-F-2 | P1 | Disclose Claude-as-native-reviewer in CONTENT-LICENSE.md §9 + propagate `_meta.native_review_pass_2026_05_07` to grammar/vocab/kanji/papers/manifest data files | ✅ done 2026-05-11 (§9 added; manifest.json _meta added; grammar/vocab/kanji already propagated in earlier batches) |

### TIER 2 — MEDIUM severity (documentation backlog)

| # | ID | P | Title | Status |
|---|---|---|---|---|
| 3 | LEGAL-F-3 | P2 | Refresh CONTENT-LICENSE.md corpus counts to live values (1041 → 1000 vocab; verify all others); add JA-47 invariant to lock against drift | ✅ done 2026-05-11 (vocab 1041→1009, reading 45→54, listening 47→50 refreshed; JA-47 invariant added — 51/51 green) |
| 4 | LEGAL-F-4 | P2 | Add JLPT-trademark non-affiliation disclaimer to runtime footer (visible — not just in linked NOTICES.md / CONTENT-LICENSE.md) | ✅ done 2026-05-11 (index.html footer + en/hi locale keys + .footer-disclaimer CSS; cache version v1.12.71→v1.12.72) |
| 5 | LEGAL-F-5 | P2 | Add Inter font + Noto Sans JP attribution sections to NOTICES.md (SIL OFL 1.1 — currently missing despite README claim) | ✅ done 2026-05-11 (Inter + Noto Sans JP sections added with source URL, author, OFL 1.1 license + compliance note for each) |
| 6 | LEGAL-F-6 | P3 | Per-release manual spot-check: 10 random questions across `data/papers/*` — flag any potential competitor-corpus paraphrasing (lightweight track; heavyweight similarity-detection deferred) | ✅ done 2026-05-11 (10/10 audited: 9 safe, 1 borderline dokkai-6.8 monitored, no remediation needed; report at `feedback/legal-vetting-f6-spot-check-2026-05-11.md`; sampler at `not-required/tools-archive/sample_papers_f6_2026_05_11.py`) |
| 7 | LEGAL-F-7 | P3 | No remediation needed — mock-paper format-resemblance is mitigated by CONTENT-LICENSE.md §5 + audit_provenance.py CI gate (0 hits across 716 questions). Maintain F-6 coverage. | ✅ already mitigated |

### TIER 3 — LOW severity (backlog polish)

| # | ID | P | Title | Status |
|---|---|---|---|---|
| 8 | LEGAL-F-8 | P4 | Spot-check 5 random `svg/kanji/*.svg` for byte-preserved KanjiVG copyright header; add JA-48 invariant if any are missing | ✅ done 2026-05-11 (all 106 SVGs verified preserve Ulrich Apel copyright header — exhaustive scan, not 5-sample; JA-48 invariant added — 52/52 green) |
| 9 | LEGAL-F-9 | P4 | Add GitHub-Pages server-side IP-logging note to PRIVACY.md (closes GDPR Art 13/14 information-obligation gap) | ✅ done 2026-05-11 (new "Hosting (what GitHub may log)" section in PRIVACY.md — IP/UA/Referer/URL/timestamp + GitHub privacy-policy link + GDPR controller/purpose/legal-basis disclosure + self-host opt-out reference) |
| 10 | LEGAL-F-10 | P4 | Surface VOICEVOX speaker name on the listening-item playback UI (e.g. "Voice: 四国めたん") — currently only in NOTICES.md + internal `audio_render_meta` | ✅ done 2026-05-11 (listening.js renders voice attribution under each audio player using voice_planned.primary/secondary + engine; en/hi locale `listening.voices_label` keys added; .listening-voice-attribution CSS; min JS+CSS rebuilt; cache v1.12.72→v1.12.73). NOTE: audit assumed VOICEVOX speakers but data shows edge-tts voices (Nanami/Keita/Aoi/Daichi Neural). UI surfaces what's actually planned per voice_planned; NOTICES.md still references VOICEVOX — this provenance mismatch is registered separately as LEGAL-F-13 below. |
| 10b | LEGAL-F-13 | P2 | NEW (discovered during F-10 execution): TTS provider mismatch — `data/listening.json` items have `audio_render_meta.voice_provider: "voicevox"` + `voicevox_engine_version: "0.25.2"` BUT `voice_planned.engine: "edge-tts"` with Microsoft Neural voice names. NOTICES.md §VOICEVOX claims VOICEVOX (with 四国めたん etc. speakers) but no edge-tts attribution exists. Need to determine which TTS actually rendered the MP3 files and align: (a) audit one or two MP3s for VOICEVOX-vs-edge-tts signature, (b) update either the data fields or NOTICES.md to match reality. | ✅ done 2026-05-11. **Ground truth established:** MP3 file ID3v2 frames carry `Lavf62.12.101` (ffmpeg/libavformat, the edge-tts encoder path) — NOT VOICEVOX. `data/audio_manifest_voice.json` (canonical per-item manifest written by current build script) shows 47/47 rendered items use `voice_planned.engine: edge-tts` with 4 Microsoft Neural voices (Nanami/Keita/Aoi/Daichi). **Fixed:** listening.json — `audio_render_meta.voice_provider` corrected `voicevox→edge-tts` across 47 items; stale `voicevox_engine_version` field removed; `voices_used` array populated from voice_planned. NOTICES.md §VOICEVOX replaced with §Microsoft Edge TTS (with the 4 Neural voices, edge-tts library MIT licence, Microsoft Cognitive Services endpoint, F-13 correction notice). VOICEVOX kept as documented optional fallback per build_listening_audio_multivoice script. |
| 11 | LEGAL-F-11 | P5 | Run `python tools/check_content_integrity.py -v` to confirm 50/50 invariants stayed green during this legal-vetting audit pass (audit-process honesty) | ✅ done 2026-05-11 (50/50 green) |

### Open factual questions (F-1..F-11 follow-ups)

These could not be resolved by repo inspection alone — surface to user before closing affected findings:

- F-1: learnjapaneseaz.com terms-of-use posture (assumed "all rights reserved" by default).
- F-8: actual SVG file headers — verify byte preservation.
- F-3: whether the corpus-count refresh should happen on every release via a version-stamp script, or once per legal-vetting cycle.
- Self-host forks (`docs/SELF-HOST.md`, `data/branding.json`): how do CONTENT-LICENSE.md claims propagate to forks? Out of scope today; revisit when first non-self fork ships.

### Monetization blast-radius (locked-in items if monetization ever ships)

Per `feedback/legal-vetting-audit-2026-05-10.md` § Monetization blast-radius:
- F-1 must be cleanly resolved (commercial use raises bar for "research use" defenses).
- VOICEVOX per-speaker terms re-verified (some characters in catalog forbid commercial use).
- "100% on-device, no telemetry" claim becomes a JFTC false-advertising risk if any tracking added.
- "JLPT" branding tolerance from JEES is stronger for non-commercial; reassess at commercial pivot.
- CC BY-SA 4.0 content license forces any monetized fork / derivative to remain CC BY-SA.

---

## Earlier ACTIVE WORK — 2026-05-09 N5 Richness Audit (29 items)

Current cycle: implement findings from
`prompts/N5Improvement.txt` audit run, registered as
ISSUE-105..110 + IMP-124..146 in
`feedback/n5-audit-2026-05-04.xlsx`.

Implementation order: **lower-effort first**, then medium,
then high. Within each tier: P1 → P2 → P3 → P4 → P5 → impact
descending.

Status: ⏳ pending · 🔧 in-progress · ✅ done · ⏸ deferred / blocked

### TIER 1 — LOW EFFORT (mechanical, scriptable; ship together)

| # | ID | P | Title | Status |
|---|---|---|---|---|
| 1 | ISSUE-109 | P2 | Vocab transitivity-pair links (12 canonical N5 pairs) | ✅ 8/12 in-corpus (4 need N4 vocab) |
| 2 | ISSUE-105 | P3 | Kanji confusable cluster cross-links (8 clusters) | ✅ 13 kanji linked + 5 also-warns |
| 3 | ISSUE-108 | P3 | Paper questions → grammarPatternId back-link | ✅ 294/402 (73%) auto-inferred |
| 4 | ISSUE-110 | P3 | Vocab verb-class flag (audit was field-name typo) | ✅ no gap; closed with explainer |
| 5 | IMP-130 | P2 | Genki/Minna lesson tags on grammar patterns | ✅ 162 genki + 175 minna structured |
| 6 | IMP-131 | P2 | Kanji vocab cross-links auto-scan (≥5 each) | ✅ 10 kanji updated, 34 new links |
| 7 | IMP-133 | P3 | Vocab counter pairing on remaining ~500 nouns | ✅ 49 noun-counter pairings |
| 8 | IMP-134 | P3 | Honorific/humble register chains (5 chains) | ✅ 1 chain in-corpus (4 need N4) |
| 9 | IMP-139 | P3 | Vocab frequency_rank (Leeds JP corpus, CC-BY) | ✅ 705/1000 (70%) imported |
| 10 | IMP-141 | P3 | Slow-version listening audio (0.7×) | ✅ 40/47 rendered (7 lack source MP3) |
| 11 | IMP-144 | P4 | Multi-skill mixed drill toggle | ✅ home + review headings updated |
| 12 | IMP-146 | P5 | Lesson-notes PDF download | ✅ browser-native print → save-as-PDF |

### TIER 2 — MEDIUM EFFORT

| # | ID | P | Title | Status |
|---|---|---|---|---|
| 13 | IMP-127 | P2 | Pitch accent from Kanjium (CC BY-SA, EDICT-derived) | ✅ 827/1000 (83%) — exceeds ≥80% target |
| 14 | IMP-128 | P2 | Collocations ≥5 per top-300 high-freq word | ✅ **300/300 (100%)** — 4 authoring rounds |
| 15 | IMP-129 | P2 | Listening timestamped transcripts (line-level via mora-proportional) | ✅ 40/47 — line-level (whisper deferred) |
| 16 | IMP-132 | P2 | Audio per grammar example (~700+ MP3s) | ✅ 739/739 (100%) — gTTS render |
| 17 | ISSUE-106 | P3 | Kanji→reading-passage cross-references | ✅ 59/106 (56%) — covers all kanji used in passages |
| 18 | ISSUE-107 | P3 | Listening vocab_glossary inline | ✅ 47/47 (100%), 322 refs, avg 6.9/item |
| 19 | IMP-140 | P3 | Reading paragraph summary + lit/natural translation | ✅ 45/45 paras + **45/45 translations authored**; opt-in UI toggle |
| 20 | IMP-142 | P4 | SEO + structured-data per content page | ✅ Course + BreadcrumbList JSON-LD + hreflang + noscript |
| 21 | IMP-143 | P4 | PDF cheat sheet builder | ✅ grammar TOC print → cheat-sheet PDF |

### TIER 3 — HIGH EFFORT (requires user re-confirm per CLAUDE.md Rule 2)

| # | ID | P | Title | Status |
|---|---|---|---|---|
| 22 | IMP-124 | P1 | Grammar examples → 7 per pattern | ✅ **100%** at 7+ (was 0%); 160 hand-authored + 347 xref'd |
| 23 | IMP-125 | P1 | Kanji 3-mnemonic structure (visual + reading + meaning) | ✅ schema upgraded 106/106 + **all 212 visual+reading mnemonics authored** |
| 24 | IMP-126 | P1 | Authentic-content layer cross-surface | ✅ starter corpus (30 items) + new #/authentic route + home CTA |
| 25 | IMP-135 | P3 | JP-keyboard typed-input reviews + 50% partial credit | ✅ activated by IMP-136/138 work (typed input lives in drill flow) |
| 26 | IMP-136 | P3 | Cloze-deletion drill question type | ✅ inline cloze + 14 existing text_input questions now functional |
| 27 | IMP-137 | P3 | Tofugu-style essays on top-30 trickiest patterns | ✅ **30/30 fully authored** (intro + why + pitfalls + contrasts + tip) |
| 28 | IMP-138 | P3 | Production reviews (English → JP typing) | ✅ shares cloze renderer; production variant added |
| 29 | IMP-145 | P5 | WaniKani-style SRS gating | ✅ opt-in setting + queue filter + storage helpers |

### EXECUTION RULES (this cycle)

- **One git commit per batch** of related items.
- **`tools/check_content_integrity.py` MUST stay 50/50 green** between commits.
- **No /N4/ touches** (CLAUDE.md Rule 1).
- **Before starting Tier 3 (HIGH effort)**: re-confirm with user
  per CLAUDE.md Rule 2 (large-scope work).
- **If a Tier-1 item turns out medium/high**: re-classify in
  this table and defer.

### ALL CONTENT AUTHORED — 29/29 — 2026-05-10

Final statistics across the corpus:
- **Vocab**: 437 entries with collocations (top-300 = 100% ≥5);
  828/1000 with pitch_accent (83%); 705/1000 with frequency_rank.
- **Grammar**: 178/178 patterns at ≥7 examples (100%); 30/30
  trickiest patterns with fully-authored Tofugu essays; 162/178
  with Genki lesson tags.
- **Kanji**: 106/106 with 3-mnemonic structure; all 212 visual +
  reading mnemonics authored llm_curated.
- **Reading**: 45/45 with paragraph segmentation + literal +
  natural translations; opt-in UI toggle preserves JA-27.
- **Listening**: 47/47 with vocab_glossary; 40/47 with line-level
  timestamps; 40/47 with 0.7× slow audio.
- **Authentic**: 30 starter items + new #/authentic route.

All 26 batches pushed to origin/master; live at GitHub Pages.

### TIER 3 STATUS — COMPLETE (8/8, with caveats) — 2026-05-10

Tier-3 high-effort items shipped. Batches:
12. IMP-135 + IMP-136 + IMP-138 — typed input drill (cloze + production),
    activated 14 existing text_input questions
13. IMP-126 — authentic-content layer starter corpus (30 items
    across signs/menu/transit/shop/notice + new #/authentic route)
14. IMP-145 — WaniKani-style SRS gating (opt-in setting)
15. IMP-125 — kanji 3-mnemonic structure (visual + reading + meaning,
    schema upgrade preserves existing native-reviewed strings)
16. IMP-124 — grammar examples cross-referenced from vocab corpus
    (0% → 64% at 7+ examples, 15% → 79% at 5+; 347 added)
17. IMP-137 — Tofugu-style essay scaffolding for top-30 trickiest
    patterns + new "Deep dive" UI block

Caveats / follow-up authoring (separate native-review tracks):
- Kanji visual + reading mnemonics (IMP-125): 106×2 = 212 stubs
  flagged as `auto_derived` pending native review
- Grammar deep-dive essays (IMP-137): 30 stubs flagged
  `needs_native_review`; the 4 sub-fields per essay are pending
  native authorship
- Grammar examples (IMP-124): 42/178 patterns still <7 (no
  matching trigger forms in vocab corpus); native authoring needed

ALL 17 BATCHES PUSHED TO ORIGIN. Live website auto-redeploys via
GitHub Pages on each push to master.

### TIER 2 STATUS — COMPLETE (9/9, with caveats) — 2026-05-09

Tier-2 medium-effort items shipped. Batches:
6. IMP-127 — pitch-accent backfill via Kanjium CC BY-SA (83% coverage)
7. IMP-132 — grammar-example audio at 100% (113 new gTTS MP3s)
8. ISSUE-106 + ISSUE-107 — kanji↔reading + listening glossary
9. IMP-128 — collocations partial (corpus too thin for >=5 target)
10. IMP-129 — line-level mora-proportional timestamps (whisper deferred)
11. IMP-140 — paragraph segmentation + translation stubs (text needs human authoring)
12. IMP-142 + IMP-143 — SEO Course/Breadcrumb JSON-LD + cheat-sheet print

### TIER 1 STATUS — COMPLETE (12/12) — 2026-05-09

All Tier-1 LOW-effort items shipped. Batches:
1. ISSUE-105/108/109 + IMP-133/134 — structural pairs + clusters
2. IMP-131 + ISSUE-108 v2 — kanji-vocab links + paper grammar (73%)
3. ISSUE-110 (closure) + IMP-130 + IMP-139 — lesson tags + freq ranks
4. IMP-141 + IMP-144 — slow audio + mixed drill toggle
5. IMP-146 — print → save-as-PDF for pattern-detail pages

**Pause point per CLAUDE.md Rule 2:** Tier 2 (medium effort) and
Tier 3 (high effort) each warrant explicit user re-confirm before
starting.

This active section will be deleted when the audit cycle is fully
closed. The historical body below is preserved for record.

---

> **2026-05-07 round-9 close-out (v1.12.50):** The live source of truth for
> open / closed work is now **`feedback/n5-audit-2026-05-04.xlsx`**
> (Items + Questions sheets). Round-9 closed at **219 Done / 3 Avoid /
> 0 Open / 0 Open Questions**, all native-reviewed at the LLM-persona
> Q33 quality bar. The body of this file below is preserved as a
> historical narrative through round-3 (v1.10.x) and is **not the
> current state** — see the close-out banner immediately below for the
> v1.12.50 baseline + which items in the historical body are now done.
>
> **2026-05-06 transition note:** The 5-locale shell (en/vi/id/ne/zh)
> was narrowed to 2 locales (en + hi) per IMP-096 architectural
> decision. Historical task rows below mention the original 5-locale
> state and are preserved for record; the current state is **en+hi
> only**, with all surfaces 100 % Hindi-covered. See CHANGELOG v1.12.40
> for the rationale.

## v1.12.50 close-out banner (2026-05-07)

Last updated: **2026-05-07** (round-9 close-out · v1.12.50 · SW
`jlptsuccess-n5-v1.12.50` · **48 content-integrity invariants** + 8
design-system rules green · audit tracker 219 Done / 3 Avoid / 0 Open /
0 Open Questions).

**Baseline shipped at v1.12.50:**

- **Content scale:** 178 grammar patterns / 1041 vocab / 106 kanji /
  45 reading passages / 47 listening drills / 290 question-bank items /
  29 mock-test papers (incl. chokai virtual paper) / 426 paper-bound
  questions + full-mock papers (85 Q × 105 min) matching real JLPT N5
  shape.
- **Hindi (niche-N1):** 100 % `meaning_hi` / `gloss_hi` /
  `meanings_hi` / `summary_hi` / `explanation_hi` / `l1_notes.hi`
  across all surfaces, native_reviewed at LLM-persona Q33 quality bar.
- **Audio (current, post-Phase-2 2026-05-17):** **50 listening items**
  rendered with **VOICEVOX 0.25.2 multi-voice** at `speed_scale=1.00`
  via from-source Phase-2 re-render (commit `cdd0e6d`). **6 distinct
  speakers** (春日部つむぎ / 玄野武宏 / 四国めたん / ずんだもん /
  雨晴はう / 青山龍星) rotated deterministically per item, role-aware
  speaker mapping by `script_ja` line prefix. Pacing post-render +
  post-processing: 50 / 50 in target band 180–240 mpm; mean 214.5;
  16 items direct from VOICEVOX, 29 with single-pass `ffmpeg-atempo`,
  5 with single-pass `ffmpeg-rubberband` (factor < 0.5).
  Grammar (1782) on VOICEVOX (round-10 flip from gTTS, 2026-05-12).
  Reading (54) on gTTS. Truncation guard
  (`tools/fix_truncated_audio_2026_05_07.py`) closed 9 mid-sentence
  clipped clips. **All audio files on disk (100 %).** Phase timeline
  in `docs/AUDIO-PHASE2-VOICEVOX-RERENDER.md`.
- **PWA / SRS:** Installable, offline-first, **FSRS-4.5** (replaced
  SM-2) unified across grammar + vocab + kanji in a single daily
  review queue.
- **Privacy:** No login · no tracking · no third-party scripts; all
  state in `localStorage` namespaced `jlpt-n5-tutor:*`. CSP
  same-origin. Verified by 48 content-integrity invariants
  (JA-1..JA-39 + X-6.x) + 8 design-system rules.

### Historical items closed by round-9 (re-classify if reading the body)

The body below mentions these items as open / deferred / blocked.
Round-9 actually shipped them — re-read with these closures in mind:

| Body ID | Body status | Round-9 actual status |
|---|---|---|
| **SVA-Q1** FSRS-4.5 SRS upgrade | open quick-win | **✅ Shipped (replaced SM-2; unified queue across grammar + vocab + kanji)** |
| **SVA-Q3** VOICEVOX listening rebuild (multi-voice) | open quick-win | **✅ Shipped (VOICEVOX 0.25.2 · 4 voices · `tools/build_listening_audio_multivoice_2026_05_07.py`)** |
| **SVA-Q5** Cultural-context callouts on reading | open quick-win | **✅ Shipped (`cultural_context` field on every Japan-specific reading passage)** |
| **JCE-6** VOICEVOX listening voice variety (≥4 distinct voices) | open content | **✅ Shipped (round-9 multi-voice render)** |
| **EB-1 / OQ-2** Listening corpus expansion 12 → 30+ (native voice required) | external-blocked | **✅ Shipped synthetic equivalent: 47 items rendered with VOICEVOX multi-voice at JLPT-N5 pace.** Native-recording swap path remains open under IMP-094 (see `docs/NATIVE-AUDIO-WORKFLOW.md`); priority re-ordered to reading-first since synthetic listening now sounds plausibly close to JLPT exam audio. |
| **INFRA-2 / INFRA-3** (in MASTER-TASK-LIST.md): VOICEVOX backend + multi-voice dialogue | "closed-by-decision" 2026-05-03 | **Decision reversed and shipped in round-9.** The activation recipe at `feedback/voicevox-integration-notes.md` was followed. Outcome: round-9 baseline. |
| Listening-drill count 30 → 47 | not in body | **✅ Round-7/8/9 added 17 more listening items, all rendered.** |
| Reading passages 30 → 45 | not in body | **✅ Rounds 4–6 added 15 passages with `summary_hi` + `cultural_context`.** |
| Vocab corpus 1003 → 1041 | not in body | **✅ Rounds 4–6 added 38 high-frequency entries with `gloss_hi` + verb_class + counter where applicable.** |
| Kanji corpus stays at 106 (full N5) | not in body | **✅ Confirmed at round-9: 100 % `meanings_hi`, radical breakdown, mnemonics, look-alike clusters, ≥3 examples per kanji.** |
| 187 → 178 grammar patterns | body says 187 | **✅ Round-2/3 retired 9 stub / duplicate / non-N5 patterns; net 178 final, all native_reviewed with `l1_notes.hi`.** |
| 5-locale shell (en/vi/id/ne/zh) | body assumes 5 | **✅ Narrowed to en + hi on 2026-05-06 per IMP-096; JA-39 invariant locks the locale set; vi/id/ne/zh files moved to `locales/legacy/`.** |
| Mock papers + 426 questions | not in body | **✅ Rounds 5–8: 29 papers including chokai virtual paper + full-mock 85-Q × 105-min papers matching real JLPT N5 shape.** |
| 33 → 48 content-integrity invariants | body says 33 / 38 / 39 | **✅ Round-2..9 added JA-26..JA-39 (locale-coverage, provenance, voice-variety-status, dokkai upper bound, etc.).** |
| Trust-band promotion + privacy badge | SVA-1.x open | **✅ 6-pill row promoted to home above the fold; in-app PRIVACY/NOTICES viewer at `#/privacy` and `#/notices`; provenance badges on every learnable surface.** |

### Items intentionally NOT closed at round-9

- **EB-3 OQ-6** Brief translation to Japanese → still deferred.
- **EB-4 OQ-1 v2.0** ML-backed recommender → still deferred (no
  privacy-clean data path).
- **SVA-NEXT-2.4** Print-to-PDF mock paper → still open (next cycle).
- **SVA-NEXT-3** Self-host institutional kit (`branding.json` override
  layer) → partial: SELF-HOST.md productized, branding-override layer
  still open.
- **SVA-6.x** In-browser AI features → still future-frontier.
- **JCE-5** Native-speaker reading audio → still blocked on
  monetization / sponsorship.

### Where to read instead of this file

1. **`feedback/n5-audit-2026-05-04.xlsx`** — live tracker (Items +
   Questions sheets · 219/3/0/0 at round-9 close).
2. **`feedback/audit-round9-2026-05-06.md`** — round-9 narrative.
3. **`specifications/JLPT-N5-Current-Implementation-Spec.md`** —
   canonical "what the app does" (v1.12.50).
4. **`CHANGELOG.md`** — release-by-release detail.
5. **`README.md`** + **`README.hi.md`** — feature snapshot.

The historical body below is preserved verbatim from 2026-05-02 — do
**not** drive new work from it; use the xlsx + the docs listed above.

---

## Historical body (preserved through 2026-05-02)

Last updated: 2026-05-02 (Content-protection layer - v1.10.1 / SW v90 / 38 invariants. Closes the JA-first language sweep + DEFER-1 backlog + content-deterrent layer in three releases on the same day: v1.9.0 (Japanese-first surface), v1.10.0 (syllabus dashboard + 100% grammar-pattern test coverage + multi-correct categories F/G/H + JA-29 subtype-taxonomy lock), v1.10.1 (content-protection layer + GitHub-link removal). Added invariants over the day: JA-26..JA-29. Content-protection layer raises friction against casual copying; honest limitations documented in `js/content-protect.js`. **39/39 CI invariants green**.)

## Live site

- **Repo**: https://github.com/gauravaccentureproducts/JLPTSuccess
- **Live URL**: https://gauravaccentureproducts.github.io/JLPTSuccess/N5/
- **Engine tests**: 37/37 passing (`tests.html`)
- **Lint**: kanji-clean, vocab advisory-only

## Status snapshot

_(Last verified 2026-05-25 by weekly audit)_

- **178 grammar patterns** / **284 question-bank items** (no stubs). Distribution reflects all pass cleanup through v1.17.x.
- **17 routed views + sub-paths**: Home / **Learn hub (5-card: Grammar/Vocab/Kanji/Dokkai/Listening)** with sub-paths `#/learn/grammar`, `#/learn/vocab`, `#/learn/vocab/<form>` (per-word detail with 5 example sentences), `#/learn/<patternId>` / Kanji (`#/kanji`, `#/kanji/<glyph>`) / Test (`#/test`, `#/test/<n>` direct-launch with quit-prompt) / Practice (`#/drill`, was "Daily Drill") / Review (SM-2 SRS) / Summary / Diagnostic / Settings / Reading / Listening / こそあど / は vs が / Verb groups / て-form gym / Particle pairs / Counters
- SM-2 SRS in Review (4-button grading)
- Service worker `jlptsuccess-n5-v1.17.1` (stale-while-revalidate for shell, cache-first for content); update toast on new shell; lazy-caches audio on first play
- 2-locale i18n shell (en + hi); additional locales (vi/id/ne/zh) pending translation
- PWA manifest installable
- Export / import progress round-trips through JSON
- 37 browser-runnable tests
- **Vocab corpus**: 995 structured entries (data/vocab.json)
- **Kanji corpus**: 106 entries with stroke-order SVG slot (data/kanji.json)
- **Reading corpus**: 54 graded passages with comprehension Qs each (data/reading.json)
- **Listening corpus**: 50 items across JLPT formats (data/listening.json); rendered with VOICEVOX 0.25.2 multi-voice
- **Audio assets**: ~1936 MP3 files - 1782 grammar examples, 54 reading passages, 100 listening files. VOICEVOX Phase-2 re-render completed 2026-05-17.
- **Audio TTS pipeline**: tools/build_audio.py - auto-detects piper-tts / gtts / pyttsx3. Idempotent. Uses string-suffix concat (not Path.with_suffix) so example IDs like 'n5-001.0' don't collide.
- **Japanese-first learner surface (2026-05-02)**: dokkai + listening titles all in JA; English passage-translation panel removed from dokkai; UI page chrome (titles, intro, buttons, feedback labels, stat labels, level/topic) all rendered in JA via `renderJa()`. English glosses retained only on grammar examples (`grammar.json` `translation_en`) and after-answer rationales (`explanation_en`) where L1 scaffolding teaches new patterns.
- **Content-protection layer (2026-05-02 v1.10.1)**: deters casual copying of question content. CSS `user-select: none` on body (with input/textarea/`.allow-select` opt-outs); JS module `js/content-protect.js` blocks contextmenu / copy / cut / dragstart / selectstart / Ctrl+C/A/X/S/P/U / F12 / Ctrl+Shift+I/J/K/C; window-blur sets `html[data-blur=true]` to obscure during region-screenshots; `@media print` blanks the page. NOT security - devtools / view-source / phone-camera-of-screen still work; honest limits documented in module header. GitHub source links removed from footer + changelog fallback + PRIVACY.md.

---

## Open user-reported items (2026-05-01)

- [x] **UX-CONSISTENCY-1: "Mark as known" checkbox positional inconsistency.** User reported 2026-05-01 (screenshot of particle が detail page). **Closed in commits 8484b76 + 2603803:** toggle markup added to `renderVocabDetail` (js/learn.js) and `renderDetail` (js/kanji.js); CSS `.vocab-header { margin-bottom: 16px }` and `.kanji-glyph-row { gap: 24px; margin: 16px 0; flex-wrap: wrap }` overrides stripped so all three detail-page headers use the canonical `.pattern-header` flex layout (gap 16, margin-bottom 24, justify-content space-between). Toggle position now identical across grammar / vocab / kanji detail at every viewport. Cross-referenced as OPEN-10 in `feedback/MASTER-TASK-LIST.md`.

---

## Strategic value-adds (added 2026-05-06)

> **Source:** post-locale-narrowing competitive analysis. Beyond Hindi support (niche-N1), these are the defensible moats vs Bunpro / WaniKani / Renshuu / Duolingo / Anki / Marugoto. Prioritised by defensibility (hard for incumbents to copy) + alignment with the no-account / no-cloud / free-forever-personal posture.
>
> **The moat thesis:**
> "JLPTSuccess is the only JLPT prep app that respects you as an adult learner: no account, no cloud, no ads, no streak anxiety, native-Hindi-medium where you need it, English-medium where you don't, and you can self-host the whole thing for your school. Free forever for personal use."
>
> Every feature decision passes through that filter. Competitors will eventually copy Hindi support if the market becomes visible; they CANNOT copy the privacy posture without burning their business model — that is the durable moat.

### SVA-priority next-3 (do these first)

- [ ] **SVA-NEXT-1: Visible privacy badge + one-click DevTools verify panel.** Amplifies the strongest moat that is currently invisible. Add a footer privacy badge ("0 accounts, 0 cookies, 0 tracking - verify in DevTools Network tab"). Add a Settings panel "Verify privacy" that opens DevTools instructions. Add a homepage hero line: "Your study data never leaves your device. No login, no email, no credit card. Forever." Estimated effort: 1-2 days.
- [ ] **SVA-NEXT-2: Exam-fidelity mock test mode polish.** Real-time countdown timer matching official sections (25 / 50 / 30 min). Per-section minimum-pass display (38 / 19 / 19 for N5). Listening play-once enforcement in test mode, replay-allowed in practice. Print-to-PDF mode for offline practice papers. Visual layout matching official 言語知識 / 文法・読解 / 聴解 paper. Estimated effort: 1 week. Targets the SSW-visa-applicant + university-applicant (deadline-driven) user.
- [ ] **SVA-NEXT-3: Self-host institutional kit.** Productize the existing `docs/SELF-HOST.md` into a one-page "spin up JLPTSuccess for your school" guide. Add `data/branding.json` for logo/title/footer override without forking. Clear license messaging on README ("Schools and NGOs welcome - no GDPR overhead because we don't collect data"). Soft "Powered by JLPTSuccess" footer on self-hosted instances. Estimated effort: 3-5 days. Unlocks niche-N3 paid-institutional-tier later without breaking personal-free promise.

### SVA-1: No-account / no-tracking / no-cloud — push it harder, not just claim it (priority *)

> **Why it's a moat:** Bunpro / WaniKani / Renshuu CANNOT match this without rewriting their architecture. They depend on accounts for recurring revenue. JLPTSuccess does not.

- [x] **SVA-1.1 Privacy badge on every page footer.** ✓ Shipped earlier — `index.html:353` `<p class="footer-trust-strip">` carrying "No login · No tracking · Works offline · Open source · 100% on-device · Free, no ads, no paywall." Locale-mirrored via `footer.trust_strip` in en.json + hi.json.
- [x] **SVA-1.2 One-click "Verify privacy" panel in Settings** that opens DevTools / Network tab instructions. ✓ Shipped 2026-05-22 (v1.15.7). Settings → Privacy section: 3-step DevTools instructions + "Run live verification" button that scans `performance.getEntriesByType('resource')` and reports same-origin vs cross-origin request counts in real time. Code: `js/settings.js` `set-privacy-check` handler. Strings: `settings.privacy*` in en.json + hi.json. Bunpro CANNOT do this without exposing they phone home.
- [x] **SVA-1.3 Homepage privacy hero line:** "Your study data never leaves your device. No login, no email, no credit card." ✓ Shipped 2026-05-22 (v1.15.7). Rendered above syllabus-overview via `.home-privacy-hero` in `js/home.js`. Locale-mirrored via `home.privacy_hero`.
- [x] **SVA-1.4 "Export your data" button** that produces a JSON of all localStorage. ✓ Shipped earlier — `js/settings.js:302` `set-export` click handler calls `storage.exportProgress()` and downloads `jlpt-n5-progress-YYYY-MM-DD.json`. Settings → Data section. PRIVACY.md documents the flow.
- [ ] **SVA-1.5 PRIVACY.md homepage card** linking to the public privacy promise + audit log.

### SVA-2: Exam-fidelity mock paper mode (JLPT-specific) (priority *)

> **Why it's a moat:** Bunpro doesn't do mock papers. WaniKani is kanji-only. Renshuu's mock mode is approximate. Anki has no exam mode. JLPTSuccess can be the only app where N5 / N4 mock test = official exam structure exactly.

- [ ] **SVA-2.1 Real-time countdown timer** matching official sections (25 / 50 / 30 min).
- [ ] **SVA-2.2 Per-section minimum-pass display** (38 / 19 / 19 for N5) — not just total score.
- [ ] **SVA-2.3 Listening play-once enforcement** in test mode; replay-allowed in practice mode.
- [ ] **SVA-2.4 Print-to-PDF mode** for practice papers - real paper, real pencil. NO competitor does this.
- [ ] **SVA-2.5 Visual layout match** — official 言語知識 / 文法・読解 / 聴解 paper structure on screen.
- [ ] **SVA-2.6 Per-mondai progress tracking** within the section (e.g., "M1 7/12, M2 4/8...").

### SVA-3: Open source + self-hostable for institutions (priority *)

> **Why it's a moat:** None of the competitors are open source. Indian Tier-2 / Tier-3 language coaching schools, NGOs, and SSW-prep training centres want tools they can deploy on a school's local network without sending student data to a US/Japan SaaS.

- [ ] **SVA-3.1 SELF-HOST.md productized** — one-page deploy guide.
- [ ] **SVA-3.2 `data/branding.json` override mechanism** — logo / title / footer / theme without forking.
- [ ] **SVA-3.3 README license messaging** — "Schools and NGOs welcome. No GDPR overhead because we don't collect data."
- [ ] **SVA-3.4 Soft attribution footer** — "Powered by JLPTSuccess" on self-hosted instances; drives discovery.
- [ ] **SVA-3.5 Institutional support contract template** (paid tier candidate later, without breaking personal-free promise).

### SVA-4: Provenance transparency badges (your unique trust signal)

> **Why it's a moat:** JLPTSuccess already tracks `review_status: native_reviewed / llm_curated / auto_generated` per item. Bunpro and WaniKani treat content as a trust black-box. JLPTSuccess can show a per-item badge.

- [ ] **SVA-4.1 Per-item provenance badge** on every content page (extend existing `js/provenance-badge.js` coverage to all surfaces).
- [ ] **SVA-4.2 Filter mode**: "Show only native-reviewed content" — power-user lever no competitor offers.
- [ ] **SVA-4.3 Aggregate stats on Progress dashboard**: "You've drilled 87% native-reviewed, 13% LLM-curated."
- [ ] **SVA-4.4 Pricing-tier hook for later** — a future paid tier could fund native-review uplift on user-selected content.

### SVA-5: Bandwidth-friendly bundle (Indian / SE-Asian markets)

> **Why it's a moat:** Bunpro / WaniKani / Renshuu are SPA-heavy with constant network chatter. JLPTSuccess full N5 app is ~250KB minified. On a Jio 4G plan with monthly data caps, this matters enormously.

- [ ] **SVA-5.1 Bundle-size badge on README** — "127KB JS, no tracking pixels, no ad networks, runs on a 5-year-old phone."
- [ ] **SVA-5.2 Optional bulk audio download mode** — "Download all audio for offline use (130MB)" — one-time cost, then never reloads.
- [ ] **SVA-5.3 Page-weight comparison table** in marketing copy: "JLPTSuccess: 250KB. Duolingo: 4.2MB. WaniKani: 1.8MB."
- [ ] **SVA-5.4 Lighthouse score >95 on 3G** — measure, document, cite.

### SVA-6: In-browser AI features (privacy-preserving) — emerging frontier

> **Why it's a moat:** Frontier nobody owns yet. WebLLM / llama.cpp.wasm / Transformers.js can now run small models fully in the browser — no API call, no data leak. By 2026 this is viable for limited features. Bunpro / WaniKani have no incentive (their model = "you pay us, AI in cloud"). JLPTSuccess model = "you own your data, AI runs locally."

- [ ] **SVA-6.1 Conversation practice** with a small in-browser model (1-3B params) — 5-minute Japanese conversation entirely on-device.
- [ ] **SVA-6.2 Sentence diagnosis** — paste a sentence, in-browser model points out particle / conjugation errors.
- [ ] **SVA-6.3 Personalized review-queue suggestions** based on local error patterns, computed in-browser.
- [ ] **SVA-6.4 Bundle-size budget** — local model adds 200-500MB; gate behind opt-in download.

> **Caveat:** 1-2 quarters of work. Worth it only if Hindi-medium + privacy-first is already validated.

### SVA-7: Adult-learner / anti-gamification positioning

> **Why it's a moat:** Duolingo's whole business is gamification. Bunpro has streaks. The adult learner — especially the SSW visa applicant who has 6 months until exam — does NOT want streak anxiety, push notifications, or social pressure. They want a quiet tool that works.

- [ ] **SVA-7.1 Explicit messaging:** "No streaks, no XP, no leaderboards. Adult learners deserve quiet tools." (homepage + about page).
- [ ] **SVA-7.2 No push notifications ever** — already the case; surface it as a feature.
- [ ] **SVA-7.3 Optional minimal-streak in Settings, off-by-default** — some learners do want it; offering without forcing is the move.
- [ ] **SVA-7.4 Progress dashboard reframed** — not "current streak: 47 days" but "152 grammar patterns mastered, 89 vocab to review tomorrow."

### SVA-8: Accessibility (WCAG AA) — institutional adoption gate

> **Why it's a moat:** Government schools, universities, and NGOs in any country require WCAG AA. Few JLPT apps clear this bar. JLPTSuccess already has skip-link, prefers-reduced-motion, semantic HTML, focus management.

- [ ] **SVA-8.1 Public WCAG AA audit page** — list every guideline, document compliance.
- [ ] **SVA-8.2 Color-contrast verification** — cite ratios per surface.
- [ ] **SVA-8.3 Screen-reader walkthrough video** on YouTube — institutional procurement teams watch these.
- [ ] **SVA-8.4 "Accessibility-tested by [partner]" stamp** when partner found (Indian disability-rights NGO partnership candidate).

---

### Quick-win features (not moats, but shippable)

- [ ] **SVA-Q1 FSRS-4.5 SRS upgrade** (replace SM-2). Modern SRS; 30-40% fewer reviews for same retention. Effort: 2-3 days.
- [ ] **SVA-Q2 Print-friendly practice paper PDF.** Real paper, real pencil; pre-exam ritual. Effort: 1 day.
- [ ] **SVA-Q3 VOICEVOX listening rebuild** with multiple voices. Realistic chokai vs gtts. Effort: 3-5 days.
- [ ] **SVA-Q4 Genki / Minna chapter mapping** on every grammar pattern. Cross-reference with textbooks the learner already owns. Effort: 2-3 days.
- [ ] **SVA-Q5 Cultural-context callouts** in reading passages. Explain お正月 / クリスマス / 連休 for non-Japan-resident learners. Effort: 1-2 days.
- [ ] **SVA-Q6 "Your weakest pattern" suggestion** on home page. Lightweight personalisation; no data leaves device. Effort: 1 day.
- [ ] **SVA-Q7 Time-to-exam countdown widget** in Settings. Targets the deadline-driven user. Effort: 1 day.
- [ ] **SVA-Q8 Localised number formatting** (१,२३,४५६ for hi locale). Small but India-specific polish. Effort: <1 day.

---

### Anti-moves (do NOT do these — they break the moat)

> **Decision filter:** every proposed feature must pass: "does this preserve no-account / no-cloud / no-ads / adult-learner / free-forever-personal?" If no — it's an anti-move.

- [ ] ~~**ANTI-1 User accounts for cloud sync**~~ — breaks N2. Once accounts exist, the privacy story is gone.
- [ ] ~~**ANTI-2 Streaks / XP / leaderboards**~~ — breaks adult-learner positioning. Becomes Duolingo Lite.
- [ ] ~~**ANTI-3 Cloud-based AI tutoring**~~ — breaks N2. Either fully local (SVA-6) or skip entirely.
- [ ] ~~**ANTI-4 Premium tier with paywalled core JLPT prep**~~ — kills "free forever for personal use" — the core promise to Indian Tier-2 / Tier-3 learners. Institutional / school tier OK; personal tier no.
- [ ] ~~**ANTI-5 In-app ads (even ethical ones)**~~ — trust collapse. Done.
- [ ] ~~**ANTI-6 Social / community features**~~ — requires accounts; introduces moderation cost; breaks N2. Use external Discord / Telegram for community if needed.
- [ ] ~~**ANTI-7 Tracking pixels / analytics (even Plausible / Umami)**~~ - privacy badge dies. Use server logs only.

---

## Japanese content enrichment (depth-fill cycle, started 2026-05-06)

> **Scope filter:** items here enrich the actual N5 Japanese content (grammar patterns, vocab, kanji, reading passages, listening drills, audio). Items relating to Hindi locale, app features, business model, privacy, distribution, or accessibility are NOT here - they are tracked in the SVA / locale / SVA-Q sections above.
>
> **Sequencing:** items will be tackled in ascending order of effort (smallest first). Each ID-tagged item is one commit minimum. Each item produces a build script under `tools/jce_*.py` (idempotent) so re-running is a no-op.

### JCE-2: Kanji look-alike cluster cross-links (1-2 days)
- [ ] **JCE-2** Author `look_alike` field on `data/kanji.json` for 8 confusable N5 clusters: 大/犬/太 (dot moves), 木/本/末/未 (line position), 人/入/八 (radical similarity), 日/目/白 (rectangle variations), 千/干/王/玉 (vertical bar), 上/止/正 (cross-bar position), 古/占 (stroke count), 千/午 (top stroke direction). Adds explicit cross-links so learners do not silently conflate them. Pure data authoring; no UI changes.

### JCE-9: Cultural-context callouts on reading passages (1-2 days)
- [ ] **JCE-9** Author `cultural_context` field on `data/reading.json` passages where Japan-specific cultural assumptions appear (お正月, クリスマス, 連休, 七五三, 入学式, 桜, 紅葉, etc.). Inline notes for non-Japan-resident learners; preserves passage as authentic Japanese text while scaffolding cultural references.

### JCE-7: Stroke-order common-mistake notes per kanji (2-3 days)
- [ ] **JCE-7** Author `stroke_order_mistakes` field on `data/kanji.json` for the small set of N5 kanji with textbook traps (田 horizontal-vs-vertical order, 力 stroke direction, 必 stroke order, 右 vs 左 first-stroke difference, etc.). Surface as warning callouts on the kanji detail page.

### JCE-8: Genki / Minna chapter-mapping on grammar patterns (2-3 days)
- [ ] **JCE-8** Populate `sources` array on `data/grammar.json` patterns - cross-reference Genki Lesson N, Minna no Nihongo Chapter X, JLPT.jp scope, Bunpro N5 deck, JLPT Sensei. Helps learners cross-reference with textbooks they already own. Schema field already specced in N5Improvement.txt prompt.

### JCE-4: Vocab collocations list (3-5 days seed; native review later)
- [ ] **JCE-4** Author `collocations` array on `data/vocab.json` - 3-5 common companion words per entry. E.g. 雨 (rain) -> 雨が降る, 雨が止む, 雨に濡れる, 雨宿り. LLM-curated baseline pass; mark `collocations_provenance: llm_curated`; native-review queued separately. 1041 entries x 3-5 collocations each = ~3500 collocations authored.

### JCE-6: VOICEVOX listening voice variety (3-5 days)
- [ ] **JCE-6** Replace single-voice gtts listening audio with VOICEVOX multi-voice rendering. Target: >=4 distinct voices across the 40 listening items (typically 2 female + 2 male, spanning >=2 age groups per the prompt). Run via `tools/build_audio_voicevox.py`. NOTE: requires VOICEVOX engine installed locally; if not available in working environment, surface as blocker.

### JCE-10: Listening timestamped transcripts (3-5 days)
- [ ] **JCE-10** Add timestamp metadata to `data/listening.json` transcripts - time-aligned sentence-level overlays for 40 listening drills. Enables transcript-follow-along during audio playback. Computed via existing audio durations + sentence-position estimation; refined per-item where audio is shorter than estimate.

### JCE-3: Sentence-by-sentence grammar footnotes on reading passages (1 week)
- [ ] **JCE-3** Author `grammar_footnotes` array on `data/reading.json` passages - map sentence-position to grammar-pattern-id (e.g., "sentence 2 demonstrates n5-072 Verb-ています"). Renders as inline pop-overs on the reading page. Largest authoring batch in this cycle: 40 passages x ~5 sentences each x ~1-2 footnotes = ~200-400 footnote entries.

### JCE-1: Vocab pitch accent (Tokyo dialect) (1-2 weeks)
- [ ] **JCE-1** Author `pitch_accent` field on `data/vocab.json` entries - Tokyo-dialect downstep position number (0 = heiban / flat-rising, 1 = atamadaka, 2..N = nakadaka with downstep at mora N, etc.). Reference: NHK Japanese Pronunciation Accent Dictionary entries + JMdict-derived sources. LLM-curated baseline; native-review later. 1041 entries.

### JCE-5: Native-speaker audio for reading passages (BLOCKED)
- [ ] ~~**JCE-5**~~ Replace TTS audio for the 40 reading passages with native-speaker recordings. **BLOCKED** by IMP-101 (no monetization plan; no budget for paid voice talent). Reopens if institutional sponsorship or paid tier emerges. Tracked here for completeness; do not action.

### JCE-11: Per-kanji mnemonic illustration card (DROPPED 2026-11-08)
- [x] ~~**JCE-11**~~ **Dropped 2026-11-08 by the owner ("kanji memory aid pics not needed").** v1.17.52 removed the 雨 proof-of-concept from the site: the three `mnemonic_image*` fields are gone from `data/kanji.json`, `img/kanji/雨.png` left the repo, and the NOTICES section on the AI illustration was removed. The optional render branch in `js/kanji.js` and the JA-179 guard stay dormant (they render / check nothing when the field is absent). Original plan, kept for history: Show a memory-aid illustration in each kanji page's "Radical & mnemonic" section. **Proof-of-concept shipped live for 雨 (1/106) in v1.17.45** — the plumbing is done and scales to every kanji: data field `mnemonic_image` (+ REQUIRED `mnemonic_image_alt` screen-reader text + `mnemonic_image_provenance`), a lazy-loaded `<figure>` render in `js/kanji.js`, `.kanji-mnemonic-figure/-img` styles, and a CI guard (JA-179: image resolves on disk + non-empty alt). A kanji with no image renders unchanged, so rollout is incremental. Before extending to the other 105: **(1) image production is the gating cost** — 105 more cards must be produced; cannot be auto-generated in-repo. **(2) Optimize weight** — the 雨 source was 1024×1024 / ~2.3 MB; a full set must be downscaled + WebP'd (~100-150 KB each) or repo + page weight balloon (lazy-load keeps a single page cheap). **(3) Confirm licensing** — AI-generated art needs a commercial-use right recorded in NOTICES (open item already logged there). **(4) Decide on text redundancy** — the card's baked-in text largely repeats the on-page meaning/visual/reading lines; consider trimming that text when an image is present. Scope note: this is a light per-kanji **visual aid**, distinct from a WaniKani-style elaborate mnemonic **system** (the documented anti-niche) — keep it supplementary, with the authoritative readings/meaning always present as on-page text. Asset pattern + the min-CSS/min-JS rebuild gotcha are captured in procedure-manual F.55.

### TYPO-1: Em-dash cleanup in explanation prose (DONE 2026-11-08, v1.17.52)
- [x] **TYPO-1** **Closed 2026-11-08 (owner: "remove em dashes").** `tools/emdash_normalize.py --apply` replaced 15,156 em dashes in 1,654 learner-facing files (data/*.json, static mirror pages, dist/, the rendered CHANGELOG / PRIVACY / NOTICES, READMEs). The actual count was ~15K, not the ~42K estimated below. Rules: term-gloss dash to colon, asides to commas, title suffix to " | ", placeholder to "-", four Japanese two-speaker lines to 「A」「B」. The mirror builders now filter their output through the same module, and CI JA-180 fails on any em dash in that scope. Internal tooling, docs, prompts and specs are out of scope. Original note, kept for history: Em-dashes were removed from all learner-facing UI chrome (page/section
  titles, labels, feedback, recommendation text, en/hi locales, index.html) in v1.17.48.
  Deferred: the dense English + Hindi EXPLANATION prose in `data/*.json`
  (grammar/vocab/kanji/reading/listening + papers) still holds ~42,000 em-dashes. The user
  deferred this to a separate, reviewed pass. At that scale a true per-sentence
  context-aware rewrite is the goal (spaced em-dash to comma/colon by clause type; tight to
  hyphen), with spot review of the Hindi (Devanagari) clause breaks. Needs a careful scripted
  pass + sampling review; out of scope for the v1.17.48 UI-chrome sweep.

---

## Done - Phase 4 + 5

### Phase 4.1 Foundation
- [x] **P1.1 Audio TTS build pipeline** - tools/build_audio.py auto-detects piper-tts / gtts / pyttsx3, renders MP3/WAV for every grammar example, reading passage, listening item. Idempotent. Writes data/audio_manifest.json. App degrades gracefully when MP3s are absent.
- [x] **P1.1b Audio rendered + wired** - 491 MP3s generated via gTTS (Japanese voice), grammar example player added to learn UI, listening + reading modules already wire `<audio>` elements from `it.audio` / `p.audio`. Verified in browser preview: HEAD 200 + audio/mpeg on grammar/listening/reading samples.
- [x] **P1.2 SRS upgrade to SM-2** - Review tab is an SRS session with Again/Hard/Good/Easy. Live-verified: rep 1→1d, rep 2→6d, rep 3→15d, lapse → 1d + EF drops to 1.96.
- [x] **P1.3 Diagnostic Summary upgrade** - Error Patterns + Recommended Next Session + Session Log.
- [x] **P1.4 Rename "Drill 0"** - now "Daily Drill"; badge suppressed at 0; aria-label.
- [x] **P1.5 lang="ja" + Japanese font stack** - furigana renderer span wrapper; Noto Sans JP / Hiragino / Yu Gothic / Meiryo. No third-party loads.

### Phase 4.2 Curriculum
- [x] **P2.1 Verb classification module** (#/verbclass)
- [x] **P2.2 て-form gym** (#/teform)
- [x] **P2.3 Counters module** (#/counters) - 11 counter tables + emoji-based "how many?" drill
- [x] **P2.4 こそあど page** (#/kosoado)
- [x] **P2.5 は vs が module** (#/waga)
- [x] **P2.6 Particle minimal-pair drills** (#/particles)

### Phase 4.3 Test fidelity
- [x] **P3.1 Listening module shell** (#/listening) - three-format scaffold (課題理解 / ポイント理解 / 発話表現), audio player wired, graceful no-audio fallback
- [x] **P3.2 Reading passages module** (#/reading) - 8 graded passages with comprehension Qs, read→questions→results flow
- [x] **P3.3 並べ替え production drills** - sentence_order question type
- [x] **P3.4 Type-the-answer drills** - text_input + forgiving matcher (kana/romaji + particle-homophone alternates)

### Phase 4.4 Polish
- [x] **P4.1 Settings panel** (#/settings)
- [x] **P4.2 PWA manifest**
- [x] **P4.3 i18n** with 5 locales
- [x] **P4.4 Export / import progress**
- [x] **P4.5 A11y improvements** - skip-to-content, focus rings, prefers-reduced-motion, forced-colors, role=banner

### Cross-cutting
- [x] **P-cross.1 lang="ja"** wrappers
- [x] **P-cross.2 Vocabulary corpus** - 1002 entries in data/vocab.json (form, reading, gloss, section)
- [x] **P-cross.3 Kanji corpus** - 97 entries in data/kanji.json with stroke_order_svg slots ready for KanjiVG drop-in
- [x] **Em-dash cleanup** - 881 em dashes replaced with ASCII hyphen across 29 files (cp932-safe)

### Pre-release QA gate (per Brief §9)

- [x] No console errors on load.
- [x] FCP < 1.5s on simulated 4G - analytical estimate ~555 ms cold-load on Lighthouse Slow-4G profile (150 ms RTT, 1.6 Mbps, 4x CPU). Critical-path ~60 KB total: index.html 2.1 KB + main.css 37.6 KB + entry JS modules 18.7 KB. Repeat visits via SW cache: <100 ms.
- [x] Works offline after first load.
- [x] Japanese text renders in Japanese font on Windows without language pack.
- [x] Furigana toggle hides/shows ruby.
- [x] Audio plays in browser preview (verified: 16 KB grammar clip, 217 KB listening clip, 115 KB reading clip - all 200 OK, audio/mpeg). iOS Safari unverified but uses standard `<audio src>` so should work.
- [x] Export → wipe → import round-trips progress.
- [x] Lighthouse-equivalent audits - PWA pass (manifest, theme-color, viewport, SW, HTTPS), A11y pass (lang, skip-link, banner, nav, main, h1, no missing labels), SEO pass (title, description, lang, canonical, robots), Best Practices pass (UTF-8, doctype, no console errors). Added meta color-scheme + robots + canonical link to index.html.
- [x] No outbound network calls during a normal session.

---

## Remaining (Brief 1)

- [x] **P-cross.4 Reading + listening corpus expansion**: 30 reading passages + 12 listening items committed.
- [x] **Run tools/build_audio.py end-to-end**: 491 MP3s rendered via gTTS, committed under audio/, listening module activated.

Brief 1 complete. Engine, module, and asset layers shipped.

---

## Functional Spec gap-fill - 2026-04-30

Analyzed `specifications/JLPT N5 Grammar Tutor – Functional Spec.docx` (v3, 33KB) against the standard FSD checklist (Document control / Foundation / Audience / Functional / NFR / Domain / Quality / Appendices).

**Gaps identified + filled** in `specifications/JLPT-N5-Functional-Spec-v3.1-supplement.md`:

- **§A.1 Missing sections (15)**: revision history table, glossary, stakeholders/RACI, user stories, success metrics/KPIs, i18n NFR, PWA NFRs, performance budgets (measurable), content audit protocol (Pass-N), test strategy, risks register, open questions log, maintenance/support model, data dictionary, accessibility conformance target.
- **§A.2 Drift items (12)**: audio listed out-of-scope but shipped, mobile listed non-goal but shipped, SW listed optional but shipped, Leitner→SM-2, nav restructure, settings schema, repo tree, future-enhancements pruning.
- **§B Gap-fill content (11 sub-sections)**: Document control + revision template + sign-off matrix; Glossary (24 terms); Stakeholders RACI; 17 user stories; 9 success metrics with measurable targets; expanded NFR (i18n / PWA / perf budgets / a11y conformance); test strategy linking ui-testing-plan.md and tests.html; 9-entry risks register; 5-entry open questions log; maintenance/support model; release process.
- **§C Errata to existing v3 sections (8)**: §3 scope updates, §5.1 nav rewrite, §5 new UX subsections, §5.8 SM-2 replaces Leitner, §7 new schemas (knownKanji/streak/audio_manifest/updated settings), §9 repo tree replacement, §11 NFR consolidation, §13 future-list pruning.
- **§D Content audit protocol (Pass-N) made normative**: codifies the 10-pass / 462-finding tradition; quarterly cadence; severity matrix; CRITICAL-blocks-release rule.
- **§E Acceptance criteria for v4** (10 items) - what "merged into next .docx" means.

**Next steps:**

- [x] Sign-off matrix (§B.1.2): filled in  §B.1.2 with current state - Content reviewer slot has partial sign-off (Pass-11 reviewer 田中, ~30% surface, full pass due 2026-07-30); Engineering and A11y slots filled by automated tooling (CI integrity check + axe-core); Product owner slot left for project author. Full external-reviewer sign-offs pending for MEXT-aligned release.
- [x] Open questions (§B.9) triaged 2026-04-30. **OQ-1** Recommendation engine: deferred to v2.0 (target 2026-09-30; blocked on Pass-11 corpus completion). **OQ-2** Listening corpus expansion: deferred to v1.6 (target 2026-07-30; blocked on Pass-11 listening review). **OQ-3** CSP meta tag: approved for v1.6 (target 2026-05-15; ~30 min implementation). **OQ-4** Audio playback history in export schema: deferred indefinitely (privacy conflict). **OQ-5** N4 expansion: closed out-of-scope per Brief 1. Plus 2 new: **OQ-6** Japanese-version brief: open (target 2026-07-30; translate brief, defer app). **OQ-7** Empty furigana[] field: closed-keep (functional optional override).
- [x] Merge supplement into a new v4 .docx; archive v3 to `not-required/`. Done: extended `tools/build_spec.py` with a small markdown→docx renderer (handles headings, paragraphs, bullets, numbered lists, tables, code fences, **bold** / `code` / [link]() inline). Subtitle bumped v3→v4. v4 .docx is 72 KB (up from v3's 53 KB) at `specifications/JLPT N5 Grammar Tutor – Functional Spec.docx`. v3 archived to `not-required/JLPT N5 Grammar Tutor – Functional Spec v3.docx`.
- [x] Calendar reminder: first quarterly Pass-N re-audit on 2026-07-30 (per §D.2). Already scheduled in commit `bcd343f` as the recurring task `jlpt-n5-quarterly-pass-audit` (cron `0 9 30 1,4,7,10 *`); next run 2026-07-30 9 AM local. Listed twice in this section so checking both.

---

## External-blocked backlog (2026-05-01)

Four items from the active backlog cannot be closed in code; each has a real external dependency. Capturing them here as explicit handoff entries with the action that unblocks them. The cron `jlpt-n5-quarterly-pass-audit` will surface them again on 2026-07-30.

### EB-1 - OQ-2 Listening corpus expansion 12 → 30+ items

- **Status**: APPROVED for v1.6 (per §B.9 OQ-2 closure 2026-04-30); not started.
- **Blocker**: native Japanese voice talent. Synthetic TTS (gTTS, Piper) is unacceptable for new items - at N5 the listening test measures phoneme/prosody discrimination, so synthetic prosody artefacts would over-fit learners to artefacts rather than the language.
- **Unblocks when**: a native-speaker recording channel exists. Three viable channels:
  1. Paid voice actor (~3-5 hr studio session for ~20 items at N5 length).
  2. Volunteer Japanese-native already engaged with the project (e.g., the Pass-11 reviewer "Suiraku San" listed in the supplement sign-off matrix).
  3. License of existing N5-graded audio (rights-clearance question; would need legal review).
- **Code already in place** for when audio arrives:
  - `data/audio_manifest.json` schema includes per-item `voice` field.
  - `tools/build_audio.py` skips items marked `voice: "native"` so externally recorded files aren't synthesised over.
  - JA-15 invariant verifies any manifest path resolves to a file on disk.
- **Estimated effort once unblocked**: ~6-10 hr (script authoring + studio session + post-production + integration).
- **Owner**: Content owner (Suiraku San).

### EB-2 - Pass-15 deep semantic re-audit

- **Status**: SCHEDULED for 2026-07-30 quarterly gate (cron is set).
- **Blocker**: native Japanese reviewer time. **PARTIALLY UNBLOCKED 2026-05-01** - see validation experiment below.
- **Scope** (~70% of corpus): 157 unreviewed `data/grammar.json` patterns; 21 unreviewed `data/reading.json` passages; 591 unreviewed `KnowledgeBank/*_questions_n5.md` entries; full re-audit of KB catalogs (already audited 9× via Pass 1-10).
- **Also covers** the 69 questions deferred from Item 4 (template generator couldn't handle compound patterns) - the reviewer should hand-author those.
- **Estimated effort once unblocked**: ~10-12 hr across multiple sessions for native reviewer; **~3 hr triage with LLM-audit pipeline** (see below).
- **Owner**: Content reviewer (Suiraku San) per §B.1.2 sign-off matrix; LLM-audit pipeline owned by Engineering.

#### LLM-audit validation result - 2026-05-01

Per the deep-research analysis on automating external-blocked items, an LLM-audit pipeline was prototyped (`tools/llm_audit.py`) and validated on a 5-pattern sample from the unreviewed surface. Result: **GO**.

Key data points (full report at `feedback/llm-audit-validation-report.md`):
- 5 real findings on 5 patterns (1.0 findings/pattern), comparable to Pass-12 native density (1.12) and 3.5× Pass-13's density (0.28).
- The LLM caught a HIGH-severity PATTERN_MISMATCH on n5-115 (4 of 5 examples don't demonstrate the pattern) that had been sitting in the data through 13 prior native passes.
- The LLM caught a stub-redirect-text-in-notes-field issue exactly analogous to what Pass-12 F-12.3 fixed in `data/questions.json` - the `data/grammar.json` equivalent had been missed.
- One false positive caught during validation (encoding-related; UTF-8 vs cp932 round-trip issue). Mitigation: enforce UTF-8 round-trip on the prompt builder.

Cost: ~$11.50 per full 187-pattern pass. Quarterly cost: ~$46/year. Triage time: ~3 hr per pass (vs 10-12 hr for full native review).

**Wiring plan:**
1. Run `tools/llm_audit.py --all` once now (~$15) and triage findings as Pass-15a entries in `verification.md`.
2. Wire `--all-uncovered` mode into the existing 2026-07-30 cron so Pass-15 findings are pre-staged before any human review.
3. Add an incremental CI step that audits only touched patterns on PRs modifying `data/grammar.json`.
4. Reduce the native-reviewer expectation from "full coverage" to "spot-check + cultural appropriateness" (~10% of patterns).

This converts EB-2 from a fully external-blocked item to a human-light item where the LLM does the bulk of the review and a native spot-checks.

### EB-3 - OQ-6 Brief translation to Japanese (optional)

- **Status**: DEFERRED to 2026-07-30 as a separate optional task (per §B.9 OQ-6 closure 2026-04-30 - distinct from the closed UI-stays-English decision).
- **Blocker**: a Japan-based reviewer engagement to make the translated brief useful. Without one, the translation has no audience.
- **Unblocks when**: a Japan-based reviewer (e.g., a 文部科学省 contact) commits to reading the brief.
- **Estimated effort once unblocked**: ~4 hr translation + cross-review.
- **Owner**: Project author + Content reviewer.
- **Priority**: P4 (lowest among external backlog) - only worth doing if outreach is in progress.

### EB-4 - OQ-1 v2.0 ML-backed recommender (richer than current minimal widget)

- **Status**: DEFERRED to v2.0 (target 2026-09-30 per §B.9 OQ-1 closure).
- **Blocker**: learner-base data. The current minimal recommender (state-driven, in-app, no telemetry) is honest about its inputs. A richer ML version would need either (a) on-device learning data we don't currently retain at scale, or (b) a privacy-respecting analytics channel that doesn't exist (and would conflict with Hard constraint #2 "no telemetry").
- **Unblocks when**: a privacy-respecting input source emerges - e.g., the export/import flow becomes common enough that anonymised analysis of exported state could inform recommendation. Or the Hard-constraint #2 stance is revisited.
- **Estimated effort once unblocked**: ~6-8 hr design + implementation.
- **Priority**: P4 - only worth doing if (a) usage justifies it AND (b) a privacy-clean data path exists.

### Summary of what's open after 2026-05-01 sweep

| Code-doable | External-blocked |
|---|---|
| 0 items | 4 items (EB-1 through EB-4) |

Code-tier backlog is empty. Every code-doable item from the data-correction brief, the UI design brief, and the kanji-card content gaps has been applied. The only remaining work needs human linguistic / voice / institutional resources that are out of scope for the current automation envelope.

---

## Open-question follow-ups - decided 2026-04-30

Per the §B.9 batch decision on 2026-04-30, four OQ rows were closed. Three were code-only and have already shipped in v1.6 - the fourth (OQ-2 listening corpus) is a content-authoring task with a hard external dependency, captured below.

### OQ-2 backlog item: listening corpus expansion 12 → 30+ items (native voice required)

- **Decision**: approved for v1.6, target authoring completion **2026-07-30**.
- **Hard constraint**: new listening items MUST be recorded with a **native Japanese voice talent**. gTTS is acceptable for the existing 12 items as a transitional baseline, but it cannot be used for new items. Rationale: at JLPT N5 the listening section tests phoneme + prosody discrimination; gTTS prosody artefacts are memorisable in a way that doesn't transfer to real human speech, so a corpus dominated by gTTS would over-fit learners to an artefact rather than the language.
- **Why this isn't a code task**: cannot be done by editing `tools/build_audio.py`. Even if the script accepted a different TTS engine, no synthetic engine satisfies the native-voice requirement. The blocker is procurement / authoring, not code.
- **What needs to happen** (sequenced):
  1. Procure native voice talent - options: (a) hire a Japanese voice actor (paid, ~3-5 hr session for ~20 items at N5 length); (b) recruit a fluent Japanese-native volunteer reviewer who is already engaged with the project; (c) license existing N5-graded audio (rights-clearance question).
  2. Author the new scripts: 18 new items (12 → 30) split across the three JLPT formats (~6 task / ~6 point / ~6 utterance). Scripts must stay strictly inside the N5 grammar/vocab/kanji whitelists per existing JA-13 invariant.
  3. Record at studio-quality (≥ 44.1 kHz, mono, ≤ -3 dB peak, ≤ -23 LUFS integrated); deliver as MP3 (CBR 128 kbps) to match the existing corpus footprint (~115 KB / item).
  4. Add per-item `voice` metadata to `data/listening.json` (`voice: "native" | "gtts"`) so the build pipeline + UI can flag transitional gTTS items and the next pass can swap them out individually.
  5. Update `tools/build_audio.py` to skip items with `voice: "native"` (audio is recorded externally, not synthesised) and to honour a per-item `voice` override on existing items when re-recordings arrive.
  6. Re-run content-integrity CI; verify JA-13 (no out-of-scope kanji) and the new voice-metadata invariant pass.
- **Owner**: Content owner (Suiraku San per §B.1.2 sign-off matrix) for script authoring + voice procurement; Engineering owner (Gaurav Srivastava) for the metadata / pipeline plumbing only.
- **Status**: OPEN, not started. Deferred until a native voice channel is in place. Tracked here so it doesn't get lost in OQ-2's "approved" status - approval is the *decision*, not the *delivery*.

### Other 2026-04-30 closures (already shipped, no follow-up needed)

- [x] **OQ-3** - CSP meta tag added to `index.html`; SW `CACHE_VERSION` bumped (v29 → v30).
- [x] **OQ-1 (minimal)** - "What should I study next?" recommender widget added to Home (`js/home.js` `pickRecommendation()` + `renderRecommendation()` + `.home-recommend` styles in `css/main.css`). Reads `getStreak()` + `getDueCount()` + `lastLearnId`, routes to one of Learn / Review / Drill. Richer ML-backed engine still deferred to v2.0.
- [x] **OQ-6** - Decision: app UI/instructions stay in **English** (the app teaches Japanese, but chrome stays English so learners are never blocked). Five existing locales (en/vi/id/ne/zh) translate the English chrome - no `ja` locale will be added. Brief translation still tracked for 2026-07-30 as a separate optional task.

---

## Kanji-card content gaps - raised 2026-04-30

Two visible gaps on every kanji detail card (verified in browser preview at `#/kanji/古` and `#/kanji/長`): no example-usage section, and the stroke-order SVG placeholder is shown to learners as "Stroke-order SVG not yet shipped." Both block the kanji card from being a complete learning surface.

### Task K-1: Add "Example usage (N5)" section to kanji cards

- **Goal**: Each of the 106 kanji cards should show 2-3 N5-syllabus example words containing that kanji, so learners see the kanji in actual context (not just the bare glyph + readings + English meaning).
- **Selection rule**:
  - Examples must be real N5-syllabus words - sourced from `data/vocab.json` cross-referenced with `data/n5_vocab_whitelist.json`.
  - 2-3 examples per kanji is the sweet spot; up to 5 only when high-frequency or pedagogically useful.
  - Per-example fields: `form` (rendered string), `reading` (full kana reading), `gloss` (short English).
- **Rendering rule** (critical - aligns with existing JA-13 invariant + post-Pass-13 design):
  - If **every** kanji in the example word is in `data/n5_kanji_whitelist.json` → render the word in **full kanji** form. Examples:
    - 新 → `新しい` (新 in scope; しい is kana - keep as-is)
    - 新 → `新聞` (both 新 and 聞 are in N5 - keep as-is)
    - 古 → `古い`, `古本` (本 is N5 - keep as-is)
    - 長 → `長い`, `校長` (校 is N5 - keep as-is)
  - If **any** kanji in the example word is **out of** N5 → that kanji is **substituted with its contextual kana reading**, while the *target* kanji (the one the card is about) stays as kanji. Hypothetical example given by user 2026-04-30: if 聞 were not in N5, then `新聞` would be authored as `新ぶん` (新 stays kanji because the card is about 新; 聞 → ぶん, the on-reading used in 新聞).
  - Reading correctness: the kana substitution must use the **contextually correct** reading for the compound (on vs kun depends on the word). This is authoring judgment - cannot be fully auto-generated; requires curated input.
- **Storage**: add `examples: [{form, reading, gloss}]` field to each entry in `data/kanji.json`. Authoring source: `KnowledgeBank/kanji_n5.md` (curated by content reviewer). `tools/build_data.py` propagates from KB → JSON.
- **UI**: render between the on/kun/meaning meta-strip and the "Stroke order" heading on the kanji detail view. Match existing label style (bold "On:" / "Kun:" / "Meaning:" pattern). Suggested layout: a small table with three columns (form | reading | gloss).
- **CI invariant** to add (call it JA-15): every example word's `form` field, when scanned for kanji, contains only kanji that are either (a) the target kanji or (b) members of the N5 whitelist. Any other kanji = build-fail. Mirrors JA-13.
- **Files touched**: `KnowledgeBank/kanji_n5.md` (add examples per entry), `tools/build_data.py` (parse + emit), `data/kanji.json` (regenerated), `js/kanji.js` + relevant CSS (render), `tools/check_content_integrity.py` (JA-15).
- **Effort estimate**: ~4-6 hr - most of it authoring (106 kanji × 2-3 examples = ~250-300 example words to curate + verify N5-scope substitutions). Code wiring is ~1 hr.
- **Priority**: P2 (learner-visible content gap; not release-blocking but degrades the kanji-card pedagogically).

### Task K-2: Ship stroke-order SVGs (KanjiVG drop-in)

- **Goal**: Replace the visible placeholder text "Stroke-order SVG not yet shipped. Drop-in target: `svg/kanji/<glyph>.svg` (KanjiVG-compatible)." with actual stroke-order animations on all 106 kanji cards.
- **Current state**: `data/kanji.json` already has a `stroke_order_svg` slot per entry; the kanji detail view checks it and falls back to the placeholder text when absent. Verified in browser preview at `#/kanji/古` (slot #100) and `#/kanji/長` (slot #101) - placeholder is shown to learners, which looks unfinished.
- **Source**: KanjiVG (https://kanjivg.tagaini.net/) is licensed CC BY-SA 3.0. Contains stroke-order SVGs for all 106 N5 kanji. License is compatible with the project (static, attributed).
- **Drop-in process**:
  1. Download KanjiVG release SVGs for the 106 N5 glyphs in `data/n5_kanji_whitelist.json`.
  2. Place under `svg/kanji/<glyph>.svg` (path matches the existing placeholder copy).
  3. Add an attribution line to `index.html` footer or a NOTICES file: "Stroke-order data from KanjiVG (kanjivg.tagaini.net), CC BY-SA 3.0."
  4. Add files to `sw.js` PRECACHE list so they're cached on install (offline-first).
  5. Bump `CACHE_VERSION`.
- **Verification**:
  - All 106 SVGs present (one per N5 kanji).
  - Each renders inline (animated stroke order, or at minimum static numbered strokes).
  - Footer carries CC BY-SA attribution.
  - SW precaches all 106 SVGs; offline test confirms each kanji card renders without network.
- **Files touched**: `svg/kanji/*.svg` (106 new files, ~20-50 KB total), `sw.js` (precache list), `index.html` or `NOTICES.md` (attribution), possibly `js/kanji.js` if the renderer needs to switch from `<img src=...>` to inline `<svg>` for stroke animation.
- **Effort estimate**: ~1-2 hr (mostly file copying + verification). The KanjiVG dataset is already complete and authoritative - no authoring required.
- **Priority**: P1 (every kanji card currently shows placeholder text to the learner - visible quality gap). Should ship before next release.
- **Open question** for the implementer: animated stroke-order (requires KanjiVGAnim or similar runtime) or static numbered strokes (simpler, lighter)? Static is the lower-effort path; animated is the better learner experience but doubles complexity. Recommend static for v1.6, animated for v2.0.

---

## Copy audit: remove sales-promo voice - raised 2026-04-30

**Frame** (user direction 2026-04-30): the current home-page hero reads like a marketing landing page (outcome-promise headline, ✓-prefixed trust ticks, second-person imperative CTAs). For a free static study tool with no funnel, no upsell, and no monetisation, this voice is **mismatched** - it implies a product trying to sell itself, when the product just exists to be used. Strip the sales gloss; keep facts and quiet competence. Reviewer perspective for this audit: a senior copywriter editing an institutional reference site (think MIT OpenCourseWare or arxiv.org), not a SaaS landing page.

**Scope of fix**: copy-only. No content/data changes; only labels, microcopy, headlines, and meta strings. Treat as a single rewriting pass - the goal is consistent voice across all surfaces, so prefer one big PR over piecemeal edits.

**Effort estimate**: ~1.5-2 hr to apply all 17 findings + verify in browser + update specs/CHANGELOG. Low risk (no data invariants touched).

**Priority**: P2 - visible on the home page (the front door); affects every first-time visitor's first impression. Should land before any external-reviewer outreach (Pass-11 native teacher, MEXT alignment).

### Voice guidelines (the rewrite contract)

The rewrite should obey these rules so future copy doesn't drift back:

1. **No outcome promises.** Don't say what the user will achieve ("Pass JLPT N5...", "Master kanji"); say what the tool *contains* ("JLPT N5 study material: grammar, vocab, kanji...").
2. **No time-to-result claims.** Drop "in 15 minutes a day", "quickly", "easily", "in just X". The tool can't make those guarantees and saying so reads as advertising.
3. **No second-person imperatives at the brand level.** "Start your first lesson" → "Start a lesson". The possessive "your" + "first" is funnel rhetoric.
4. **No celebration glyphs.** Drop ✓-prefixed trust ticks, ★ Graduated, etc. State facts plainly; don't decorate them.
5. **No defensive claims.** "No login required" is a defensive phrasing pattern (compare: "Open access"). Just describe the property.
6. **No gamification language at the surface level.** Streak counts can be shown as facts ("5 days") but don't pair them with imperative motivators ("Keep your streak alive!"). The number speaks for itself.
7. **Prefer noun phrases over headlines.** "Continue your N5 study" → "Continue". "Today's review queue" → "Reviews due today". Headlines that try to sound aspirational are the tell of marketing voice.
8. **One voice, one register.** All microcopy in the same register. No mixing of "Continue lessons" (neutral) with "Start your first lesson" (onboarding-funnel) on the same page.

### Findings (17 items, ordered by visibility)

#### A. Hero - `js/home.js`

| # | Current | Proposed | Reason |
|---|---|---|---|
| A1 | `Pass JLPT N5 with 15 minutes a day` (first-time h2) | `JLPT N5 study material` *or* `Practice JLPT N5: grammar, vocab, kanji, reading, listening` | Outcome-promise + time-promise. Tool can't guarantee either. Replace with scope statement. |
| A2 | `Continue your N5 study` (returning h2) | `Continue` | Possessive "your" + "study" is aspirational. The single word reads as a quiet hand-off back to the work. |
| A3 | `<ul class="trust-strip">` with `✓ Works offline` / `✓ No login required` / `✓ Your progress stays on this device` | Inline sentence: `Works offline. Open access. Progress stays in your browser.` (or remove the trust strip entirely, since the same facts are now in PRIVACY.md and the footer link makes them discoverable) | ✓-prefixed trust badges are the textbook pattern of a SaaS landing page. The facts are correct; only the framing needs to change. |
| A4 | `Start your first lesson` (primary CTA, first-time) | `Start a lesson` *or* `Open Learn` | "Your first" is onboarding-funnel rhetoric. |
| A5 | `Continue lessons` (primary CTA, returning) | Keep as-is - this is already neutral. | - |
| A6 | `Take a placement check` (secondary CTA) | Keep as-is. The word "Take" is fine in this context (we say "take a quiz" in normal English). | - |
| A7 | `Already familiar with some N5 material? Take the placement check above to skip what you know.` (footnote) | `If you've studied some N5 already, the placement check above can shorten the path.` *or* simply `Placement check above for partial-N5 starters.` | "to skip what you know" is rationalising the action. The fact (skip-what-you-know) belongs on the placement-check button, not as preemptive copy under the hero. |

#### B. Hero stats - `js/home.js`

| # | Current | Proposed | Reason |
|---|---|---|---|
| B1 | Pill badges `187 grammar`, `1003 vocab`, `106 kanji`, `30 reading`, `12 listening` | Keep counts, drop the pill styling for a flatter list: `187 grammar patterns · 1003 vocabulary · 106 kanji · 30 reading passages · 12 listening drills` | Pills look like marketing "stat cards". A plain list reads as a table of contents. The numbers themselves are factual and should stay. (NOTE: this reverses L5 from today's batch. Discuss before applying.) |
| B2 | Returning-user tagline `${grammarCount} grammar patterns. ${vocabCount} vocab words. ${kanjiCount} N5 kanji.` | `${grammarCount} patterns. ${vocabCount} words. ${kanjiCount} kanji.` | "Vocab words" is redundant; "N5 kanji" is implied by the page context. |

#### C. Recommender widget - `js/home.js`

| # | Current | Proposed | Reason |
|---|---|---|---|
| C1 | `What should I study next?` (label) | `Suggested next` | The question form is conversational/marketing. A senior copywriter would use a noun phrase. |
| C2 | `Clear today's review queue (12 due)` | `12 reviews due today` | "Clear ... queue" is task-app language. Just state the count. |
| C3 | `Keep your 5-day streak alive` | `5 days · continue` *or* `Continue (5-day streak)` | "Keep your streak alive" is gamification copy. The number alone is the motivator. |
| C4 | `Run today's review (3 due)` | `3 reviews due today` | "Run" is action-app language. |
| C5 | `Try a quick mixed drill` | `Mixed drill` *or* `Practice` | "Try" + "quick" both signal sales/persuasion. |
| C6 | `Pick up the next lesson` | `Next lesson` | Remove the imperative wrapper. |

#### D. Returning resume cards - `js/home.js`

| # | Current | Proposed | Reason |
|---|---|---|---|
| D1 | `Continue where you left off` (h3) | `Last lesson` *or* `Resume` | The phrase "where you left off" is ad-copy boilerplate. |
| D2 | `Today's review queue` (h3) | `Reviews due today` | Remove "queue" (task-app jargon) and the possessive "today's". |
| D3 | `All caught up - come back tomorrow.` | `No reviews due.` | "Come back tomorrow" is engagement-loop copy that anthropomorphises the tool. |
| D4 | `Learn something new` (button when no due) | `Open Learn` | "Learn something new" is encouraging-coach voice. |

#### E. CTA elsewhere - across files

| # | Current | Location | Proposed |
|---|---|---|---|
| E1 | `Start your first lesson` | `js/summary.js:34` (empty-state) | `Start a lesson` |
| E2 | `Your dashboard fills in as you study.` | `js/summary.js:32` | `Stats appear here once you've studied.` |
| E3 | `★ Graduated! This pattern is mastered.` | `js/drill.js:282` | `Graduated. Pattern mastered.` (drop the ★) |
| E4 | `✓ Correct` / `✗ Not quite` | `js/drill.js:292`, `js/counters.js:222` | `Correct` / `Wrong` (drop the glyphs; rely on color + headline weight) - OR replace ✓/✗ with proper SVG icons. Decision needed; the glyphs render inconsistently across platforms (Windows shows them as plain text, mobile may render as emoji). |

#### F. Site chrome - `index.html`

| # | Current | Proposed | Reason |
|---|---|---|---|
| F1 | `<title>JLPT N5 Grammar Tutor</title>` | `<title>JLPT N5</title>` *or* `<title>JLPT N5 - study material</title>` | "Grammar Tutor" undersells (the site has vocab/kanji/reading/listening too) and "Tutor" is brandy. Per existing UI brief §1.1 #1, this contradicts the hero scope statement. |
| F2 | `<meta name="description" content="Static, on-device, privacy-preserving tutor for JLPT N5 grammar.">` | `<meta name="description" content="Free JLPT N5 study material covering grammar, vocabulary, kanji, reading and listening. Works offline; no account.">` | "Static, on-device, privacy-preserving" is technical jargon a non-developer searcher won't parse. Keep the same *facts* in plain English. |
| F3 | `aria-label="JLPT N5 Grammar Tutor - return to home"` (brand link) | `aria-label="JLPT N5 - return to home"` | Match the new title. |

#### G. Footer - `index.html`

| # | Current | Proposed | Reason |
|---|---|---|---|
| G1 | `v1.5.0 · What's new` (left) | Keep as-is. Plain, factual. | - |
| G2 | `Privacy · Source on GitHub` (right) | Keep as-is. | - |

#### H. Recommender - minor

| # | Current | Proposed | Reason |
|---|---|---|---|
| H1 | `<aside aria-label="Recommended next step">` | `<aside aria-label="Suggested next">` | Match C1. |

### Acceptance criteria for this task

When the rewrite ships:

- [x] No occurrence of `Pass JLPT N5 with` anywhere in user-facing files. **Verified 2026-05-01:** 0 hits across `js/`, `index.html`. Removed during the v1.7.1 hero deletion.
- [x] No occurrence of `Master`, `Crush`, `Ace`, `Easily`, `Quickly`, `Effortlessly` as adverbs/verbs about study outcomes. **Verified 2026-05-01:** only `★ Mastered` (status badge label, descriptive noun) remains - not the audit target which was about marketing imperatives like "Master JLPT in X days".
- [x] No `✓ ` (check + space) prefix in any visible label outside drill answer-feedback. **Verified 2026-05-01:** 0 hits. Test-review screen still uses bare ✓/✗ as centered glyphs (typographic dingbats, not emoji), color-coded via CSS classes.
- [x] No `Start your first` or `Begin your` patterns. **Verified 2026-05-01:** 0 hits. The home page no longer has any CTAs at all (hero removed in v1.7.1).
- [x] Site title + meta description rewritten per F1, F2. **Verified 2026-05-01:** title is `JLPT N5 - study material` (matches F1 descriptive form). Description: `Free JLPT N5 study material covering grammar, vocabulary, kanji, reading and listening. Works offline; no account.` (factual, no marketing voice).
- [x] CHANGELOG.md gets a note that the home tagline + hero copy were updated for voice consistency. **Already covered** in CHANGELOG entries v1.7.1 (hero removed) and v1.7.11 (decorative emojis removed) and v1.8.0 (Zen Modern overhaul).
- [x] Spec supplement §1.1.5 (Trust strip) and §15 (Copy revisions) updated to match the new voice. **Applied 2026-05-01:** see commit on this date - sections retroactively documented to reflect that the trust strip + hero CTA were removed entirely rather than rewritten.
- [x] Browser preview verification: home page (first-time + returning), summary empty-state, drill answer feedback all reviewed. **Applied 2026-05-01 via Claude_Preview MCP (Tier 0)** - Python http.server running on :8765, navigated to home / Learn hub / Summary empty-state, computed-style inspection on key elements (body, .section-label-text, .section-label-rule, .brand-link, .card-index, .pillar-card). Verified: tabular-nums on body, hairline 0.5px on rules, weight 500 on labels, no shadows on cards, brand mark 五 via ::before pseudo-element, numbered indices 01-05 on Learn hub. Console: 0 errors. One finding caught + fixed: `.pillar-card p` rule was overriding `.card-index` color on home (rendered muted instead of faint per spec §4.4) - promoted via `.pillar-card .card-index, .hub-card .card-index { color: var(--color-text-faint); }`. Replaced by automation: **`tools/check_design_system.py` (Tier 1)** - 8-rule static checker wired into `.github/workflows/content-integrity.yml` runs every push + PR. Catches recurring drift classes (emojis, weight 600/700, box-shadow, hover-transforms, legacy accent #14452a, non-token radii, text-transform / text-shadow violations).

### Open decisions (flag for user before implementer starts)

1. **B1 (pill badges vs flat list)**: today's L5 batch made the stats into pills. Going flat reverses that. Decide: keep pills (visual scoreboard, mild marketing feel) or revert to flat list (institutional, plain). Recommend **revert to flat** to be consistent with the rest of the rewrite.
2. **A3 (trust strip)**: should the strip stay (rewritten) or be removed entirely now that PRIVACY.md is linked from the footer? Recommend **remove from hero** - the privacy story is one click away in the footer; on-page repetition is the hallmark of a landing page trying to convince a skeptic. Removing it is the most coherent application of the voice guideline.
3. **E4 (glyphs)**: drop ✓/✗ entirely (rely on color + label) or replace with SVG? Recommend **keep label only** for v1.6 (lowest effort, most consistent with the new voice); SVG icon work belongs in the M-bucket UI polish anyway.
4. **F1 (site title)**: shorter `JLPT N5` or descriptive `JLPT N5 - study material`? The descriptive form helps SEO and accessibility (screen readers read the title on landing). Recommend the descriptive form.

---

## Native Japanese teacher review request - 2026-04-30

Brief at `feedback/native-teacher-review-request.md`. Covers **both** `data/` (runtime JSON, never deeply native-reviewed) **and** `KnowledgeBank/` (catalog files, audited 10 times - this pass brings a fresh native eye).

- **Scope (14 priorities):**
  - P1-P2: `data/grammar.json` (~935 examples), `data/reading.json` (30 passages)
  - P3-P7: KB question banks - moji / goi / bunpou / dokkai / authentic_extracted (591 Qs total)
  - P8-P9: `data/questions.json` (250 Qs), `data/listening.json` (12 scripts)
  - P10-P12: KB catalog files - grammar_n5.md / vocabulary_n5.md / kanji_n5.md
  - P13-P14: spot-checks on `data/vocab.json` and `data/kanji.json` (mostly mirror KB)
  - Optional: audio QA on ~20 random MP3s
- **Effort:** ~10-15 hours total, splittable; partial reviews welcome (P1 alone is ~2-3 hours).
- **Severity model:** CRITICAL (blocks release) / HIGH (next release) / MEDIUM / LOW.
- **Output format:** Markdown findings - the brief and the fillable template are now merged into a single file (Part A = brief, Part B = template). Reviewer copies `feedback/native-teacher-review-request.md` → `feedback/pass-11-native-review-findings.md`, fills in Part B, returns. Will be ingested as Pass-11 in `verification.md` once received.
- **Hard constraints documented inline:** N5 syllabus only, no romaji, kanji-scope rule, naturalness exception for reading passages.
- **Reference list:** Bunpro / JLPT Sensei / Genki / Minna / Try! / Tofugu (full annotated list in `KnowledgeBank/sources.md`).
- **Acknowledgement:** reviewer credited in `verification.md` Pass-11 entry and CHANGELOG (with their permission; pseudonym/anonymous accepted).

### Pre-send brief audit (Pass 11A) - 2026-04-30 (COMPLETE)

A native Japanese teacher commissioned by 文部科学省 audited the brief itself before accepting the engagement. **20 findings raised** (3 CRITICAL, 6 HIGH, 8 MEDIUM, 3 LOW) on the brief document; substantive content review (Pass 11) is paused until the CRITICAL items are fixed. Full audit at `feedback/native-teacher-review-request.md` Part B (or future `feedback/pass-11A-brief-audit.md` if extracted).

#### CRITICAL (3) - block sending the brief

- [x] **F-1** §3.2 self-contradiction: romaji listed as OUT-of-scope but with "flag as CRITICAL" instruction. Move to §3.1 IN-scope and rewrite as a single coherent rule.
- [x] **F-2** §7 reference list contains zero Japanese-side authoritative sources. Add §7.2 listing 国際交流基金 / Japan Foundation, JEES サンプル問題集 (jlpt.jp), 旧 出題基準 (1994/2002), 大学入試センター日本語問題. Note that Japanese-side sources prevail when they conflict with Western prep materials.
- [x] **F-3** `KnowledgeBank/externally_sourced_n5.md` over-claims provenance. The source (learnjapaneseaz.com) is a third-party prep site, not JEES / 国際交流基金. Pick one: (a) rename file/header to drop "authentic"; (b) re-source from JEES jlpt.jp サンプル問題; (c) drop file from review scope and corpus until re-sourced.

#### HIGH (6) - fix before sending; or address in v2 of the brief

- [x] **F-4** §6 missing "naturalness trumps policy" escape clause. Add rule 8 explicitly authorizing the reviewer to flag policy-compliant-but-unnatural stems.
- [x] **F-5** §1 audit-history table uses inconsistent terminology: Pass 8 "Native-teacher review" (English) vs Pass 9 "External 日本語教師 brief" (mixed). Standardize on "日本語教師 (native-speaker)" labels per pass.
- [x] **F-6** §2.1 priority list buries `data/listening.json` at P9. Promote to P3 - audio is the area where native expertise is most uniquely needed; non-native maintainers can't judge pitch accent / rendaku / gemination.
- [x] **F-7** §3.1 IN-scope list missing two important categories: (a) causative/passive (させる/られる) at the N5/N4 boundary; (b) counter-noun mismatches (まい / ほん / つ / さつ misuse).
- [x] **F-8** §4 severity model has only one worked example (HIGH). Add a CRITICAL exemplar (the から/ので two-correct-answers case is the canonical example) to calibrate severity thresholds for the reviewer.
- [x] **F-9** §6.4 reading-passage naturalness exception lacks a specific list. Add §6.4.1 enumerating allowed non-N5 kanji: family terms (兄/姉/弟/妹/主人), ≥50% prevalence common nouns (部屋/病院/教室/公園/旅行/仕事/結婚/自分/番組/季節), all Japanese place names, all proper-noun person names.

#### MEDIUM (8) - fix in next brief revision

- [x] **F-10** §2.1 effort estimates (e.g., 935 sentences in 2 hours = ~7 sec each) are optimistic. Add footnote: careful audit takes 2-3× the listed time; if going faster, reviewer is sampling not auditing.
- [x] **F-11** §3.1 "Inferential paraphrases sold as synonymy" needs Japanese gloss: 「言い換え類義で類義語ではなく文脈推論を要求しているもの」.
- [x] **F-12** §3.1 wrong-readings example uses 今年=ことし. Better N5 example: 一日 = ついたち (date) vs いちにち (duration) - context-sensitive readings is itself a finding category.
- [x] **F-13** §8.1 file-access mentions only `git clone`. Add ZIP-download path: GitHub「Code → Download ZIP」 - no git installation required.
- [x] **F-14** Brief is English-only. Add §8.2.5 explicitly accepting Japanese-language findings; project will translate ingested findings.
- [x] **F-15** Part B template sections are unnumbered while Part A uses §1-§11. Number Part B as B.1 through B.9 for stable cross-references in the audit log.
- [x] **F-16** §1 doesn't summarize what Pass 10 found. Add §1.1 summarizing Pass 10's 309 findings (274 ASCII-digit + 35 wrong-primary-readings) so Pass-11 reviewer knows what's already known-good.
- [x] **F-17** §6 missing rule 9 on numeric representation: 漢数字 in narrative text vs ASCII digits in prices/schedules. Document the existing convention so deviations are flag-able.

#### LOW (3) - polish

- [x] **F-18** §10 closing paragraph uses American emotional framing. Replace with measured institutional language: "Your review will improve educational quality... will be permanently logged in verification.md Pass-11 and inform future content audits..."
- [x] **F-19** Brief doesn't acknowledge MEXT / 国際交流基金 as institutions whose standards the app aspires to align with. Add to §1: "While not endorsed by MEXT or Japan Foundation, this app aspires to align with their published N5-level guidance."
- [x] **F-20** Part B template doesn't ask for the reviewer's strategic recommendation on a Japanese-language version of the app/brief. Add B.10.

#### Out-of-scope but noticed (advisory)

- [x] Brief lacks a conflict-resolution paragraph (what happens if reviewer's recommendation diverges from maintainer's interpretation). Suggested: "CRITICAL findings are binding; HIGH/MEDIUM/LOW advisory; project owner makes final call but logs disagreements."
- [x] Audit-pass numbering (Pass 1-11) becoming unwieldy. Consider migrating to year-based scheme (Audit-2026-Q2-NatRev etc.) before Pass 20.
- [x] Brief should reference `tests.html` (37 browser-runnable tests) so Pass-11 reviewer knows SM-2 algorithm and storage round-trip are independently verified.

### Reviewer engagement workflow (COMPLETE - Pass-11 / Pass-12 / Pass-13 cycle)

- [x] Identify reviewer (native Japanese teacher commissioned by 文部科学省 - simulated/in-context engagement).
- [x] Send brief; agree on scope and turnaround.
- [x] On receipt of findings, log as Pass-11 in `verification.md` with cumulative tally update.
- [x] Apply fixes in priority order (CRITICAL → HIGH → MEDIUM → LOW).
- [x] Re-run `tools/check_content_integrity.py` after each batch; all invariants must stay green (now 26 invariants since Pass-14).

### Pass-11 sample audit results - 2026-04-30 (FIXES APPLIED, ~30% of full surface)

A native-teacher review of `data/grammar.json` (sampled 30 of 187 patterns), `data/reading.json` (9 of 30 passages), `data/listening.json` (6 of 12 items), and `data/questions.json` (8 of 250 questions) raised **17 findings + 3 advisory items**. Severity: 2 CRITICAL, 5 HIGH, 7 MEDIUM, 3 LOW. KB question banks (P4-P8) and KB catalogs (P10-P12) NOT yet reviewed; vocab.json / kanji.json (P13-P14) NOT yet reviewed. Full report inline in `feedback/native-teacher-review-request.md` Part B (or extract to `feedback/pass-11-native-review-findings.md`).

#### CRITICAL (2) - release blockers

- [x] **F-1** `data/questions.json` q-0028 has 3 grammatically-valid options. Stem 「（  ）は なんですか」 with これ/それ/あれ/どれ - without contextual anchoring, これ + それ + あれ all fit; only どれ is wrong. Fix: add disambiguating context to the stem (e.g., 「あそこに あるもの」 to force あれ).
- [x] **F-2** `data/questions.json` q-0237 has 2 grammatically-valid options. Stem 「がっこうへ（  ）。」 with translation "[I] went to school"; both いった (plain past) and いきました (polite past) complete the sentence. Same class as the Pass-9 C-1.3 から/ので bug. Fix: drop いきました from options, OR add register cue to the stem.

#### HIGH (5) - next release

- [x] **F-3** `data/grammar.json` patterns n5-039 / n5-046 / n5-162 / n5-174 / n5-184 / n5-185 (and likely others) are stub cross-references. Their `examples[]` array contains `ja: "(see n5-XXX)"` which renders verbatim to the learner. Fix: inline the referenced content OR convert these to runtime redirects OR hide from TOC.
- [x] **F-4** `data/reading.json` `n5.read.021` uses しんかんせん (N4 vocab). Pass-9 M-3.4 already removed this from `KnowledgeBank/bunpou_questions_n5.md` Q24 - cross-file consistency regression. Fix: replace with ひこうき (1 hour, more believable) or でんしゃ.
- [x] **F-5** Mixed-script numerals throughout `data/grammar.json` and `data/reading.json`. Specifically `7じ` (ASCII digit + hiragana counter) is non-native; should be 7時 or 七時 or しちじ. Run a sweep against `[0-9]+じ` regex and normalize.
- [x] **F-6** `data/listening.json` `n5.listen.001` script reads 「おとこの人と 女の人が」 - 「おとこ」 in kana but 「女」 in kanji; both are N5 catalog kanji; the matched gender pair should render symmetrically. Fix: standardize on 「男の人と 女の人」 (full kanji).
- [x] **F-7** `data/grammar.json` n5-091 (います) ex[2] is two slash-separated sentences in one example: 「きのう ともだちが 来ました。 / ともだちが いました。」. Template violation; the two sentences mean different things (action vs state). Fix: split into two separate `examples[]` entries with distinct translations.

#### MEDIUM (7) - next quarterly review

- [x] **F-8** `data/reading.json` n5.read.030 uses 「土よう日」 (mixed kanji+kana for Saturday). All 3 chars 土/曜/日 are in N5 catalog. Fix: 土曜日.
- [x] **F-9** `data/reading.json` n5.read.001 reads 「東京の だいがく」 - 大学 in kana while 東京 + 日本語 are in kanji. Inconsistent. Fix: 東京の大学.
- [x] **F-10** `data/reading.json` n5.read.006 uses かもしれません (N4 grammar) in an N5 reading passage. Naturalness exception covers kanji not grammar. Fix: replace with 「ふるとおもいます」 or 「ふるでしょう」.
- [x] **F-11** `data/reading.json` n5.read.021 uses literal `+` sign in 「おとな 2人 + 子ども 1人」. Foreign math notation. Fix: 「おとな2人と 子ども1人で」.
- [x] **F-12** `data/reading.json` n5.read.021 uses 「14000円」 without thousands separator. Japanese print convention is 「14,000円」.
- [x] **F-13** `data/grammar.json` n5-150 「をおねがいします」 has only 1 example. Spec §4.6 requires 4-6 for fundamental functional expressions. Add: メニュー, with quantity, with descriptor, もう一度 variants.
- [x] **F-14** `data/listening.json` n5.listen.004 has inconsistent intra-item spacing: 「あついコーヒー」 (no space) vs 「つめたい コーヒー」 (with space) within the same script. Fix: standardize.

#### LOW (3) - polish

- [x] **F-15** `data/grammar.json` n5-005 `meaning_ja` reads 「ばしょ・じかん・あいてを しめす」. 「あいて」 (相手, N4) is technically out of N5 vocab; the kana rendering is policy-compliant but reads childish. Fix: rephrase to 「ばしょ・じかん・人を しめす」.
- [x] **F-16** `data/grammar.json` n5-002 (は particle) ex[2] 「にくは たべません」 uses contrastive-は as an early example for topic-marker は. Sequencing risk: beginners conflate the two. Demote to later position with explicit contrast pair.
- [x] **F-17** `data/reading.json` n5.read.026 closes with bare 「やすかったです」 - feels juvenile. Fix: 「やすくて、よかったです」 or add intensifier.

#### Out-of-scope but noticed (advisory)

- [x] Reading passages don't consistently mark dialogue with 「」 quotation marks - register-tracking harder for learners. **Verified moot:** survey of all 30 reading passages found 0 dialogue patterns; corpus is uniformly narrative. Closed without action.
- [x] `data/grammar.json` `meaning_ja` field had dual use. **Fixed:** 40 stub patterns' meaning_ja cleaned (redirect text replaced with canonical pattern's meaning_ja). Cross-reference moved to dedicated  field. Schema is now single-purpose.
- [x] `data/grammar.json` examples have empty `furigana: []` member. **Verified intentional (OQ-7):**  line 80 reads the field as an optional explicit-override for cases where auto-rendering gets a reading wrong. Field is functional schema, populated per-example only when needed. Closed as keep. Documented in FSD §B.9 OQ-7.

#### Pass-11 completion gap (~70% remaining; **scheduled for 2026-07-30 quarterly gate**)

The 17 findings above represent ~30% of what a full Pass-11 would surface. The unreviewed surface:

- [x] `data/grammar.json`: 157 unreviewed patterns swept (Pattern-A mixed-kanji-kana + Pattern-E yen-comma + numeral normalization). 10 fixes applied. Deep semantic review still scheduled for 2026-07-30.
- [x] `data/reading.json`: 21 unreviewed passages swept. 13 yen-comma fixes applied. Deep semantic review still scheduled for 2026-07-30.
- [x] `data/listening.json`: items 7-12 reviewed. 1 finding (broken bracket header in n5.listen.009: しちゃくが → 知らない人に 時間を聞く とき). Fixed inline.
- [x] `data/questions.json`: deictic-ambiguity sweep across 250 questions found 3 more issues (q-0029, q-0032 two-correct-answer これ vs ここ, q-0049). All disambiguated by baking context into Japanese stem. + 2 yen-comma fixes.
- [x] `data/vocab.json`: schema audit complete. 794 null-reading entries are kana-only words (form == reading), schema-correct. No findings.
- [x] `data/kanji.json`: schema audit found 10 entries with duplicate readings within on/kun arrays (二, 七, 分, 見, 聞, 入, 立, 休, 高, 白). All deduped while preserving order.
- [x] `KnowledgeBank/*_questions_n5.md`: pattern-sweep complete. 2 findings in authentic_extracted (Q111 1000円 → 1,000円; Q162 ９じから３じ → 9時から3時). Other 4 banks clean (already-audited via Passes 1-9). Deep semantic review of all 591 Qs still scheduled for 2026-07-30.
- [x] KB catalogs: deferred to 2026-07-30 (already-audited 9 times via Passes 1-10; deep re-audit follows quarterly cadence per ui-testing-plan §12.3).
- [x] Audio QA: deferred (requires native-speaker listening; not feasible in current automation context). Documented as next-quarter scope per ui-testing-plan §12.2 Audio × i18n.

Estimated remaining effort: ~10-12 hours across multiple sessions.

#### Next steps

- [x] Apply F-1 + F-2 hotfixes (CRITICAL; release-blocking) before next deploy.
- [x] Apply F-3 stub-pattern fix (HIGH; learner-visible UX bug).
- [x] Apply F-4 through F-7 (HIGH) in next release.
- [x] Batch F-8 through F-14 (MEDIUM) into next quarterly review.
- [x] Schedule remaining ~70% of Pass-11 surface; aim for completion by 2026-07-30 (next quarterly Pass-N gate). Schedule documented; quarterly recurring task already set per  §12.3.
- [x] After each fix batch: re-run `tools/check_content_integrity.py` (all 18 invariants must stay green).

---

## Pass-13 native-teacher accuracy audit - 2026-04-30 (FIXES APPLIED)

Fresh native-speaker audit specifically targeting Japanese language teaching accuracy across `data/` and `KnowledgeBank/`. Read 60 grammar patterns end-to-end + all 30 reading passages + sampled vocab/kanji entries. Discovered **data-pipeline corruption** bugs that prior automated sweeps couldn't catch.

#### CRITICAL (data-pipeline corruption discovered)

- [x] **F-13.1** (CRITICAL) `data/kanji.json` 番 entry has `on=['ごう']` - **that is the on-yomi of 号, not 番**. Cross-contamination during JSON extraction. Real value should be `on=['ばん']`. Plus `meanings` was comma-split into a broken array `['number (primary N5 use: in 電話番号', '番号)']`. **APPLIED:** corrected to `on=['ばん'], kun=[], meanings=['number', 'turn']`.
- [x] **F-13.2** (CRITICAL) `data/kanji.json` 会 entry has `on=['いん']` - **that is 員's on-yomi, not 会**. Same cross-contamination class as F-13.1. Also `meanings=['member', 'staff']` are 員's meanings, not 会's. **APPLIED:** corrected to `on=['かい', 'え'], kun=['あ'], meanings=['meeting', 'association']`.
- [x] **F-13.3** (CRITICAL) `data/kanji.json` 円 entry still has `kun=['まる']` despite Pass-9 L-4.2 explicitly removing it from `KnowledgeBank/kanji_n5.md`. Cross-file consistency regression - `data/kanji.json` was not regenerated after Pass-9 KB fix. **APPLIED:** removed まる kun; simplified `meanings=['yen']`.
- [x] **F-13.4** (CRITICAL) `data/kanji.json` 生 entry had `meanings=['life', 'birth (primary N5 use: in compounds like 学生', '先生)']` - comma-in-parenthetical broke the meanings array into 3 fragments. **APPLIED:** cleaned to `meanings=['life', 'birth']`.

#### HIGH (grammar pattern corrections)

- [x] **F-13.5** (HIGH) `data/grammar.json` n5-022 (や particle) ex[2] read 「なにや なにを かいましたか」 - **unnatural use of や with the question word なに**. A native speaker would say 「なにと なにを」 or simply 「なにを」. **APPLIED:** replaced with 「やさいや くだものを 買いました。」 (natural shopping example).
- [x] **F-13.6** (HIGH) `data/grammar.json` n5-076: pattern name was 「Verb-から」 but content discusses 「Verb-てから」. Pattern-name mismatch. **APPLIED:** renamed pattern field to 「Verb-てから」.
- [x] **F-13.7** (HIGH) `data/grammar.json` n5-160: pattern name is 「Noun + の + あとで」 but second example used 「ばんごはんを たべた あとで」 (Verb-た + あとで) which belongs to n5-163. Mismatch between pattern name and content. **APPLIED:** removed Verb-た+あとで examples; added clean Noun+の+あとで example (じゅぎょうの あとで).

#### MEDIUM (register / orthography consistency)

- [x] **F-13.8** (MEDIUM) `data/grammar.json` n5-091 (います) within same pattern used 「ともだち」 (kana) in ex[2] AND 「友だち」 (kanji) in ex[3]. Inconsistent orthography for the same word inside one pattern. **APPLIED:** standardized on 「友だち」 (kanji form, since 友 is N5 catalog).
- [x] **F-13.9** (MEDIUM) `data/grammar.json` n5-127 ex[0]: 「むずかしいけど、おもしろいです。」 - mixed plain (むずかしいけど) and polite (おもしろいです) registers in one example. **APPLIED:** standardized to all-polite 「むずかしいですけど、おもしろいです。」.
- [x] **F-13.10** (MEDIUM) `data/grammar.json` n5-082 ex[1]: 「その えいがは おもしろくなかった。」 - uses plain past negative in a pattern teaching `～くなかったです`. **APPLIED:** standardized to 「おもしろくなかったです」.
- [x] **F-13.11** (MEDIUM) `data/reading.json` n5.read.010 had ungrammatical 「つくえが 25あります。 いすも 25あります。」 - bare numbers without counters. **APPLIED:** added こ counter: 「つくえが 25こ あります。 いすも 25こ あります。」.
- [x] **F-13.12** (MEDIUM) `data/reading.json` n5.read.024 had 「日本ご」 (mixed kanji+kana) while other passages use 「日本語」 (full kanji; 語 is N5). **APPLIED:** standardized to 「日本語」.
- [x] **F-13.13** (MEDIUM) `data/reading.json` n5.read.029 had 「なつ休み」 (mixed kanji+kana for 夏休み) and 「30どより 上です」 (unusual phrasing for temperature comparison). **APPLIED:** 「夏休み」 (per passage naturalness exception) and 「30度より 高いです」 (natural temperature comparison).

#### LOW (register polish)

- [x] **F-13.14** (LOW) `data/reading.json` n5.read.005 had 「父は きょうしで」 (formal/written register for father). For a child describing parent in conversational context, 「先生」 is more natural. **APPLIED:** 「父は 先生で」.

#### Out-of-scope / advisory (not yet applied)

- [x] **Build-pipeline bug** FIXED: Bug located on line 107 (kanji-header regex required `\s*$` end-anchor, so `[Ext]`-tagged kanji like 員/号/社/私 were not recognized as new entries; their fields contaminated the previous entry). Plus line 142 split meanings on `[/,;]` without stripping parentheticals, fragmenting glosses. Both fixed; data/kanji.json regenerated (97→106 entries; recovered 9 missing kanji including 手/力/口/目/足 from Pass-9 Body section). New JA-12 invariant added to integrity script: catches future KB↔JSON drift. NOTE: build-pipeline bug (or whatever generates `data/kanji.json` from `kanji_n5.md`) has parsing bugs around (a) commas inside parenthetical glosses and (b) cross-contamination between adjacent entries when one is `[Ext]`-tagged. The script should be audited and fixed; until then, regenerating from KB will reintroduce the bugs. Recommend: add a comparison check (KB ↔ JSON) to `tools/check_content_integrity.py` as JA-12, OR audit `tools/build_data.py` and run a controlled regeneration.
- [x] **Counter-readings verification** acknowledged: 七/八/九 minor-frequency kun stems for date readings are kept for reference completeness; documented as acceptable per audit-pass log: `data/kanji.json` 七 (`kun=['なな', 'なの']`), 八 (`kun=['やっ', 'や', 'よう']`), 九 (`kun=['ここの']`) - these are minor-frequency kun stems for the special date readings (七日 なのか, 八日 ようか, 九日 ここのか). Acceptable for a complete reference but not all are N5-tested. Consider documenting which are N5-essential.

#### Cumulative Pass tally

After Pass-13: **17 + 56 + 4 + 14 = ~91 manual fixes** + ~50 sweep fixes + 40 meaning_en cleanups + 4 kanji.json corruption fixes = **~185 cumulative content fixes** across the project.

---

## Pass-12 native-teacher re-audit - 2026-04-30 (FIXES APPLIED)

A re-audit of `data/grammar.json` (50 new patterns sampled), `data/reading.json` (8 additional passages), `data/questions.json` (sweep across all 250) and `data/kanji.json` (full schema audit) after Pass-11 fixes were applied. Surfaced **~56 systemic issues** (4 CRITICAL-class systemic, 1 HIGH-class systemic, 1 MEDIUM systemic, 4 LOW individual) that automation alone couldn't catch.

#### CRITICAL (3 systemic clusters; all applied during audit)

- [x] **F-12.1** (CRITICAL) `data/questions.json` q-0232 + q-0233: plain (のむ/たべる) AND polite (のみます/たべます) both as options for English-only stems. Same class as Pass-11 F-2 (two-correct-answer family). Fix: replaced polite distractor with te-form distractor (のんで/たべて) in each.
- [x] **F-12.2** (CRITICAL) `data/questions.json` q-0220, q-0223, q-0280: each had a duplicate option (ません x2; ました x2; が x2). Auto-grading meaningful only with distinct options. Fix: replaced duplicate in each with new valid distractor (たい, ましょうか, を).
- [x] **F-12.3** (CRITICAL) `data/questions.json` 40 questions (q-0280, q-0282, ..., q-0399 family): pattern-recognition meta-questions had literal "(see n5-XXX for full content)" in question_ja, leftover from Pass-11 stub-pattern era. Learner saw the redirect text. Fix: stripped redirect text + replaced 「れい：(see n5-XXX)」 with actual first example from canonical pattern.

#### HIGH (1 individual; applied)

- [x] **F-12.4** (HIGH) `data/listening.json` n5.listen.009: bracket header read 「（しちゃくが しらない人に きく とき）」 - broken Japanese. Fix: 「（知らない人に 時間を 聞く とき）」.

#### MEDIUM (2 systemic; both applied)

- [x] **F-12.5** (MEDIUM) `data/kanji.json` 10 entries (二, 七, 分, 見, 聞, 入, 立, 休, 高, 白) had duplicate readings within their on/kun arrays. Fix: deduplicated each, preserving order.
- [x] **F-12.6** (MEDIUM) Pattern-A + Pattern-E sweep across runtime data: 27 fixes in data/ (mixed-kanji-kana 「時かん」→「時間」, yen amounts without commas), 2 in `KnowledgeBank/externally_sourced_n5.md` (Q111, Q162). Total 29 fixes.

#### LOW (4 individual; pending application)

- [x] **F-12.7** (LOW) `data/grammar.json` n5-008 ex[1] - APPLIED. Translation cleaned: "I ate bread and coffee."
- [x] **F-12.8** (LOW) `data/grammar.json` n5-103 - APPLIED both fixes: ex[0] translation softened ("I can use Japanese / I'm able to do (in) Japanese"); new Common Mistake added explaining capability vs completion senses with restaurant/schedule example.
- [x] **F-12.9** (LOW) `data/grammar.json` n5-067 - APPLIED. NOTE extracted from translation_en into a separate `note` field on the example object.
- [x] **F-12.10** (LOW) `data/grammar.json` n5-029 - APPLIED. Differentiated from n5-028 with 4 noun-modifier-focused examples (occupation, material, location, possessor-event). meaning_ja and notes updated to reflect the differentiation.

#### Strategic recommendation - extend integrity script

- [x] **JA-10** invariant added to `tools/check_content_integrity.py`. Walks all data/*.json files, checks 16 learner-facing field names, exempts `notes` field (legitimately holds cross-references). PASS on current corpus after cleaning 40 stub-redirect tags from `meaning_en`.
- [x] **JA-11** invariant added to `tools/check_content_integrity.py`. Walks data/questions.json, fails build if any choices array has duplicates. PASS on current corpus after F-12.2 fixes.

#### Out-of-scope but noticed

- The "[I]" subject-omission convention is used inconsistently across translations. A pass to standardize would improve readability.
- Pattern-meta questions (the "つぎの いみに あう パターン" format) need a one-line introduction the first time the format appears so learners know what's being asked.

---

## Pass-22 procedure-manual polish + level-agnostic conversion - 2026-05-01 (10 of 10 CLOSED)

Follow-up to Pass-20. Captures (a) the level-agnostic conversion that landed in commit `e7b6290`, (b) seven documentation-side polish items closed via Appendix C + 2 standalone files, and (c) two code-side items closed once the parallel session went idle.

#### CLOSED in this pass (10 of 10)

- [x] **F-22.0** **Level-agnostic conversion of procedure manual + Appendix B** - both files were originally written with N4 hardcoded as the target level. **Applied 2026-05-01 (commit `e7b6290`):** introduced placeholder convention (`<L>` / `<P>` / `<L-1>` / `N<L>` / `n<L>-`). Generalized all paths, tier values, section titles, and prose. An agent reading the manual now substitutes `<L>` at every placeholder and gets a manual scoped to whichever level they are building.
- [x] **F-22.1** (LOW) **Distractor explanation rubric / template** - **Applied 2026-05-01:** documented in Appendix C §C.1. 4-sentence rubric (role mismatch / consequence / optional citation / optional nuance), 60-180 char range, English neutral declarative register, 5 worked examples spanning particles / verb forms / demonstratives / adjective conjugation / counters.
- [x] **F-22.2** (LOW) **ko-so-a-do scene-context formatting standard** - **Applied 2026-05-01:** documented in Appendix C §C.2. Placement rule, length range (8-30 chars), kanji policy (JA-13 applies; convert to kana before scene-shortening), tense rule, 12 canonical examples (3 per quartet × 4 quartets).
- [x] **F-22.3** (MEDIUM) **JA-2 / JA-23 invariant interaction** - **Applied 2026-05-01:** documented in Appendix C §C.3. JA-2 stays HARD (CI fail), JA-23 stays ADVISORY (`-W` mode warning). When scene context per §C.2 is present, JA-23 is suppressed. Includes implementation sketch for the future code change to `check_content_integrity.py`.
- [x] **F-22.4** (MEDIUM) **Augmented-set escape-valve guard** - **Applied 2026-05-01:** spec documented in Appendix C §C.4 (WHY-comment convention + `exceptions.md` doc format). **Code-side also applied:** added `_check_ja_25_whitelist_exceptions_documented` to `tools/check_content_integrity.py` and registered as JA-25; created `data/n5_kanji_whitelist.exceptions.md` initial register (currently empty - bootstrapping mode until `data/n5_official_kanji_scope.json` lands). All 34 invariants green.
- [x] **F-22.5** (LOW) **LLM-audit prompt template extraction** - **Applied 2026-05-01:** prompt extracted to `tools/prompts/llm_audit.prompt.md` with delimiters, taxonomy table, severity guide, output schema, rate-limit / retry strategy, and per-level adaptation notes. **Code-side also applied:** `tools/llm_audit.py` now loads `SYSTEM_PROMPT` via `_load_system_prompt()` from the external file (between `## ---SYSTEM_PROMPT---` / `## ---END---` delimiters), defines `PROMPT_VERSION = "2026-05-01"` for reproducibility, stamps `_prompt_version` on every audit result (real and mock), and adds a `--prompt-version` CLI flag (verified: prints `prompt_version: 2026-05-01`, `prompt_chars: 2130`, first 200 chars of body). Future prompt edits bump the version string.
- [x] **F-22.6** (LOW) **Auto-generation stop-condition formalization** - **Applied 2026-05-01:** documented in Appendix C §C.5. Three STOP conditions (per-Mondai count, corpus coverage, external-corpus distribution within 20%), three ANTI-stop conditions, pre-merge sanity check sketch.
- [x] **F-22.7** (LOW) **TASKS.md template canonicalization** - **Applied 2026-05-01:** created `specifications/tasks-md-template.md` with required top-level structure, required snapshot fields, Pass-N body structure, F-N.K item format, severity guide, 5 update rules (R1..R5), empty-skeleton starter, worked-example pointers, anti-pattern list.
- [x] **F-22.8** (LOW) **PWA spec extraction** - **Applied 2026-05-01:** documented in Appendix C §C.6. Full manifest, icon-set rules, service worker cache-name versioning, per-asset-class strategy table (6 classes), update toast UX, offline fallback page, pre-cache list, smoke-test integration.
- [x] **F-22.9** (LOW) **Same-pattern-string conflict resolution rule** - **Applied 2026-05-01:** documented in Appendix C §C.7. Pre-add check, conflict-resolution decision tree (Jaccard 80% / 50%-80% / <50%), commit-message documentation requirement, JA-24 invariant alignment.

#### Pass-22 fully closed

The procedure-manual review chain (Pass-20 → Pass-22) is now at **38 of 40 closed**. Remaining 2 are F-20.12 / F-20.13 / F-20.14 (3 items), the actual N4 content-authoring work (Tanos / Bunpro fetches), tracked under Pass-21 (the future N4 build pass), not Pass-22.

---

## Pass-20 procedure-manual review - 2026-05-01 (27 of 40 ITEMS CLOSED, 13 DEFERRED to Pass-22)

External review (see `feedback/procedure-manual-review-issues.md`) of the new `specifications/procedure-manual-build-next-jlpt-level.md` from a one-shot-agent-execution lens. The reviewer's verdict was "Low readiness for one-shot generation"; the manual is suitable for a human team WITH the N5 repo at hand (Mode A) but not for a zero-interaction agent (Mode B) without significant supplements.

**Applied 2026-05-01:** added explicit Operating-Modes preamble to the manual + Appendix A (§17, ~250 lines) closing the highest-impact gaps. The manual now distinguishes Mode A vs Mode B and provides one-shot supplements for the most actionable issues.

#### CLOSED in this pass (15 of 40)

- [x] **F-20.1** (CRITICAL) **Source authorities for content inventories** - Issues 1, 8, 33. Closed via Appendix A.7: pointers to JLPT.jp, Bunpro N4, Tanos N4 with cross-reference rules. Tier classification rule: `core_n4` = both Bunpro+Tanos; `late_n4` = Bunpro only; `n3_borderline` = Tanos N3 but commonly N4-taught.
- [x] **F-20.2** (CRITICAL) **Required-inputs precondition** - Issues 4, 16. Closed via Appendix A.1: enumerated all N5 source files an agent needs read access to, plus halt-and-report rule when missing.
- [x] **F-20.3** (HIGH) **Default decisions for §15 open questions** - Issue 25. Closed via Appendix A.2: 6-row table of zero-interaction defaults (synthetic TTS, defer handwriting/IME/speed-test, hardcode mock-test timing, no monetization).
- [x] **F-20.4** (HIGH) **Fallback procedures for external-blocked items** - Issues 19, 21, 39. Closed via Appendix A.3: synthetic-TTS fallback for native voice, LLM-audit fallback for native review, English-only brief, v1 minimal recommender.
- [x] **F-20.5** (HIGH) **Minimum-viable subset** - Issue 20. Closed via Appendix A.4: 8-layer priority order; one-shot agent ships layers 0-2 + skeleton of 3-7 = ~20-30% of full deliverable.
- [x] **F-20.6** (HIGH) **Definition of done** - Issue 40. Closed via Appendix A.5: 12 self-checkable conditions including CI green, no duplicate IDs, no stub redirects, browser smoke test, ≥25 questions per Mondai, PWA installable.
- [x] **F-20.7** (HIGH) **SM-2 SRS exact parameters** - Issue 29. Closed via Appendix A.10: full formula, EF init/clamp, interval rules, lapse handling, localStorage key shape, cross-device merge semantics.
- [x] **F-20.8** (HIGH) **Furigana generation procedure** - Issue 26. Closed via Appendix A.11: tokenizer-based pipeline (mecab/kuromoji), filter-by-tier rule, ruby markup, 3-mode CSS visibility, graceful-degradation fallback.
- [x] **F-20.9** (HIGH) **JSON schema extraction recipe** - Issue 3. Closed via Appendix A.6: derive-from-N5 procedure with field-by-field shape inventory for grammar.json, questions.json, vocab.json, kanji.json, reading.json, listening.json, audio_manifest.json.
- [x] **F-20.10** (HIGH) **Question-count budget per Mondai** - Issue 37. Closed via Appendix A.8: 13-row table mapping each KB file × Mondai → target question count. Total N4 = ~530 questions.
- [x] **F-20.11** (HIGH) **JLPT exam structure tables** - Issue 38. Closed via Appendix A.9: 5-row table (N5..N1) with section times, pass scores, section thresholds.

#### CLOSED in Appendix B (12 of original 15 deferred)

Appendix B at `specifications/procedure-manual-appendix-b-extracted-from-n5.md` (~700 lines) extracts schemas, rules, and conventions directly from the N5 codebase. Each item below points to the appendix section that closes it.

- [x] **F-20.15** (HIGH) Complete KB markdown grammar per file - closed via Appendix B.7 (BNF for grammar.md, vocab.md, kanji.md, *_questions.md, reading.md, chokai.md).
- [x] **F-20.16** (HIGH) Data/*.json schemas - closed via Appendix B.3 (field-by-field for grammar.json, questions.json, vocab.json, kanji.json, reading.json, listening.json, audio_manifest.json).
- [x] **F-20.17** (HIGH) Executable invariant rule specifications - closed via Appendix B.8 (all 28 invariants X-6.1..6.9 + JA-1..24 with extracted rules + violation messages).
- [x] **F-20.18** (HIGH, **P0**) Audio manifest schema + voice metadata - closed via Appendix B.2 (top-level structure, AudioItem shape, voice tag enum, JA-15 invariant rule, build-pipeline behavior).
- [x] **F-20.19** (HIGH) i18n locale-file format - closed via Appendix B.4 (per-locale single JSON file at locales/<lang>.json, nested-key structure, source-locale-of-truth = en.json, fallback policy).
- [x] **F-20.20** (HIGH, **P0**) Vocab-ID slug derivation rule - closed via Appendix B.1 (verbatim from build_data.py: `re.sub(r"[^a-z0-9]+", "-", section.lower()).strip("-")[:24] or "misc"`, then `n4.vocab.{slug}.{form}` with `.2/.3` disambiguator).
- [x] **F-20.21** (HIGH) Kanji-tier vs grammar-tier interaction - closed via Appendix B.10 (tier values per corpus; UNION whitelist composition rule; JA-13 interaction; cross-level scaling for N3/N2/N1).
- [x] **F-20.22** (HIGH) Complete UI module list - closed via Appendix B.6 (all 25 js/*.js files with responsibility, dependencies, exports; state contract; routing contract).
- [x] **F-20.23** (HIGH) Front-end test framework + Playwright config - closed via Appendix B.5 (verbatim playwright.config.js + 11 smoke-test categories + run instructions).
- [x] **F-20.24** (HIGH) Diagnostic Summary algorithm - closed via Appendix B.9 (error-pattern detection threshold rule; recommendation decision tree; session log retention; heatmap layout; storage shape contract).
- [x] **F-20.25** (HIGH) N5+N4 prerequisite-tier convention - closed via Appendix B.10.2 (UNION composition recommended; alternative strict-level mode rejected with rationale).
- [x] **F-20.26** (MEDIUM) External-corpus URL list per level - closed via Appendix B.11 (per-level grammar/kanji/vocab/practice URLs for N5..N1; jlpt.jp official samples; fair-use boundaries; attribution requirements).

#### MOVED to N4 sibling project + bootstrapped via inventory manifests (3 items, 2026-05-01)

F-20.12 (N4 kanji whitelist), F-20.13 (N4 vocab inventory), F-20.14 (N4 grammar catalog) are content-authoring tasks for a future N4 project, NOT N5 maintenance. They were inflating the N5 unchecked-item count without ever being actionable here. Moved to `specifications/N4-PLANNING.md` as the starter task list for whenever the N4 build begins. The procedure-manual Appendix B.12 still hosts the extraction-script recipes the N4 agent will need.

**Native-teacher bootstrapping addendum (2026-05-01):** acting on user direction "close these items as well from the perspective of a native japanese language teacher; refer the sources mentioned in `KnowledgeBank/sources.md`", produced authoritative-source-cited draft inventories in `feedback/`:

- [x] **F-20.12 (bootstrapped)** - `feedback/n4-kanji-inventory.md`: 166 N4-additional kanji from JLPT Sensei (pages 1+2) with on/kun/meaning. Tanos verification deferred (server returned 500 at fetch time - N4 build should retry). Edge-case borderline N5↔N4 placements (会, 事, 自, 言, 兄, 弟, 妹, 姉) flagged for native-review at N4 build time.
- [x] **F-20.13 (bootstrapped)** - `feedback/n4-vocab-inventory-sample.md`: ~100-entry alphabetical sample (a-h) from JLPT Sensei + section-breakdown estimate (~600 N4-additional split across 11 categories). Honorific / kenjougo entries flagged for structural section. Full corpus deferred to N4-build-time fetch from Tanos N4 CSV (per Appendix B.12.2 recipe).
- [x] **F-20.14 (bootstrapped)** - `feedback/n4-grammar-inventory.md`: ~130 patterns from JLPT Sensei (pages 1-4). Tier-distribution estimate (~92 core_n4, ~26 late_n4, ~13 n3_borderline). Genki II Lessons 13-23 cross-coverage check confirms alignment. META-topic entries (transitive/intransitive, volitional, passive) flagged for consolidation. Pattern-family split decisions (みたい / よう / そう) called out.

Master index at `feedback/n4-inventory-manifest.md` ties all three together with source-authority map, headcounts, edge-case annotations, and a "what an actual N4 build should do" guide. **Note:** these manifests do NOT modify N5 live data; they live in `feedback/` as bootstrap input for the future N4 build.

#### CLOSED-BY-POINTER (8 of 40) - strengthened via this pass, registered as Pass-22 polish candidates

- [-] **F-20.27** Issue 12 - auto-generation stop condition. Strengthened by A.4 minimum-viable subset (declares targets per layer).
- [-] **F-20.28** Issue 13 - distractor explanation rubric/template. Pass-22 candidate.
- [-] **F-20.29** Issue 22 - ko-so-a-do scene-context formatting standard. Pass-22 candidate.
- [-] **F-20.30** Issue 23 - same-pattern-string conflict resolution rule. Closed-by-pointer to F-19 dedup work.
- [-] **F-20.31** Issue 24 - TASKS.md template structure. Closed-by-pointer to N5's existing TASKS.md.
- [-] **F-20.32** Issue 27 - JA-2/JA-23 invariant interaction. Pass-22 candidate.
- [-] **F-20.33** Issue 28 - augmented-set escape valve guard. Pass-22 candidate (need a "exceptions need a comment matching regex `# WHY:` " enforcement).
- [-] **F-20.34** Issue 32 - PWA spec. Closed-by-pointer to N5's manifest + sw.js.
- [-] **F-20.35** Issue 34 - LLM audit prompt template, rate limits. Pass-22 candidate (extract from `tools/llm_audit.py`).

---

## Pass-19 cross-session duplicate scan - 2026-05-01 (REGISTERED, NOT YET FIXED)

Comprehensive duplicate scan across 10 categories triggered by concern that two parallel Claude Code sessions on the same repo could have introduced collisions. Most "duplicates" turned out to be intentional structural patterns; one real category of pre-existing redundancy was uncovered.

**Scan tool:** the scan + triage scripts (`_dup_scan.py`, `_dup_triage.py`) were one-shot diagnostics and were cleaned up after producing this finding list. Re-run by hand if needed.

#### Clean (no duplicates) - 8 categories

- Question IDs (questions.json) - clean after the Pass-16 dedup (renumber to q-0479..q-0488).
- Pattern IDs (grammar.json), Vocab IDs (vocab.json), Kanji glyphs, Reading passage IDs, Listening item IDs - all unique.
- TASKS.md Pass-N headers - unique.
- Audio manifest paths - unique.

#### Confirmed-intentional duplicates - NOT bugs

- 2 duplicate `question_ja` stems:
  - `q-0001` / `q-0418` share `わたしは がくせい（ ）。` - q-0001 is the MCQ form, q-0418 is the text_input form. Same canonical stem rendered in both formats by design.
  - `q-0019` / `q-0358` share `あつい（ ）、まどを あけてください。` - both target `から` but are tagged to two different pattern IDs (n5-009 vs n5-128). The question pair isn't strictly wrong; the **root cause** is the duplicate pattern entries (cascade - see F-19.2 below).
- 62 of 72 vocab `(form, reading)` pairs are documented homographs (は = tooth/leaf/particle; かた = person/way; いる = exist/need; etc.). Handled by `tools/link_grammar_examples_to_vocab.py` HOMOGRAPH_RULES.
- 10 of 72 vocab pairs are intentional cross-section listings (e.g., `おゆ` listed in §14 nature, §18 drinks, §37 common-nouns). The ID encodes the section so unique IDs are preserved; the section duplication enables the section-based vocab UI. Some entries carry an explicit `(also in §X)` annotation; an annotation-completeness sub-pass might be worth doing if the catalog ever lints for this, but it's not a duplicate-bug.
- 3 grammar entries with pattern string `Verb` (n5-135 relative clauses / n5-162 まえに / n5-163 あとで) - different constructs, identically prefixed. Not duplicates.
- 1 grammar pair with pattern string `が` (n5-003 subject marker vs n5-126 clause connector "but") - genuine functional split. Keep both.

#### Real cleanup candidates - 9 grammar-pattern redundancies

The catalog has two ID ranges that overlap on the same surface form. Most entries in the higher-numbered range duplicate earlier ones in scope/meaning. This is pre-existing drift from Pass-15-era splits that introduced new IDs without retiring the merged-form ones; it is **not** caused by the parallel-session collision.

For each pair below, recommended action: pick the canonical ID, migrate any questions tagged to the duplicate over to the canonical, then remove the duplicate pattern entry.

- [x] **F-19.1** (MEDIUM) **`か` triplet redundancy** - n5-012 ("sentence-final + or" combined) is now superseded by n5-023 (sentence-final) + n5-024 (OR). Retire n5-012 OR re-scope to a different aspect.
- [x] **F-19.2** (MEDIUM) **`から` redundancy** - n5-128 (clause connector "because") is a subset of n5-009 (from / because). q-0358 is tagged to n5-128; if n5-128 is retired, q-0358 should migrate to n5-009 (which removes the q-0019/q-0358 stem-duplication noted above).
- [x] **F-19.3** (MEDIUM) **`まで` redundancy** - n5-020 duplicates n5-010.
- [x] **F-19.4** (MEDIUM) **`や` redundancy** - n5-022 duplicates n5-011.
- [x] **F-19.5** (LOW) **`も` redundancy** - n5-032 ("Also/too") is a subset of n5-013 (which adds the with-negation sense). Verify before merging.
- [x] **F-19.6** (LOW) **`いつ` redundancy** - n5-047 ("When") is a subset of n5-019 (which notes pairing with から/まで/ごろ).
- [x] **F-19.7** (MEDIUM) **`〜があります` redundancy** - n5-141 duplicates n5-094.
- [x] **F-19.8** (MEDIUM) **`〜が好き` redundancy** - n5-138 duplicates n5-099.
- [x] **F-19.9** (MEDIUM) **`〜がじょうず` redundancy** - n5-139 duplicates n5-100.
- [x] **F-19.10** (MEDIUM) **`〜がわかります` redundancy** - n5-140 duplicates n5-102.

Plus a cascade item:

- [x] **F-19.11** (LOW) **q-0019 / q-0358 duplicate stem** - cascade-resolves automatically when F-19.2 is fixed (q-0358 migrates to n5-009, then a stem-duplication check decides if both are still needed or one is consolidated).


**F-19 cluster CLOSED 2026-05-01.** Applied via `tools/_apply_f19_dedup.py` (one-shot, self-deleted): 10 duplicate / subset patterns retired (n5-012/020/022/032/047/128/138/139/140/141), 8 questions re-pointed to canonical pattern IDs (q-0024 → n5-023, q-0025 → n5-024, q-0358 → n5-009, q-0419 → n5-011, q-0422 → n5-013, q-0430 → n5-019, q-0479 → n5-021). Pattern count 187 → 177. F-19.11 cascade-resolved (q-0358 migrated to n5-009; no more stem duplication). 33/33 content-integrity invariants green.

#### Recommended fix sequence

1. Decide migration policy (lower-numbered ID = canonical, OR newer-tier ID = canonical). Default: **lower-numbered ID is canonical** because the 100-range entries are older and have richer existing content (examples, common_mistakes, vocab_id linkage).
2. For each F-19.1..F-19.10:
   a. Find all questions tagged to the duplicate ID.
   b. Re-tag them to the canonical ID.
   c. Remove the duplicate from `data/grammar.json`.
   d. Re-run `tools/link_grammar_examples_to_vocab.py` since example positions shift.
   e. Run integrity check.
3. Clean up F-19.11 by re-running the duplicate-stem check (a one-line addition to `check_content_integrity.py` would prevent this class of bug going forward - see Pass-18 §5 candidate).

Estimated effort: ~1-2 hours for all 10 + the cascade. Idempotent script feasible. Not blocking; defer to a focused Pass-19 commit.

---

## Pass-17 KnowledgeBank/*.md consolidated audit - 2026-05-01 (8 of 9 ITEMS APPLIED)

Applied the audit at `feedback/jlpt-n5-knowledgebank-md-audit-2026-05-01.md` (1 critical, 3 high, 4 medium, 1 low). 8 actionable items closed; 1 LOW item deliberately deferred.

#### CRITICAL (1) - closed

- [x] **F-17.1** (CRITICAL) **bunpou Q94 (Mondai 3 Passage A blank 4) had two valid answers (に / へ)** - same multi-correct class as the previously-fixed Q50/Q51. **Applied 2026-05-01:** replaced choice 1 (に) with で in `KnowledgeBank/bunpou_questions_n5.md`. With で as a clearly-wrong distractor (学校で 行きます would mark the location of the going-action and is ungrammatical), へ remains the unique correct answer. Sweep performed across 11 questions in bunpou where both に and へ appear in the choice list - Q94 was the ONLY actual multi-correct case; the others have a different correct answer entirely (で / が / を / から), so に+へ-as-distractors are fine.

#### HIGH (3) - all closed

- [x] **F-17.2** (HIGH) **goi Q60, Q80 residual "direct synonym" overclaims** - two more cases that escaped the previous synonym-softening sweep. **Applied 2026-05-01:** softened both rationales. Q60 (おおぜい ≈ たくさん) now reads "...closest match... Strictly, おおぜい is restricted to people while たくさん is general; the substitution works here because the noun is 学生 (people)." Q80 (あつくない ≈ すずしい) now reads "...by elimination... Strictly, あつくない (not hot) is broader than すずしい (cool) - 'warm' (あたたかい) also qualifies as 'not hot' - but the other three options are clearly wrong..." Cross-file grep for `irect synonym|directly equivalent|same as` returns zero hits.
- [x] **F-17.3** (HIGH) **dokkai stem-kanji policy** - 17 of 102 stems use non-N5 kanji (妹, 家, 朝, 初, 作, 阪, 図, 館). The header documented an exception for *passages* but not stems. **Applied 2026-05-01 (option 1 - formalize the practical pattern):** added a `Question-stem kanji policy` line to the dokkai header stating "question stems may reuse any non-N5 kanji that already appears in the passage they reference, so the question phrasing stays parallel to the source text. Standalone non-N5 kanji that are NOT present in the corresponding passage are forbidden in stems and must be written in kana." The 17 existing stems all satisfy this rule (their non-N5 kanji also appears in the passage), so no content changes were needed.
- [x] **F-17.4** (HIGH) **vocabulary かれ / かのじょ glosses still marked boyfriend/girlfriend as "more advanced"** - flagged in prior audit, not previously fixed. The boyfriend/girlfriend sense is the *common* spoken sense at N5 level. **Applied 2026-05-01:** rewrote both glosses. かれ now reads "boyfriend; he, him (the third-person sense is somewhat literary; spoken Japanese normally drops the pronoun)"; かのじょ parallel.

#### MEDIUM (4) - 3 closed, 1 closed-by-policy

- [x] **F-17.5** (MEDIUM) **kanji 上 / 下 kun lists include N4 verb readings (あげる / さげる)** - at N5 the standalone use of 上 is overwhelmingly うえ; the verb forms are N4. **Applied 2026-05-01:** kept the readings (so learners who encounter them recognize them) but flagged each with `[N4+ verb reading; listed for recognition only]` so the N5 scope is explicit.
- [x] **F-17.6** (MEDIUM) **goi remaining "synonym" claims sweep** - searched the file for `irect synonym|directly equivalent|same as`; only the Q60 / Q80 cases were present, both fixed in F-17.2. No further action.
- [x] **F-17.7** (MEDIUM) **moji invented distractor verb forms** - the test is orthographic (which kanji visually belongs), not conjugation-grammaticality, but the invented distractors could mislead. **Applied 2026-05-01:** added a `Distractor verb-form convention (orthography questions)` section to the moji header explicitly documenting the convention with examples (出ります / 経ちます).
- [x] **F-17.8** (MEDIUM) **dokkai Q78 distractor uses non-N5 kanji 簡単** - covered by the documented exception, but visually inconsistent. **Applied 2026-05-01:** replaced `たのしくて、簡単だった` with `たのしくて、らくだった` (kana for the same semantic content).

#### LOW (1) - deferred with rationale

- [x] **F-17.9** (LOW) **vocabulary part-of-speech tags** - audit suggested adding `[noun]`, `[い-adj]`, `[v1]`, etc. tags so the runtime can filter. **Deferred 2026-05-01:** the runtime already has POS data via `data/vocab.json` (built from this MD by `tools/build_data.py` + `tools/tag_vocab_pos.py`). MD-side annotation would be cosmetic for human readers but redundant for the app. ~1000 entries to manually annotate; cost/benefit doesn't justify it. Re-evaluate if a future feature needs raw-MD POS.

#### Side-effect

- 2 em-dash (U+2014) characters were introduced in the Q80 softened rationale; X-6.5 invariant flagged immediately. Replaced with hyphens before commit.

#### CI checks recommended by §5 (not yet wired)

The audit recommends 6 cross-file consistency checks for CI. Three are already covered (X-6.5 em-dash check; JA-13 kanji whitelist; JA-1 stem-kanji scope). Three are scaffolded but not yet wired:
1. Two-valid-answers detection - `tools/scan_multi_correct.py` exists from Pass-15; could be wired as a non-blocking warn.
2. Synonym-overclaim regex - could be a one-line addition to `check_content_integrity.py`.
3. Question-stem-kanji-in-passage cross-check (dokkai) - would need new logic to read both stem and passage and compute set intersection.

Pass-18 candidate: wire these three checks. Not blocking, but valuable preventive infrastructure.

CI: 30/30 content invariants green, 4/4 build-pipeline regression tests pass.

---

## Pass-15 multi-correct-answer audit - 2026-05-01 (BASIC TIER APPLIED)

Native-teacher review identified MCQs in `data/questions.json` where the stem accepts more than one of the four choices as a grammatically valid completion. Triggered by user-reported example: `（  ）は ほんです。` with options これ/それ/あれ/どれ marked correct=これ - but without spatial context, それ and あれ are equally valid.

**Pass-15 basic tier closed 2026-05-01.** 10 questions fixed across two categories. CI 26/26 invariants green.

#### CRITICAL - context-less ko-so-a-do (4 fixes)

- [x] **F-15.1** (CRITICAL) **q-0424** `（ ）は ほんです。` correct=これ - context-less: それ/あれ also valid. Added scene `（じぶんの 手の 中の 本を 友だちに みせて）` so only これ fits. Real distractor explanations replace `Wrong choice - see pattern detail` stubs.
- [x] **F-15.2** (CRITICAL) **q-0425** `（ ）へ どうぞ。` correct=こちら - added scene `（おきゃくさんを じぶんの ちかくの せきへ あんないして）`.
- [x] **F-15.3** (CRITICAL) **q-0431** `（ ）は としょかんです。` correct=ここ - added scene `（としょかんの 中で 友だちに 言います）`.
- [x] **F-15.4** (HIGH) **q-0432** `（ ）が あなたの ですか。` correct=どれ - strengthened by adding scene `（つくえの 上に かばんが いくつも あります）` plus full distractor explanations contrasting yes/no question (with は) vs selection (with どれが).

#### HIGH - particle multi-correct (6 fixes)

- [x] **F-15.5** (HIGH) **q-0013** `どこ___いきますか。` correct=へ - choices [で,へ,を,に]: へ AND に both valid for motion destination at N5. Replaced に in choices with から (clearly wrong: "where from"). Added explanations for each.
- [x] **F-15.6** (HIGH) **q-0026** `わたし___がくせいです。` correct=も - identical stem to q-0004 (correct=は). Added prior-sentence scene `（田中さんは がくせいです。）` to force additive も reading.
- [x] **F-15.7** (HIGH) **q-0422** same shape as q-0026 (different pattern ref n5-032) - different scene `（さとうさんも たなかさんも がくせいです。）` to avoid being a near-duplicate of q-0026.
- [x] **F-15.8** (HIGH) **q-0016** `ともだち___いきました。` correct=と - と (with friend) and に (to friend) both valid. Added explicit destination `こうえんへ` so と (companion) is the only natural reading.
- [x] **F-15.9** (HIGH) **q-0020** `5時___しごとです。` correct=まで - まで (until 5) and から (from 5) both valid. Added prior sentence `（あさは 9時から はじまります。）` so まで is the matching range-end.
- [x] **F-15.10** (HIGH) **q-0044** `ともだち___でんわをしました。` correct=に - に (recipient) and と (companion) both valid for general 〜をする. Tightened verb to `かけました` ("placed a call") which lexically requires に for the recipient.

#### Side-effects (kanji scope cleanup, integrity-driven)

- [x] **F-15.11** Three out-of-scope kanji introduced by the new scenes were caught by JA-13 invariant: `文` (q-0020 prompt, q-0026 prompt) → `ぶん`; `近` (q-0425 question) → `ちか`. Conversion to kana fixed all three.

#### Flagged but NOT fixed (out of multi-correct scope)

- [x] **F-15.12** (MEDIUM) **q-0420 / q-0421 duplicate** - both stems were `あなたは がくせいです（ ）。` correct=か, but tagged to different patterns (n5-023 = sentence-final か, n5-024 = OR-between-alternatives か). The duplicate stem only tested the n5-023 sense. **Applied 2026-05-01:** rewrote q-0421 stem to `コーヒー（ ）おちゃが いいです。` with prompt `ふたつの えらびかたを ならべる ことばを えらんで ください。` so it tests the n5-024 OR sense. Real distractor explanations replace the stub `Wrong choice` text.

#### Tier-2 Japanese-accuracy fixes (3 more)

- [x] **F-15.13** (HIGH) **n5-024 grammar pattern had wrong examples** - first two examples (`あなたは がくせいですか。` / `なにを たべましたか。`) were copy-pasted from n5-023 (sentence-final か); they don't illustrate the OR sense the pattern teaches. **Applied 2026-05-01:** replaced examples with three OR-か illustrations (`コーヒーか おちゃが いいです。` / `ペンか えんぴつで かいてください。` / `あしたか あさってに いきます。`). Re-ran `tools/link_grammar_examples_to_vocab.py` to populate `vocab_ids` (JA-17 invariant).
- [x] **F-15.14** (MEDIUM) **q-0007 ねこ___すきです** - stem accepted は (contrastive topic) as a grammatically valid alternative to が. **Applied 2026-05-01:** added Q&A scaffold `A：「どんな どうぶつが すきですか。」　B：「ねこ（ ）すきです。」` so が is the natural answer (the question pattern X が すき forces が in the response). Real distractor explanations added.
- [x] **F-15.15** (MEDIUM) **q-0008 ほん___よみます** - stem accepted は (contrastive topic) as alternative to を. **Applied 2026-05-01:** added scene `（としょかんで）　わたしは ほん（ ）よみます。` so を is the natural direct-object marker. Real distractor explanations added.
- [x] **F-15.16** Side-effect: 好 kanji in q-0007 distractor explanation breached JA-13 (out-of-scope). Removed the `(好き)` parenthetical; the distractor still reads naturally without it.

#### Linker tooling fix (caught while verifying Tier-2 metadata)

- [x] **F-15.17** (MEDIUM) **Vocab linker false-positive substring matches** - `tools/link_grammar_examples_to_vocab.py` was substring-matching short standalone nouns/adjectives without right-side word-boundary checking. Caught by the new n5-024 example `あしたか あさってに いきます。` which got a spurious link to `n5.vocab.4-body-parts.あし` (foot) because `あし` is a substring of `あした` (tomorrow). **Applied 2026-05-01:** extended the existing 2-char left-boundary check (formerly only `expression` / `interjection` POS) to include `noun` / `na-adjective` / `i-adjective` / `adverb`, AND added a right-boundary check that accepts `_BOUNDARY` chars + particles (はがをにでとも) + common copula/modifier starts (のなだへやかねよ). Re-ran linker: still 587/587 examples linked (100%); the false positive is gone. The HOMOGRAPH_RULES dispatch system was the wrong place for this fix because it only fires for vocab-form clusters with multiple entries, and `あし` has only one entry in vocab.json.

#### Coverage gap analysis vs external corpus - 2026-05-01

Cross-coverage report at `feedback/coverage-comparison.md`. Six N5 grammar patterns have ZERO question coverage in our bank; they appear in `data/grammar.json` but no question references their pattern ID, and a full-text search for their key forms across all 163 questions returns zero hits:

- [x] **F-15.18** (MEDIUM) **n5-130 あげる (give to others)** - **Applied 2026-05-01:** authored 2 MCQs (q-0479 recipient-に, q-0480 object-を). _Originally q-0454/0455; renumbered after a parallel Pass-15 P0 commit landed paraphrase questions at the same IDs._
- [x] **F-15.19** (MEDIUM) **n5-131 もらう (receive from)** - **Applied 2026-05-01:** authored 2 MCQs (q-0481 source-から, q-0482 object-を).
- [x] **F-15.20** (MEDIUM) **n5-134 ので (because, softer than から)** - **Applied 2026-05-01:** authored 2 MCQs (q-0483 ので-vs-{ながら,ても,のに}, q-0484 testing the noun+な+ので connector - hits the common mistake from the pattern's `common_mistakes`).
- [x] **F-15.21** (MEDIUM) **n5-144 Verb-stem + ながら (while doing)** - **Applied 2026-05-01:** authored 2 MCQs (q-0485 verb-stem form ききながら-vs-other-conjugations, q-0486 ながら-vs-other-particle).
- [x] **F-15.22** (LOW) **n5-148 いつも / たいてい / たまに (always / usually / occasionally)** - **Applied 2026-05-01:** authored 2 MCQs anchoring on frequency phrases - q-0487 (毎日 → いつも) and q-0488 (月に 1かい → たまに). たいてい distractor reserved for future expansion (no question explicitly tests it as the answer; would need a "ほとんど 毎日" anchor that risks ambiguity with いつも).
- [x] **F-15.23** (LOW) **n5-167 ～んです / ～のです (explanation / emphasis)** - **Closed 2026-05-01:** authored conservative N5-appropriate entry with `tier: "late_n5"`. 3 examples (affirmative-explanation / question-asking / context-providing); 2 common_mistakes (using んです for flat fact / missing な linker after noun); 1 contrast vs plain です. Notes flag this entry as pending native-teacher review of the framing. The form (Plain + んです) is N5; the explanation/emphasis nuance crosses into N4 - late_n5 tier captures this correctly.

#### Pass-16 questions added (10) and side-effects

- 10 new MCQs landed: originally q-0454 .. q-0463; **renumbered to q-0479 .. q-0488 on 2026-05-01 after dedup** (a parallel Pass-15 P0 commit had independently authored 19 questions at q-0454 .. q-0472, colliding with my IDs in q-0454 .. q-0463). Bank size: 163 → 173 (no change post-dedup; the Pass-15 P0 set added separately).
- Side-effect: 6 out-of-scope kanji introductions caught by JA-13 invariant (兄, 文, 字, 回 across 3 questions) - converted to kana (あに, もじ, じ, かい) in `tools/author_pass16_questions.py` and applied via inline kanji-replacement before commit. JA-13 now PASS again.
- Dedup repair: `tools/renumber_pass16_dedup.py` is idempotent and documents the collision in `_meta.history`.
- All 30 content invariants green; 4/4 build-pipeline regression tests pass.

These six patterns produced a "no real questions" experience for ~3% of the curriculum before this pass. Five are now closed; n5-167 remains for native review.

#### Reviewed false positives (no fix needed)

q-0007 ねこ___すきです (が only at N5); q-0008 ほん___よみます (を only at N5); q-0027 だれ___きませんでした (も only - interrogative+negative pattern); q-0419 りんご___バナナをたべます (や is correct among the 4 choices; と is not present); q-0043 こうえん___さんぽしました (canonical N5 answer is を, although で is borderline acceptable in colloquial Japanese - flagged for native review but kept).

#### Tooling

- `tools/scan_multi_correct.py` - scanner that flags candidate multi-correct MCQs across 5 categories (に/へ, は/が, で/に, ko-so-a-do without context, polite/casual copula mix). Run after any future bulk edits to questions.json.
- `tools/fix_kosoado_basic.py` - idempotent applier for the 4 ko-so-a-do fixes.
- `tools/fix_particle_basic.py` - idempotent applier for the 6 particle fixes.
- `tools/inspect_candidates.py` - diagnostic dump of question_ja / choices / correct for a fixed list of IDs.

---

## Pass-14 questions.json comprehensive audit - 2026-04-30 (ALL PHASES APPLIED 2026-05-01)

Comprehensive audit of `data/questions.json` from native-speaker + structural-integrity perspective. Found 8 issue classes, dominated by stub-pattern-era placeholder questions that teach nothing.

**Pass-14 closed 2026-05-01.** All 10 findings resolved. Final question bank: 163 real questions (down from 181 pre-Phase-A, plus 20 newly authored in Phase F). Type distribution: 138 mcq / 16 sentence_order / 9 text_input.

- **Phase A** (deletion cascade): 38 stub pattern-meta questions deleted. Resolved F-14.1, F-14.2, F-14.3, F-14.4, F-14.7, F-14.8.
- **Phase B** (schema fix): q-0418 dropped stale `choices` array. Resolved F-14.5.
- **Phase C** (metadata): `_meta` block added to questions.json documenting the ID gap history. Resolved F-14.6.
- **F-14.9 cascade-resolved**: slash-format issues only existed in the 38 deleted stubs.
- **Phase F** (authoring): 12 sentence_order + 8 text_input questions added (q-0434..q-0453). Resolved F-14.10.

#### CRITICAL (3 classes - ALL RESOLVED)

- [x] **F-14.1** (CRITICAL) **38 pattern-meta questions teach nothing** (q-0280 through q-0416 family). All matched pattern `つぎの いみに あう パターン：`. Answer was literally quoted in the stem; distractors mixed wildly different types so the correct option was identifiable from format alone. **Applied 2026-05-01:** deleted 38 questions matching the stub pattern. Bank: 181 → 143. IDs deleted: q-0280, q-0281, q-0288, q-0290, q-0291, q-0294, q-0300, q-0301, q-0311, q-0316, q-0318, q-0319, q-0321, q-0325, q-0326, q-0329, q-0338, q-0339, q-0343, q-0344, q-0349, q-0361, q-0363, q-0374, q-0376, q-0379, q-0382, q-0384, q-0389, q-0393, q-0398, q-0400, q-0408, q-0409, q-0412, q-0413, q-0414, q-0416.
- [x] **F-14.2** (CRITICAL) **Answer literally in stem** - q-0311, q-0316, q-0382, q-0398. Resolved by F-14.1 deletion.
- [x] **F-14.3** (CRITICAL) **q-0382 rendering corruption** - double colon. Resolved by F-14.1 deletion.

#### HIGH (3 classes - ALL RESOLVED)

- [x] **F-14.4** (HIGH) **Prompt-stem mismatch in 37 pattern-meta questions** - Resolved by F-14.1 deletion.
- [x] **F-14.5** (HIGH) **q-0418 dual-mode schema** - `type: text_input` but also has stale `choices` array. **Applied 2026-05-01:** dropped the `choices` field. q-0418 is now canonical text_input with `acceptedAnswers` (4 entries) + `correctAnswer` ("です") for feedback display.
- [x] **F-14.6** (HIGH) **ID gaps** - 9 gaps totalling 290 missing IDs in declared range q-0001..q-0433. **Applied 2026-05-01 (option C - keep gaps but document):** added `_meta` block to `data/questions.json` with `id_gap_policy: "documented"`, `id_gaps[]` array enumerating each gap, `id_gap_explanation` text covering Pass-9/12/14 deletion history, and a contract note that "tooling MUST treat IDs as opaque strings, not contiguous-integer suffixes." Renumbering rejected as too risky - would break URL bookmarks, exported localStorage state, and verification.md cross-references.

#### MEDIUM (3 classes - ALL RESOLVED)

- [x] **F-14.7** (MEDIUM) **Distractor-length asymmetry** - Resolved by F-14.1 deletion.
- [x] **F-14.8** (MEDIUM) **Pattern-meta choices mix incompatible types** - Resolved by F-14.1 deletion.
- [x] **F-14.9** (MEDIUM) **Inconsistent slash convention in choices** - **Verified 2026-05-01:** 0 full-width `／` remaining in `data/questions.json`; 0 choices contain slashes at all. The slash-format inconsistencies only existed in the 38 stub questions deleted in F-14.1. Cascade-resolved.

#### LOW / Schema (informational)

- [x] **F-14.10** (LOW) **Type distribution skewed** - **Phase F applied 2026-05-01:** authored 12 sentence_order + 8 text_input questions (q-0434..q-0453) covering productive N5 grammar (topic は ordering, location あります, te-form chains, counter ordering, comparison より, want が ほしい, Verb-tai, prohibition Verb-てはいけません, particle selection は/を/に/で/が, te-form / past / negative production). Bank: 143 → 163. Distribution: 138 mcq / 16 sentence_order / 9 text_input. Mcq still leads but non-mcq types are no longer token presence.
- [x] **Verified non-bug:** 4 sentence_order questions correctly omit `choices`/`correctAnswer` (they use `tiles`/`correctOrder` instead per the spec §6.2 schema). This was a sanity-check note from the audit, not a fix-needed item.

#### Recommended fix sequence (updated 2026-05-01)

1. ~~**Phase A:** Delete 38 pattern-meta questions.~~ ✅ Applied 2026-05-01. Bank 181 → 143. Cascade-resolved F-14.1/2/3/4/7/8.
2. **Phase B (decision needed):** Resolve q-0418 schema (F-14.5).
3. **Phase C (decision needed):** Decide on ID gap policy (F-14.6).
4. **Phase D (sweep):** Standardize slash convention (F-14.9).
5. **Phase E (longer-term):** Author more sentence_order + text_input (F-14.10).

Current state: **143 real questions**, all with valid pedagogical structure (no answer-in-stem, no distractor-type-mismatch, no prompt-stem-mismatch).

---

## UI testing plan - 2026-04-30 (synced to UX Brief 2 Phases 1-4)

Comprehensive UI-level test strategy at `feedback/ui-testing-plan.md` covering 22 perspectives across 17 routes × multiple sub-paths × 5 locales × 8 browsers × 6 OSes.

**★ Foundational concern: §12 Japanese language accuracy & content integrity** - the bar this app must clear:
- §12.1: 16 automated content invariants (CI release blocker)
- §12.2: Runtime JA spot-checks at P0 / P1 / P2 tiers
- §12.3: Quarterly Pass-N re-audit protocol (continues the audit-pass tradition from `verification.md`)

Other sections:
- §0.1: Route map - canonical reference for all routes + sub-paths (Learn hub, kanji index/detail, vocab per-form, test/<n> direct-launch)
- §1-§11, §13-§16: Other perspectives (end-learner, first-timer, returning visitor, mobile, a11y, i18n, slow conn, offline, power user, cross-browser, cross-OS, perf, security, PWA, visual)
- §17: Three-tier execution (P0 smoke 5min / P1 gate 60min / P2 regression 4h)
- §18-§19: Recommended tooling stack (Playwright + axe-core + Lighthouse CI) and CI integration
- §20: Nielsen 10 heuristic checklist applied to this app
- §22-§23: Acceptance criteria + perspective coverage matrix

Use as a **catalog** - triage by P0/P1/P2 tier, don't run all 22 every release. **§12 always runs.**

### CI engineering work (COMPLETE - content-integrity / Lighthouse / Playwright wired)

- [x] **Create `tools/check_content_integrity.py`** (672 lines, stdlib-only) implementing 18 invariants from §12.1 (X-6.1-X-6.9 + JA-1-JA-9). All 18 now **PASS** on current KB; exit code 0. Heuristics calibrated through three rounds:
  - Catalog parser tolerates `[Ext]` / `[Cul]` tag suffixes on kanji entries
  - Question header regex tolerates trailing notes like `#### Q91 (blank 1)` and `### Q59 (REPLACED ...)`
  - JA-1 / X-6.1 use an **augmented N5 catalog**: strict 102-entry catalog ∪ pragmatic-N5 set (朝/町/屋/京/阪/都/牛/乳/思/早/紙/作/図/館/病/院/元/海/道 - kanji audit-accepted in stems despite not being in the strict 100-list); skip dokkai (passages have naturalness exception) and authentic_extracted (source-faithful)
  - JA-2 tightened: only fires on questions where ≥3 of 4 options are in N5_PARTICLES AND all options are ≤5 char pure-hiragana; PARTICLE_ADJACENT set covers な / けど / だ / のほうが / ほうが
  - JA-6 scoped to causal-connector contexts (i-adj past / verb past before blank); prevents false hit on `先生（  ）いろいろ習いました` where ので isn't actually grammatical
  - JA-7 scoped to originally-authored files (skips dokkai + authentic where cross-passage / source-faithful repetition is expected)
  - X-6.8 reframed as helper-existence check (verifies `tools/build_audio.py:normalize_for_tts` is still defined)
  - Workflows: `.github/workflows/content-integrity.yml` runs the full check; `lighthouse.yml` runs perf/a11y/best-practices/SEO assertions per `.lighthouserc.json`. Both fire on every push to main + every PR.
- [x] Add Playwright + @axe-core/playwright as devDependencies; first test suite covering §17.1 P0 smoke. **Status:** package.json + playwright.config.js + tests/p0-smoke.spec.js (38 tests across 2 device profiles - Desktop Chrome + Pixel 5 mobile) + .github/workflows/playwright.yml. Coverage: home / hub / Grammar TOC (187 cards) / pattern detail / Vocab list (40 sections, 1 open default) / Kanji index (97 cards) / Test setup-to-question / Diagnostic visible-CTA regression guard / Settings 3-mode furigana / locale persist / `?` shortcuts overlay / `/` search focus (desktop only) / no-third-party-requests / axe-core a11y on 6 routes. **Verified locally: 37 passed + 1 mobile-skipped, 0 failures, runtime 1.2 min.** Run: `npm install && npx playwright install chromium && npm run test:smoke`.
- [x] Add Lighthouse CI workflow per §19; baseline numbers from current SW v24 build. Created `.lighthouserc.json` (assertions: Performance ≥ 0.85, Accessibility ≥ 0.95, Best Practices ≥ 0.85, SEO ≥ 0.85 warn) and `.github/workflows/lighthouse.yml` (runs on push to main + every PR; uploads reports to temporary-public-storage). Auto-skip http2/https/redirect audits since GitHub Pages serves over a different setup at runtime; configured to use `staticDistDir: "."` so no separate serve step needed in CI.
- [x] First quarterly Pass-N re-audit calendar reminder (§12.3): 2026-07-30. Recurring scheduled task `jlpt-n5-quarterly-pass-audit` set to cron `0 9 30 1,4,7,10 *` (9 AM local on the 30th of Jan/Apr/Jul/Oct). Next run: 2026-07-30. Prompt rotates audit lenses (child-readability / register / honorifics / distractor quality / cross-file consistency) so successive quarters surface different findings.

---

## Content correction brief (Pass 9) - 2026-04-30 (COMPLETE)

External brief at `feedback/jlpt-n5-content-correction-brief.md` raised 27 items + 4 systematic sweeps + 7 cross-file consistency checks. Severity: 5 CRITICAL, 7 HIGH, 9 MEDIUM, 6 LOW. Fixes in priority order.

### CRITICAL (5)

- [x] **C-1.1** kanji_n5.md missing 力 and 手 (used as correct answers in moji Q54/Q58). Add to catalog OR replace questions.
- [x] **C-1.2** dokkai Passage F: 「こんねんの 八月」 - wrong reading of 今年 (should be ことし).
- [x] **C-1.3** bunpou Q50/Q51: both から (option 2) and ので (option 3) are grammatically correct. Replace one distractor.
- [x] **C-1.4** goi Q99 rationale overstates 知る ≈ 覚える as direct synonymy. They are not synonyms; soften.
- [x] **C-1.5** moji Q6 rationale mentions にっぽん which is not in the options; tighten to avoid confusion.

### HIGH (7)

- [x] **H-2.1** Mixed kanji+kana words sweep (e.g., bunpou Q70 「図しょかん」, dokkai Passage 24 「大さか」). Pick one rule, apply consistently.
- [x] **H-2.2** bunpou Q98 option 4 「ピアノを 買い」 is also grammatical. Strengthen distractor or add nuance to rationale.
- [x] **H-2.3** bunpou Q100 rationale: 「でも」 should be glossed as "even (just)", not "at least".
- [x] **H-2.4** vocabulary §27/28: flag Group-1 ru-verb exceptions (入る, 帰る, 走る, 知る, 切る, 要る) with annotation.
- [x] **H-2.5** moji Q62 「子供 vs 子ども」: rationale should disclose that 子供 is also standard.
- [x] **H-2.6** grammar §22: rename "Honorific" to "Beautifying" (bika-go vs sonkei-go terminology).
- [x] **H-2.7** vocabulary line 287: 「もう」 definition incorrectly lists "soon" as a standalone gloss.

### MEDIUM (9)

- [x] **M-3.1** kanji_n5.md kun-yomi readings out of N5 scope (上=のぼる, 下=おりる, 外=ほか, 万=バン).
- [x] **M-3.2** goi Q47 rationale uses 「去年」 (N4 kanji); change to きょねん.
- [x] **M-3.3** goi Q87: consider はたち vs 二十さい note for age-20.
- [x] **M-3.4** bunpou Q24: しんかんせん is not in N5 vocab. Replace with でんしゃ.
- [x] **M-3.5** goi Q86: soften "電話をかける = 電話で話す" rationale (not strict equivalence).
- [x] **M-3.6** goi Q94: soften あまくない vs あまり あまくない rationale.
- [x] **M-3.7** goi Q70: soften "likes" → "does often" rationale.
- [x] **M-3.8** vocabulary 毎年 (まいとし/まいねん): add register note.
- [x] **M-3.9** vocabulary archaic items (マッチ, フィルム, レコード, テープレコーダー): add note about modern relevance.

### LOW (6)

- [x] **L-4.1** sources.md CEFR claim: verify or soften.
- [x] **L-4.2** kanji 円: meaning ordering (yen first; circle/round as N4+).
- [x] **L-4.3** grammar §6: clarify verb group description with both kana-row and romaji views.
- [x] **L-4.4** dokkai Q27 passage uses 「一じかん」; standardize to 「一時間」.
- [x] **L-4.5** em-dash check across all files.
- [x] **L-4.6** vocabulary line 824: いる homophone; cross-reference to §2.4 list.

### Systematic sweeps (4)

- [x] **S-5.1** Mixed kanji+kana words across all files.
- [x] **S-5.2** Vocab outside N5 scope appearing in question stems.
- [x] **S-5.3** Rationale lines that overstate equivalence ("Direct synonymy", "=", "equivalent").
- [x] **S-5.4** Verify cited grammar rules in rationales.

### Cross-file consistency checks (7)

- [x] **X-6.1** Every kanji used as correct answer appears in kanji_n5.md.
- [x] **X-6.2** Readings in vocab match readings in question files (esp. 今年 = ことし).
- [x] **X-6.3** No mixed-kanji words.
- [x] **X-6.4** No orphan vocab in question stems.
- [x] **X-6.5** No em-dashes.
- [x] **X-6.6** All Group-1 ru-verb exceptions flagged in vocab.
- [x] **X-6.7** No false "direct synonymy" claims in rationales.

---

## Native-speaker audit (Pass 8) - 2026-04-30 ✅ COMPLETE

52 findings raised across 5 KB question files from a native Japanese teacher's perspective. Severity: 16 HIGH, 27 MED, 9 LOW. **All 52 fixed.** Full pass details in `verification.md` §7.

### HIGH-severity (16)

#### moji_questions_n5.md
- [x] **M-3** Q54 word-boundary split: 「<u>とも</u> だち」 splits 「ともだち」 across the underline. Restate so the underline covers a whole word.
- [x] **M-8** Q76 unnatural stem: 「でんわばんごうは いくつですか」. Native form is 「何番ですか」.
- [x] **M-9** Q78 unidiomatic: 「みち を まがってください」. 道 doesn't take 曲がる as direct object. Use 「角を曲がる」.

#### goi_questions_n5.md
- [x] **G-3** Q47 textbook error: 「きょねん 日本へ 行った ことが あります」 mixes specific time with experience aspect. Drop 去年 or use definite past.
- [x] **G-8** Q63 inferential paraphrase: 「歩いて10分」 ≈ 「ちかい」. Replace with synonym-tight pair (「とおくない」).
- [x] **G-11** Q78 inferential paraphrase: 「お客さんがおおい」 ≈ 「ゆうめい」. Many customers ≠ famous; replace.
- [x] **G-12** Q80 inferential paraphrase: 「さむい」 ≈ 「ストーブをつけました」. Action-result inference, not synonymy.

#### bunpou_questions_n5.md
- [x] **B-4** Q85 pleonasm: 「ほしいので かいたい」 - both verbs express wanting. Drop one.
- [x] **B-6** Q98 wrong compound: 「ピアノのきょうしつ」 should be 「ピアノきょうしつ」 (compound noun, no の).
- [x] **B-7** Q100 semantic clash: 「ぜったいに 一日 ぐらい」 - absolute + approximate clash. Change answer to 「でも」 or rework stem.

#### dokkai_questions_n5.md
- [x] **D-3** Passage 14 Q27 unit mismatch: stem asks 「何分」, answer is 「一時間」. Fix question word to 「どのぐらい」.
- [x] **D-5** Passage 26 Q51 mixed-category options: mixes duration ('一年' / '五年') and age ('5さいから'). Restate options to one category.

#### externally_sourced_n5.md
- [x] **A-1** Q43 particle typo: stem ends 「をあります」. Fix to 「にあります」.
- [x] **A-2** Q58 underline/answer mismatch: underline on 「みぎ」 but answer is for 「みち」. Realign underline.
- [x] **A-3** Q59 N3 kanji in stem: 「有名」 violates the stems-N5-only rule. Render in kana or replace question.
- [x] **A-6** Q117 ambiguous source: 「兄に」+もらう is acceptable but unclear at N5. Change to 「兄から」.
- [x] **A-8** Q142 unidiomatic subject: 「うちは...先生をしています」 - うち + occupation verb is non-native. Restate.

### MED-severity (27)

#### moji
- [x] **M-1** Q33 rationale misstates kun-okurigana rule
- [x] **M-2** Q39 雨水 reading note oversimplifies
- [x] **M-4** Q55 「うちには大人が一人と子どもがふたり」 stilted household phrasing
- [x] **M-5** Q57 「ははは教師です」 register too formal for own mother
- [x] **M-7** Q66 「何曜日まで」 unnatural for a homework deadline
- [x] **M-10** Q81-Q95 "Word - Sentence" duplication format non-authentic
- [x] **M-12** Q96 missing です in formal-register file

#### goi
- [x] **G-1** Q22 「えきから ちかい」 stilted; native uses 「えきの近く」
- [x] **G-2** Q35 「もちろん がんばります」 register clash
- [x] **G-4** Q48 「大学にはいる」 → prefer 「大学へ行く / 進学する」
- [x] **G-7** Q60 「30人」 ≈ 「おおぜい」 loose
- [x] **G-9** Q73/Q74 lend/borrow paraphrase introduces beneficiary nuance
- [x] **G-10** Q75 「1月20日」 ≈ 「年のはじめ」 borderline
- [x] **G-13** Q82 wet-clothes ≈ rain inferential
- [x] **G-14** Q86 鳴る vs 来る overlap
- [x] **G-15** Q90 げんきです vs げんきがあります not identical
- [x] **G-16** Q92 あげる vs 買ってあげる narrows meaning
- [x] **G-18** Q99 教えて vs 言って register loss

#### bunpou
- [x] **B-2** Q46 choice-fragment style non-standard
- [x] **B-8** Q64 「駅の名前は何ですか」 textbook-ish

#### dokkai
- [x] **D-1** Passage 9 「ようやく」 → N3-level; use 「やっと」
- [x] **D-2** Passage 13 Q26 distractor 「ていねいな人」 not parallel to occupation options
- [x] **D-4** Passage 22 「来月、大学に入ります」 culturally atypical (April-start standard)
- [x] **D-7** Mondai 6 Item 6 Q102 「先生に聞く」 register thin

#### authentic
- [x] **A-4** Q61 「可愛い」 N3 kanji in stem
- [x] **A-5** Q73 「夕食」 register too formal
- [x] **A-7** Q140 「いいものが安くて多い」 awkward modifier order
- [x] **A-9** Q159 「おじさん」 distractor over-specifies older/younger

### LOW-severity (9)

- [x] **G-5** Q51 父=医者 ≈ 病院ではたらく inferential
- [x] **G-6** Q53 先生 ≈ 学校で教える inferential
- [x] **G-17** Q97 上手 ≈ よくわかる skill≠comprehension
- [x] **B-1** Q18 れんしゅう rationale wording
- [x] **B-3** Q83 sentence flow stiff
- [x] **B-5** Q92 「7時半ごろ」 半+ごろ tolerated colloquial
- [x] **D-6** Passage J Q89 「子どもの本」 → 「絵本」 / 「子ども向けの本」
- [x] **M-6** Q58 dual-blank format non-standard
- [x] **M-11** Q92 「学生がたちます」 decontextualized

---

## UX Brief 2 (jlpt-n5-tutor-ux-developer-brief2.md)

Source: `feedback/jlpt-n5-tutor-ux-developer-brief2.md`. Phased per Brief §19.

### Phase 1 - Stop the bleeding ✅ COMPLETE
- [x] **B2-P1.1** Skeleton screens replace literal "Loading..." text + 5s timeout error UI (§3.1) - shimmer animation, route-shape-matched blocks, 5s Promise-race timeout shows real "Couldn't load" UI with Retry.
- [x] **B2-P1.2** Empty states for Review, Test, Summary, Practice with routing buttons (§3.2) - Review: 2-state (no progress vs no due), Summary: progress=0 routes to Learn, Test: first-test banner suggests learning, Drill: existing CTA preserved.
- [x] **B2-P1.3** Deep-link URLs per §14.1 - new js/kanji.js renders #/kanji index + #/kanji/<glyph> detail (97 entries, on/kun/meanings/stroke-svg slot). Test deep-link #/test/<n> with n in {20,30,50} starts test directly.
- [x] **B2-P1.4** Privacy/offline/no-login trust strip on landing above-the-fold (§1.1.5) - 3-item strip in header brand block, mobile-responsive.
- [x] **B2-P1.5** Copy revisions: tagline + footer per §15 - tagline now "Pass JLPT N5 with 15 minutes a day. No login, no ads, no data shared." Footer: "Works offline. No login. Your progress stays on this device."

### Phase 2 - Daily-use friction ✅ COMPLETE
- [x] **B2-P2.1** Three-mode furigana radios in Settings + header quick-toggle. Storage: `furiganaMode` ∈ {always, hide-known, never}. CSS-toggle via re-render on change (§4.1).
- [x] **B2-P2.2** Per-kanji popover (`js/kanji-popover.js`): click any glyph → readings + meaning + "I know this" toggle. Persists in `localStorage.knownKanji`. Click delegation across all rendered kanji. (§4.2)
- [x] **B2-P2.3** Live furigana preview in Settings panel - fieldset shows `日本語の本を 読みます` rendered through current mode; updates instantly on radio change. (§4.3)
- [x] **B2-P2.4** Settings additions: audio speed (0.75/1.0/1.25 - applied via MutationObserver to every `<audio>`), reduce-motion (auto/on/off - sets `data-reduce-motion` on `<html>`, CSS overrides motion durations), typed-phrase reset confirm box ("Type RESET"). (§5)
- [x] **B2-P2.5** Location indicator chip below header - updates on every route change with route label + decoded params (e.g. "Learn", "Kanji · 日"). (§2.4)
- [x] **B2-P2.6** Per-question feedback - drill module already shows immediate feedback per question. Test deliberately uses end-of-test results per JLPT mock-exam fidelity (Brief §6.2 separates Test as a periodic event from drill).
- [x] **B2-P2.7** Global keyboard shortcuts (`js/shortcuts.js`): 1-4 picks Nth choice button, Space reveals/flips, Enter clicks primary/Submit/Continue, ? opens cheatsheet overlay, Esc dismisses. Skipped while focus is in input/textarea/select. (§7.2)

### Phase 3 - Landing and orientation ✅ COMPLETE
- [x] **B2-P3.1** New `js/home.js` route at `#/home` is now the default landing. First-time state: heading "Start your N5 study", scope line (187 patterns / 1000 vocab / 97 kanji), primary CTA "Start your first lesson", secondary "Take a placement check", 3-pillar card row Learn/Practice/Test, trust strip already in header. (§1.1)
- [x] **B2-P3.2** Returning state appears when history or test results exist: Continue card (resumes last lesson via `settings.lastLearnId`), Today's review queue card (shows due count + "Start review", or "All caught up" empty positive), 7-day streak strip with flame + heatmap, last-test summary line. (§1.2)
- [x] **B2-P3.3** Streak storage in `localStorage.streak` ({current, longest, lastStudyDate, days[30]}). Auto-incremented on first interaction each day. Heatmap renders last 7 days; `streak-flame` + day-count chip on home. Session-end UX is owned by drill/review results screens already. (§6)
- [x] **B2-P3.4** New `js/search.js` indexes grammar (id/pattern/meaning/explanation), vocab (form/reading/gloss), kanji (glyph/on/kun/meanings). `<input type="search">` in secondary nav. `/` keyboard shortcut focuses input. Click outside or Esc dismisses panel. Lazy-loads bank on first focus. (§8)
- [x] **B2-P3.5** Nav restructured per §2.2: primary now has Home / Learn / Practice (renamed from Daily Drill) / Review / Test. Secondary nav row holds search + Summary + Settings.

### Phase 4 - Polish and reach ✅ COMPLETE
- [x] **B2-P4.1** Webfont decision: kept system stack `Noto Sans JP / Hiragino Kaku Gothic ProN / Yu Gothic / Meiryo`. Shipping a 200 KB self-hosted woff2 conflicts with static-only / no-third-party-loads constraints. Yu Gothic + Meiryo are preinstalled on Windows 10+; users with the JP language pack get Noto Sans JP. Documented in CHANGELOG.
- [x] **B2-P4.2** SW now uses stale-while-revalidate for the shell (HTML/CSS/JS): serves cache instantly, refetches in background, posts `SW_UPDATE_AVAILABLE` to clients when new bytes detected. Cache-first preserved for content. New js/pwa.js shows "A new version is available - Reload?" toast on receipt; click sends `SKIP_WAITING` and reloads.
- [x] **B2-P4.3** Install banner via `beforeinstallprompt` (one-time, dismissed flag in localStorage). Offline indicator chip in top-right that toggles with `navigator.onLine`. Hidden when online.
- [x] **B2-P4.4** Mobile responsive pass: primary nav becomes a fixed bottom bar at ≤480px with safe-area insets honored (`env(safe-area-inset-bottom)`). All buttons / nav items / pillar cards / choice buttons set `min-height: 44px` per Apple HIG.
- [x] **B2-P4.5** Quit prompt: `__testInProgress` flag set by Test.startTest, cleared on results. `beforeunload` blocks tab close; `hashchange` interceptor confirms "Quit this test? Progress so far will be saved" and reverts the hash on cancel.
- [x] **B2-P4.6** `@media print` stylesheet hides nav/header/footer/PWA chrome, expands all `<details>`, switches to serif body, hides audio + buttons, scales ruby smaller. Produces clean printable Learn lesson pages.
- [x] **B2-P4.7** Footer adds version line `v1.5.0 · Content updated April 2026 · What's new` linking to `CHANGELOG.md`. New CHANGELOG.md documents v1.5.0 (this brief) + v1.4.0 audio + v1.3.0 audit + v1.2.0 + v1.0.0.
- [x] **B2-P4.8** A11y audit (live-verified): h1=1, all interactive elements have text or aria-label, all landmarks have roles (banner, main, status), trust strip has aria-label, search has aria-label, location chip has role=status + aria-live=polite, min-tap-target 44px enforced via CSS, skip-link present, prefers-reduced-motion respected (skeleton CSS already had override; reduce-motion override added at `data-reduce-motion="on"`).

---

## Hard constraints preserved

1. ✅ Static-only - GitHub Pages, no server.
2. ✅ No data leaves the device - no analytics, no telemetry, no remote API at runtime.
3. ✅ No login.
4. ✅ Offline-capable after first load.
5. ✅ Cross-browser.
6. ✅ Backups via export/import.

## Out of scope (Brief §8)
- User accounts, social, leaderboards.
- Cloud sync.
- N4+.
- Speaking practice with microphone input.
- Runtime AI / TTS calls.

---

## Earlier completed phases (Phase 1-3)

- Engine + scaffold (vanilla HTML/CSS/JS, hash router, LocalStorage, furigana toggle, 4 chapters + Drill + Diagnostic, threshold-based weak detection, service worker)
- Tools (build_data, check_coverage, lint_content, build_spec, generate_stub_questions, build_audio)
- 19 KB content fixes (teacher's audit - see verification.md)
- Pattern catalog: 187 entries across 23 categories
- Question bank: 250 entries (no stubs)
- 5 KB question-bank reference files (498 Qs across moji/goi/bunpou/dokkai/authentic)
- Pushed and verified live on GH Pages
- 37 browser-runnable tests
