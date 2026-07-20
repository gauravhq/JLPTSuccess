# -*- coding: utf-8 -*-
"""
verify_kanji_data.py  -- permanent, re-runnable invariant checker for the N4 kanji workbook data.

Replaces the throwaway one-off audit scripts. Every check states its SCOPE and proves it, so a
"0 findings" result cannot come from a check that silently skipped the broken cases (the failure
mode that let 写す/集まる slip: an earlier check only looked at form==glyph).

Primary sources (auto-cached under ../Workbook/_refcache, auto-downloaded if missing):
  * KANJIDIC2  (edrdg.org)  -- reading existence + partner-kanji readings for decomposition
  * JMdict_e   (edrdg.org)  -- example-gloss grounding

Checks (FAIL blocks release; WARN is informational):
  1  cross-file reading sync   kanji.json <-> n4_kanji_readings.json <-> Excel cols 15/16
  2  reading vs KANJIDIC2      our on/kun readings absent from the primary source  (FAIL)
  3  reading-consistency       every example reading decomposes from OUR on/kun    (FAIL if the
                               example needs a reading KANJIDIC2 has but we don't; WARN if the
                               whole word is jukujikun / irregular)
  4  duplicate gloss           two examples on one card sharing a first-word gloss  (FAIL)
  5  example count             each card has 3-4 examples                           (FAIL)
  6  gloss content             dark real-world clauses on a kids' card              (FAIL)
  7  gloss grounding (JMdict)  each example gloss piece exists in JMdict for the word (WARN)
  8  field completeness        required fields present (empty kun allowed: on-only kanji)
  9  stroke count (SVG)        each KanjiVG diagram's <path> count == KANJIDIC2 stroke_count (FAIL);
                               radical annotation present (WARN). Radical NUMBER not cross-checked
                               (KanjiVG radical systems don't map 1:1 to KANJIDIC2's classical no.)
  10 ♪ sound-tag coverage     every 形声 card's Scene cell carries the ♪ tag/footnote (FAIL, spec);
                               rendered ♪-presence per built card = KI-13, auto-scans once HTML built
Exit code 0 iff no FAIL.
"""
import json, gzip, os, sys, subprocess, urllib.request, functools
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "data"))
CACHE = os.path.normpath(os.path.join(HERE, "..", "Workbook", "_refcache"))
XLSX = os.path.normpath(os.path.join(HERE, "..", "Workbook", "N4_Kanji_Workbook",
                                     "N4_Kanji_Card_Prompts_20260702_143703.xlsx"))
KD2 = os.path.join(CACHE, "kanjidic2.xml.gz")
JMD = os.path.join(CACHE, "_jmdict_e.gz")
URLS = {KD2: "http://www.edrdg.org/kanjidic/kanjidic2.xml.gz",
        JMD: "http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz"}

def ensure(path):
    if os.path.exists(path):
        return True
    os.makedirs(CACHE, exist_ok=True)
    try:
        print("  fetching %s ..." % os.path.basename(path))
        urllib.request.urlretrieve(URLS[path], path)
        return True
    except Exception as e:
        print("  WARN could not fetch %s (%s)" % (path, e))
        return False

# ---------- reading helpers ----------
def kata2hira(s):
    return "".join(chr(ord(c) - 0x60) if "ァ" <= c <= "ヶ" else c for c in s)
VOICE = {"か":"が","き":"ぎ","く":"ぐ","け":"げ","こ":"ご","さ":"ざ","し":"じ","す":"ず","せ":"ぜ",
         "そ":"ぞ","た":"だ","ち":"ぢ","つ":"づ","て":"で","と":"ど","は":"ば","ひ":"び","ふ":"ぶ",
         "へ":"べ","ほ":"ぼ","う":"ゔ"}
HANDAKU = {"は":"ぱ","ひ":"ぴ","ふ":"ぷ","へ":"ぺ","ほ":"ぽ"}

