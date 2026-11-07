# -*- coding: utf-8 -*-
"""check_label_phonetics_and_carriers.py - Phase-0 check for accuracy-prompt A95 / A96.

A95  answer-key label phonetics: a label that says a distractor "voices" X->Y must name a real
     dakuten / handakuten pair (か->が, は->ぱ); "unvoices" the reverse. The N4 kanji book printed
     "voices り->じ", "voices む->ぶ", "voices に->じ", "voices か->げ" and "wrong voicing (ち)" for
     しん->ちん, none of which is voicing. ち->じ / つ->ず are accepted (じ, ず are the modern
     spellings of ぢ, づ).
A96  empty carrier frames: a stem that only says someone thought about / asked about / looked up
     the target, with no situation, e.g. 「Xの ことを 考えました」, 「Xに ついて 聞きました」,
     「Xか どうか しらべました」. 135 such carriers were rewritten in the N4 supplement.

Scans every string in data/*.json for A95 and every question stem in data/questions.json for A96.
Usage:  python tools/check_label_phonetics_and_carriers.py [--self-test]
Exit:   0 = no hits, 1 = hits (each printed with its location)
"""
import glob
import io
import json
import os
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PAIR = re.compile(r"\b(un)?voic\w*[^ぁ-ん\n]{0,24}?([ぁ-ん])\s*(?:->|→)\s*([ぁ-ん])", re.I)
# じ / ず are the modern spellings of ぢ / づ, so ち->じ and つ->ず count as voicing
MODERN = {("ち", "じ"), ("つ", "ず")}
EMPTY = re.compile(r"(の ?ことを ?(考え|おぼえ|しらべ)|に ?ついて ?(聞き|話し|しらべ)|"
                   r"か ?どうか ?(聞き|しらべ)|ときの ?ことを ?(話し|おぼえ))")


def voiced(a, b):
    d = unicodedata.normalize("NFD", b)
    return (a, b) in MODERN or (len(d) == 2 and d[0] == a and d[1] in "゙゚")


def bad_label(s):
    out = []
    for m in PAIR.finditer(s):
        un, a, b = m.group(1), m.group(2), m.group(3)
        ok = voiced(b, a) if un else voiced(a, b)
        if not ok:
            out.append(m.group(0))
    return out


def strings(x, path=""):
    if isinstance(x, str):
        yield path, x
    elif isinstance(x, list):
        for i, y in enumerate(x):
            yield from strings(y, "%s[%d]" % (path, i))
    elif isinstance(x, dict):
        for k, y in x.items():
            yield from strings(y, "%s.%s" % (path, k))


def self_test():
    bad = ["voices り->じ", "voices む->ぶ", "voices に->じ", "voices か->げ", "unvoices ち->し"]
    good = ["voices か->が", "voices は->ぱ", "unvoices ど->と", "voices ち->じ", "wrong kana じ for に"]
    carriers_bad = ["自分の ことを 考えました。", "図書館で 開始に ついて 聞きました。", "同じか どうか 聞きました。"]
    carriers_good = ["自分の へやは 毎日 そうじします。", "しあいの 開始は 午後 三時です。"]
    ok = all(bad_label(s) for s in bad) and not any(bad_label(s) for s in good) and \
        all(EMPTY.search(s) for s in carriers_bad) and not any(EMPTY.search(s) for s in carriers_good)
    print("SELF-TEST %s (%d planted defects caught, %d clean strings passed)"
          % ("PASS" if ok else "FAIL", len(bad) + len(carriers_bad), len(good) + len(carriers_good)))
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        return self_test()
    hits, n_str, n_stem = [], 0, 0
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "*.json"))):
        try:
            data = json.load(io.open(f, encoding="utf-8"))
        except ValueError as e:
            print("SKIP %s: not JSON (%s)" % (os.path.basename(f), e))
            continue
        for path, s in strings(data):
            n_str += 1
            for b in bad_label(s):
                hits.append("A95 %s%s: %r" % (os.path.basename(f), path, b))
    q = json.load(io.open(os.path.join(ROOT, "data", "questions.json"), encoding="utf-8"))
    for it in (q["questions"] if isinstance(q, dict) else q):
        stem = it.get("question_ja") or ""
        if stem:
            n_stem += 1
            if EMPTY.search(stem):
                hits.append("A96 %s: %s" % (it.get("id"), stem))
    print("A95 label phonetics: %d strings in data/*.json | A96 empty carriers: %d stems in "
          "data/questions.json | hits: %d" % (n_str, n_stem, len(hits)))
    for h in hits:
        print("  " + h)
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
