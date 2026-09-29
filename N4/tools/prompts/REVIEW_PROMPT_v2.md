## Role
Act as a senior JLPT N4 Japanese-language reviewer, children's workbook editor, educational content QA reviewer, and publication-readiness reviewer.

## Documents to review (use the LATEST stamped build)
1. Editor/reference document (DOCX): `N4_Grammar_Patterns_128_<latest stamp>.docx`
2. Publication-target student workbook (PDF): `my-n4-grammar-adventure-complete_<latest stamp>.pdf`

Output files are datetime-stamped (`_YYYYMMDD_HHMMSS`). Review the most recent stamp of each artifact. If a specific filename is given but a newer stamp exists, review the newer one. State the exact filenames you actually reviewed at the top of your report.

## Conventions (read first — these resolve most ambiguity)
- Spelling: British English. Expected forms: colour, favour, flavour, behaviour, neighbour, honour; metre/centre/litre; recognise, organise, realise, apologise; travelled, cancelled. "practice" = noun, "practise" = verb — both are correct in their roles, NOT typos (e.g. "Practice Time" page title vs "when you practise").
- Two-version model. The DOCX is the editor/reference source and may legitimately contain provenance/audit tags, a legend, and revision metadata. The PDF is the learner-facing product and must contain none of that. A provenance tag in the DOCX is expected; the same tag in the PDF is a publication defect.
- Audience: a 12-year-old JLPT N4 learner. The PDF must be clean, child-facing, polished, and publication-ready.

## Main instruction
Review both documents from all important perspectives. Be strict, specific, and evidence-based. Do not give generic feedback. For every issue, identify the exact document, page number or pattern number, the current problematic text, why it is an issue, and the exact recommended fix (drop-in replacement text).

Do not suggest brand-new sections, brand-new pages, or new learning features unless they are required to fix a real defect. Focus on issues, bugs, inconsistencies, publication-readiness risks, and improvements in the existing content.

## Primary goal
Decide whether the PDF is publication-ready and whether the DOCX is source-ready. If not, provide a precise pending bug list. A "no issue" verdict on any machine-checkable item must be backed by a number, not by inspection (see Verification discipline).

---

## Verification discipline (method + evidence) — applies throughout
For every check that can be verified mechanically, state the method and report the number. Inspection-only "looks fine" is not acceptable for these. Machine-checkable items and the evidence each must produce:

| Check | Report this |
|-------|-------------|
| DOCX↔PDF content parity | field/sentence match count (e.g. `1152/1152 fields present verbatim in PDF`) |
| Pattern count | count in DOCX and in PDF source (e.g. `128 / 128`) |
| Chapter-count math | per-chapter counts and their sum (must = total patterns) |
| Page count | actual vs expected |
| Clip / overflow | per-page content-bottom margin scan; report the count under threshold |
| Internal-tag leak (PDF) | exact counts, e.g. `[corpus]=0 [AI-gen]=0 [n4-=0 core_n4=0 Rev.=0` |
| TOC / page-reference accuracy | confirm every listed page number matches the real page sequence |
| English spelling | number of tokens scanned + list of every residue (see §9) |
| Typography | counts of em-dash, en-dash, ellipsis, curly quotes |
| Japanese fidelity | verbatim-match count + anomaly-class counts (see §1) |

Prefer programmatic extraction (PDF text dump, token sweep, count scripts) over visual scanning for these. Visual/eyeball judgement is reserved for things that genuinely need it (naturalness, layout aesthetics, child-friendliness).

---

## Review perspectives

### 1. Japanese grammar correctness
Check every grammar pattern, usage formula, and example sentence for: grammatical correctness; naturalness; N4-level appropriateness; correct particle usage; correct verb/adjective conjugation; correct distinction between similar patterns; correct kanji/kana usage; no malformed mixed notation; no unnatural or misleading learner examples.

Pay special attention to commonly confused patterns:
- 間 / 間に
- ば / たら / なら / と / ても
- そうだ [1] (hearsay) / そうだ [2] (appearance) / そうに・そうな
- みたいだ / ようだ / らしい / に見える
- てあげる / てくれる / てもらう / てやる
- にくい / づらい / やすい
- のに (concessive) / のに (purpose)
- ことがある (past experience / occasional action)
- ではないか / じゃないか
- と聞いた / という / ということ / と言われている / って