def base_readings(on_list, kun_list):
    base = set()
    for o in on_list:
        base.add(kata2hira(o.replace("-", "")))
    for k in kun_list:
        k = k.replace("-", "")
        stem = k.split(".")[0].split("(")[0]
        base.add(stem)
        if "." in k:
            base.add(k.replace(".", ""))
        elif "(" in k:
            base.add(k.replace("(", "").replace(")", ""))
    return {b for b in base if b}

def variants(base, is_first):
    out = set()
    for b in base:
        if not b:
            continue
        out.add(b)
        if b[-1] in "つちくき":
            out.add(b[:-1] + "っ")          # gemination of final mora (学->がっ)
        if b[-1] == "つ":
            out.add(b[:-1] + "ち")          # 連用形 of つ-verb (待つ->待ち), okurigana often elided
        if b[-1] in "つち":
            out.add(b[:-1])                 # 連用形-style final-drop (待ち->待, 立ち->立)
        if not is_first:
            if b[0] in VOICE:
                out.add(VOICE[b[0]] + b[1:])
            if b[0] in HANDAKU:
                out.add(HANDAKU[b[0]] + b[1:])
    return out

def is_kanji(c):
    return "一" <= c <= "鿿" or c == "々"

# ---------- load data ----------
def load():
    main = json.load(open(os.path.join(DATA, "kanji.json"), encoding="utf-8"))
    ref = json.load(open(os.path.join(DATA, "n4_kanji_readings.json"), encoding="utf-8"))
    return main, ref

def load_kanjidic():
    with gzip.open(KD2, "rb") as f:
        root = ET.parse(f).getroot()
    kd = {}
    for ch in root.findall("character"):
        lit = ch.findtext("literal")
        on = [r.text for r in ch.iter("reading") if r.get("r_type") == "ja_on"]
        kun = [r.text for r in ch.iter("reading") if r.get("r_type") == "ja_kun"]
        sc = ch.findtext("misc/stroke_count")
        rad = next((r.text for r in ch.findall("radical/rad_value")
                    if r.get("rad_type") == "classical"), None)
        kd[lit] = {"on": on, "kun": kun, "base": base_readings(on, kun),
                   "stroke": int(sc) if sc else None, "rad": rad}
    return kd

def load_jmdict(forms):
    """form -> set(lowercased glosses). Only keep entries whose keb/reb is in `forms`."""
    gmap = {}
    want = set(forms)
    with gzip.open(JMD, "rb") as f:
        for ev, el in ET.iterparse(f, events=("end",)):
            if el.tag != "entry":
                continue
            kebs = [k.text for k in el.findall("k_ele/keb")]
            rebs = [r.text for r in el.findall("r_ele/reb")]
            keys = [x for x in kebs + rebs if x in want]
            if keys:
                glosses = {g.text.lower() for g in el.findall("sense/gloss") if g.text}
                for k in keys:
                    gmap.setdefault(k, set()).update(glosses)
            el.clear()
    return gmap

