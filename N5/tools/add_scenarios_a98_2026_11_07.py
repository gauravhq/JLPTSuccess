# -*- coding: utf-8 -*-
"""add_scenarios_a98_2026_11_07.py - scenario row for accuracy-prompt A98 (third N4 language read,
2026-11-07): cross-section twins, stale labels, rare-reading distractors.

JA-116 requires every A-NN, FP-NN and Phase-0 block in the prompts to be named in at least one row of
specifications/test-scenarios-by-specialist-perspective.xlsx, so the rows go in the same change.
House style as in add_scenarios_a94_2026_11_07.py.

Run:  python tools/add_scenarios_a98_2026_11_07.py
"""
import os
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import openpyxl

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
XLSX = os.path.join(ROOT, "specifications", "test-scenarios-by-specialist-perspective.xlsx")
TAB = "A. Japanese language"
TOOL = "tools/check_label_phonetics_and_carriers.py"

ROWS = [
    ("A-162", "Accuracy prompt category", "1",
     "Accuracy prompt audit category A98: CROSS-SECTION TWINS, STALE LABELS, RARE-READING DISTRACTORS - "
     "one word per test across all sections; labels re-read when options change; distractors checked "
     "against rarer real readings",
     "1. Reference: prompts/Japanese language Accuracy check.txt A98. "
     "2. List each test's tested words by kanji string across all sections; flag repeats. "
     "3. For every item whose options changed, re-read each per-option label. "
     "4. Run the distractor-reading gate and python %s." % TOOL,
     "No word tested twice in one test and no label describing a replaced option, for the tests read; "
     "0 distractor-reading collisions.",
     "P2", "Major", "Documentation + audit",
     "Trigger: third read of the N4 kanji book found 24 same-word pairs across sections, 問386 labels "
     "for replaced options, and 4 new distractors that JMdict lists as real readings.",
     "30m", "Native-teacher reviewer", "prompts/Japanese language Accuracy check.txt A98; " + TOOL),
]


def main() -> int:
    wb = openpyxl.load_workbook(XLSX)
    sh = wb[TAB]
    before_rows = sh.max_row
    existing = {str(sh.cell(r, 1).value) for r in range(5, before_rows + 1)}
    for r in ROWS:
        assert r[0] not in existing, "%s already present" % r[0]
    # no side copy: the xlsx is tracked in git, and *.bak* writes are denied by the user's settings
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