Japanese check method (report counts):
1. Confirm the PDF Japanese is verbatim from the DOCX (state the field match, e.g. 1152/1152). Anything not verbatim is either a defect or unflagged authoring.
2. Scan for anomaly classes and report each count: kanji outside the N4 whitelist; orphaned/broken mixed kana-kanji fragments; full-width vs half-width inconsistencies; stray ASCII inside Japanese strings; malformed notation.

### 2. English meaning and translation accuracy
Check all English meanings/translations for: accurate meaning; no overgeneralization; no missing nuance; no gendered subject added when the Japanese does not specify gender; no awkward literal translation; no misleading simplification; no mismatch between the meaning label, the examples, and the grammar recipe.

Flag, with the exact pattern and text:
- English says "he/she" when the Japanese only says あの人, 田中さん, or an omitted subject. (A non-gendered implied subject such as "(you)" is milder — note it but classify it as subjective-preference, not a defect.)
- A meaning label covers only one usage while the examples show more than one.
- A translation sounds unnatural for a child workbook.
- A meaning is too broad and may cause learner misuse.
- A correct gendered pronoun that is specified by the Japanese (e.g. 弟 → "him", おばあさん → "her") is correct — do not flag it.

### 3. Usage formula ("Grammar Recipe") accuracy
Check every recipe for: correct form; correct tense/form requirement; consistency with the examples shown; no missing important form variant; no overbroad rule; no technical wording confusing for a 12-year-old (e.g. avoid "verbal-noun/する-noun" jargon — prefer "N").

Spot targets (verify each is satisfied):
- ころ includes specific time + ごろ and N + の + ころ.
- 終わる covers both standalone 終わる (to end) and V-ます-stem + 終わる.
- に見える uses い-adj stem + く見える, な-adj + に見える, N + に見える.
- ではないか distinguishes N/な-adj + ではないか from V/い-adj + のではないか.
- お〜ください uses learner-friendly wording.
- のに (purpose) covers use with 使う / いる / かかる.
- て / で covers "and", "so", and "because of".

### 4. DOCX-to-PDF consistency
Compare for: same pattern count and numbers; same Japanese examples; same corrected meanings; same corrected recipes; no missing pattern in the PDF; no extra unintended pattern; no stale content in either file. Report the parity number. State clearly that the DOCX intentionally carries editor-only content (tags/legend/rev line); if any editor-only content appears in the PDF, flag it as a publication defect.

### 5. Categorization and chapter structure
Confirm each pattern sits in a sensible chapter (Time Castle, If-Then Forest, Te-form Workshop, Can-Do Castle, Kindness Cafe, Please Plaza, Must-Do Mountain, Looks-Like Lake, Quote Library, Question Quarry, Decision Den, Plan Peak, Compare Cove, Adverb Avenue, Connector Bridge, Reason Realm, Polite Palace, Handy Corner). Check: category names are accurate enough; chapter subtitles match the included patterns; no item is obviously misplaced; chapter counts match the actual gems; all chapter counts sum to the total (report the sum); the table of contents, adventure map, chapter intros, review pages, progress tracker, and answer key are mutually consistent.

### 6. Exercise and answer key logic
Check all Practice Time, review, and Answer Key pages: every blank has a valid answer; every "which gem?" item has a clear answer; word-bank items match expected answers; answer key agrees with practice pages and with review-matching pages; review pages don't overclaim coverage; score counts are correct; no answer is accidentally pre-shown unless the task is "which gem?"; a full sentence is never shown without the "(which gem?)" cue. Report: number of practice fill-items checked and how many answers were missing from their word bank (target 0).

### 7. Publication-readiness of the PDF
No internal tags anywhere learner-facing (AI-gen, GenAI, corpus, corpus-fixed, QA/audit/source/revision labels, internal disclaimers, editor metadata) — report the scan counts. Clean title/subtitle; consistent page numbers; clear TOC; readable Adventure Map; no text collisions, clipped content, broken Japanese wrapping, awkward English wrapping, chapter names running together, missing/broken images, repeated/duplicated pages, accidental blank pages, layout overflow, or low-contrast text. "How to Use This Book" matches the actual structure; every page reference matches the real page. (A legitimate legal/credits page — e.g. "not affiliated with the JLPT" — is appropriate publication front-matter, not an internal tag.)

### 8. Child-friendly suitability
For a 12-year-old: language friendly but not childish; explanations concise; examples age-appropriate (no needless adult/business framing); nothing culturally inappropriate or discouraging; no confusing technical labels; mascot/support text helpful not distracting; the workbook stays motivating and readable. Flag only problems in existing wording/examples/presentation — do not invent new features.

