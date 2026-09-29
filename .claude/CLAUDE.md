# JLPTSuccess - Project Instructions for Claude

## Permission posture

The user has granted blanket autonomous-operation authorization for this repo. See `.claude/settings.local.json` for the per-tool allow / deny lists.

## BINDING governance rules (set 2026-05-04)

These rules override default helpful-assistant behavior. Read them at session start and before every action.

### Rule 1 - N4 WORK-BLOCK LIFTED (2026-06-19)

**LIFTED 2026-06-19** by explicit user directive ("unblock n4"): N4 work is RESUMED, and the permission-deny on `/N4/` (the `Edit(**/N4/**)` / `Write(**/N4/**)` rules) has been removed from the global settings.json. The original block (set 2026-05-04) is struck through below, retained for history but no longer in effect. NOTE: Rule 2's "even a directly-worded N4 fix request triggers Rule 2" clause and Rule 5's "touching `/N4/` is a POLICY BLOCK" exit condition referenced this block — they no longer apply to `/N4/`.

~~**Do NOT touch anything under `/N4/`.**~~ (Historical, lifted 2026-06-19) Specifically:

- Do not edit any file inside `/N4/` (data, code, KB, audio, SVGs, tests, tools, configs, anything).
- Do not run any builder under `/N4/tools/` (`build_n4_*.py`, `enrich_*.py`, etc.).
- Do not commit changes that affect `/N4/`.
- Do not push changes that affect `/N4/`.
- Do not generate Playwright tests for, or run smoke tests against, `/N4/`.
- The N4 card is hidden from the JLPTSuccess homepage. Do not re-enable it.
- The N4 deploy at `/JLPTSuccess/N4/` continues to serve (legacy URL still works), but the **product is paused** - no further development, no further deploys touching that subtree.

**The block is lifted only when the user issues an explicit, unambiguous instruction like "unblock N4" or "resume N4 work."** Anything else - even a directly worded request to fix a specific N4 issue - should trigger Rule 2.

### Rule 2 - Finish one job before starting another

When the user asks for ANY new work, BEFORE starting:

1. Identify the current outstanding job (the most recently active task that is not yet complete).
2. Surface it back to the user explicitly: "Before I start <new request>, the current outstanding job is <X>. Should I finish that first, or pause it and switch?"
3. **Wait for an explicit re-confirm** ("yes do <new request>", "switch", "drop X and do <new request>") before starting the new work.
4. If the user says "finish X first" - finish X, then come back and ask again.

This applies even when the new request looks small or trivial. The user has explicitly requested this discipline; do not skip it to be more "helpful."

If there is no outstanding job (e.g., previous work was committed and pushed cleanly), proceed with the new request directly - no reminder needed in that case.

### Rule 3 - Keep N4 history intact

The /N4/ subtree is in the migrated state from 2026-05-04. Even though it's blocked from further work, the existing files are valid and tested. Do not delete or refactor them. If a tooling issue forces an N4 file edit (e.g., a security fix in shared dependencies), surface it to the user as an exception request rather than acting unilaterally.

### Rule 4 - Always propagate learnings to procedure manual + audit prompts (set 2026-05-15)

Whenever an audit cycle, fix batch, methodology change, new CI invariant, new false-positive class, or other generalizable learning is produced, the following docs MUST be updated **as part of the same commit** (or the immediately-following commit if grouping for cleanliness) — **without being asked**:

1. **`JLPT Common/procedure-manual-build-next-jlpt-level.md`** — the cross-level build manual (sits in its own git repo: `gauravaccentureproducts/JLPT-Common`, embedded as a submodule of JLPTSuccess). Add to the most recent Appendix (F as of 2026-05-15), or open a new Appendix when the learning class is significantly new. Capture: methodology, false-positive classes documented, CI invariants added, anti-patterns observed, sample/heuristic thresholds. Style: actionable for an Nx-level builder, NOT N5-narrative — abstract the lesson.

2. **`N5/prompts/Japanese language Accuracy check.txt`** — the audit prompt. Add new audit categories (A-numbered), new false-positive classes (FP-numbered), and update the closing block with the session-added CI invariants.

3. **`N5/prompts/N5Improvement.txt`** — the improvement prompt. Add new Section-10 anti-items + new Phase-0 regression-check blocks (validated to return 0 against the current corpus).

4. **`N5/docs/AUDIT-COVERAGE-YYYY-MM-DD.md`** — when the change is audit-related, update or append to the coverage matrix + the "future native-human review" section.

**This rule applies WITHOUT being asked.** Do not surface "should I update the manual?" as a question — just do it as part of the same commit. The user has set this discipline explicitly so methodology drift between code-state and documentation never happens. If you find yourself thinking "the user didn't ask for the manual update," that's the cue to do it anyway.

**Exception:** if the change is purely mechanical (renaming a file, fixing a typo, settings change) with no methodology implication, the doc update can be skipped — but flag it briefly in the commit message ("skipped doc update; mechanical change only").

**Practical commit pattern:** when wrapping up a substantive change, before writing the commit message, list the 4 doc files above and ask yourself per-file: "did this change produce a learning that belongs here?" If yes, edit it; if no, skip. The commit message should note which docs were updated.

