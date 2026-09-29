# -*- coding: utf-8 -*-
"""sync_kanji_kb.py - bring KnowledgeBank/kanji_n4.md up to data/kanji.json.

WHY, and why in this direction.

`check_content_integrity.py` JA-12 requires the KB and data/kanji.json to hold the same glyph set.
kanji.json carries 170; the KB documents 143. The header of the KB calls itself the source and says
the build pipeline parses it into kanji.json, so the obvious move is to regenerate kanji.json from
the KB. Running the repaired builder in report mode shows why that would be wrong: the KB is STALE
in 25 of its 143 entries, and regenerating would revert content that has been through review.

    dropped readings   代 住 写 家 明 楽 答 赤 通 集 青 黒 夕 公 究  (kanji.json has more, and
                       verify_kanji_data.py corroborates them against KANJIDIC2)
    corrected values   町 meanings (2026-09-28 gloss fix), 起 kun okurigana boundary
                       (2026-09-19), 鳥 primary とり/kun, 早 on サッ, 早 meanings
    representation     京 and 以 write their secondary readings inline in `on:` / `kun:`, while
                       kanji.json splits them into `secondary_readings`. The KB already has
                       `secondary_on:` / `secondary_kun:` syntax - 14 and 6 entries use it - so
                       this is the KB not using its own convention, not a data difference.

So the flow is JSON -> KB for this one reconciliation, after which the two agree and the builder's
KB -> JSON direction becomes a no-op. That no-op is the proof: run `tools/build_data.py --report`
and it must print 0 field changes. From then on the KB is genuinely the source and edits belong
there.

Every value written here comes from data/kanji.json's own on / kun / primary_reading /
primary_kind / meanings / secondary_readings / tier. Nothing is invented. Those fields already pass
verify_kanji_data.py checks 1-9 against KANJIDIC2 and the Joyo table.

Run:  python tools/sync_kanji_kb.py [--out PATH]   (--out writes elsewhere; default is in place)
"""
import argparse
import io
import json
import os
import re
import shutil
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
KB = os.path.join(ROOT, "KnowledgeBank", "kanji_n4.md")
KJ = os.path.join(ROOT, "data", "kanji.json")

ENTRY_START = re.compile(r"^- \*\*([一-鿿])\*\*")


def entry_md(e: dict) -> str:
    """One KB record in the exact shape the existing entries use, and the builder parses."""
    sec = e.get("secondary_readings") or {}
    join = lambda xs: "、".join(xs) if xs else "(none)"
    out = ["- **%s**  (tier: %s)" % (e["glyph"], e.get("tier", "core_n4")),
           "  - on: %s" % join(e.get("on"))]
    if sec.get("on"):
        out.append("  - secondary_on: %s" % "、".join(sec["on"]))
    out.append("  - kun: %s" % join(e.get("kun")))
    if sec.get("kun"):
        out.append("  - secondary_kun: %s" % "、".join(sec["kun"]))
    out.append("  - primary: %s  (kind: %s)" % (e["primary_reading"], e["primary_kind"]))
    out.append("  - meanings: %s" % ", ".join(e["meanings"]))
    return "\n".join(out)


