# JLPT N5 - Blank-Frame Part-of-Speech Lesson Propagation (2026-11-07)

This document records a **cross-level lesson propagation**, not an N5 audit cycle. The lesson came
from a manual Japanese-language read of the merged N4 kanji book
(`N4/Workbook/N4_Kanji_Workbook/n4-kanji-adventure-complete-with-extended-practice_*.pdf`: 170 kanji
cards, 15 practice banks, the 405-item Extended Practice Set). Per Rule 4 the generalizable part is
propagated to the four documentation surfaces and **validated against the live N5 corpus**.

**Writing-discipline note.** Counts are bounded by *what was scanned* (the 214 items with a fill-in
blank in `data/questions.json` on 2026-11-07) and *how they were matched* (option part of speech
taken from `data/vocab.json`). "0 violations" means the check found no frame break **for the options
the corpus vocab types**; an option vocab.json does not list is not judged, and a manual read still
owns those.

---

## The lesson (procedure-manual F.65)

A fill-in blank must be grammatical for **every one of the four options**, not just the key. Each
option can read fine on its own while the frame around the blank breaks for it.

Origin defects in the N4 book, both of which had passed every automated gate and several review
rounds:

- 「えんそくは とても（　　）でした」 with options かなしい / むずかしい / つまらない / 楽しい: every option
  yields 「〜いでした」, which is ungrammatical. Fixed as 「とても（　　）えんそくでした」.
- 「その 店の 人は とても（　　）人です」 keyed to 親切: a な-adjective before a noun needs な. Fixed by
  printing the options attributively: つめたい / 親切な / こわい / しずかな.

---

## Propagation ledger (Rule 4, four surfaces)

| Surface | Edit | Status |
|---------|------|--------|
| `JLPT Common/procedure-manual-build-next-jlpt-level.md` | Appendix **F.65** | Added |
| `N5/prompts/Japanese language Accuracy check.txt` | Category **A94** (blank-frame part-of-speech agreement) | Added |
| `N5/prompts/N5Improvement.txt` | **Phase-0 blank-frame part-of-speech agreement block** | Added |
| `N5/docs/AUDIT-COVERAGE-2026-11-07.md` | This document | Added |

JA-116 coverage kept in the same change: rows **A-158** (A94) and **Phase-0-blank-frame-pos** were
added to `specifications/test-scenarios-by-specialist-perspective.xlsx`, so the prompt additions do
not repeat the 2026-06-09 gap that left the content-integrity workflow red for four months.

---

## Validation against the live N5 corpus

| Check | Scope | Result |
|-------|-------|--------|
| `tools/check_blank_frame_pos.py` | 214 blank items in `data/questions.json` | 0 violations |
| Same tool, mutation run | the two N4 originals and their fixes as a 4-item synthetic corpus | both originals caught, both fixes pass |

No N5 content change was needed against this check's scope.

---

## Second read, same day (procedure-manual F.66)

Four independent reads of the rebuilt N4 book (cards, banks, fixed text and answer keys, supplement)
produced four more lesson classes. Each finding was checked against the data and the gates before
it was applied; two were withdrawn (FP-25).

| Class | N4 evidence | Surface |
|-------|-------------|---------|
| A95 label phonetics | 7 labels called non-voicing changes "voicing"; 3 on/kun tags wrong | prompt A95; Phase-0 block; `tools/check_label_phonetics_and_carriers.py` |
| A96 empty carriers | 135 of 340 supplement carriers had no situation | prompt A96; same Phase-0 block and tool |
| A97 worked examples / duplicates | 12 of 15 (れい) 漢字読み examples malformed; 2 targets tested twice per test | prompt A97; N5Improvement Section-10 anti-items |
| FP-25 recorded decisions | 下町 item and 貸 かし were reviewed decisions | prompt FP-25 |

| Check | Scope | Result |
|-------|-------|--------|
| `tools/check_label_phonetics_and_carriers.py` | 157,799 strings in `data/*.json`; 268 stems in `data/questions.json` | 0 hits |
| Same tool, `--self-test` | the N4 originals planted (8) plus 7 clean strings | 8 caught, 7 pass |

JA-116 rows added in the same change: A-159 (A95), A-160 (A96), A-161 (A97), FP-25,
Phase-0-label-phonetics-carriers. No N5 content change was needed against this tool's scope.

---

## Third read, same day (procedure-manual F.67)

Four more independent reads of the rebuilt book. New class A98: the same word tested in two sections
of one test (24 pairs), per-option labels left describing replaced options, and new distractors that
JMdict lists as rare real readings. 46 more empty carriers were rewritten, including 11 that
`tools/check_label_phonetics_and_carriers.py` itself flagged in the N4 data after a pass had kept
them as natural enough. The tool's regex was extended to those frames.

| Check | Scope | Result |
|-------|-------|--------|
| `tools/check_label_phonetics_and_carriers.py` | 157,799 strings in `data/*.json`; 268 stems | 0 hits |
| Same tool, `--self-test` | 10 planted defects, 7 clean strings | 10 caught, 7 pass |

JA-116 row added: A-162 (A98).

---

## Fourth read, same day (procedure-manual F.68)

A98 extended: worked examples and distractors leaked other items' answers (6 found by readers,
4 more by a string-search sweep), and 用法 example distractors relied on an omitted object, which is
natural Japanese. No new A-category, so no new JA-116 row; N5's question bank has no worked
examples, so the sweep has no N5 target at this checkpoint.

---

## Fifth read, 2026-11-08 (procedure-manual F.69)