### 9. Consistency and style
- Spelling (exhaustive, not spot-check). Target British English (see Conventions). Extract every English token from the PDF, lowercase, and test against (a) a spell-checker/dictionary and (b) a word-boundary US↔UK pair list: color/colour, favor/favour, flavor/flavour, behavior/behaviour, neighbor/neighbour, honor/honour, meter/metre, center/centre, theater/theatre, liter/litre, fiber/fibre, recognize/recognise, organize/organise, realize/realise, apologize/apologise, memorize/memorise, traveler/traveller, traveled/travelled, canceled/cancelled, modeling/modelling, gray/grey, tire/tyre, jewelry/jewellery, math/maths, airplane/aeroplane. Use `\b` boundaries so "honorific", "tired", "practice"(noun) don't false-positive. Report the token count and list every US residue (target 0).
- Typography. Report counts of em-dash (—), en-dash (–), ellipsis (…), and curly quotes (" " ' '); target ASCII (use `-`, `...`, `"`, `'`).
- Consistent use of "Practice Time", "Chapter Review", "Grammar Recipe", "My sentence", "Gem"; consistent capitalization, punctuation, Japanese brackets/slashes/tildes; consistent pattern naming (e.g. そうだ [1] / そうだ [2]); a stated romanization policy (or none); consistent translation style; consistent phrasing of recurring notes ("for me/us", "speaker's side", "someone lower in status").

### 10. Final source hygiene
DOCX: editor/reference labels are appropriate for the DOCX; revision/version info is accurate (not stale after later edits); the filename/stamp matches the content header; it states the correct pattern count and actually contains that many; no known old issue has regressed. PDF: publication-facing only; no source-hygiene/editor content.

---

## Re-review / regression mode (for any pass after the first)
If a change-log or list of previously-fixed items is available (e.g. a bug registry / `_BUGS.csv`):
- Treat those items as resolved. For each, confirm the fix still holds (cite its current evidence) rather than re-listing it as an open issue.
- Report only regressions or genuinely new findings.
- Because §9's spelling and §-table checks are exhaustive and method-backed, a correct pass should leave nothing for the next re-run — aim to converge in one cycle.

---

## Output format
Start with a one-line verdict, then:

1. Executive verdict — files reviewed (exact names); PDF publication readiness: Ready / Not ready; DOCX source readiness: Ready / Not ready; Blocking issues: X; Non-blocking improvements: Y; one-line recommendation. Include the key evidence numbers (parity, page count, clip count, tag-leak counts, spelling tokens/residues, typography counts).

2. Blocking issue list — true release blockers only. For each: `Issue ID · Document · Page/Pattern · Current text · Problem · Recommended fix (drop-in text) · Severity`.

3. Non-blocking issue / improvement list — real existing-content improvements only (no optional new additions). Same fields, including drop-in fix text.

4. DOCX vs PDF consistency findings — aligned or not; exact mismatches; the parity number.

5. Exercise and answer key findings — correct or not; exact mismatches; the items-checked / answers-missing numbers.

6. Publication-readiness findings — layout/cleanliness verdict with the tag-leak and clip numbers.

7. Final go/no-go verdict — exactly one of: `GO — publication-ready` / `GO WITH MINOR TEXT FIXES — no blockers, fix listed items` / `NO-GO — blockers must be fixed`.

## Severity classification (tag every finding)
- BLOCKER — would embarrass in print or mislead the learner (e.g. internal tag in the PDF, wrong grammar, clipped content, wrong answer).
- CONSISTENCY-DEFECT — objective inconsistency worth fixing (e.g. a US spelling in a British book, a stray em-dash, a stale rev number that is grossly wrong).
- SUBJECTIVE-PREFERENCE — a judgement call (e.g. a slightly verbose gloss, a parenthesised non-gendered "(you)"). List these separately and sparingly; never let them inflate the issue count.

## Important rules
- Be specific. Never write "some examples are awkward" — name the exact pattern/page/text.
- Do not invent issues. If a check is clean, say so with its number.
- Do not suggest new content additions unless required to fix an existing defect.
- Do not comment on unrelated repository, git, or implementation details.
- Do not include URLs. Do not include generic praise.
- Give drop-in replacement text for every recommended fix so the fix step is unambiguous.
- If no issue is found, say clearly: "No further issue found."
