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

## Future native-human review

The mechanical check covers two frame shapes (blank + でした/だ/では, blank + noun; い-adjective + です
is correct and deliberately not flagged) and only options the
vocab file types. Shapes it does not cover (blank + な with い-adjective options, verb-form agreement
before a blank, mixed parts of speech in one option set) remain a native reader's job: substitute
each option into the blank and read the whole sentence aloud.