A95 extended: answer-key labels that hid a real reading behind a sound-change note ("voices た->だ"
for 台風 だいふう). Readers found 21 in the N4 banks; a KANJIDIC2 split sweep of every kanji-reading
distractor found 8 more of the same kind, and after the fix it matches only rare readings (6 items in
the N4 banks scanned), which keep their error-type labels. No new A-category, so no new JA-116 row.
The sweep needs KANJIDIC2, which is not in the repo, so it runs locally, not in CI. N5's question
bank was not swept at this checkpoint.

---

## One-round review checklist, 2026-11-08 (procedure-manual F.70)

The N4 review workbook now has one Checklist row per Japanese item in the merged PDF (948 rows in
the PDF scanned: 170 cards, 245 practice items, 63 printed worked examples, 405 extended-set items,
65 fixed-text blocks; 5,596 Japanese text blocks, 0 not covered). Six fixed checks per row; 19
automated checks, one per issue type found so far: 6 open hits and 10 accepted hits at this
checkpoint. No N5 artifact changed. The 6 open hits (4 answer leaks inside one test, 1 word tested twice,
1 label) were fixed the same day; after the fix the checks report 0 open hits on the N4 data scanned.
C1-C6 round 1 (all 947 rows, after a placement fix removed an unprinted worked example): 5 blocking
failures fixed (4 card meanings, 1 worked-example key); round 2 on the 5 changed rows: 0. Against
these 6 checks and this reviewer setup only; 105 non-blocking style notes are listed separately.

Later rounds the same day (F.70 points 6-7): 176 style notes recorded, 160 applied, 15 not applied
with a reason, 1 open; each note now also shows on its own Checklist row. The last batch (40 notes
from a fresh full round 7) reopened 39 rows; their recheck found 1 blocking failure (a reworded
answer-key label), fixed, and the recheck of that row found 0. At this checkpoint the checklist
records 947 of 947 rows reviewed with 0 C1-C6 failures against these checks and this AI reviewer
setup; no native-speaker review is implied.

Queue closed the same day (F.70 point 8): the 123 Review Items awaiting recheck and 2 new worked
examples were rechecked by 4 AI reviewer agents (round 11, 0 failures); 16 style notes from rounds
11-12 were decided (14 applied, 2 not applied with the reason) and the 14 edited rows rechecked
(rounds 12-13, 0 failures). At this checkpoint: Review Items 245 of 245 PASS (123 of them by the
AI recheck, attributed per item), 192 style notes with 0 open, Checklist 947 of 947 rows with 0
C1-C6 failures, against these checks and this AI reviewer setup only. Rendered-visual sign-offs
R11C-R11J stay PENDING: they are human-only by the project's rule.

Full checklist round 14 the same evening (all 947 rows, 8 fresh AI reviewers): 0 reported failures,
18 style notes, of which 4 were card meanings missing a sense their examples need and were counted
as C5 failures (度, 公, 色, 口) and fixed. Rechecks of the changed rows: round 15 (17 rows) 1 failure
(色 still missing 'character'), round 16 (3 rows) 1 failure introduced by a fix (口 人口, removed),
round 17 (2 rows) 0. At this checkpoint: Checklist 947 of 947 rows with 0 C1-C6 failures, 0 open
automated hits, 215 style notes with 0 open, Review Items 245 of 245 PASS, against these checks and
this AI reviewer setup only; no native-speaker review is implied.

Checklist coverage review, 2026-11-09 (procedure-manual F.73): an external review found the test
registry still aimed at the 245-item, 388-page component build. The workbook now has 316 test cases
(30 final-release cases added: TC-FIN / WEX / WRT / ENG / PRD / GOV, none executed yet), a
release_scope per registry case, the final PDF's checksum and page-order manifest in the run
configuration, the extended-set sources in the manifest, and 28 coverage-matrix rows (7 existing
rows corrected for relevance, 15 new component rows). Mode corrections: 3 grammar cases out of the visual mode, 5
governance cases into a new MANUAL_GOVERNANCE mode. The self-audit's registry checks were found to
read the wrong column and were fixed. These change what the checklist covers; they are not test
results against the PDF.

Release-case run, 2026-11-09 (F.73 points 9-10), against the merged PDF with SHA-256 3451c960...:
13 PASS, 9 FAIL, 7 BLOCKED, 1 PENDING of the 30 cases. PASS includes the 650-question answer
mapping, full content fidelity (5,588 Japanese blocks, 2,704 English fields), merge boundaries,
build identity, all 340 stroke strips frame by frame, the 170 writing entries and their cells.
FAIL: 5 same-unit answer leaks in the extended set, 20 extended usage options against their
subsection rule (plus 6 label mismatches), 9 English issues, a How-to promise and running head the
merged edition contradicts, 2 credits claims without current evidence, missing illustration
provenance and an undelivered notices file, empty PDF metadata, waiver records without approver,
and the closure case. BLOCKED: production profile, gutter, image PPI threshold, physical proof,
cover files, previewer, qualified-teacher handwriting review. PENDING: per-occurrence visual
inspection (R11C-R11J). Reviewers were AI agents; no native-speaker or qualified-teacher review
is implied, and nothing was fixed in this run.

---

## Future native-human review

The mechanical check covers two frame shapes (blank + でした/だ/では, blank + noun; い-adjective + です
is correct and deliberately not flagged) and only options the
vocab file types. Shapes it does not cover (blank + な with い-adjective options, verb-form agreement
before a blank, mixed parts of speech in one option set) remain a native reader's job: substitute
each option into the blank and read the whole sentence aloud.