# ---------- checks ----------
def run():
    main, ref = load()
    entries = main["entries"]
    mmap = {e["glyph"]: e for e in entries}
    results = []  # (level, name, detail)
    have_kd = ensure(KD2)
    kd = load_kanjidic() if have_kd else {}

    # ---- 1 cross-file sync ----
    xl = {}  # glyph -> {"on","kun","type","scene"} from the Excel Card Render Prompts sheet
    try:
        import openpyxl
        if os.path.exists(XLSX):
            ws = openpyxl.load_workbook(XLSX, read_only=True)["Card Render Prompts"]
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[1]:  # cols: 4 Type,11 Scene,15 On,16 Kun,19 ConfLevel,22 sound_tag_mode
                    xl[row[1]] = {"on": row[14], "kun": row[15],
                                  "type": row[3] or "", "scene": row[10] or "",
                                  "conf_level": (row[18] or "") if len(row) > 18 else "",
                                  "sound_tag_mode": (row[21] or "") if len(row) > 21 else ""}
    except Exception as e:
        results.append(("WARN", "1-sync", "Excel not read (%s)" % e))
    def nrm(v):
        # Excel uses "-" as a "no reading" placeholder; kanji.json uses []
        toks = [x.strip() for x in (v or "").replace("，", "、").split("、")]
        return [x for x in toks if x and x not in ("-", "—", "−", "－")]
    drift = []
    for e in entries:
        g = e["glyph"]
        if g in ref and (e.get("on", []) != ref[g].get("on", []) or e.get("kun", []) != ref[g].get("kun", [])):
            drift.append("%s json/ref" % g)
        if g in xl:
            if e.get("on", []) != nrm(xl[g]["on"]) or e.get("kun", []) != nrm(xl[g]["kun"]):
                drift.append("%s json/xlsx" % g)
    results.append(("FAIL" if drift else "PASS", "1-cross-file-sync",
                    "%d drift: %s" % (len(drift), drift[:12]) if drift else "all readings agree across 3 files"))

    # secondary_readings (demoted-but-listed jouyo readings) count as "listed" for consistency
    def all_on(e):
        return list(e.get("on", [])) + list(e.get("secondary_readings", {}).get("on", []))
    def all_kun(e):
        return list(e.get("kun", [])) + list(e.get("secondary_readings", {}).get("kun", []))

    # ---- 2 readings vs KANJIDIC2 ----
    if have_kd:
        extras = []
        for e in entries:
            g = e["glyph"]
            kb = kd.get(g, {}).get("base", set())
            mb = base_readings(all_on(e), all_kun(e))
            miss = mb - kb
            if miss:
                extras.append("%s:%s" % (g, "/".join(sorted(miss))))
        results.append(("FAIL" if extras else "PASS", "2-reading-vs-KANJIDIC2",
                        "readings absent from primary source: %s" % extras if extras
                        else "every on/kun reading exists in KANJIDIC2"))
    else:
        results.append(("WARN", "2-reading-vs-KANJIDIC2", "KANJIDIC2 unavailable; skipped"))

    # ---- 3 reading-consistency (full decomposition) ----
    def decompose(form, reading, target, target_base):
        n = len(form)
        @functools.lru_cache(maxsize=None)
        def rec(fi, ri):
            if fi == n:
                return ri == len(reading)
            c = form[fi]
            if not is_kanji(c):
                ch = kata2hira(c)
                return ri < len(reading) and reading[ri] == ch and rec(fi + 1, ri + 1)
            kc = form[fi - 1] if c == "々" and fi > 0 else c
            if c == target or (c == "々" and target in form[:fi]):
                base = target_base
            else:
                base = kd.get(kc, {}).get("base", set())
            for cand in sorted(variants(base, fi == 0), key=len, reverse=True):
                if reading.startswith(cand, ri) and rec(fi + 1, ri + len(cand)):
                    return True
            return False
        return rec(0, 0)

    gaps, juku, bad_single = [], [], []
    if have_kd:
        for e in entries:
            g = e["glyph"]
            ourb = base_readings(all_on(e), all_kun(e))
            kdb = kd.get(g, {}).get("base", set())
            for x in e["examples"]:
                form, reading = x["form"], x["reading"]
                if form == g and kata2hira(reading) not in ourb:
                    bad_single.append("%s/%s" % (g, reading))
                if decompose(form, reading, g, frozenset(ourb)):
                    continue
                if decompose(form, reading, g, frozenset(kdb)):
                    gaps.append("%s %s/%s" % (g, form, reading))   # needs a reading we lack
                else:
                    juku.append("%s %s/%s" % (g, form, reading))   # jukujikun / irregular
        fail3 = bad_single or gaps
        results.append(("FAIL" if fail3 else "PASS", "3-reading-consistency",
                        "single-kanji-off=%s | example-needs-missing-reading=%s | jukujikun(ok)=%d"
                        % (bad_single, gaps, len(juku))))
    else:
        results.append(("WARN", "3-reading-consistency", "KANJIDIC2 unavailable; skipped"))

    # ---- 4 duplicate gloss ----
    dups = []
    for e in entries:
        fw = [x["gloss"].split(";")[0].strip().lower() for x in e["examples"]]
        if len(fw) != len(set(fw)):
            dups.append(e["glyph"])
    results.append(("FAIL" if dups else "PASS", "4-duplicate-gloss",
                    "cards with dup first-word gloss: %s" % dups if dups else "none"))

    # ---- 5 example count ----
    bad_n = [(e["glyph"], len(e["examples"])) for e in entries if not 3 <= len(e["examples"]) <= 4]
    results.append(("FAIL" if bad_n else "PASS", "5-example-count",
                    "off-range: %s" % bad_n if bad_n else "all cards 3-4 examples"))

    # ---- 6 gloss content ----
    DARK = ["traffick", "narcotic", " drug", "weapon", "firearm", "prostitut", "sexual",
            " sex ", "brothel", "corpse", "execution", "slaughter", "massacre", "smuggl",
            "heroin ", "cocaine", "opium", "hostage", "torture", " bomb"]
    dark = []
    for e in entries:
        for x in e["examples"]:
            gl = x["gloss"].lower()
            for d in DARK:
                if d in gl:
                    dark.append("%s %s: %s" % (e["glyph"], x["form"], x["gloss"]))
                    break
    results.append(("FAIL" if dark else "PASS", "6-gloss-content",
                    "dark clauses: %s" % dark if dark else "no dark real-world clauses"))

    # ---- 7 gloss grounding vs JMdict ----
    if ensure(JMD):
        import re
        # look up the plain noun too (JMdict stores 発音, not the する-verb surface form 発音する)
        def lookup_keys(form):
            keys = [form]
            for suf in ("する", "した", "な", "だ", "に"):
                if form.endswith(suf) and len(form) > len(suf):
                    keys.append(form[:-len(suf)])
            return keys
        def toks(s):
            return {w for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 2}
        forms = {k for e in entries for x in e["examples"] for k in lookup_keys(x["form"])}
        gm = load_jmdict(forms)
        ungrounded = []
        for e in entries:
            for x in e["examples"]:
                jm = set()
                for k in lookup_keys(x["form"]):
                    jm |= gm.get(k, set())
                if not jm:
                    ungrounded.append("%s (not in JMdict)" % x["form"])
                    continue
                gt = toks(x["gloss"])
                jt = set().union(*[toks(j) for j in jm]) if jm else set()
                if gt and not (gt & jt):
                    ungrounded.append("%s=%s" % (x["form"], x["gloss"]))
        results.append(("WARN" if ungrounded else "PASS", "7-gloss-grounding-JMdict",
                        "%d gloss(es) share no word with any JMdict sense (review): %s"
                        % (len(ungrounded), ungrounded[:15]) if ungrounded
                        else "every example gloss shares vocabulary with a JMdict sense for that word"))
    else:
        results.append(("WARN", "7-gloss-grounding-JMdict", "JMdict unavailable; skipped"))

    # ---- 8 field completeness ----
    # NOTE: empty kun is legitimate (on-only jouyo kanji). We do NOT flag it against KANJIDIC2,
    # because KANJIDIC2 kun includes NON-jouyo readings (英 はなぶさ, 銀 しろがね, ...) and there
    # is no per-reading jouyo marker in KANJIDIC2 to distinguish them. Missing-jouyo-kun would
    # need the 常用漢字表 itself; flagging on KANJIDIC2 alone only manufactures false positives.
    req = ["glyph", "on", "meanings", "examples", "primary_reading", "stroke_order_svg"]
    miss = [("%s.%s" % (e["glyph"], f)) for e in entries for f in req if not e.get(f)]
    results.append(("FAIL" if miss else "PASS", "8-field-completeness",
                    "missing required fields: %s" % miss if miss
                    else "all required fields present (empty kun allowed: on-only kanji)"))

    # ---- 9 stroke count (KanjiVG SVG diagram) vs KANJIDIC2 + radical annotation present ----
    # Validates the actual stroke-order artwork the cards depend on against the primary dictionary.
    # NOTE: radical NUMBER is deliberately NOT cross-checked. KanjiVG's kvg:radical carries several
    # systems (general / tradit / nelson / jis) and component variants (氵 for 水, 亻 for 人), which
    # do not map 1:1 to KANJIDIC2's single "classical" Kangxi number - a naive comparison cries wolf
    # (it flagged 11 kanji that are all radical-system differences, not errors). Presence is checked.
    if have_kd:
        n4root = os.path.dirname(DATA)
        sc_bad, no_svg, no_rad = [], [], []
        for e in entries:
            g, rel = e["glyph"], e.get("stroke_order_svg", "")
            p = os.path.join(n4root, rel.replace("/", os.sep)) if rel else ""
            if not p or not os.path.exists(p):
                no_svg.append(g); continue
            s = open(p, encoding="utf-8").read()
            strokes = s.count("<path")
            kdsc = kd.get(g, {}).get("stroke")
            if kdsc is not None and strokes != kdsc:
                sc_bad.append("%s svg=%d kanjidic=%d" % (g, strokes, kdsc))
            if "kvg:radical" not in s:
                no_rad.append(g)
        if sc_bad or no_svg:
            lvl9, det9 = "FAIL", "SVG missing: %s | stroke count != KANJIDIC2: %s" % (no_svg, sc_bad)
        elif no_rad:
            lvl9, det9 = "WARN", "stroke counts all match; %d SVG lack kvg:radical: %s" % (len(no_rad), no_rad)
        else:
            lvl9, det9 = "PASS", "all %d SVG stroke counts match KANJIDIC2; radical annotation present" % len(entries)
        results.append((lvl9, "9-stroke-count-vs-KANJIDIC2", det9))
    else:
        results.append(("WARN", "9-stroke-count-vs-KANJIDIC2", "KANJIDIC2 unavailable; skipped"))

    # ---- 10 ♪ sound-tag coverage (KI-01 spec + KI-13 render hook) ----
    # SPEC (checkable now): every 形声 card's Scene cell must carry the ♪ sound-tag/footnote.
    # RENDER (KI-13): once card HTML is built, the same ♪ must appear in the rendered output.
    if xl:
        # keisei = the Type STARTS WITH 形声. A 会意-shinjitai card whose Type merely mentions
        # its traditional form's 形声 nature (e.g. 体 "会意 ... trad. 體 = 形声", 医 "会意 ... 醫
        # also read 形声") must NOT be counted as keisei -- it has no phonetic in its taught form,
        # so it is not required to carry a ♪ tag. (recheck-4 fix, 2026-07-20)
        keisei = [e["glyph"] for e in entries if xl.get(e["glyph"], {}).get("type", "").startswith("形声")]
        # a standard 形声 card must show the ♪ in its Scene; exception modes (footnote-only /
        # traditional-form / integrated) are approved to omit the separable tag (item 16).
        spec_missing = [g for g in keisei if "♪" not in xl.get(g, {}).get("scene", "")
                        and (xl.get(g, {}).get("sound_tag_mode", "standard") or "standard") == "standard"]
        # RENDER (KI-13): scan the built KANJI-workbook HTML only (not the sibling vocab/grammar
        # books). Each 形声 card must emit >=1 ♪, so a current build must carry >= len(keisei).
        import glob as _glob
        htmls = _glob.glob(os.path.join(os.path.dirname(DATA), "Workbook",
                                        "N4_Kanji_Workbook", "*kanji*.html"))
        render_fail = False
        if htmls:
            built = max(htmls, key=os.path.getmtime)
            n = open(built, encoding="utf-8", errors="ignore").read().count("♪")
            if n < len(keisei):
                render_fail = True
                render_note = " | built HTML %s carries only %d ♪ (< %d 形声 cards)" % (
                    os.path.basename(built), n, len(keisei))
            else:
                render_note = " | built HTML carries %d ♪ (>= %d 形声 cards)" % (n, len(keisei))
        else:
            render_note = " | no built kanji card HTML yet (rendered ♪-presence = KI-13, render-stage)"
        results.append(("FAIL" if (spec_missing or render_fail) else "PASS", "10-sound-tag-coverage",
                        "%d 形声 cards; Scene-cell ♪ missing: %s%s"
                        % (len(keisei), spec_missing if spec_missing else "none", render_note)))
    else:
        results.append(("WARN", "10-sound-tag-coverage", "Excel not read; skipped"))

    # ---- 11 example readability (mirrors the relaxed JA-16 policy, 2026-07-20) ----
    # Examples may use ANY kanji (natural high-frequency words are wanted), but any example
    # containing kanji outside the N4+N5 whitelist MUST carry a reading so it is displayable.
    import re as _re
    wl_path = os.path.join(DATA, "n4_kanji_whitelist.json")
    if os.path.exists(wl_path):
        wl = set(json.load(open(wl_path, encoding="utf-8")))
        KRE = _re.compile(r"[一-鿿]")
        unreadable = []
        for e in entries:
            t = e["glyph"]
            for x in e["examples"]:
                oos = [c for c in KRE.findall(x["form"]) if c != t and c not in wl]
                if oos and not (x.get("reading") or "").strip():
                    unreadable.append("%s %s %s" % (t, x["form"], oos))
        results.append(("FAIL" if unreadable else "PASS", "11-example-readability",
                        "out-of-scope-kanji examples missing a reading: %s" % unreadable
                        if unreadable else
                        "every example with out-of-scope kanji carries a reading (JA-16 relaxed policy)"))
    else:
        results.append(("WARN", "11-example-readability", "whitelist file missing; skipped"))

    # ---- 12 Confidence-level <-> origin_disputed consistency (controlled values) ----
    if xl:
        ALLOWED = {"High", "Medium", "Low", "Disputed"}
        bad_val = [g for g in mmap if g in xl and xl[g].get("conf_level") not in ALLOWED]
        mism = [g for g in mmap if g in xl and
                (xl[g].get("conf_level") == "Disputed") != bool(mmap[g].get("origin_disputed"))]
        results.append(("FAIL" if (bad_val or mism) else "PASS", "12-confidence-consistency",
                        "non-controlled values: %s | Disputed!=origin_disputed: %s"
                        % (bad_val, mism) if (bad_val or mism)
                        else "every Confidence level is High/Medium/Low/Disputed and Disputed <-> origin_disputed"))
    else:
        results.append(("WARN", "12-confidence-consistency", "Excel not read; skipped"))

    # ---- 13 no conjugation/grammar note left inside an example gloss ----
    import re as _re13
    gn = [(e["glyph"], x["form"]) for e in entries for x in e["examples"]
          if _re13.search(r"Group\s*\d\s*exception", x["gloss"])]
    results.append(("FAIL" if gn else "PASS", "13-gloss-no-grammar-note",
                    "glosses with grammar notes (move to grammar_note): %s" % gn if gn
                    else "no example gloss carries a Group-exception grammar note"))

    # ---- report ----
    print("\n=== verify_kanji_data.py : %d kanji ===" % len(entries))
    nfail = 0
    for lvl, name, detail in results:
        print("[%s] %-26s %s" % (lvl, name, detail))
        if lvl == "FAIL":
            nfail += 1
    print("=== %d FAIL, %d checks ===" % (nfail, len(results)))
    return 1 if nfail else 0

if __name__ == "__main__":
    sys.exit(run())
