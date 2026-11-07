# -*- coding: utf-8 -*-
"""check_blank_frame_pos.py - Phase-0 check: a fill-in blank must be grammatical for EVERY option.

Added 2026-11-07 after a language read of the N4 kanji book found two context items where the
frame around the blank broke for the keyed answer:

  「えんそくは とても（　　）でした」  options all い-adjectives -> 楽しいでした (ungrammatical)
  「とても（　　）人です」           key 親切 (な-adjective)      -> 親切人 (needs な)

Both had passed every automated gate and several review rounds, because each option reads fine on
its own; the error only exists in the frame. Rules checked:
  (a) blank followed by でした / です  -> no option may be an い-adjective;
  (b) blank followed by a noun        -> no option may be a bare な-adjective (no な).
Option part of speech comes from the corpus's own vocab.json, so an option the vocab does not list
is not judged (reported as unscored, never as a violation).

Usage:  python tools/check_blank_frame_pos.py [questions.json] [vocab.json]
Exit:   0 = no violations, 1 = violations found.
Validated 2026-11-07: N5 data/questions.json 214 blank items, 0 violations; the two N4 originals
above, run as a synthetic corpus, are both caught and both fixed versions pass.
"""
import io
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BLANK = re.compile(r"(?:（[\s　]*）|\([\s　]*\)|＿{2,}|_{2,})")


def main() -> int:
    qpath = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "questions.json")
    vpath = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "data", "vocab.json")
    q = json.load(io.open(qpath, encoding="utf-8"))
    questions = q["questions"] if isinstance(q, dict) else q
    v = json.load(io.open(vpath, encoding="utf-8"))
    pos = {}
    for e in (v["entries"] if isinstance(v, dict) else v):
        for k in ("form", "reading"):
            if e.get(k):
                pos.setdefault(e[k], e.get("pos", ""))

    hits, scanned = [], 0
    for x in questions:
        stem = x.get("prompt_ja") or x.get("stem") or x.get("sentence") or ""
        m = BLANK.search(stem)
        if not m:
            continue
        scanned += 1
        after = stem[m.end():].lstrip(" 　")
        opts = [str(o) for o in (x.get("choices") or x.get("options") or [])]
        if after.startswith(("でした", "です")):
            bad = [o for o in opts if pos.get(o) == "i-adj"]
            rule = "い-adjective before でした/です"
        elif re.match(r"[一-鿿ァ-ヶ]", after[:1] or " "):
            bad = [o for o in opts if pos.get(o) == "na-adj" and not o.endswith("な")]
            rule = "bare な-adjective before a noun"
        else:
            continue
        if bad:
            hits.append((x.get("id"), rule, bad, stem))

    print("blank items scanned: %d | violations: %d" % (scanned, len(hits)))
    for h in hits:
        print("   %s  %s  %s  %s" % h)
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
