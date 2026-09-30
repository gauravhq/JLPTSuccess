"""Build N4 data files from the KnowledgeBank markdown source-of-truth.

Run from the repo root:
    python tools/build_data.py            # regenerate the kanji path
    python tools/build_data.py --report   # parse and diff only, write nothing

Generates (kanji path only):
    data/kanji.json                - merge-preserving refresh of the build-owned fields
    data/n4_kanji_readings.json    - merge-preserving refresh of on / kun / primary / primary_kind

WHY THIS FILE WAS REWRITTEN (2026-09-29)
----------------------------------------
The previous version parsed an N5-era markdown dialect that `KnowledgeBank/kanji_n4.md` has not
used for a long time. It expected `- On:` / `- Kun:` / `- Meaning:` (capitalised, comma-separated),
converted on-yomi to hiragana and stripped okurigana parentheses. The current KB writes `- on:` /
`- kun:` / `- meanings:`, separates readings with an ideographic comma, keeps on-yomi in katakana,
keeps okurigana as `あたら(しい)`, states `(none)` for an empty set, and carries an explicit
`- primary: R  (kind: on|kun)` line plus `secondary_on` / `secondary_kun`.

None of that matched, so every field came back empty, and because the empty values were still
present as keys the merge-preserve step wrote them over good data. Running it once emptied on / kun
/ meanings across all 170 kanji.json entries, emptied the primary of 167 of 252 readings, cut the
kanji whitelist from 249 to 170 and took `check_content_integrity.py` from 27 violations to 160.

Three changes stop that from being possible again:

  1. The parser follows the KB's actual format, and asserts it parsed something. An entry that
     yields no readings and no meanings is a PARSE FAILURE, not an empty record.
  2. A glyph in data/kanji.json with no KB entry is an ERROR, not a silent deletion. The old
     behaviour dropped it along with its hand-authored examples, notes and review_status.
  3. The builder no longer writes the three files it had no business owning. `extract_vocab_corpus`
     rebuilt data/vocab.json as a naive overwrite that discarded `examples`, `pos`, `kb_pos_tag`
     and `tier` on all 637 entries; `extract_vocab` rebuilt a whitelist the committed data holds
     empty; and the kanji whitelist is the N5 union N4 UNION (249), which the N4-only catalogue
     cannot produce. Those paths are quarantined below with the measurements that condemned them.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_content_integrity import EXPECTED_PRIMARY_READING  # noqa: E402  (single source, see below)

NONE_TOKENS = {"", "-", "(none)", "（none）", "none"}
HEADER_RE = re.compile(r"^\s*-\s+\*\*([一-鿿])\*\*\s*(?:\(tier:\s*([A-Za-z0-9_]+)\s*\))?")
FIELD_RE = re.compile(r"^\s+-\s*([A-Za-z_]+)\s*:\s*(.*)$")
PRIMARY_RE = re.compile(r"^(.*?)\s*\(\s*kind\s*:\s*(on|kun)\s*\)\s*$")
READING_SEP = re.compile(r"[、,]")


def _readings(value: str) -> list[str]:
    """Split a reading line. Readings keep their script and their okurigana parentheses."""
    if value.strip().lower() in NONE_TOKENS:
        return []
    out, seen = [], set()
    for part in READING_SEP.split(value):
        p = part.strip()
        if p and p.lower() not in NONE_TOKENS and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _meanings(value: str) -> list[str]:
    """Glosses separate on comma or semicolon. 起 writes `wake up, get up; rouse` and
    data/kanji.json stores that as three glosses, so a comma-only split is wrong."""
    if value.strip().lower() in NONE_TOKENS:
        return []
    return [p.strip() for p in re.split(r"[,;]", value) if p.strip()]


def parse_kb(md_path: Path) -> dict[str, dict]:
    """Parse KnowledgeBank/kanji_n4.md into one record per glyph.

    Record: glyph, tier, on[], kun[], secondary_on[], secondary_kun[], primary_reading,
    primary_kind, meanings[]. Readings are kept verbatim: on-yomi stays katakana and kun-yomi
    keeps its okurigana, because that is what data/kanji.json stores.
    """
    entries: dict[str, dict] = {}
    cur = None
    for lineno, raw in enumerate(md_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.rstrip()
        m = HEADER_RE.match(line)
        if m:
            glyph, tier = m.group(1), m.group(2)
            if glyph in entries:
                raise ValueError("%s:%d duplicate entry for %s" % (md_path.name, lineno, glyph))
            cur = {"glyph": glyph, "tier": tier, "on": [], "kun": [],
                   "secondary_on": [], "secondary_kun": [],
                   "primary_reading": None, "primary_kind": None, "meanings": [],
                   "_line": lineno}
            entries[glyph] = cur
            continue
        if cur is None:
            continue
        f = FIELD_RE.match(line)
        if not f:
            if not line.strip() or line.startswith("#"):
                cur = None
            continue
        key, val = f.group(1).lower(), f.group(2)
        if key in ("on", "kun", "secondary_on", "secondary_kun"):
            cur[key] = _readings(val)
        elif key == "meanings":
            cur["meanings"] = _meanings(val)
        elif key == "primary":
            pm = PRIMARY_RE.match(val.strip())
            if not pm:
                raise ValueError("%s:%d %s primary line has no (kind: on|kun): %r"
                                 % (md_path.name, lineno, cur["glyph"], val))
            cur["primary_reading"], cur["primary_kind"] = pm.group(1).strip(), pm.group(2)

    # A silently-empty parse is the failure mode that caused the 2026-09-29 data loss. Refuse it.
    broken = [e["glyph"] for e in entries.values()
              if not (e["on"] or e["kun"]) or not e["meanings"] or not e["primary_reading"]]
    if broken:
        raise ValueError(
            "parsed %d entries but %d have no readings / no meanings / no primary: %s\n"
            "This means the markdown dialect changed. FIX THE PARSER - do not let it write."
            % (len(entries), len(broken), "".join(broken[:20])))
    for e in entries.values():
        e.pop("_line", None)
    return entries


def corpus_fields(e: dict) -> dict:
    """The kanji.json fields this build owns, derived from one KB record."""
    out = {
        "glyph": e["glyph"],
        "on": list(e["on"]),
        "kun": list(e["kun"]),
        "primary_reading": e["primary_reading"],
        "primary_kind": e["primary_kind"],
        "meanings": list(e["meanings"]),
    }
    if e["secondary_on"] or e["secondary_kun"]:
        out["secondary_readings"] = {"on": list(e["secondary_on"]),
                                     "kun": list(e["secondary_kun"])}
    if e["tier"]:
        out["tier"] = e["tier"]
    return out


# data/kanji.json carries fields the build does NOT own - hand-authored `examples`, `notes`,
# the flags (`mnemonic_not_etymology`, `origin_disputed`), `deck_order_rank`, `lesson_order`,
# `review_status`, `display_meaning`, `stroke_order_svg`, plus `_meta.history`. Refresh only the
# build-owned reading/meaning fields and keep the rest, or a rebuild destroys authored content.
BUILD_OWNED = {"glyph", "on", "kun", "primary_reading", "primary_kind", "meanings",
               "secondary_readings", "tier"}
# n4_kanji_readings.json additionally covers 82 n5_prerequisite glyphs the N4-only KB does not
# document. Those are preserved untouched; only the documented glyphs are refreshed.
# `tier` is deliberately NOT owned here. The two files use the name for different questions, the
# same way they do for `primary`. In data/kanji.json `tier` says which lesson tier the CARD belongs
# to, and all 170 cards are core_n4. In n4_kanji_readings.json it says whether the GLYPH is an N5
# prerequisite, and 24 of those 170 cards teach a glyph the learner already met at N5 (会 力 口 古
# 員 安 店 手 新 曜 田 目 社 私 空 立 花 言 買 足 週 道 飲 駅). That set is load-bearing:
# practice_validate.py and build_language_review_xlsx.py QA #25 both define the always-allowed
# background pool as exactly `tier == n5_prerequisite`, so overwriting it with the card tier makes
# ordinary N5 kanji read as out-of-scope in early worlds. Letting the builder own this field flipped
# all 24 and failed World 1 on 会 / 空 / 立. Do not add it back.
READ_OWNED = {"on", "kun", "primary", "primary_kind", "secondary_readings"}


def furigana_primary(glyph: str, catalogue_primary: str) -> str:
    """The reading n4_kanji_readings.json should carry for `glyph`.

    The two files ask different questions of the word "primary". data/kanji.json is a catalogue,
    so its `primary_reading` is the headline reading in the form the catalogue prints it: on-yomi
    in katakana, kun-yomi with its okurigana (会 カイ, 新 シン, 安 やす(い)). n4_kanji_readings.json
    feeds js/furigana.js, which pastes `primary` over a bare glyph as ruby, so it needs the
    context-most-common reading in the form you would actually write above the character
    (会 かい, 新 しん, 安 やす).

    For 167 of the 170 glyphs those coincide and the catalogue value is used directly. The three
    that differ are fixed by EXPECTED_PRIMARY_READING in tools/check_content_integrity.py, which
    check X-6.9 enforces and which JA-24 backs up for i-adjectives. That table is imported rather
    than copied: a second copy is a second thing to forget. The previous builder carried its own
    PASS10_PRIMARY_OVERRIDES for this job; dropping it silently reintroduced 3 X-6.9 failures.
    """
    return EXPECTED_PRIMARY_READING.get(glyph, catalogue_primary)


def reading_fields(e: dict) -> dict:
    """The n4_kanji_readings.json fields this build owns, derived from one KB record."""
    out = {"on": list(e["on"]), "kun": list(e["kun"]),
           "primary": furigana_primary(e["glyph"], e["primary_reading"]),
           "primary_kind": e["primary_kind"]}
    if e["secondary_on"] or e["secondary_kun"]:
        out["secondary_readings"] = {"on": list(e["secondary_on"]),
                                     "kun": list(e["secondary_kun"])}
    return out


VOCAB_LINE = re.compile(
    r"^\s*-\s+(?P<forms>[^\s\(\-]+)\s*(?:\((?P<reading>[^)]+)\))?\s*-\s*(?P<gloss>.+?)\s*$", re.M)
_JP = re.compile(r"[぀-ヿ一-鿿]")


def vocab_forms(md_path: Path) -> list[str]:
    """Every vocabulary form in KnowledgeBank/vocabulary_n4.md, in source order.

    This is the RECOGNITION ALLOWLIST that tools/lint_content.py reads to decide whether a
    kanji-bearing token in grammar.json / questions.json is in scope. It is deliberately a
    SUPERSET of data/vocab.json's forms, not a mirror: a multi-form entry (`いい / よい - ...`)
    contributes both spellings while vocab.json carries only the canonical one, and a word may be
    recognised as in-scope before it has a full structured catalogue entry. An audit reporting
    "forms in the whitelist but not in vocab.json" is describing that design, not a defect.

    Unlike vocab.json this file is purely generated - it has no hand-authored fields - so writing
    it whole is safe. What is NOT safe is writing it empty, which is how it has sat since the
    monorepo migration: `[]` makes lint_content.py treat every vocabulary token as out of scope.
    Hence the floor assertion in the caller.
    """
    out, seen = [], set()
    for m in VOCAB_LINE.finditer(md_path.read_text(encoding="utf-8")):
        for form in m.group("forms").split("/"):
            f = form.strip()
            if f and _JP.search(f) and f not in seen:
                seen.add(f)
                out.append(f)
    return out


def write_json(path: Path, payload) -> None:
    """Write indent-2 JSON, preserving whether the file already ended with a newline.

    A mismatch here shows up as a whole-file diff in review and buries the real change. The
    committed files end WITHOUT a trailing newline; the previous builder appended one.
    """
    tail = "\n" if path.exists() and path.read_bytes().endswith(b"\n") else ""
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + tail, encoding="utf-8")


def diff_report(kb: dict[str, dict], data_dir: Path) -> tuple[list[str], list[str]]:
    """What a rebuild would change, field by field. Returns (changes, errors)."""
    changes, errors = [], []
    kpath = data_dir / "kanji.json"
    prev = {e["glyph"]: e for e in json.loads(kpath.read_text(encoding="utf-8"))["entries"]}

    undocumented = sorted(set(prev) - set(kb))
    if undocumented:
        errors.append(
            "%d glyph(s) in data/kanji.json have no KnowledgeBank entry: %s\n"
            "  A rebuild must not delete them. Write their KB entries first "
            "(check_content_integrity.py JA-12 requires this too)."
            % (len(undocumented), "".join(undocumented)))

    for g in sorted(set(prev) & set(kb)):
        new = corpus_fields(kb[g])
        for k in sorted(BUILD_OWNED):
            if k in new and prev[g].get(k) != new[k]:
                changes.append("kanji.json  %s.%-19s %r -> %r" % (g, k, prev[g].get(k), new[k]))
        for k in sorted(set(prev[g]) & BUILD_OWNED - set(new)):
            changes.append("kanji.json  %s.%-19s %r -> (KB is silent; kept)"
                           % (g, k, prev[g].get(k)))

    rpath = data_dir / "n4_kanji_readings.json"
    prev_r = json.loads(rpath.read_text(encoding="utf-8"))
    for g in sorted(set(prev_r) & set(kb)):
        new = reading_fields(kb[g])
        for k in sorted(READ_OWNED):
            if k in new and prev_r[g].get(k) != new[k]:
                changes.append("readings    %s.%-19s %r -> %r" % (g, k, prev_r[g].get(k), new[k]))
    return changes, errors


def main() -> int:
    report_only = "--report" in sys.argv
    kanji_md = ROOT / "KnowledgeBank" / "kanji_n4.md"
    data_dir = ROOT / "data"
    if not kanji_md.exists():
        print("ERROR: missing %s" % kanji_md, file=sys.stderr)
        return 1

    kb = parse_kb(kanji_md)
    print("parsed %d kanji entries from %s" % (len(kb), kanji_md.name))

    changes, errors = diff_report(kb, data_dir)
    for e in errors:
        print("\nERROR: %s" % e, file=sys.stderr)
    print("\n%d field change(s) a rebuild would make:" % len(changes))
    for c in changes:
        print("   %s" % c)
    if errors:
        print("\nrefusing to write: fix the errors above first", file=sys.stderr)
        return 1
    if report_only:
        print("\n--report: nothing written")
        return 0

    kpath = data_dir / "kanji.json"
    payload = json.loads(kpath.read_text(encoding="utf-8"))
    for entry in payload["entries"]:
        new = corpus_fields(kb[entry["glyph"]])
        for k in BUILD_OWNED:
            if k in new:
                entry[k] = new[k]
    write_json(kpath, payload)
    print("\nWrote %4d kanji corpus entries to data/kanji.json (merge-preserving)"
          % len(payload["entries"]))

    rpath = data_dir / "n4_kanji_readings.json"
    merged = json.loads(rpath.read_text(encoding="utf-8"))
    for g, e in kb.items():
        m = dict(merged.get(g, {}))
        m.update(reading_fields(e))
        merged[g] = m
    write_json(rpath, merged)
    print("Wrote %4d kanji readings to data/n4_kanji_readings.json (merge-preserving)"
          % len(merged))

    wpath = data_dir / "n4_vocab_whitelist.json"
    forms = vocab_forms(ROOT / "KnowledgeBank" / "vocabulary_n4.md")
    prev = json.loads(wpath.read_text(encoding="utf-8")) if wpath.exists() else []
    # The whitelist is a superset of vocab.json's forms by design, so it can never legitimately
    # hold fewer. An extraction that comes back short means the markdown dialect moved and the
    # regex stopped matching - the same failure that emptied the kanji fields. Refuse to write it.
    catalogue = {e["form"] for e in
                 json.loads((data_dir / "vocab.json").read_text(encoding="utf-8"))["entries"]}
    short = sorted(catalogue - set(forms))
    if short:
        print("\nERROR: %d vocab.json form(s) did not come back from vocabulary_n4.md: %s\n"
              "The whitelist is a SUPERSET of the catalogue, so this means the parser stopped "
              "matching. Refusing to write it." % (len(short), "".join(short[:12])), file=sys.stderr)
        return 1
    write_json(wpath, forms)
    print("Wrote %4d vocab forms to data/n4_vocab_whitelist.json (%d before)"
          % (len(forms), len(prev)))
    return 0


# ---------------------------------------------------------------------------
# QUARANTINED. These three outputs were rebuilt by this script until 2026-09-29 and every one of
# them was destructive, measured against the committed data on that date:
#
#   data/n4_kanji_whitelist.json  249 -> 143. The KB header defines the whitelist as the N5 union
#       N4 UNION; this catalogue holds N4 only, so it cannot produce the N5 half. It stays
#       quarantined here permanently - tools/build_n4_kanji.py is the writer, building it as
#       `N5 whitelist (106) + N4 entries`. RESOLVED 2026-09-30: the 249 committed then was short
#       by 可 的 身, which entered kanji.json and the readings file in the 143 -> 170 expansion and
#       were never added here, because neither writer had run since. The file now holds 252 and
#       equals the readings tier union, which JA-35 asserts on every run.
#   data/vocab.json               637 -> 637 but ALL 637 glosses differed, and the rebuild was a
#       naive overwrite with no merge-preserve, so it also discarded `examples`, `pos`,
#       `kb_pos_tag` and `tier` from every entry. STAYS QUARANTINED, but the 2026-09-30
#       investigation showed vocab.json is not the wrong side and nothing needs correcting in it:
#       a KB line reads `- form (reading) - [pos] gloss [tier:X] [examples:N]`, and vocab.json is a
#       correct DECOMPOSITION of that into gloss / kb_pos_tag / tier. Checked across all 637
#       entries: 637/637 glosses match once the annotations are stripped, 637/637 kb_pos_tag match
#       the [pos] tag, 637/637 tier match the [tier:] tag. The old extractor simply predated the
#       annotations and left them in the gloss. Rebuilding vocab.json needs a merge-preserving
#       writer that understands that shape AND keeps `examples`; until someone writes one, the
#       file is hand-maintained and JA-31 guards the PoS relationship.
#   data/n4_vocab_whitelist.json  RESTORED 2026-09-30, this script writes it again. It had been an
#       empty list since the monorepo migration - the only commit that ever touched it - which was
#       not a deliberate state: it is the recognition allowlist tools/lint_content.py reads, and
#       empty means every vocabulary token reads as out of scope (the lint reported 15 such tokens;
#       after repopulating, 7, all conjugated or compound forms its own note calls unresolvable
#       without a morphological analyzer). Unlike vocab.json it carries no hand-authored fields, so
#       writing it whole is safe. JA-36 asserts it covers the catalogue.
#
# Restoring any of them means deciding what the file is FOR, then writing a merge-preserving
# builder for it the way the kanji path has. Until then this script does not touch them.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main())
