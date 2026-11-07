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

## Future native-human review

The mechanical check covers two frame shapes (blank + でした/だ/では, blank + noun; い-adjective + です
is correct and deliberately not flagged) and only options the
vocab file types. Shapes it does not cover (blank + な with い-adjective options, verb-form agreement
before a blank, mixed parts of speech in one option set) remain a native reader's job: substitute
each option into the blank and read the whole sentence aloud.