**Writing discipline for audit docs (added 2026-05-15):** every audit-coverage, reconciliation, or native-teacher report MUST use bounded phrasing — never absolutist phrasing — when describing coverage. Prefer "every X *in the corpus snapshot scanned*" over "every X"; prefer "0 findings *against the N patterns scanned*" over "0 findings"; prefer "addressed for M of N items in scope" over "RESOLVED"; prefer "closed against currently-observed values" over "closed enum"; prefer "JA-NN prevents re-introduction of *these specific patterns*" over "JA-NN locks the gain"; prefer "saturated *against this prompt's pattern set*" over "saturated" or "converged"; prefer "CI invariants at this checkpoint" over "Final CI count". A future JLPT exam, native reviewer, or institutional adopter reads audit docs as quality-coverage claims; terminal/absolutist language overclaims and breaks the trust contract when an item-class outside our audited scope surfaces. The full rewrite table + a Phase-0 regression check live in `N5/prompts/Japanese language Accuracy check.txt` (WRITING DISCIPLINE FOR AUDIT DOCS section) and `N5/prompts/N5Improvement.txt` (Phase-0 Audit-doc writing-discipline scan).

### Rule 5 - Cross-artifact synchronization protocol (set 2026-05-17)

**Generalizes Rule 4 from "the 4 doc-propagation files" to a 9-class artifact set.** Rule 4 still applies — when an audit cycle / fix batch / methodology change produces a learning, the 4 docs (procedure manual, accuracy prompt, N5Improvement, audit-coverage) must update in the same commit. Rule 5 extends this to every artifact class in the project, triggered on every change (not just audit-cycle changes).

**The 9 synced artifact classes:**

1. **Specifications** — `N5/specifications/JLPT-N5-Current-Implementation-Spec.md`, ADRs, schema definitions, acceptance criteria.
2. **Code** — `N5/js/*`, `N5/tools/*`, `.github/workflows/*`, build scripts, migration helpers.
3. **Data / content** — `N5/data/*.json` (grammar / vocab / kanji / reading / listening / questions / papers / version), `N5/locales/*.json`, fixtures.
4. **UI** — `N5/index.html`, `N5/learn/**/index.html`, `N5/kanji/**/index.html`, `N5/reading/**/index.html`, etc.; rendered surfaces, copy strings, accessibility attributes, themes.
5. **Bug tracker** — `N5/specifications/test-scenarios-by-specialist-perspective.xlsx` "User Reported Bugs" sheet (BUG-NNN canonical).
6. **Test scenarios** — same xlsx 14 category tabs (A. Japanese language..N. End-user POV); `tools/check_content_integrity.py` (the JA-NN content-integrity invariants — the script is the source of truth for the live count); Playwright + axe-core P0 smoke suite.
7. **Prompts** — `N5/prompts/Japanese language Accuracy check.txt`, `N5/prompts/N5Improvement.txt`, system prompts, autonomous-loop prompts.
8. **Procedure manuals** — `JLPT Common/procedure-manual-build-next-jlpt-level.md` (submodule), runbooks, deploy playbooks.
9. **User-facing docs** — `N5/README.md`, `N5/README.hi.md`, `N5/CHANGELOG.md`, `N5/PRIVACY.md`, `N5/NOTICES.md`, `N5/CONTENT-LICENSE.md`, `N5/AUDIO.md`, `N5/SELFHOST.md`, `N5/TASKS.md`, plus `N5/docs/*`.

**The sync trigger:** whenever ONE artifact changes (the SOURCE), before committing, every OTHER artifact that references or implements the changed thing (DEPENDENTS) must be updated in the same change set. Atomicity is required — either all dependents update or none do. The dependency matrix + commit-time checklist + INV-N invariant catalog live in `N5/docs/cross-artifact-sync-map.md` (the operational handbook for this rule).

**Sync invariants currently wired** (subset of the protocol's INV-1..INV-10):

- INV-4 → **JA-107** (`version.json.counts` ↔ live data corpus sizes)
- INV-5 → **JA-108** (`N5/locales/*.json` key-set parity across all locales)
- INV-7 → JA-15 (audio refs) + JA-17 (vocab_id refs) + JA-82 (`_meta.see_also` refs) + JA-100 (kanji↔vocab form) — partial coverage; passage_id/pattern_id cross-corpus refs not yet enforced
- INV-10 → **JA-109** (procedure manual + prompts → script references resolve to actual files)
- INV-9 → Section 25.8 of implementation spec (every closed-bug invariant lineage tabulated)

**Practical commit pattern (Rule 5 extension to Rule 4's pattern):** when wrapping up ANY substantive change, before writing the commit message, walk the 9 artifact classes above and ask per-class: "did my change touch this class, or does my change require an update in this class?" If yes, edit it in this commit; if no, skip. The commit message must name every artifact class touched. The structured-report emitter at `tools/cross_artifact_sync_report.py` automates the walk for tooling-friendly contexts; for human-driven changes the checklist lives in `N5/docs/cross-artifact-sync-map.md`.

**Exit conditions** (per the protocol):
- CLEAN EXIT — every dependent updated, all CI invariants pass, CHANGELOG documents the ripple.
- POLICY BLOCK — a required update would violate a binding rule (e.g., touching `/N4/` is blocked by Rule 1). Surface, do not partial-sync.
- OSCILLATION — two iterations cannot reach consistency. Surface and stop.
- CAP — 30 cross-artifact iterations in one change. Surface for review.

**Existing drift is fixed in the same change set** (per the protocol): if propagating a fresh change reveals pre-existing drift in any artifact class, fix it inside this commit. Drift compounds — letting one slip means the next change inherits the gap.

## Operational notes

- Live URL: https://gauravaccentureproducts.github.io/JLPTSuccess/
- Default branch: `master`
- Repo: `gauravaccentureproducts/JLPTSuccess`
- N5 is the only currently-active level.
- Pre-migration backups remain at `gauravaccentureproducts/jlpt-n5-tutor` and `…/jlpt-n4-tutor`. Do not push to those.
