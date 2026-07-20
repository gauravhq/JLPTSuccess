"""Enforce JA-accuracy and content-integrity invariants across the KB question banks.

Run from the repo root:
    python tools/check_content_integrity.py

Exits with 0 if every invariant passes, 1 otherwise. Designed as a CI release
blocker so future JSON / KB edits cannot silently regress past the bar set by
audit Passes 1-10 (`verification.md`).

Spec reference: feedback/ui-testing-plan.md §12.1.

The 16 invariants:

X-6.1 Catalog completeness     - every kanji in any correct-answer option is in kanji_n4.md
X-6.2 Reading consistency      - 今年 reads ことし everywhere except as a deliberate distractor
X-6.3 No mixed-kanji-kana      - no broken compounds like 図しょかん, 大さか, 東きょう, 京と
X-6.4 No orphan vocab          - guard list (advisory; lint_content.py is the deeper check)
X-6.5 No em-dashes             - 0 occurrences of U+2014 across all 9 KB files
X-6.6 Group-1 ru-verb flags    - 入る / 帰る / 走る / 知る / 切る / 要る all carry the flag
X-6.7 No false synonymy claims - "Direct synonymy" / "Direct antonym pair" only on whitelisted pairs
JA-1  Stem-kanji scope         - every kanji in a question stem AND correct-answer text is in kanji_n4.md
JA-2  Particle-set sanity      - questions whose options are particles use only N5 particles
JA-3  Furigana / catalog match - heuristic; flagged occurrences require manual review
JA-4  Vocab-reading uniqueness - vocab entries with multiple readings list all of them
JA-5  Answer-key sanity        - every "**Answer: N**" has N in {1,2,3,4} and matching option exists
JA-6  No two-correct answers   - regression guard for the "から vs ので" class of bug
JA-7  No same-stem duplicates  - within each question file
JA-8  Q-count integrity        - moji=100, goi=100, bunpou=100, dokkai=102, authentic=189; total=591
JA-9  Engine display contract  - every question file has the "Engine display note" header
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
KB = ROOT / "KnowledgeBank"

QUESTION_FILES = [
    "moji_questions_n4.md",
    "goi_questions_n4.md",
    "bunpou_questions_n4.md",
    "dokkai_questions_n4.md",
    "externally_sourced_n4.md",
]

CATALOG_FILES = ["grammar_n4.md", "kanji_n4.md", "vocabulary_n4.md", "sources.md"]

EXPECTED_Q_COUNTS = {
    "moji_questions_n4.md": 100,
    "goi_questions_n4.md": 100,
    "bunpou_questions_n4.md": 100,
    "dokkai_questions_n4.md": 102,
    "externally_sourced_n4.md": 189,
}
EXPECTED_TOTAL = sum(EXPECTED_Q_COUNTS.values())  # 591

# X-6.6: required ru-verb exception flags
RU_VERB_EXCEPTIONS = ["入る", "はいる", "かえる", "帰る", "はしる", "走る", "しる", "知る", "きる", "切る"]
# 要る is "いる - to need" - the entry uses kana, so flag is checked separately
# Note: vocab uses kana for some forms; we'll fuzzy-match on the romanized verb root.
RU_VERB_FLAG_TEXT = "Group 1 exception"

# X-6.5: em-dash codepoint
EM_DASH = "—"

# X-6.3: known mixed-kanji-kana antipatterns from Pass-9 audit
MIXED_KANJI_KANA_ANTIPATTERNS = [
    "図しょ",  # 図書館 written as 図しょかん
    "大さか",  # 大阪 written as 大さか
    "東きょ",  # 東京 written as 東きょう
    "京と",   # 京都 written as 京と
    "中ご",   # 中国語 etc.
    "日ご",   # 日本語 etc.
]

# X-6.7: pairs that are GENUINELY synonymous (whitelisted; "Direct synonymy" claim is OK here)
GENUINE_SYNONYMY_WHITELIST = [
    ("おおぜい", "たくさん"),  # for people, truly synonymous
    ("とおくない", "ちかい"),   # direct antonym pair
    ("あつくない", "すずしい"), # direct antonym pair
]

# JA-2: N5 particle set. Question options that look like particles must come from this set.
N5_PARTICLES = {
    "は", "が", "を", "に", "で", "へ", "と", "から", "まで", "より",
    "の", "も", "や", "か", "ね", "よ", "ぐらい", "ごろ", "だけ", "しか",
    "など", "ばかり", "でも",
}

# JA-9: required header text
ENGINE_DISPLAY_NOTE_PHRASE = "Engine display note"

# Regex
KANJI_RE = re.compile(r"[一-鿿]")
# Question header tolerates trailing notes like "#### Q91 (blank 1)" / "### Q59 (REPLACED ...)"
QUESTION_HEADER_RE = re.compile(r"^(### Q\d+|#### Q\d+)(?:\s|$)", re.M)
ANSWER_LINE_RE = re.compile(r"^\*\*Answer:\s*(\d+)\*\*", re.M)
OPTION_LINE_RE = re.compile(r"^(\d)\.\s+(.+?)\s*$", re.M)
KATAKANA_RE = re.compile(r"[゠-ヿ]")
HIRAGANA_RE = re.compile(r"[぀-ゟ]")
INLINE_FORMAT_RE = re.compile(r"<[^>]+>|__|\*\*")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_inline_format(s: str) -> str:
    return INLINE_FORMAT_RE.sub("", s)


def kanji_catalog() -> set[str]:
    """Extract every kanji from kanji_n4.md catalog. Tolerates `[Ext]` / `[Cul]` tag suffixes:
    `- **員** **[Ext]**` matches just like `- **学**`."""
    text = load_text(KB / "kanji_n4.md")
    out: set[str] = set()
    for line in text.splitlines():
        m = re.match(r"^- \*\*([一-鿿])\*\*", line)
        if m:
            out.add(m.group(1))
    return out


# Pragmatic N5 augmentation: kanji that are not in the strict catalog but appear in
# stems / correct answers across audit Passes 1-10 and were accepted by the audits.
# Genki / Minna no Nihongo / Try! list these at N5; the strict JLPT-Sensei list omits
# them. Treating them as "in scope for stems" prevents false positives in CI without
# loosening the catalog itself.
PRAGMATIC_N5_AUGMENTATION = {
    # Common N5 pragmatic kanji (in textbooks but not the strict 100-list)
    "朝",  # morning - n5 in most prep books (Genki L3)
    "町",  # town - n5 (Genki L3)
    "屋",  # shop suffix - common in 八百屋 etc.
    "公",  # public - in 公園
    "園",  # garden/park - in 公園 / 動物園
    "早",  # early - common N5 adverb (早く)
    "紙",  # paper - in N5 vocab
    "作",  # make - 作る is N5
    "図",  # figure - in 図書館
    "館",  # building - in 図書館 / 美術館
    "病",  # illness - in 病院
    "院",  # institution - in 病院
    "元",  # origin - in 元気
    "牛",  # cow - in 牛乳 (milk; N5 vocab)
    "乳",  # milk - in 牛乳
    "思",  # think - と思います is N5 pattern
    # Place-name kanji - naturalness exception applies to place names even in grammar stems
    "京",  # 東京 / 京都 / 北京
    "阪",  # 大阪
    "都",  # 京都
    "海",  # 北海道
    "道",  # 北海道 / 道路
    "川",  # river / 川崎 (already in catalog as kun, but check)
}


def augmented_kanji_catalog() -> set[str]:
    """Stem/answer scope set: catalog ∪ N5 prereq whitelist ∪ pragmatic.

    Per the 2026-05-04 'no N5 repetition' refactor, kanji_n4.md only teaches
    the 143 N4-new glyphs, but content (stems, answers, distractors) may
    legitimately use any kanji in the project whitelist (N5 ∪ N4 = 249).
    This function returns the broader content-scope set."""
    out = kanji_catalog() | PRAGMATIC_N5_AUGMENTATION
    # Add the full project whitelist (which includes N5 prereqs).
    try:
        wl_path = ROOT / "data" / "n4_kanji_whitelist.json"
        if wl_path.exists():
            out |= set(json.loads(wl_path.read_text(encoding="utf-8")))
    except Exception:
        pass
    return out


def parse_questions(md_text: str) -> list[dict]:
    """Split a question file into question blocks. Returns list of dicts:
        {qid, stem, options: [(num, text), ...], answer_index, raw_block}
    Best-effort; tolerant of formatting variants.
    """
    # Use the question headers to split (tolerates trailing notes after the Q-number)
    parts = re.split(r"^(### Q\d+|#### Q\d+)(?:\s|$)[^\n]*", md_text, flags=re.M)
    # parts will be [preamble, "### Q1", body1, "### Q2", body2, ...]
    questions = []
    for i in range(1, len(parts), 2):
        qid = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        # Find the first non-empty content line after the header (the stem)
        stem = ""
        for line in body.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith(("_", "**", "1.", "2.", "3.", "4.", ">")):
                continue
            stem = line
            break
        # Options
        options = OPTION_LINE_RE.findall(body)
        # Answer
        ans_match = ANSWER_LINE_RE.search(body)
        ans = int(ans_match.group(1)) if ans_match else None
        questions.append({
            "qid": qid,
            "stem": stem,
            "options": options,  # list of (num_str, text)
            "answer_index": ans,
            "body": body,
        })
    return questions


# ---------------------------------------------------------------------------
# Invariant checks. Each returns list of failure messages (empty = pass).
# ---------------------------------------------------------------------------

def check_x_6_1_catalog_completeness() -> list[str]:
    """Every kanji used as a correct-answer-option text is in kanji_n4.md (or pragmatic N5 set).
    Skips dokkai (passages get the naturalness exception per `dokkai_questions_n4.md` line 17)
    and authentic_extracted (source-faithful to learnjapaneseaz.com)."""
    catalog = augmented_kanji_catalog()
    failures = []
    audited = ["moji_questions_n4.md", "goi_questions_n4.md", "bunpou_questions_n4.md"]
    for fname in audited:
        text = load_text(KB / fname)
        for q in parse_questions(text):
            if q["answer_index"] is None or not q["options"]:
                continue
            answer_text = None
            for num, opt_text in q["options"]:
                if int(num) == q["answer_index"]:
                    answer_text = opt_text
                    break
            if answer_text is None:
                continue
            for ch in strip_inline_format(answer_text):
                if KANJI_RE.match(ch) and ch not in catalog:
                    failures.append(
                        f"X-6.1 {fname}:{q['qid']} correct-answer kanji '{ch}' "
                        f"not in kanji_n4.md catalog (answer text: {answer_text!r})"
                    )
    return failures


def check_x_6_2_today_kotoshi() -> list[str]:
    """今年 reading must be ことし everywhere except as a deliberate distractor option."""
    failures = []
    for fname in QUESTION_FILES:
        text = load_text(KB / fname)
        # Skip occurrences in option lines like `1. こんねん` (they're distractors by design)
        for line_no, line in enumerate(text.split("\n"), 1):
            if "こんねん" not in line:
                continue
            # If the line is an option line (starts with digit + period), allow it
            if re.match(r"^\d\.\s", line.strip()):
                continue
            # If it appears inside a passage / stem / rationale, that's a regression
            failures.append(f"X-6.2 {fname}:L{line_no} contains こんねん outside option list: {line.strip()[:80]!r}")
    return failures


def check_x_6_3_no_mixed_kanji_kana() -> list[str]:
    """No mixed-kanji-kana antipatterns."""
    failures = []
    for fname in QUESTION_FILES + CATALOG_FILES:
        path = KB / fname
        if not path.exists():
            continue
        text = load_text(path)
        for pattern in MIXED_KANJI_KANA_ANTIPATTERNS:
            if pattern in text:
                # Skip if it appears only inside a code block / inline code (audit notes can mention these)
                # Heuristic: count occurrences; if it appears in plain text, fail.
                # For now, simple presence-based fail.
                failures.append(f"X-6.3 {fname} contains mixed-kanji-kana antipattern: {pattern!r}")
    return failures


def check_x_6_4_orphan_vocab() -> list[str]:
    """Advisory check - lint_content.py is the deeper N5-vocab-scope check.
    Here we just verify the lint script exists so we don't drift."""
    failures = []
    if not (ROOT / "tools" / "lint_content.py").exists():
        failures.append("X-6.4 tools/lint_content.py missing (deep N5-vocab-scope lint)")
    return failures


