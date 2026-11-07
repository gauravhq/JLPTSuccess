# -*- coding: utf-8 -*-
"""add_scenarios_a95_2026_11_07.py - scenario rows for accuracy-prompt A95 / A96 / A97, FP-25 and the
Phase-0 label-phonetics and empty-carrier block (second N4 language read, 2026-11-07).

JA-116 requires every A-NN, FP-NN and Phase-0 block in the prompts to be named in at least one row of
specifications/test-scenarios-by-specialist-perspective.xlsx, so the rows go in the same change.
House style as in add_scenarios_a94_2026_11_07.py.

Run:  python tools/add_scenarios_a95_2026_11_07.py
"""
import os
import shutil
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import openpyxl

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
XLSX = os.path.join(ROOT, "specifications", "test-scenarios-by-specialist-perspective.xlsx")
TAB = "A. Japanese language"
TOOL = "tools/check_label_phonetics_and_carriers.py"

ROWS = [
    ("A-159", "Accuracy prompt category", "1",
     "Accuracy prompt audit category A95: ANSWER-KEY LABEL PHONETICS AND READING TYPE - a label that "
     "says 'voices X->Y' must name a real dakuten / handakuten pair, and on/kun tags must match the "
     "kanji's reading table",
     "1. Reference: prompts/Japanese language Accuracy check.txt A95. "
     "2. Run python %s. "
     "3. For each on/kun tag in a distractor label, check the kanji's reading table by hand." % TOOL,
     "0 phonetics hits against the current corpus snapshot; on/kun tags match the reading table for "
     "the labels read.",
     "P2", "Major", "Documentation + audit",
     "Trigger: 2026-11-07 second read of the N4 kanji book found 'voices り->じ', 'voices か->げ', "
     "'wrong voicing (ち)' and three wrong on/kun tags in printed answer keys.",
     "20m", "Native-teacher reviewer", "prompts/Japanese language Accuracy check.txt A95; " + TOOL),
    ("A-160", "Accuracy prompt category", "1",
     "Accuracy prompt audit category A96: EMPTY CARRIER FRAMES - a carrier sentence must state one "
     "concrete situation, not only that someone thought / asked about the target",
     "1. Reference: prompts/Japanese language Accuracy check.txt A96. "
     "2. Run python %s. "
     "3. When one empty frame is found, sweep the whole template output with a regex." % TOOL,
     "0 stems match the empty-frame regex against the current corpus snapshot; frames outside the "
     "regex stay a native read.",
     "P2", "Major", "Documentation + audit",
     "Trigger: 135 of 340 N4 supplement carriers (「自分の ことを 考えました」 class) after an earlier "
     "pass had fixed 44 by example.",
     "30m", "Native-teacher reviewer", "prompts/Japanese language Accuracy check.txt A96; " + TOOL),
    ("A-161", "Accuracy prompt category", "1",
     "Accuracy prompt audit category A97: WORKED EXAMPLES AND IN-TEST DUPLICATES - item-format checks "
     "apply to (れい) examples too, and no target is tested twice in one test",
     "1. Reference: prompts/Japanese language Accuracy check.txt A97. "
     "2. For every worked example, apply the numbered-item format rules for its type. "
     "3. List each test's targets and look for repeats.",
     "Every worked example follows its type's format and no test repeats a target, for the tests read.",
     "P2", "Major", "Documentation + audit",
     "Trigger: 12 of 15 N4 漢字読み worked examples were malformed (11 underlined kana); 元気 and "
     "漢字 were each tested twice on one page.",
     "20m", "Native-teacher reviewer", "prompts/Japanese language Accuracy check.txt A97"),
    ("FP-25", "False-positive class", "1",
     "FP-25: a structural flag that reverses a recorded review decision is a false positive unless "
     "the decision itself is shown wrong",
     "1. Reference: prompts/Japanese language Accuracy check.txt FP-25. "
     "2. Before a structural or reading-table fix, search the authoring guide, review ledger and "
     "superseded-wording lists. 3. Run the data gates before and after.",
     "No recorded review decision is reversed without a stated reason, in the changes reviewed.",
     "P2", "Major", "Documentation + audit",
     "Trigger: N4 W06-M3-Q12 (下町 moved to 漢字読み in the 2026-07-25 native review) and 貸 kun "
     "かし (needed for 貸家) were both 'fixed' and withdrawn on 2026-11-07.",
     "10m", "Engineer + Auditor", "prompts/Japanese language Accuracy check.txt FP-25"),
    ("Phase-0-label-phonetics-carriers", "Phase-0 block", "1",
     "Phase-0 label-phonetics and empty-carrier block - run the label and carrier check before any "
     "release that touches distractor labels or question stems",
     "1. Reference: prompts/N5Improvement.txt Phase-0 label-phonetics and empty-carrier block. "
     "2. Run python %s --self-test (must PASS), then python %s." % (TOOL, TOOL),
     "0 hits against the current corpus snapshot (2026-11-07: 157,799 strings and 268 stems, 0); "
     "self-test catches the 8 planted N4 originals.",
     "P2", "Major", "Phase-0 regression",
     "Validated 2026-11-07 against N5 data/*.json and data/questions.json. Pairs with A-159 / A-160.",
     "5m", "Engineer + Auditor", "prompts/N5Improvement.txt; " + TOOL),
]


def main() -> int:
    wb = openpyxl.load_workbook(XLSX)
    sh = wb[TAB]
    before_rows = sh.max_row
    existing = {str(sh.cell(r, 1).value) for r in range(5, before_rows + 1)}
    for r in ROWS:
        assert r[0] not in existing, "%s already present" % r[0]
    shutil.copy2(XLSX, os.path.join(
        ROOT, "specifications",
        "test-scenarios-by-specialist-perspective.bak_a95_%s.xlsx"
        % datetime.now().strftime("%Y%m%d_%H%M%S")))
    template = before_rows
    for i, row in enumerate(ROWS):
        dest = before_rows + 1 + i
        for col, value in enumerate(row, start=1):
            c = sh.cell(dest, col, value)
            src = sh.cell(template, col)
            c.font, c.alignment = src.font.copy(), src.alignment.copy()
            c.border, c.fill = src.border.copy(), src.fill.copy()
        sh.row_dimensions[dest].height = sh.row_dimensions[template].height
    wb.save(XLSX)

    wb2 = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ids = [str(r[0]) for r in wb2[TAB].iter_rows(min_row=5, values_only=True)]
    assert ids[-len(ROWS):] == [r[0] for r in ROWS], "rows not at the tail: %s" % ids[-6:]
    print("%s: %d rows -> %d rows" % (TAB, before_rows - 4, len(ids)))
    for r in ROWS:
        print("   + %-34s %s" % (r[0], r[3][:60]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
