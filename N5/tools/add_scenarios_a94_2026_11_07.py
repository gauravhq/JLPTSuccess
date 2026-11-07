# -*- coding: utf-8 -*-
"""add_scenarios_a94_2026_11_07.py - scenario rows for accuracy-prompt A94 and its Phase-0 block.

JA-116 requires every A-NN category and every Phase-0 block in the prompts to be named in at least
one row of specifications/test-scenarios-by-specialist-perspective.xlsx. A94 (blank-frame
part-of-speech agreement) and the matching N5Improvement Phase-0 block were added on 2026-11-07, so
their rows go in the same change - the 2026-06-09 propagation that skipped this step left the
content-integrity workflow red for four months.

House style as in add_scenarios_a93_fp24_2026_09_30.py: A-NNN id for the category, a Phase-0-<slug>
id for the block, the code named in the Scenario, bounded expected-result wording.

Run:  python tools/add_scenarios_a94_2026_11_07.py
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

ROWS = [
    ("A-158", "Accuracy prompt category", "1",
     "Accuracy prompt audit category A94: BLANK-FRAME PART-OF-SPEECH AGREEMENT - a fill-in blank "
     "must be grammatical for every one of the four options, not just the key",
     "1. Reference: prompts/Japanese language Accuracy check.txt A94. "
     "2. For each blank item, substitute each option into the blank and read the whole sentence. "
     "3. Flag い-adjective options before でした/です (楽しいでした) and bare な-adjective options "
     "before a noun (親切人). "
     "4. Run python tools/check_blank_frame_pos.py for the mechanical part.",
     "Every option yields a grammatical sentence in its frame, against the current corpus snapshot; "
     "check_blank_frame_pos.py returns 0 for the options the corpus vocab types.",
     "P2", "Major", "Documentation + audit",
     "Trigger: 2026-11-07 language read of the N4 kanji book found 「えんそくは とても（　　）でした」 "
     "and 「とても（　　）人です」 after every automated gate and several review rounds had passed "
     "them. Each option read fine alone; the error was only in the frame.",
     "30m", "Native-teacher reviewer",
     "prompts/Japanese language Accuracy check.txt A94; tools/check_blank_frame_pos.py; "
     "tools/check_content_integrity.py JA-116"),
    ("Phase-0-blank-frame-pos", "Phase-0 block", "1",
     "Phase-0 blank-frame part-of-speech agreement block - run the blank-frame check before any "
     "release that touches fill-in items",
     "1. Reference: prompts/N5Improvement.txt Phase-0 blank-frame part-of-speech agreement block. "
     "2. Run python tools/check_blank_frame_pos.py. "
     "3. Any hit: move the blank so it modifies a noun, or print the options in attributive form; "
     "never fix by changing only the key.",
     "0 violations against the current corpus snapshot (2026-11-07: 214 blank items scanned, 0); "
     "a 0 is bounded to options the corpus vocab types.",
     "P2", "Major", "Phase-0 regression",
     "Validated on 2026-11-07 against N5 data/questions.json, and against the two N4 originals run "
     "as a synthetic corpus (both caught, both fixed versions pass). Pairs with row A-158.",
     "10m", "Engineer + Auditor",
     "prompts/N5Improvement.txt; tools/check_blank_frame_pos.py"),
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
        "test-scenarios-by-specialist-perspective.bak_a94_%s.xlsx"
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
    assert ids[-2:] == [r[0] for r in ROWS], "rows not at the tail: %s" % ids[-3:]
    print("%s: %d rows -> %d rows" % (TAB, before_rows - 4, len(ids)))
    for r in ROWS:
        print("   + %-24s %s" % (r[0], r[3][:70]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