def check_x_6_5_no_em_dashes() -> list[str]:
    """Zero em-dashes across all 9 KB files plus any data/*.md README docs.

    Extended 2026-05-04 to also scan data/*.md so design-rationale READMEs
    (e.g., data/n4_vocab_whitelist_README.md) don't slip past the no-em-
    dash policy. Previously the check was KB-only; one em-dash slipped
    into the v1.12.8 README rewrite and was caught by an external auditor
    rather than CI.
    """
    failures = []
    for fname in QUESTION_FILES + CATALOG_FILES:
        path = KB / fname
        if not path.exists():
            continue
        text = load_text(path)
        if EM_DASH in text:
            count = text.count(EM_DASH)
            failures.append(f"X-6.5 {fname} contains {count} em-dash(es) (U+2014)")
    # Also scan data/*.md (READMEs / design rationale docs).
    data_dir = ROOT / "data"
    if data_dir.exists():
        for md in sorted(data_dir.glob("*.md")):
            text = load_text(md)
            if EM_DASH in text:
                count = text.count(EM_DASH)
                failures.append(f"X-6.5 data/{md.name} contains {count} em-dash(es) (U+2014)")
    return failures


def check_x_6_6_ru_verb_flags() -> list[str]:
    """All 6 Group-1 ru-verb exceptions in vocabulary_n4.md carry the flag annotation."""
    failures = []
    vocab = load_text(KB / "vocabulary_n4.md")
    # Required verbs by their disambiguating substring. Hints are matched
    # case-sensitively as substrings; they tolerate a `[pos]` tag inserted
    # between the leading "- form -" and the gloss (added 2026-05-02 by
    # DEFER-5 PoS-tag pass) by using OR-form fallback hints.
    required = {
        "入る": ["入る (はいる)"],
        "かえる": ["かえる"],
        "はしる": ["はしる"],
        "しる": ["しる"],
        # "きる - to cut" disambiguates from "きる - to wear". After the PoS
        # pass the gloss is "[v1] to cut" so we accept either substring.
        "きる": ["きる - to cut", "to cut (Group 1 exception"],
        # "いる - to need" disambiguates from existence いる.
        "要る": ["いる - to need", "to need (Group 1 exception"],
    }
    flag_count = vocab.count(RU_VERB_FLAG_TEXT)
    if flag_count < 6:
        failures.append(
            f"X-6.6 vocabulary_n4.md has only {flag_count} '{RU_VERB_FLAG_TEXT}' annotation(s); expected >= 6"
        )
    # Spot-check that each required verb's entry line carries the flag
    for verb, hints in required.items():
        found_flagged = False
        for line in vocab.split("\n"):
            if not line.startswith("- "):
                continue
            if any(h in line for h in hints):
                if RU_VERB_FLAG_TEXT in line:
                    found_flagged = True
                break
        if not found_flagged:
            failures.append(f"X-6.6 vocabulary_n4.md: ru-verb exception '{verb}' missing '{RU_VERB_FLAG_TEXT}' flag")
    return failures


def check_x_6_7_no_false_synonymy() -> list[str]:
    """Rationales claiming 'Direct synonymy' / 'Direct antonym pair' must reference whitelisted pairs."""
    failures = []
    claim_patterns = ["Direct synonymy", "Direct antonym pair"]
    for fname in QUESTION_FILES:
        text = load_text(KB / fname)
        for i, line in enumerate(text.split("\n"), 1):
            for claim in claim_patterns:
                if claim in line:
                    # Check if any whitelisted pair appears in the same line
                    whitelisted = any(
                        a in line and b in line for (a, b) in GENUINE_SYNONYMY_WHITELIST
                    )
                    if not whitelisted:
                        failures.append(
                            f"X-6.7 {fname}:L{i} claims '{claim}' without a whitelisted "
                            f"genuinely-synonymous pair: {line.strip()[:100]!r}"
                        )
    return failures


def check_x_6_8_no_ascii_digits_in_tts_source() -> list[str]:
    """Pass-10 regression guard: no ASCII digits adjacent to Japanese in TTS-source fields.
    The fix landed in tools/build_audio.py:normalize_for_tts(). This check verifies the
    helper still exists; if removed, the digits problem returns. The presence of digits
    in source data is by design (audit Pass-10 closure).
    """
    failures = []
    build_audio = ROOT / "tools" / "build_audio.py"
    if not build_audio.exists():
        failures.append("X-6.8 tools/build_audio.py is missing")
        return failures
    if "normalize_for_tts" not in build_audio.read_text(encoding="utf-8"):
        failures.append(
            "X-6.8 tools/build_audio.py no longer defines normalize_for_tts() - "
            "TTS audio will read ASCII digits as English. Pass-10 fix regressed."
        )
    return failures


# Reference table from Pass 10. Each kanji's `primary` field in
# data/n4_kanji_readings.json must match the N5-context-most-common reading.
EXPECTED_PRIMARY_READING = {
    "一": "いち", "二": "に", "三": "さん", "四": "よん", "五": "ご",
    "六": "ろく", "七": "しち", "八": "はち", "九": "きゅう", "十": "じゅう",
    "千": "せん", "本": "ほん", "日": "にち", "時": "じ", "分": "ふん",
    "円": "えん", "月": "がつ", "学": "がく", "生": "せい", "先": "せん",
    "半": "はん", "番": "ばん", "国": "こく", "後": "あと", "会": "かい",
    "車": "しゃ", "新": "しん",
    # 高/長/安: kun-yomi primary (Pass-15 consolidated audit §2.1, applied
    # 2026-05-01). At N5, the i-adjective use (高い/長い/安い) is the
    # high-frequency standalone form; on-yomi compounds are mostly N4+.
    "高": "たか", "長": "なが", "安": "やす",
    "中": "ちゅう", "外": "がい", "東": "とう", "年": "ねん", "人": "にん",
}