def split_entries(lines: list[str]) -> tuple[list[str], dict[str, str], list[str]]:
    """Return (preamble, {glyph: block text}, trailing) from the KB's lines."""
    starts = [i for i, l in enumerate(lines) if ENTRY_START.match(l)]
    if not starts:
        raise ValueError("no entries found in the KB")
    blocks, order = {}, []
    for n, i in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        body = lines[i:end]
        while body and not body[-1].strip():
            body.pop()
        g = ENTRY_START.match(lines[i]).group(1)
        blocks[g] = "\n".join(body)
        order.append(g)
    if len(set(order)) != len(order):
        raise ValueError("duplicate glyph in the KB")
    return lines[:starts[0]], blocks, order


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=KB)
    a = ap.parse_args()

    entries = json.load(io.open(KJ, encoding="utf-8"))["entries"]
    entries.sort(key=lambda e: e["lesson_order"])
    raw = io.open(KB, encoding="utf-8", newline="").read()
    crlf = raw.count("\r\n")
    lines = raw.replace("\r\n", "\n").split("\n")
    pre, old_blocks, old_order = split_entries(lines)

    new_blocks = {e["glyph"]: entry_md(e) for e in entries}
    added = [g for g in new_blocks if g not in old_blocks]
    removed = [g for g in old_blocks if g not in new_blocks]
    changed = [g for g in old_blocks if g in new_blocks and old_blocks[g] != new_blocks[g]]
    if removed:
        raise ValueError("the KB documents glyphs kanji.json does not have: %s" % "".join(removed))

    # ---- preamble counts describe this file's own contents
    text_pre = "\n".join(pre)
    n_old, n_new = len(old_blocks), len(new_blocks)
    for a_, b_ in ((("Catalogue (this file) = N4 only = %d glyphs." % n_old),
                    ("Catalogue (this file) = N4 only = %d glyphs." % n_new)),
                   (("## N4 kanji (%d)" % n_old), ("## N4 kanji (%d)" % n_new))):
        if a_ not in text_pre:
            raise ValueError("preamble line not found verbatim: %r" % a_)
        text_pre = text_pre.replace(a_, b_)

    body = "\n\n".join(new_blocks[e["glyph"]] for e in entries)
    out = text_pre.rstrip("\n") + "\n\n" + body + "\n"
    if crlf:
        out = out.replace("\n", "\r\n")

    if a.out == KB:
        shutil.copy2(KB, os.path.join(
            ROOT, "KnowledgeBank",
            "kanji_n4.md.bak_sync_%s" % datetime.now().strftime("%Y%m%d_%H%M%S")))
    io.open(a.out, "w", encoding="utf-8", newline="").write(out)

    # ---------------------------------------------------------------- change guard
    print("entries %d -> %d   (added %d, changed %d, removed %d)"
          % (n_old, n_new, len(added), len(changed), len(removed)))
    print("line endings: %s" % ("CRLF" if crlf else "LF"))
    if changed:
        print("\nCHANGED - kanji.json values back-ported into the KB:")
        for g in sorted(changed, key=lambda g: [e["glyph"] for e in entries].index(g)):
            o = {l.split(":", 1)[0].strip(" -"): l.split(":", 1)[1].strip()
                 for l in old_blocks[g].split("\n")[1:] if ":" in l}
            n = {l.split(":", 1)[0].strip(" -"): l.split(":", 1)[1].strip()
                 for l in new_blocks[g].split("\n")[1:] if ":" in l}
            for k in sorted(set(o) | set(n)):
                if o.get(k) != n.get(k):
                    print("   %s  %-14s %s  ->  %s" % (g, k, o.get(k, "(absent)"),
                                                       n.get(k, "(absent)")))
    if added:
        print("\nADDED - %d entries that had no KB record (JA-12's 27):" % len(added))
        for e in entries:
            if e["glyph"] in added:
                print("   %3d  %s  on=%-12s kun=%-14s primary=%s (%s)"
                      % (e["lesson_order"], e["glyph"],
                         "、".join(e.get("on") or []) or "-",
                         "、".join(e.get("kun") or []) or "-",
                         e["primary_reading"], e["primary_kind"]))

    check = io.open(a.out, encoding="utf-8").read()
    got = re.findall(r"^- \*\*(.)\*\*", check, re.M)
    assert len(got) == n_new, "wrote %d entries, expected %d" % (len(got), n_new)
    assert set(got) == set(new_blocks), "glyph set mismatch after write"
    assert "## N4 kanji (%d)" % n_new in check, "header count not updated"
    print("\nwrote %s  (%d entries, header says %d)" % (a.out, len(got), n_new))
    return 0


if __name__ == "__main__":
    sys.exit(main())