def check_x_6_9_furigana_primary_reading_sanity() -> list[str]:
    """Pass-10 regression guard: data/n4_kanji_readings.json `primary`
    field must match the N5-context-most-common reading for each kanji
    in the reference table. The auto-ruby renderer (js/furigana.js) uses
    `primary` as a fallback when no explicit furigana annotation is given.
    Drift here causes 本(もと) instead of 本(ほん), 時(とき) instead of 時(じ),
    etc.
    """
    failures = []
    path = ROOT / "data" / "n4_kanji_readings.json"
    if not path.exists():
        return ["X-6.9 skipped: data/n4_kanji_readings.json missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"X-6.9 failed to parse n4_kanji_readings.json: {e}"]
    for k, expected in EXPECTED_PRIMARY_READING.items():
        if k not in data:
            failures.append(f"X-6.9 kanji '{k}' missing from n4_kanji_readings.json (expected primary={expected!r})")
            continue
        actual = data[k].get("primary")
        if actual != expected:
            failures.append(f"X-6.9 kanji '{k}' primary={actual!r}, expected {expected!r}")
    return failures


def check_ja_1_stem_kanji_scope() -> list[str]:
    """Every kanji in question stems is in the augmented N5 catalog (strict ∪ pragmatic).
    Skips dokkai (passages have naturalness exception) and authentic_extracted (source-faithful)."""
    catalog = augmented_kanji_catalog()
    failures = []
    audited = ["moji_questions_n4.md", "goi_questions_n4.md", "bunpou_questions_n4.md"]
    for fname in audited:
        text = load_text(KB / fname)
        for q in parse_questions(text):
            stem = strip_inline_format(q["stem"])
            for ch in stem:
                if KANJI_RE.match(ch) and ch not in catalog:
                    failures.append(
                        f"JA-1 {fname}:{q['qid']} stem contains non-N5 kanji '{ch}' "
                        f"(stem: {stem[:60]!r})"
                    )
                    break  # one report per question is enough
    return failures


def check_ja_2_particle_set() -> list[str]:
    """Questions whose options are EXCLUSIVELY particles must come from the N5 particle set.

    Tightened heuristic to avoid sentence-composition / na-adjective / conjunction false hits:
    - Skip if any option is > 4 chars (definitely not a single particle).
    - Skip if any option contains a kanji or katakana char.
    - Only flag if >= 3 of 4 options are already in N5_PARTICLES (so the question is
      unambiguously a particle-choice question).
    """
    # Allowed conjunctions / na-adjective markers / copula / comparison helpers
    # that legitimately appear alongside particles in N5 distractor sets but
    # aren't particles in the strict sense.
    PARTICLE_ADJACENT = {
        "な", "けど", "けれど", "けれども", "ば", "たら", "なら",
        "だ",      # plain copula - N5 distractor in particle questions
        "のほうが", # comparison construction - N5
        "ほうが",   # comparison construction - N5
    }

    failures = []
    for fname in QUESTION_FILES:
        text = load_text(KB / fname)
        for q in parse_questions(text):
            opts = [opt.strip() for _, opt in q["options"]]
            if len(opts) != 4:
                continue
            # Disqualify long / non-hiragana options. Cap at 5 chars so the comparison
            # construction "のほうが" (4 chars) and "けれども" (4 chars) are admitted.
            if any(len(o) > 5 for o in opts):
                continue
            if any(KANJI_RE.search(o) or KATAKANA_RE.search(o) for o in opts):
                continue
            # Now require strong particle-ness (>= 3 out of 4 in the canonical set)
            in_set = sum(1 for o in opts if o in N5_PARTICLES)
            if in_set < 3:
                continue
            for o in opts:
                if o in N5_PARTICLES or o in PARTICLE_ADJACENT:
                    continue
                failures.append(
                    f"JA-2 {fname}:{q['qid']} option '{o}' is not in the N5 particle/adjacent set "
                    f"(options: {opts})"
                )
    return failures


def check_ja_3_furigana_match() -> list[str]:
    """Heuristic: if a <ruby> tag is used, flag for manual review.
    A full check would parse the ruby and compare to data/n4_kanji_readings.json,
    which is broader than this MD-level lint. Returns advisory output only."""
    failures = []
    # Ruby is rarely used in MD (mostly in HTML inside MD); spot-check.
    for fname in QUESTION_FILES:
        text = load_text(KB / fname)
        # Don't fail on absence; only fail if ruby tags are malformed
        ruby_count = text.count("<ruby>")
        rt_count = text.count("<rt>")
        if ruby_count != rt_count:
            failures.append(f"JA-3 {fname} has unbalanced <ruby> ({ruby_count}) vs <rt> ({rt_count}) tags")
    return failures


def check_ja_4_vocab_reading_uniqueness() -> list[str]:
    """Vocab entries with parenthesized multiple readings must list all of them.
    Heuristic: lines like `- 毎年 (まいとし / まいねん)` are OK; lines like `- 毎年 (まいとし)`
    that should have multiple readings would need a manual whitelist."""
    failures = []
    # No automated check possible without a reference list; advisory only.
    # We at least verify the file parses without obvious malformed entries.
    vocab = load_text(KB / "vocabulary_n4.md")
    for line_no, line in enumerate(vocab.split("\n"), 1):
        # Detect `(reading1 / reading2 ...)` pattern; ensure no broken parens
        if re.search(r"\([^)]*\s/\s[^)]*\)", line) is None:
            continue
        if line.count("(") != line.count(")"):
            failures.append(f"JA-4 vocabulary_n4.md:L{line_no} unbalanced parens: {line.strip()[:80]!r}")
    return failures


def check_ja_5_answer_key_sanity() -> list[str]:
    """Every Answer line points to a valid option index, and that option exists & is non-empty."""
    failures = []
    for fname in QUESTION_FILES:
        text = load_text(KB / fname)
        for q in parse_questions(text):
            ans = q["answer_index"]
            if ans is None:
                continue  # No answer to check (might be a non-question section)
            if ans < 1 or ans > 4:
                failures.append(f"JA-5 {fname}:{q['qid']} answer index {ans} not in 1..4")
                continue
            # Find option text at index `ans`
            opt_texts = {int(num): text for num, text in q["options"]}
            if ans not in opt_texts:
                # Not all questions have 4 numbered option lines (e.g., sentence-comp uses inline 'Elements: 1. X')
                # so skip without failing; this is a heuristic.
                continue
            if not opt_texts[ans].strip():
                failures.append(f"JA-5 {fname}:{q['qid']} answer option {ans} is empty / whitespace")
    return failures


def check_ja_6_no_two_correct_answers() -> list[str]:
    """Regression guard: no causal-connector question has both から and ので as options.

    Pass-9 C-1.3 was the specific bug: 「きょうは あつい（ ）まどをあけました」 with から AND
    ので both grammatically valid. The fix replaced ので → けど in bunpou Q50/Q51. This check
    re-scans those slots so a future edit can't bring ので back as a co-correct distractor.

    Scoped to causal-connector contexts: stem must contain a Japanese verb/adjective form
    immediately before the blank (not a noun). Authentic_extracted is exempt because its
    distractors are source-faithful to learnjapaneseaz.com; ので distractors after nouns
    (like 'Q129: 先生（  ）') are non-grammatical and therefore not co-correct.
    """
    failures = []
    audited = ["moji_questions_n4.md", "goi_questions_n4.md", "bunpou_questions_n4.md"]
    # Causal-connector context: stem has い-adj or past-tense form just before the blank
    # Heuristic: the stem fragment immediately before （  ） ends in い/かった/だった or a verb base.
    causal_context_re = re.compile(r"(い|かった|だった|します|ました|です|でした)\s*[（(]")
    for fname in audited:
        text = load_text(KB / fname)
        for q in parse_questions(text):
            opts_set = {opt.strip() for _, opt in q["options"]}
            if not ({"から", "ので"} <= opts_set):
                continue
            stem = strip_inline_format(q["stem"])
            if not causal_context_re.search(stem):
                continue
            failures.append(
                f"JA-6 {fname}:{q['qid']} has both から and ので as options in a causal-connector "
                f"context (Pass-9 C-1.3 regression). Stem: {stem[:60]!r}"
            )
    return failures


def check_ja_7_no_duplicate_stems() -> list[str]:
    """No two questions in the same file share an identical stem.
    Scoped to originally-authored files only:
    - dokkai passages legitimately repeat short comprehension stems across passages
      (e.g. "パーティーは何時にはじまりますか" appears in two unrelated party passages);
    - authentic_extracted is source-faithful to learnjapaneseaz.com test papers,
      which themselves contain duplicate templates across test pages.
    Both are documented design choices; flagging them as bugs would be noise."""
    failures = []
    audited = ["moji_questions_n4.md", "goi_questions_n4.md", "bunpou_questions_n4.md"]
    for fname in audited:
        text = load_text(KB / fname)
        stems_seen: dict[str, str] = {}
        for q in parse_questions(text):
            stem = q["stem"].strip()
            if not stem or len(stem) < 10:
                continue
            if stem in stems_seen:
                failures.append(
                    f"JA-7 {fname} duplicate stem: {q['qid']} duplicates {stems_seen[stem]} "
                    f"(stem: {stem[:60]!r})"
                )
            else:
                stems_seen[stem] = q["qid"]
    return failures


def check_ja_8_q_count_integrity() -> list[str]:
    """Question counts per file must match expected; total must be 591."""
    failures = []
    actual_total = 0
    for fname, expected in EXPECTED_Q_COUNTS.items():
        text = load_text(KB / fname)
        actual = len(QUESTION_HEADER_RE.findall(text))
        actual_total += actual
        if actual != expected:
            failures.append(f"JA-8 {fname} has {actual} questions; expected {expected}")
    if actual_total != EXPECTED_TOTAL:
        failures.append(f"JA-8 total Q-count = {actual_total}; expected {EXPECTED_TOTAL}")
    return failures


def check_ja_9_engine_display_contract() -> list[str]:
    """Every question file must contain the 'Engine display note' header section."""
    failures = []
    for fname in QUESTION_FILES:
        text = load_text(KB / fname)
        if ENGINE_DISPLAY_NOTE_PHRASE not in text:
            failures.append(f"JA-9 {fname} missing '{ENGINE_DISPLAY_NOTE_PHRASE}' header")
    return failures


def check_ja_10_no_stub_redirect_text_in_data() -> list[str]:
    """No learner-facing string field in data/*.json contains '(see n5-' redirect text.

    Pass-12 finding: 40 questions in data/questions.json had leftover '(see n5-XXX)' text in
    question_ja, residual from the stub-pattern era. Pass-11 inlined examples in grammar.json
    but missed the parallel cleanup in questions.json. This invariant prevents recurrence.

    The 'notes' field is exempt because it intentionally records cross-references (audit trail).
    """
    LEARNER_FACING_FIELDS = {
        'ja', 'question_ja', 'prompt_ja', 'meaning_ja', 'example',
        'script_ja', 'translation_ja', 'translation_en', 'wrong', 'right',
        'gloss', 'meanings', 'pattern', 'meaning_en', 'explanation_en',
        'title_en', 'title_ja',
    }
    failures = []
    for fname in ['data/grammar.json', 'data/reading.json', 'data/listening.json',
                  'data/questions.json', 'data/vocab.json', 'data/kanji.json']:
        path = ROOT / fname
        if not path.exists():
            continue
        try:
            d = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue

        def walk(obj, path_str=''):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == 'notes':
                        continue  # notes are exempt
                    yield from walk(v, f'{path_str}.{k}' if path_str else k)
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    yield from walk(v, f'{path_str}[{i}]')
            elif isinstance(obj, str):
                # Get the last segment of the path to check field name
                last_field = path_str.split('.')[-1].split('[')[0] if path_str else ''
                if last_field in LEARNER_FACING_FIELDS or path_str.endswith(']'):
                    if '(see n5-' in obj or '（see n5-' in obj:
                        yield path_str, obj[:80]

        for path_str, snippet in walk(d):
            failures.append(f"JA-10 {fname}:{path_str} contains '(see n5-' text: {snippet!r}")

    return failures


def check_ja_12_kanji_kb_data_consistency() -> list[str]:
    """data/kanji.json must agree with KnowledgeBank/kanji_n4.md on every kanji entry.

    Pass-13 finding: data/kanji.json had silently-corrupted entries because
    tools/build_data.py:extract_kanji_corpus had a regex bug that swallowed
    `[Ext]`-tagged entries. Specifically: 番 had on=['ごう'] (= 号's reading)
    and 会 had on=['いん'] (= 員's reading). Plus 円 had a stale kun=['まる']
    that Pass-9 had explicitly removed from KB.

    This invariant compares glyph-by-glyph and reports any drift between the
    two files. Fixes go to KB first; then regenerate JSON via build_data.py.
    """
    import re as _re
    failures = []
    kb_path = ROOT / "KnowledgeBank" / "kanji_n4.md"
    json_path = ROOT / "data" / "kanji.json"
    if not kb_path.exists() or not json_path.exists():
        return failures

    # Parse KB to extract canonical glyphs
    kb_text = kb_path.read_text(encoding="utf-8")
    kb_glyphs = set(_re.findall(r"^\s*-\s+\*\*([一-鿿])\*\*", kb_text, _re.MULTILINE))

    # Read JSON
    try:
        d = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        failures.append(f"JA-12 data/kanji.json failed to parse: {e}")
        return failures
    json_glyphs = {e["glyph"] for e in d.get("entries", [])}

    missing_in_json = kb_glyphs - json_glyphs
    extra_in_json = json_glyphs - kb_glyphs
    for g in sorted(missing_in_json):
        failures.append(
            f"JA-12 KB has kanji '{g}' but data/kanji.json does not. "
            f"Run `python tools/build_data.py` to regenerate."
        )
    for g in sorted(extra_in_json):
        failures.append(
            f"JA-12 data/kanji.json has kanji '{g}' but KnowledgeBank/kanji_n4.md does not. "
            f"Either add to KB or remove from JSON."
        )
    return failures


def check_ja_11_no_duplicate_choices() -> list[str]:
    """No MCQ question's `choices` array contains duplicates.

    Pass-12 finding: 3 questions (q-0220, q-0223, q-0280) had a duplicate option in the
    choices array (e.g., 'ません' appearing twice). Auto-grading is meaningful only when
    options are distinct. This invariant prevents recurrence in data/questions.json.
    """
    failures = []
    qpath = ROOT / 'data' / 'questions.json'
    if not qpath.exists():
        return failures
    try:
        d = json.loads(qpath.read_text(encoding='utf-8'))
    except Exception:
        return failures
    for q in d.get('questions', []):
        choices = q.get('choices')
        if not isinstance(choices, list):
            continue
        if len(choices) != len(set(choices)):
            from collections import Counter
            dups = [c for c, n in Counter(choices).items() if n > 1]
            failures.append(
                f"JA-11 data/questions.json {q.get('id', '?')} has duplicate choice(s): {dups} "
                f"(full choices: {choices})"
            )
    return failures


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

CHECKS: list[tuple[str, str, callable]] = [
    ("X-6.1", "Catalog completeness",       check_x_6_1_catalog_completeness),
    ("X-6.2", "今年 / こんねん consistency",  check_x_6_2_today_kotoshi),
    ("X-6.3", "No mixed kanji+kana",        check_x_6_3_no_mixed_kanji_kana),
    ("X-6.4", "Lint script present",        check_x_6_4_orphan_vocab),
    ("X-6.5", "No em-dashes",               check_x_6_5_no_em_dashes),
    ("X-6.6", "Ru-verb exception flags",    check_x_6_6_ru_verb_flags),
    ("X-6.7", "No false synonymy claims",   check_x_6_7_no_false_synonymy),
    ("X-6.8", "No ASCII digits in TTS src", check_x_6_8_no_ascii_digits_in_tts_source),
    ("X-6.9", "Primary-reading sanity",     check_x_6_9_furigana_primary_reading_sanity),
    ("JA-1",  "Stem-kanji scope",           check_ja_1_stem_kanji_scope),
    ("JA-2",  "Particle-set sanity",        check_ja_2_particle_set),
    ("JA-3",  "Furigana / catalog match",   check_ja_3_furigana_match),
    ("JA-4",  "Vocab reading uniqueness",   check_ja_4_vocab_reading_uniqueness),
    ("JA-5",  "Answer-key sanity",          check_ja_5_answer_key_sanity),
    ("JA-6",  "No two-correct-answers",     check_ja_6_no_two_correct_answers),
    ("JA-7",  "No duplicate stems in file", check_ja_7_no_duplicate_stems),
    ("JA-8",  "Q-count integrity",          check_ja_8_q_count_integrity),
    ("JA-9",  "Engine display contract",    check_ja_9_engine_display_contract),
    ("JA-10", "No (see n5-) redirect text", check_ja_10_no_stub_redirect_text_in_data),
    ("JA-11", "No duplicate MCQ choices",   check_ja_11_no_duplicate_choices),
    ("JA-12", "Kanji KB / JSON consistency", check_ja_12_kanji_kb_data_consistency),
    ("JA-13", "No out-of-scope kanji in user-facing data", lambda: _check_ja_13_no_out_of_scope_kanji_in_data()),
    ("JA-14", "No auto-ruby code in renderer",  lambda: _check_ja_14_no_auto_ruby_in_renderer()),
    ("JA-15", "Audio refs resolve to files on disk", lambda: _check_ja_15_audio_refs_on_disk()),
    ("JA-16", "Kanji examples with out-of-scope kanji carry a reading (relaxed 2026-07-20)", lambda: _check_ja_16_kanji_examples_in_scope()),
    ("JA-17", "Grammar examples have vocab_ids (homograph guard)", lambda: _check_ja_17_examples_have_vocab_ids()),
    ("JA-18", "Reading explanation kanji subset of passage", lambda: _check_ja_18_reading_explanation_kanji()),
    ("JA-19", "Reading info-search has format_type", lambda: _check_ja_19_reading_info_search_format()),
    ("JA-20", "Reading choices kanji subset of passage", lambda: _check_ja_20_reading_choices_kanji()),
    ("JA-21", "N4-grammar markers require tier=late_n5", lambda: _check_ja_21_n4_grammar_tier_flag()),
    ("JA-22", "Kanji kun readings deduplicated", lambda: _check_ja_22_kun_dedup()),
    ("JA-23", "Listening script choices match choices array", lambda: _check_ja_23_listening_script_choices_match()),
    ("JA-24", "i-adj kanji primary reading is kun-yomi", lambda: _check_ja_24_iadj_kanji_primary_kun()),
    ("JA-25", "Whitelist exceptions documented (Pass-22 F-22.4)", lambda: _check_ja_25_whitelist_exceptions_documented()),
    ("JA-26", "No duplicate question IDs (Pass-23 2026-05-02)", lambda: _check_ja_26_no_duplicate_question_ids()),
    ("JA-27", "No English-translation/title fields in reading/listening (2026-05-02)", lambda: _check_ja_27_no_english_in_japanese_modules()),
    ("JA-28", "Dokkai-paper kanji bounded by N5 + exception list (2026-05-02)", lambda: _check_ja_28_dokkai_kanji_bounded()),
    ("JA-29", "Question subtype taxonomy is closed (paraphrase / kanji_writing only) (2026-05-02)", lambda: _check_ja_29_subtype_taxonomy()),
    ("JA-30", "No past-paper provenance signatures in question text (2026-05-02)", lambda: _check_ja_30_provenance()),
    ("JA-31", "Vocab PoS tags in vocabulary_n4.md agree with data/vocab.json (2026-05-02)", lambda: _check_ja_31_vocab_pos_parity()),
    ("JA-32", "Paper-JSON rationales appear verbatim in source MD (2026-05-04)", lambda: _check_ja_32_paper_rationale_md_parity()),
    ("JA-33", "No seed-template literals in grammar examples (2026-05-04 LLM audit closure)", lambda: _check_ja_33_no_seed_template_literals()),
]


def _check_ja_33_no_seed_template_literals() -> list[str]:
    """No grammar example carries the literal "(Seed example" prefix or the
    "to be authored by native reviewer" placeholder. Closes the regression
    surface from the 2026-05-04 LLM-audit pass: the prior enrichment script
    produced template-only content that flagged PATTERN_MISMATCH on every
    entry. After native-teacher review lands, this invariant ensures the
    seed templates never silently re-appear via a build-tool regression."""
    failures: list[str] = []
    grammar_path = ROOT / "data" / "grammar.json"
    if not grammar_path.exists():
        return failures
    try:
        d = json.loads(grammar_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-33: could not parse grammar.json: {e}"]
    for p in d.get("patterns", []):
        pid = p.get("id", "?")
        for i, ex in enumerate(p.get("examples", []) or []):
            tr = ex.get("translation_en", "") or ""
            if tr.startswith("(Seed example"):
                failures.append(
                    f"JA-33 grammar.json pattern '{pid}' examples[{i}].translation_en is "
                    f"a seed-template literal (starts with '(Seed example'). "
                    f"Replace with native-teacher content or empty the examples array."
                )
        for i, cm in enumerate(p.get("common_mistakes", []) or []):
            wrong = cm.get("wrong", "") or ""
            if "to be authored by native reviewer" in wrong:
                failures.append(
                    f"JA-33 grammar.json pattern '{pid}' common_mistakes[{i}].wrong is "
                    f"a seed-template placeholder. Replace or empty the array."
                )
    return failures


# ---------------------------------------------------------------------------
# JA-13 / JA-14 added in Pass 13 (auto-furigana removal)
# ---------------------------------------------------------------------------

def _check_ja_13_no_out_of_scope_kanji_in_data() -> list[str]:
    """No out-of-scope kanji appears in user-facing fields of grammar.json,
    questions.json, reading.json, listening.json. Enforces the 'kanji only
    if in N5 syllabus, kana otherwise' rule from the Pass-13 redesign."""
    failures = []
    try:
        whitelist = set(json.loads((ROOT / "data" / "n4_kanji_whitelist.json").read_text(encoding="utf-8")))
    except Exception as e:
        return [f"JA-13 could not load n4_kanji_whitelist.json: {e}"]
    KANJI_LOCAL = re.compile(r"[一-鿿]")
    SKIP_FIELDS = {"translation_en", "explanation_en", "meaning_en", "gloss",
                   "title_en", "prompt_en", "distractor_explanations",
                   "common_mistakes", "reading", "furigana",
                   # meaning_ja is a Japanese-language META explanation
                   # ("how the pattern works"), not user-target Japanese
                   # to be read for comprehension. It naturally uses
                   # grammar-meta kanji (期間 / 動詞 / 助詞 / etc.) that
                   # exceeds the learner's reading scope. The scope
                   # restriction applies to LEARNER-TARGET text (examples,
                   # stems, choices), not to teaching-language metadata.
                   "meaning_ja"}
    def walk(obj, key, path, hits):
        if isinstance(obj, str):
            if key in SKIP_FIELDS: return
            for ch in obj:
                if KANJI_LOCAL.match(ch) and ch not in whitelist:
                    hits.append((path, ch, obj[:60]))
                    return
        elif isinstance(obj, dict):
            for k, v in obj.items(): walk(v, k, f"{path}.{k}", hits)
        elif isinstance(obj, list):
            for i, v in enumerate(obj): walk(v, key, f"{path}[{i}]", hits)
    for fname in ["data/grammar.json", "data/questions.json", "data/reading.json", "data/listening.json"]:
        try:
            d = json.loads((ROOT / fname).read_text(encoding="utf-8"))
        except Exception:
            continue
        hits = []
        walk(d, None, fname, hits)
        for path, kanji, text in hits[:5]:
            failures.append(f"JA-13 {path}: out-of-scope kanji '{kanji}' in {text!r}")
        if len(hits) > 5:
            failures.append(f"JA-13 {fname}: ... and {len(hits) - 5} more")
    return failures


def _check_ja_14_no_auto_ruby_in_renderer() -> list[str]:
    """js/furigana.js must not auto-generate ruby for in-scope N5 kanji.
    The Pass-13 redesign removed this feature because the single-primary
    lookup picks wrong context-dependent readings (大学 displays
    だい+がく, but 大[おお] alone). Guard the regression here."""
    src = (ROOT / "js" / "furigana.js").read_text(encoding="utf-8") if (ROOT / "js" / "furigana.js").exists() else ""
    if not src:
        return ["JA-14: js/furigana.js missing"]
    # Look for the bad pattern: a ruby tag that references readings[ch].primary
    if "readings[ch]?.primary" in src or "readings[ch].primary" in src:
        return ["JA-14: js/furigana.js still references readings[ch].primary - auto-furigana not fully removed"]
    # The function should not import primary readings as a render input
    if "n5KanjiReadings" in src and "primary" in src:
        return ["JA-14: js/furigana.js still wires the readings map into the renderer"]
    return []


def _check_ja_16_kanji_examples_in_scope() -> list[str]:
    """K-1 invariant (RELAXED 2026-07-20, user decision): a kanji example may use
    ANY kanji, provided the example carries a non-empty `reading` (furigana) so the
    learner can read it. The kanji view (js/kanji.js) renders form + reading + gloss,
    and the printed workbook shows furigana, so an out-of-scope kanji is always
    readable. This supersedes the earlier target-or-N5-whitelist-only rule, which
    blocked natural, high-frequency examples (図書館, 風邪, 野菜, 散歩, 黒板 ...) that
    are exactly what an N4 learner should meet. The only hard failure now is an
    out-of-scope kanji WITHOUT a reading (i.e. genuinely unreadable at display time).
    """
    failures: list[str] = []
    kanji_path = ROOT / "data" / "kanji.json"
    wl_path = ROOT / "data" / "n4_kanji_whitelist.json"
    if not kanji_path.exists() or not wl_path.exists():
        return ["JA-16: data files missing"]
    try:
        whitelist = set(json.loads(wl_path.read_text(encoding="utf-8")))
        data = json.loads(kanji_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-16: parse error: {e}"]
    KANJI_RE = re.compile(r"[一-鿿]")
    for entry in data.get("entries", []):
        target = entry.get("glyph")
        for ex in entry.get("examples", []):
            form = ex.get("form", "")
            reading = (ex.get("reading") or "").strip()
            oos = [ch for ch in KANJI_RE.findall(form)
                   if ch != target and ch not in whitelist]
            if oos and not reading:
                failures.append(
                    f"JA-16 kanji '{target}' example '{form}' uses out-of-scope "
                    f"kanji {oos} but has NO reading; add a reading (furigana) so it "
                    f"is displayable."
                )
    return failures


def _check_ja_17_examples_have_vocab_ids() -> list[str]:
    """Every non-empty example in data/grammar.json must have a
    `vocab_ids` field (a list, possibly empty). This prevents the
    homograph mismatch class flagged 2026-05-01 — without explicit
    example→vocab links, the renderer falls back to substring matching
    on the form field, which can't disambiguate homographs.

    Auto-population: tools/link_grammar_examples_to_vocab.py walks every
    example and assigns vocab_ids. Run that tool whenever new examples
    are added; this invariant guards the result.
    """
    failures: list[str] = []
    grammar_path = ROOT / "data" / "grammar.json"
    if not grammar_path.exists():
        return ["JA-17: data/grammar.json missing"]
    try:
        data = json.loads(grammar_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-17: parse error: {e}"]
    for p in data.get("patterns", []):
        for i, ex in enumerate(p.get("examples", [])):
            if not ex.get("ja"):
                continue  # placeholder examples without ja text are ignored
            if "vocab_ids" not in ex or not isinstance(ex["vocab_ids"], list):
                failures.append(
                    f"JA-17 {p.get('id', '?')} examples[{i}] is missing the "
                    f"`vocab_ids` field. Run "
                    f"`python tools/link_grammar_examples_to_vocab.py` to populate."
                )
                if len(failures) >= 20:
                    failures.append("JA-17 ... (truncated at 20 failures)")
                    return failures
    return failures


def _check_ja_15_audio_refs_on_disk() -> list[str]:
    """Every entry in data/audio_manifest.json must point to a file that
    exists on disk. Per data-correction brief §4.1: a release-blocker check
    for "no question, grammar pattern, listening item references a missing
    audio file." If this fails, the runtime app would 404 on `<audio src>`.

    The `skipped: true` flag in the manifest is a build-script status (file
    already on disk, skipped re-rendering); it does NOT mean missing.
    """
    failures: list[str] = []
    manifest_path = ROOT / "data" / "audio_manifest.json"
    if not manifest_path.exists():
        return ["JA-15: data/audio_manifest.json missing"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-15: could not parse audio_manifest.json: {e}"]
    items = manifest.get("items", [])
    for it in items:
        path = it.get("path", "")
        # Manifest paths use OS-native separators (Windows backslash on the
        # author machine). Normalise so the check works on any OS.
        rel = path.replace("\\", "/")
        full = ROOT / rel
        if not full.exists():
            failures.append(
                f"JA-15 manifest entry {it.get('id', '?')} points to missing file: {rel}"
            )
            if len(failures) >= 20:
                failures.append(f"JA-15 ... and more (truncated at 20)")
                break
    return failures


def _check_ja_18_reading_explanation_kanji() -> list[str]:
    """Every kanji that appears INSIDE a single-quoted phrase in an
    explanation_en field must also appear in the passage's `ja` text.

    The convention in data/reading.json is that explanations quote the
    relevant passage line in single quotes, like `'毎日 30どより 高いです'`.
    These quoted phrases must match the passage rendering exactly — if
    the passage uses うち (kana) but the explanation quotes 家 (kanji),
    the learner scans for the quoted phrase in the passage, fails to
    find it, and trust degrades.

    We deliberately do NOT check prompt_ja or unquoted explanation text,
    because prompts legitimately use question words (何, 人, etc.) that
    the passage doesn't echo. Only the quoted-quote-of-the-passage
    convention is checked.

    Originally Pass-15-reading audit §2.2: 8 explicit occurrences across
    n5.read.001 / 002 / 008 / 013 / 016 / 022. This invariant prevents
    recurrence and would have flagged all 8.
    """
    failures: list[str] = []
    reading_path = ROOT / "data" / "reading.json"
    if not reading_path.exists():
        return ["JA-18: data/reading.json missing"]
    try:
        data = json.loads(reading_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-18: parse error: {e}"]

    def is_kanji(ch: str) -> bool:
        cp = ord(ch)
        return 0x3400 <= cp <= 0x9FFF

    # Match either ASCII '...' or Japanese 「...」 quoted phrases.
    QUOTE_RE = re.compile(r"'([^']+)'|「([^」]+)」")

    for p in data.get("passages", []):
        pid = p.get("id", "?")
        passage_kanji = {ch for ch in p.get("ja", "") if is_kanji(ch)}
        for q in p.get("questions", []):
            qid = q.get("id", "?")
            text = q.get("explanation_en", "")
            for m in QUOTE_RE.finditer(text):
                quoted = m.group(1) or m.group(2) or ""
                for ch in quoted:
                    if is_kanji(ch) and ch not in passage_kanji:
                        failures.append(
                            f"JA-18 {qid} explanation quotes kanji "
                            f"'{ch}' not in passage {pid} "
                            f"(passage uses different rendering — "
                            f"likely kana). Quote: {quoted[:50]!r}"
                        )
                        if len(failures) >= 20:
                            failures.append("JA-18 ... (truncated at 20)")
                            return failures
                        break
    return failures


def _check_ja_20_reading_choices_kanji() -> list[str]:
    """Reading-question MCQ choices must use the same kana/kanji rendering
    as the passage. If a choice contains a kanji that the passage doesn't
    use, the learner cannot match-answer-to-text and answer authority is
    undermined. Pass-15-reading audit §5.4 (3).

    We accept the case where a choice contains a kanji that ALSO doesn't
    appear in the passage but is conceptually allowed (e.g., 何 or 人 in
    a question-style distractor). Specifically: only flag kanji that
    appear in the OTHER choices' rendering as kana — that's the strong
    inconsistency signal (n5.read.010 q1 had bare numbers but the passage
    used 〜こ counter; that's the class to catch).
    """
    failures: list[str] = []
    reading_path = ROOT / "data" / "reading.json"
    if not reading_path.exists():
        return ["JA-20: data/reading.json missing"]
    try:
        data = json.loads(reading_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-20: parse error: {e}"]

    def is_kanji(ch: str) -> bool:
        cp = ord(ch)
        return 0x3400 <= cp <= 0x9FFF

    for p in data.get("passages", []):
        pid = p.get("id", "?")
        passage_text = p.get("ja", "")
        passage_kanji = {ch for ch in passage_text if is_kanji(ch)}
        for q in p.get("questions", []):
            qid = q.get("id", "?")
            choices = q.get("choices", [])
            correct = q.get("correctAnswer", "")
            # The strong consistency check: every kanji in the
            # CORRECT-answer choice must appear in the passage. If the
            # correct answer rendering doesn't match the passage, the
            # question is inconsistent. (Distractors get more leeway —
            # they're foils.)
            for ch in correct:
                if is_kanji(ch) and ch not in passage_kanji:
                    failures.append(
                        f"JA-20 {qid} correctAnswer uses kanji '{ch}' "
                        f"not in passage {pid} (rendering mismatch — "
                        f"the answer should match the passage's form). "
                        f"correctAnswer={correct!r}"
                    )
                    if len(failures) >= 20:
                        failures.append("JA-20 ... (truncated at 20)")
                        return failures
                    break
    return failures


# Heuristic patterns that strongly suggest N4 grammar in a passage. Each
# entry: (regex, description). Used by JA-21. Patterns are deliberately
# conservative — false negatives are acceptable, false positives must be
# rare since they'd block release.
#
# Calibrated against the live corpus 2026-05-01:
# - Original "(?:う|く|...)と、" pattern false-fired on `3つと、` (counter
#   + と for noun-listing). Tightened with a negative-look-behind on
#   numerals + counter kana so only verb dictionary forms match.
N4_GRAMMAR_PATTERNS = [
    # 〜と conditional: verb-dictionary-form + と + comma. The verb-dict
    # ends in u-row hiragana. Exclude counter kana (つ/こ/本/etc.) which
    # are preceded by a digit or kanji numeral.
    # Negative-look-behind: NOT preceded by a digit, fullwidth digit, or
    # kanji numeral. Then a verb-dict-ending hiragana, then と + 、.
    (re.compile(
        r"(?<![0-9０-９一二三四五六七八九十百千万])"
        r"(?:う|く|ぐ|す|ぬ|ぶ|む|る)と、"),
     "〜と conditional (Verb-dict + と + comma)"),
    # Potential form -られ + ます/ません/た/ない (verb-2 potential).
    (re.compile(r"(?:け|げ|せ|て|ね|べ|め|れ)られ(?:ます|ません|た|ない)"),
     "Potential form (-られ + ます/ません/た/ない)"),
]


def _check_ja_21_n4_grammar_tier_flag() -> list[str]:
    """Reading passages that use heuristically-detected N4 grammar markers
    must be flagged with `tier: "late_n5"` (or be rewritten). Pass-15-
    reading audit §5.4 (4).

    Currently checks for: 〜と conditional, potential form. Both were
    audit-flagged on n5.read.030 / n5.read.007 and have been fixed. This
    check guards against re-introduction.
    """
    failures: list[str] = []
    reading_path = ROOT / "data" / "reading.json"
    if not reading_path.exists():
        return ["JA-21: data/reading.json missing"]
    try:
        data = json.loads(reading_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-21: parse error: {e}"]
    for p in data.get("passages", []):
        pid = p.get("id", "?")
        ja = p.get("ja", "")
        tier = p.get("tier", "core_n5")
        for pat, desc in N4_GRAMMAR_PATTERNS:
            m = pat.search(ja)
            if m and tier not in ("late_n5", "info_search"):
                failures.append(
                    f"JA-21 {pid} contains N4 grammar pattern "
                    f"({desc}) at {m.group(0)!r} but tier is "
                    f"{tier!r}. Either rewrite to N5 or set "
                    f"tier=late_n5."
                )
    return failures


def _check_ja_19_reading_info_search_format() -> list[str]:
    """Reading passages with `level: info-search` must declare a
    `format_type` (schedule_table | menu_list | notice | etc.) so the
    renderer can give them the appropriate visual treatment. Originally
    Pass-15-reading audit §3.6.
    """
    failures: list[str] = []
    reading_path = ROOT / "data" / "reading.json"
    if not reading_path.exists():
        return ["JA-19: data/reading.json missing"]
    try:
        data = json.loads(reading_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-19: parse error: {e}"]
    allowed_formats = {"schedule_table", "menu_list", "notice",
                       "signage", "form"}
    for p in data.get("passages", []):
        if p.get("level") != "info-search":
            continue
        pid = p.get("id", "?")
        if "format_type" not in p:
            failures.append(
                f"JA-19 {pid} (level=info-search) is missing the "
                f"`format_type` field. Allowed: {sorted(allowed_formats)}"
            )
            continue
        if p["format_type"] not in allowed_formats:
            failures.append(
                f"JA-19 {pid} format_type {p['format_type']!r} not in "
                f"allowed set {sorted(allowed_formats)}"
            )
    return failures


def _check_ja_22_kun_dedup() -> list[str]:
    """Every kanji's `kun` reading list in n4_kanji_readings.json must
    contain no duplicate entries. Pass-15 consolidated audit §2.2 found
    10 entries with repeats (二/七/分/見/聞/入/立/休/高/白) — artefacts
    of stripping okurigana.
    """
    failures: list[str] = []
    path = ROOT / "data" / "n4_kanji_readings.json"
    if not path.exists():
        return ["JA-22: data/n4_kanji_readings.json missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-22: parse error: {e}"]
    for k, entry in data.items():
        kun = entry.get("kun", [])
        if not isinstance(kun, list):
            continue
        if len(kun) != len(set(kun)):
            seen = set()
            dups = []
            for r in kun:
                if r in seen and r not in dups:
                    dups.append(r)
                seen.add(r)
            failures.append(
                f"JA-22 kanji '{k}' has duplicate kun reading(s): "
                f"{dups} (full list: {kun})"
            )
    return failures


def _check_ja_23_listening_script_choices_match() -> list[str]:
    """Listening utterance items that embed numbered choices in
    `script_ja` (style: '1. xxx\\n2. yyy\\n3. zzz') must have those exact
    strings in the `choices` array. Pass-15 consolidated audit §1.1
    found n5.listen.011 mismatch (script said 'ありがとう' but choices
    array said 'ありがとうございます') — a direct grading bug.

    We do not require items to embed numbered choices; this check only
    fires when items DO embed them and validates consistency.
    """
    failures: list[str] = []
    path = ROOT / "data" / "listening.json"
    if not path.exists():
        return ["JA-23: data/listening.json missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-23: parse error: {e}"]
    for item in data.get("items", []):
        script = item.get("script_ja", "")
        choices = item.get("choices", [])
        if not script or not choices:
            continue
        # Extract numbered lines: '1. xxx', '2. yyy' etc.
        embedded: list[str] = []
        for line in script.split("\n"):
            m = re.match(r"^\s*(\d+)\.\s*(.+?)\s*$", line)
            if m:
                embedded.append(m.group(2).strip())
        if not embedded:
            continue  # No embedded choices; nothing to check.
        # Each embedded choice must appear in the choices array.
        for emb in embedded:
            if emb not in choices:
                failures.append(
                    f"JA-23 {item.get('id','?')} embedded script choice "
                    f"{emb!r} not found in choices array {choices!r}"
                )
    return failures


def _check_ja_24_iadj_kanji_primary_kun() -> list[str]:
    """For kanji whose most common N5 use is as an i-adjective, the
    `primary` reading in n4_kanji_readings.json must be the kun-yomi.
    Pass-15 consolidated audit §2.1: 高/長/安 had on-yomi primaries
    that mis-rendered the high-frequency standalone use 高い/長い/安い.

    The list is curated; new i-adjective kanji can be added when N5
    scope shifts.
    """
    IADJ_KANJI_EXPECTED_KUN = {
        "高": "たか",
        "長": "なが",
        "安": "やす",
    }
    failures: list[str] = []
    path = ROOT / "data" / "n4_kanji_readings.json"
    if not path.exists():
        return ["JA-24: data/n4_kanji_readings.json missing"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-24: parse error: {e}"]
    for k, expected_kun in IADJ_KANJI_EXPECTED_KUN.items():
        if k not in data:
            continue  # JA-12 already catches missing entries.
        actual = data[k].get("primary")
        if actual != expected_kun:
            failures.append(
                f"JA-24 kanji '{k}' primary={actual!r} but most-common "
                f"N5 use is i-adjective {k}い (kun {expected_kun!r}). "
                f"Set primary={expected_kun!r}."
            )
    return failures


def _check_ja_25_whitelist_exceptions_documented() -> list[str]:
    """Pass-22 F-22.4: every kanji in n4_kanji_whitelist.json that is NOT in
    the official JLPT N4 scope MUST appear in
    data/n4_kanji_whitelist.exceptions.md with a `WHY:` justification.

    Without this guard, an agent or contributor could silently add an
    out-of-scope kanji to the whitelist to silence a JA-13 violation. With
    this guard, every exception is a deliberate, reviewable, justified
    addition.

    Spec: specifications/procedure-manual-appendix-c-pass22-polish.md C.4.

    The exceptions doc is OPTIONAL — if absent, the check passes (allows
    bootstrapping). Once present, every project-whitelist entry that is
    not in the official scope must be justified there.

    Bootstrapping the official-scope list: the N5 official scope is
    canonically 103 kanji per JLPT.jp (the project whitelist is 106 — the
    extra 3 are documented exceptions). For now we accept the project
    whitelist verbatim if the exceptions doc is absent; once the
    exceptions doc lands, validation kicks in.
    """
    failures: list[str] = []
    project_wl_path = ROOT / "data" / "n4_kanji_whitelist.json"
    exceptions_md_path = ROOT / "data" / "n4_kanji_whitelist.exceptions.md"
    official_scope_path = ROOT / "data" / "n5_official_kanji_scope.json"

    if not project_wl_path.exists():
        return ["JA-25: data/n4_kanji_whitelist.json missing"]
    if not exceptions_md_path.exists():
        # Bootstrapping mode: skip until the exceptions doc lands.
        return []
    if not official_scope_path.exists():
        # Without an official-scope reference we can't compute exceptions.
        # Skip but emit a one-time hint via a comment in the exceptions doc.
        return []

    try:
        project_wl = set(json.loads(project_wl_path.read_text(encoding="utf-8")))
        official = set(json.loads(official_scope_path.read_text(encoding="utf-8")))
    except Exception as e:
        return [f"JA-25: parse error loading whitelist or official scope: {e}"]

    md_text = exceptions_md_path.read_text(encoding="utf-8")
    # Parse: each line "- {KANJI}  WHY: <reason>" registers one exception.
    documented_with_why: dict[str, str] = {}
    for line in md_text.splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        # Skip non-kanji lines (e.g., docstring text starting with "- ").
        body = line[2:].strip()
        if not body or body[0] not in "一二三四五六七八九十百千万円木金土水火日月年人本中大小上下右左前後内外山川田":
            # Heuristic check: first char is a CJK kanji. Use a broader range.
            if not (0x4E00 <= ord(body[0]) <= 0x9FFF):
                continue
        # Pull off the kanji glyph (handles multi-char or trailing space).
        kanji = body[0]
        if "WHY:" in body:
            why = body.split("WHY:", 1)[1].strip()
            # Strip trailing "REVIEW_DATE:..." if present.
            if "REVIEW_DATE:" in why:
                why = why.split("REVIEW_DATE:", 1)[0].strip()
            documented_with_why[kanji] = why
        else:
            documented_with_why[kanji] = ""  # listed but no WHY

    project_exceptions = project_wl - official
    for kanji in sorted(project_exceptions):
        if kanji not in documented_with_why:
            failures.append(
                f"JA-25 kanji '{kanji}' is in n4_kanji_whitelist.json but not "
                f"in official JLPT N4 scope, AND not documented in "
                f"data/n4_kanji_whitelist.exceptions.md. Add an entry with WHY: <reason>."
            )
        elif not documented_with_why[kanji]:
            failures.append(
                f"JA-25 kanji '{kanji}' is documented in exceptions.md but "
                f"lacks WHY: justification. Add WHY: <reason> on the same line."
            )
    return failures


def _check_ja_26_no_duplicate_question_ids() -> list[str]:
    """Pass-23 (2026-05-02): no two entries in data/questions.json may
    share the same `id` field. JA-7 catches duplicate STEMS but not
    duplicate IDs — and the latter happened twice (Pass-16 ↔ Pass-15-P0
    over q-0454..q-0463; parallel-session ↔ Pass-16 over q-0479..q-0488).

    The runtime uses IDs as primary keys for storage and SRS state, so
    duplicate IDs cause one entry's progress to silently overwrite the
    other's. This invariant prevents the regression class going forward.
    """
    from collections import Counter
    failures: list[str] = []
    qpath = ROOT / "data" / "questions.json"
    if not qpath.exists():
        return ["JA-26: data/questions.json missing"]
    try:
        data = json.loads(qpath.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-26: parse error: {e}"]
    ids = [q.get("id") for q in data.get("questions", [])]
    counts = Counter(ids)
    dups = sorted(qid for qid, n in counts.items() if n > 1)
    for qid in dups:
        failures.append(
            f"JA-26 question id '{qid}' appears {counts[qid]} times in "
            f"data/questions.json. Run a dedup tool to renumber the "
            f"second occurrence."
        )
    return failures


def _check_ja_27_no_english_in_japanese_modules() -> list[str]:
    """Per user direction 2026-05-02: dokkai (data/reading.json) and
    listening (data/listening.json) are Japanese-first learner surfaces
    and must not carry English title or English-passage-translation
    fields, since both are rendered to the learner.

    Specifically banned at the item level:
      - title_en       (replaced by title_ja, used in renderIndex/renderRead/
                        renderQuestions/renderResults for reading and
                        renderListening/renderItem for listening)
      - translation_en (was rendered in a "Show English translation"
                        <details> panel on reading; that panel and field
                        are now removed from data + renderer)

    Allowed because they teach (NOT banned):
      - explanation_en (rationale shown after a wrong answer)
      - prompt_en      (legacy on listening; no items currently carry it)
      - any field on data/grammar.json (grammar pattern teaching genuinely
        needs English glosses — out of scope for this invariant)
      - any field on data/questions.json (question stems are short and
        sometimes carry translation_en for the learner; orthogonal to the
        passage-EN-translation rule we are locking down here)
    """
    BANNED = {"title_en", "translation_en"}
    failures: list[str] = []
    for fname, item_key in [
        ("data/reading.json",   "passages"),
        ("data/listening.json", "items"),
    ]:
        path = ROOT / fname
        if not path.exists():
            continue
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            failures.append(f"JA-27: {fname} parse error: {e}")
            continue
        items = d.get(item_key, [])
        for it in items:
            for bad in BANNED:
                if bad in it:
                    failures.append(
                        f"JA-27 {fname} item id={it.get('id','?')!r} carries "
                        f"banned field '{bad}'. The learner-facing surface "
                        f"in dokkai/listening must be Japanese only; remove "
                        f"the field (and migrate title_en -> title_ja if "
                        f"applicable). See tools/fix_dokkai_titles_remove_en.py "
                        f"and tools/fix_listening_titles_ja.py for prior "
                        f"migrations."
                    )
    return failures


def _check_ja_28_dokkai_kanji_bounded() -> list[str]:
    """data/papers/dokkai/*.json passages may contain non-N5 kanji ONLY
    if those kanji are explicitly documented in
    data/dokkai_kanji_exception.json. This formalizes the dokkai
    naturalness exception (KnowledgeBank/dokkai_questions_n4.md line 17)
    so the runtime can't silently introduce a new non-N5 kanji.

    Bunpou / moji / goi are NOT covered here; they stay strictly N5
    via JA-13.
    """
    failures: list[str] = []
    try:
        whitelist = set(json.loads(
            (ROOT / "data" / "n4_kanji_whitelist.json").read_text(encoding="utf-8")))
    except Exception as e:
        return [f"JA-28: could not load n4_kanji_whitelist.json: {e}"]
    try:
        exc_doc = json.loads(
            (ROOT / "data" / "dokkai_kanji_exception.json").read_text(encoding="utf-8"))
        exception_kanji = set(exc_doc.get("exception_kanji", []))
    except Exception as e:
        return [f"JA-28: could not load dokkai_kanji_exception.json: {e}"]
    allowed = whitelist | exception_kanji
    KANJI_RE = re.compile(r"[一-鿿]")
    dokkai_dir = ROOT / "data" / "papers" / "dokkai"
    if not dokkai_dir.exists():
        return []
    offenders: dict[str, list[str]] = {}  # kanji -> sample passages
    for p in sorted(dokkai_dir.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            failures.append(f"JA-28: parse error on {p.name}: {e}")
            continue
        def walk(obj):
            if isinstance(obj, str):
                for ch in obj:
                    if KANJI_RE.match(ch) and ch not in allowed:
                        offenders.setdefault(ch, []).append(
                            f"{p.name}: {obj[:60]!r}")
            elif isinstance(obj, dict):
                for v in obj.values(): walk(v)
            elif isinstance(obj, list):
                for v in obj: walk(v)
        walk(d)
    for ch, samples in sorted(offenders.items()):
        s = samples[0]
        failures.append(
            f"JA-28: kanji '{ch}' is neither in N5 catalog nor in "
            f"dokkai_kanji_exception.json. Either replace with kana, "
            f"or add to data/dokkai_kanji_exception.json (with "
            f"justification in KnowledgeBank/dokkai_questions_n4.md "
            f"header). First seen: {s}")
    return failures


def _check_ja_30_provenance() -> list[str]:
    """Past-paper provenance scan: no question text may contain markers
    that suggest direct copying from JLPT past papers (JEES citations,
    year-numbered exam markers, "過去問" / "真題" terminology, etc.).

    Mirrors the standalone tool tools/audit_provenance.py — kept inline
    here so the standard CI integrity check (one command) catches a
    leak without needing a separate workflow step. See CONTENT-LICENSE.md
    §3 for the policy this enforces.

    Failure here means: a contributor introduced text that could be
    interpreted as a past-paper reference. Fix by re-authoring the
    stem/rationale/note in the project's own voice, not by exempting
    the rule.
    """
    failures: list[str] = []
    SUSPECT = [
        (re.compile(r"\bJEES\b"), "JEES citation"),
        (re.compile(r"Japan\s*Educational\s*Exchanges?", re.I), "JEES full name"),
        (re.compile(r"(19|20)\d{2}年[\s　]*[1-9七十二]+月.*?(本試験|公開|JLPT)"),
         "year+month past-paper marker"),
        (re.compile(r"本試験[\s　]*第\d+回"), "past-paper round number"),
        (re.compile(r"実試験|実問題|真題"), "past-paper terminology"),
        (re.compile(r"(JLPT|日本語能力試験)\s*N[1-5]\s*(20\d{2}|19\d{2})年"),
         "JLPT year-paper citation"),
        (re.compile(r"過去問"), "kakomon (past-question) self-attestation"),
    ]

    def _scan(text: str, where: str) -> None:
        if not isinstance(text, str) or not text:
            return
        for pat, why in SUSPECT:
            m = pat.search(text)
            if m:
                failures.append(
                    f"JA-30 {where}: {why} — '{m.group(0)[:60]}'"
                )

    qpath = ROOT / "data" / "questions.json"
    if qpath.exists():
        try:
            data = json.loads(qpath.read_text(encoding="utf-8"))
        except Exception as e:
            return [f"JA-30: parse error questions.json: {e}"]
        for qq in data.get("questions", []):
            qid = qq.get("id", "?")
            for f in ("question_ja", "prompt_ja", "explanation_en", "rationale"):
                _scan(qq.get(f, ""), f"{qid}.{f}")
            de = qq.get("distractor_explanations") or {}
            if isinstance(de, dict):
                for k, v in de.items():
                    _scan(v, f"{qid}.distractor_explanations.{k}")

    papers_dir = ROOT / "data" / "papers"
    if papers_dir.exists():
        for f in papers_dir.rglob("paper-*.json"):
            try:
                p = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                continue
            for qq in p.get("questions", []):
                qid = qq.get("id", "?")
                for fld in ("stem_html", "rationale", "explanation_en",
                            "passage_text", "prompt_ja"):
                    _scan(qq.get(fld, ""), f"{qid}.{fld}")

    return failures


def _check_ja_31_vocab_pos_parity() -> list[str]:
    """The PoS tags inline in KnowledgeBank/vocabulary_n4.md
    (`[n.]` / `[v1]` / etc., added 2026-05-02 per DEFER-5) must agree
    with the `pos` field on the corresponding entry in data/vocab.json.

    Drift class this catches:
      - A contributor edits one file (say, fixes a wrong PoS in the
        markdown) but forgets the JSON, or vice versa. Since both
        files describe the same per-form attribute, drift is silent.
      - The PoS-injection pass (DEFER-5) had two homograph entries
        get the wrong tag (`いる - to need` mistagged `[v2]` instead
        of `[v1]`); JA-31 would have caught it before commit.

    Match strategy is *section-aware* because many forms are
    homographs (e.g., 'はる' is a noun in §14 Weather but a verb-1
    in §27 Verbs; 'いる' is verb-2 in §28 but verb-1 in §30). The
    audit tracks the current `## N. Section title` heading while
    parsing the markdown and looks up `(form, reading, section)` in
    JSON for an exact match; if the section doesn't match exactly,
    word-overlap with the JSON's `section` field picks the closest.
    Form-only fallback (any pos in JSON for that form) is the last
    resort.
    """
    POS_ABBREV = {
        "noun": "n.", "verb-1": "v1", "verb-2": "v2", "verb-3": "v3",
        "i-adj": "i-adj", "na-adj": "na-adj", "adverb": "adv.",
        "particle": "part.", "conjunction": "conj.", "pronoun": "pron.",
        "counter": "count.", "numeral": "num.", "demonstrative": "dem.",
        "question-word": "Q-word", "expression": "exp.",
        "interjection": "interj.",
    }

    failures: list[str] = []
    md_path = ROOT / "KnowledgeBank" / "vocabulary_n4.md"
    json_path = ROOT / "data" / "vocab.json"
    if not md_path.exists() or not json_path.exists():
        return ["JA-31: source files missing (vocabulary_n4.md or vocab.json)"]

    try:
        vocab = json.loads(json_path.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-31: parse error vocab.json: {e}"]

    def normalize_section(s: str) -> str:
        s = re.sub(r"^\d+\.\s*", "", s).strip().lower()
        return re.sub(r"\s+", " ", s)

    # Build two indexes:
    #   by_full[(form, reading, section_norm)]      = pos_tag (exact match)
    #   by_form_reading[(form, reading)]            = list of (section_norm, pos_tag)
    #   by_form[form]                               = set of pos_tags (any-of fallback)
    # by_full now stores a SET of valid tags per (form, reading, section) key.
    # Homograph case in section 30: `いる` (exist, v2) and `いる` (to need, v1)
    # share the key, and either tag should pass parity for that key.
    # Without this, the dict-based "last write wins" returned only one tag and
    # JA-31 would flag the other MD line as a mismatch despite both being correct.
    by_full: dict[tuple[str, str, str], set[str]] = {}
    by_form_reading: dict[tuple[str, str], list[tuple[str, str]]] = {}
    by_form: dict[str, set[str]] = {}
    for e in vocab.get("entries", []):
        form = e.get("form")
        reading = e.get("reading", form)
        pos = e.get("pos")
        section = e.get("section", "")
        if not (form and pos):
            continue
        tag = POS_ABBREV.get(pos, pos)
        sec_norm = normalize_section(section)
        by_full.setdefault((form, reading, sec_norm), set()).add(tag)
        by_form_reading.setdefault((form, reading), []).append((sec_norm, tag))
        by_form.setdefault(form, set()).add(tag)

    POS_TAGS_RE = "|".join(re.escape(t) for t in
        ["n.", "v1", "v2", "v3", "i-adj", "na-adj", "adv.", "part.",
         "conj.", "pron.", "count.", "num.", "dem.", "Q-word", "exp.",
         "interj."])
    LINE_RE = re.compile(
        r"^(- )([^\s\(]+)(\s+\(([^)]+)\))?( \[(?:Ext|Cul)\])?(\s*-\s*)"
        rf"\[({POS_TAGS_RE})\]\s+(.+)$"
    )
    SECTION_HEADER_RE = re.compile(r"^##\s+(.+?)\s*$")
    is_jp = re.compile(r"^[ぁ-んァ-ヶー一-鿿]")

    text = md_path.read_text(encoding="utf-8")
    current_section_norm = ""
    line_no = 0
    for raw in text.splitlines():
        line_no += 1
        sh = SECTION_HEADER_RE.match(raw)
        if sh:
            current_section_norm = normalize_section(sh.group(1))
            continue
        m = LINE_RE.match(raw)
        if not m:
            continue
        form = m.group(2)
        reading = m.group(4) or form
        md_tag = m.group(7)
        if not is_jp.match(form):
            continue
        # Lookup priority: exact (form, reading, section) → word-overlap
        # tiebreaker on (form, reading) → form-only any-of fallback.
        # by_full holds a SET (homograph case e.g. section-30 いる); MD tag
        # passes if it's a member of the set for the matched key.
        full_set = by_full.get((form, reading, current_section_norm))
        expected: str | None
        if full_set:
            if md_tag in full_set:
                continue  # MD tag matches one of the valid POS for this key
            # Otherwise emit a comma-list of expected values for the error
            expected = "/".join(sorted(full_set))
        else:
            candidates = by_form_reading.get((form, reading), [])
            if len(candidates) == 1:
                expected = candidates[0][1]
            elif candidates:
                cur_words = set(current_section_norm.split())
                best = None; best_score = -1
                for sec, tag in candidates:
                    score = len(cur_words & set(sec.split()))
                    if score > best_score:
                        best, best_score = tag, score
                expected = best
            else:
                expected = None
        if expected is None:
            allowed = by_form.get(form)
            if allowed is None:
                failures.append(
                    f"JA-31 vocabulary_n4.md:{line_no} entry '{form}' "
                    f"({reading}) [{md_tag}] has no matching record in "
                    f"data/vocab.json"
                )
                continue
            if md_tag in allowed:
                continue
            expected_str = "/".join(sorted(allowed))
            failures.append(
                f"JA-31 vocabulary_n4.md:{line_no} '{form}' ({reading}) "
                f"tagged [{md_tag}] but data/vocab.json says "
                f"'{expected_str}'"
            )
            continue
        if md_tag != expected:
            failures.append(
                f"JA-31 vocabulary_n4.md:{line_no} '{form}' ({reading}) "
                f"tagged [{md_tag}] in section '{current_section_norm}' "
                f"but data/vocab.json says '{expected}'"
            )
    return failures


def _check_ja_32_paper_rationale_md_parity() -> list[str]:
    """Paper-JSON rationale kanji must all appear in the source MD Q-block.

    Drift class this catches:
      - KB markdown rationale is corrected to use kana (e.g., 熱がある ->
        ねつが ある for kanji-scope) but the paper extractor wasn't
        re-run, so the paper JSON still carries the stale kanji. The
        auditor's 2026-05-04 flag of paper-2 Q19 ("熱がある" in JSON,
        but MD says "ねつが ある") is the canonical example.

    Method: for each paper JSON in data/papers/{moji,goi,bunpou,dokkai}/
    paper-*.json with a kbSourceId, locate the corresponding MD Q-block.
    For each kanji in the JSON rationale, verify it also appears
    somewhere in the MD Q-block (stem, choices, answer line, or notes).

    This narrow check avoids false-positives on AUTHORED rationales
    (e.g., bunpou-5/6 sentence-rearrange where the rationale was
    expanded during audit fixes) — authored rationales reuse kanji
    that were already in the MD's stem / choices, so they pass. But a
    stale-extracted rationale that uses a kanji the MD has corrected
    to kana fails immediately.

    A complementary check (kana-only JSON rationale where MD has
    kanji) is intentionally NOT enforced — kana is always permissible
    at N5 level; only stale kanji that contradicts a kana-only MD
    surface as drift.
    """
    failures: list[str] = []
    PAPERS_DIR = ROOT / "data" / "papers"
    if not PAPERS_DIR.exists():
        return failures
    KB_BY_CATEGORY = {
        'moji':   KB / 'moji_questions_n4.md',
        'goi':    KB / 'goi_questions_n4.md',
        'bunpou': KB / 'bunpou_questions_n4.md',
        'dokkai': KB / 'dokkai_questions_n4.md',
    }
    KANJI_RE_LOCAL = re.compile(r'[一-鿿]')

    md_cache: dict[str, str] = {}
    for paper_path in sorted(PAPERS_DIR.rglob('paper-*.json')):
        category = paper_path.parent.name
        kb_path = KB_BY_CATEGORY.get(category)
        if kb_path is None or not kb_path.exists():
            continue
        if category not in md_cache:
            md_cache[category] = kb_path.read_text(encoding='utf-8')
        md = md_cache[category]

        try:
            paper = json.loads(paper_path.read_text(encoding='utf-8'))
        except Exception as e:
            failures.append(f"JA-32 {paper_path}: parse error: {e}")
            continue
        for q in paper.get('questions', []):
            rat = q.get('rationale')
            kb_q = q.get('kbSourceId')
            if not rat or not kb_q:
                continue
            block_re = re.compile(
                rf'### {re.escape(kb_q)}\b([\s\S]+?)(?=\n### Q\d|\Z)'
            )
            m = block_re.search(md)
            if not m:
                failures.append(
                    f"JA-32 {paper_path.name} {q.get('id', '?')}: "
                    f"kbSourceId={kb_q} has no matching block in {kb_path.name}"
                )
                continue
            block_text = m.group(0)
            json_kanji = set(KANJI_RE_LOCAL.findall(rat))
            md_kanji = set(KANJI_RE_LOCAL.findall(block_text))
            stale = json_kanji - md_kanji
            if stale:
                failures.append(
                    f"JA-32 {paper_path.name} {q.get('id', '?')} "
                    f"({kb_q}): rationale uses kanji not in MD source: "
                    f"{sorted(stale)} — possible stale extraction "
                    f"(MD may have corrected to kana)"
                )
    return failures


def _check_ja_29_subtype_taxonomy() -> list[str]:
    """Question subtypes are a closed taxonomy. New subtypes must be added
    here AND get explicit renderer support before shipping; an unknown
    subtype slipping through means the renderer treats it as a plain mcq
    silently, which masks design intent.

    Closing DEFER-2 (Pass-23 r5, 2026-05-02): rather than promote
    paraphrase to a top-level question type (which would require renderer
    changes for marginal gain), we lock the subtype field as the canonical
    extension point. Any new subtype must be registered here.
    """
    ALLOWED_SUBTYPES = {"paraphrase", "kanji_writing"}
    failures: list[str] = []
    qpath = ROOT / "data" / "questions.json"
    if not qpath.exists():
        return ["JA-29: data/questions.json missing"]
    try:
        data = json.loads(qpath.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"JA-29: parse error: {e}"]
    for q in data.get("questions", []):
        sub = q.get("subtype")
        if sub is None:
            continue
        if sub not in ALLOWED_SUBTYPES:
            failures.append(
                f"JA-29 question id '{q.get('id', '?')}' has unknown "
                f"subtype '{sub}'. Allowed: {sorted(ALLOWED_SUBTYPES)}. "
                f"Register the subtype in tools/check_content_integrity.py "
                f"and confirm renderer support before adding new instances."
            )
    return failures


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    verbose = "-v" in argv or "--verbose" in argv

    overall_failures: list[str] = []
    print(f"JLPT N4 Content Integrity - {len(CHECKS)} invariants")
    # Note: invariant count grew from 23 to 24 with JA-15 (audio refs on disk).
    print("=" * 60)

    for code, label, check_fn in CHECKS:
        try:
            failures = check_fn()
        except Exception as e:  # noqa: BLE001 - report any check-internal error
            failures = [f"{code} check raised {type(e).__name__}: {e}"]
        status = "PASS" if not failures else f"FAIL ({len(failures)})"
        print(f"  {code:<6} {label:<32} {status}")
        if failures and verbose:
            for f in failures[:10]:
                print(f"           - {f}")
            if len(failures) > 10:
                print(f"           ... and {len(failures) - 10} more")
        overall_failures.extend(failures)

    print("=" * 60)
    if overall_failures:
        print(f"FAIL: {len(overall_failures)} integrity violation(s)")
        if not verbose:
            print("Run with -v / --verbose to see all violations")
        return 1

    print(f"PASS: all {len(CHECKS)} invariants green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
