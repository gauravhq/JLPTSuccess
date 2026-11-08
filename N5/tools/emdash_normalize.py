"""Em-dash (U+2014) normalizer for the N5 website's learner-facing text.

Owner decision 2026-11-08 (TYPO-1): the site shows no em dashes. This module
is the single rule set used three ways:

  1. one-off rewrite of committed content:  python tools/emdash_normalize.py --apply
  2. CI / pre-commit check:                 python tools/emdash_normalize.py --check
     (also wired as JA-180 in tools/check_content_integrity.py)
  3. builder output filter: build_static_mirrors.py, build_lesson_html_mirrors.py
     and build_llm_surfaces_2026_05_18.py pass every file they write through
     normalize(), so a rebuild cannot put em dashes back.

Rules (D below stands for the em dash), decided per dash run from the ORIGINAL text (results never cascade):
  placeholder  nothing textual on either side ("D", <td>D</td>, `D`)  -> "-"
  lead         dash opens a text unit ("\\nD Tanaka")                  -> removed
  trail        dash ends a text unit ("text D</li>")                   -> removed
  title        " D JLPT..." site-name suffix in titles                  -> " | "
  after_stop   dash after . ! ? 。 । (not after "etc.")                 -> removed
  after_punct  dash after : ; , 、                                      -> removed
  range        tight digitDdigit ("1D5")                                -> "-"
  pair         two dashes framing an aside in one sentence             -> ", " each
  conj         next word starts a clause (but, which, लेकिन ...)        -> ", "
  comma        the sentence already has a colon                         -> ", "
  colon        everything else (term D gloss, label D explanation)     -> ": "
A few Japanese two-speaker example lines are rewritten to 「A」「B」 first.
After a Japanese term, gloss words ("ぜんぜん D not at all", "どの D which")
take the colon, not the conjunction comma.

Only U+2014 is touched. The katakana long-vowel mark (ー, U+30FC) and the
horizontal bar (―, U+2015) are different characters and are never changed.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

EM_DASH = "\u2014"
N5_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = N5_ROOT.parent

# ----- scope: what a learner can see ---------------------------------------
# Internal folders (tooling, audit docs, prompts, specs, tests) are out of scope.
INTERNAL_PREFIXES = ("N5/not-required/", "N5/not_required/", "N5/feedback/", "N5/docs/",
                     "N5/specifications/", "N5/prompts/", "N5/tests/", "N5/node_modules/",
                     "N5/tools/", "N5/.claude/")
# Markdown the SPA renders (changelog.js, md-viewer.js) plus the user-facing READMEs.
RENDERED_ROOT_FILES = {"N5/CHANGELOG.md", "N5/PRIVACY.md", "N5/NOTICES.md", "N5/README.md",
                       "N5/README.hi.md", "N5/llms.txt"}
SERVED_CODE = ("N5/js/min/", "N5/locales/")


def in_scope(rel: str) -> bool:
    """True when the repo-relative path is learner-facing N5 content."""
    if rel in RENDERED_ROOT_FILES:
        return True
    if not rel.startswith("N5/") or rel.startswith(INTERNAL_PREFIXES):
        return False
    if rel.startswith("N5/data/") and rel.endswith(".json"):
        return True
    if rel.startswith("N5/dist/"):
        return True
    if rel.startswith(SERVED_CODE) and rel.endswith((".js", ".json")):
        return True
    return rel.endswith((".html", ".htm")) or rel == "N5/css/main.min.css"


def tracked_scope_files() -> list[str]:
    """Repo-relative paths of tracked, in-scope files."""
    out = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "-z", "N5"],
                         capture_output=True, check=True).stdout.decode("utf-8")
    return [f for f in out.split("\0") if f and in_scope(f)]


# ----- rule tables ----------------------------------------------------------
DIALOGUE_LINES = {
    "ありがとうございました。\u2014 どういたしまして。": "「ありがとうございました。」「どういたしまして。」",
    "ただいま。\u2014 おかえりなさい。": "「ただいま。」「おかえりなさい。」",
    "おげんきですか。\u2014 はい、げんきです。": "「おげんきですか。」「はい、げんきです。」",
    "おしごとは（\u3000）ですか。 \u2014 たのしいです。": "「おしごとは（\u3000）ですか。」「たのしいです。」",
}
SENTENCE_END = set(".!?。！？।…")
CLAUSE_PUNCT = set(":;,、，：；")
OPENERS = set("([{「『（【")
CLOSERS = set(")]}」』）】")
BLOCK_TAGS = {"p", "li", "td", "th", "tr", "div", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol",
              "table", "title", "br", "section", "article", "header", "footer", "nav", "main",
              "figure", "figcaption", "blockquote", "pre", "dd", "dt", "dl", "option", "summary",
              "details", "body", "head", "html", "script", "style", "noscript", "caption", "hr"}
CONJUNCTIONS = {"but", "and", "or", "so", "yet", "nor", "not", "which", "who", "whose", "where",
                "when", "while", "whereas", "although", "though", "because", "since", "unless",
                "unlike", "rather", "plus", "then", "otherwise", "hence", "thus", "i.e.", "e.g.",
                "especially", "including", "even",
                "लेकिन", "पर", "परंतु", "किंतु", "और", "या", "यानी", "जो", "क्योंकि", "बल्कि", "तो",
                "फिर", "जबकि"}
STRONG_CONJUNCTIONS = {"but", "although", "though", "because", "since", "unless", "whereas", "while",
                       "unlike", "otherwise", "hence", "thus", "i.e.", "e.g.",
                       "लेकिन", "परंतु", "किंतु", "क्योंकि", "बल्कि", "जबकि"}
CLAUSE_AFTER_NOT = {"what", "the", "a", "an", "in", "on", "at", "for", "to", "just", "only",
                    "because", "here", "used", "required", "correct", "natural", "possible", "part",
                    "this", "that", "as", "with", "by", "from", "about", "like", "all", "every",
                    "one", "something"}
ENTITY_QUOTES = {"quot", "#x27", "#39", "apos", "#34", "rsquo", "rdquo", "lsquo", "ldquo"}
JA_CHAR = re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF\u3000-\u303F]")
ABBREV_END = re.compile(r"(etc|vs|e\.g|i\.e|cf|approx|incl)\.$", re.I)
HTML_ENTITY = re.compile(r"&(#x?[0-9a-fA-F]+|[a-zA-Z]+);")
SITE_SUFFIX_START = ("JLPT", "JLPTSuccess")
PAIR_MAX_GAP = 120          # chars between the two dashes of an aside
SEGMENT_REACH = 400         # how far to look for a sentence boundary
COLON_LOOKAHEAD = 40        # chars after the dash checked for an existing colon
SEPARATORS = {"pair": ",", "conj": ",", "comma": ",", "colon": ":"}


def mode_for(path: str) -> str:
    """Text mode by file extension: json, html, md, tsv or txt."""
    if path.endswith(".json"):
        return "json"
    if path.endswith((".html", ".htm", ".xml", ".xsl")):
        return "html"
    if path.endswith(".md"):
        return "md"
    if path.endswith(".tsv"):
        return "tsv"
    return "txt"


def _tag_name(tag: str) -> str:
    m = re.match(r"</?\s*([a-zA-Z0-9]+)", tag)
    return m.group(1).lower() if m else ""


def _is_space(c: str, mode: str) -> bool:
    if c in " \u3000":
        return True
    if c == "\t":
        return mode != "tsv"
    if c in "\r\n":
        return mode in ("html", "md", "txt")
    return False


class _Scan:
    """Look outward from a dash run for the nearest meaningful neighbour."""

    def __init__(self, t: str, mode: str):
        self.t, self.mode = t, mode
        self.crossed_left = self.crossed_right = False

    def left(self, i: int) -> tuple[str, str]:
        t, mode = self.t, self.mode
        j = i - 1
        self.crossed_left = False
        while j >= 0:
            c = t[j]
            if mode == "md" and c == "\n" and j >= 1 and t[j - 1] == "\n":
                return "BOUND", "\n"
            if _is_space(c, mode):
                j -= 1
                continue
            if mode == "html" and c == ">":
                k = t.rfind("<", 0, j)
                if k == -1:
                    return "TEXT", c
                tag = t[k:j + 1]
                if _tag_name(tag) in BLOCK_TAGS and not tag.startswith("</"):
                    return "BOUND", "<"
                self.crossed_left = True
                j = k - 1
                continue
            if mode == "html" and c == ";":
                m = re.search(r"&(#?\w+);$", t[max(0, j - 10):j + 1])
                if m:
                    if m.group(1) in ENTITY_QUOTES:
                        k = j - len(m.group(0))
                        before = t[k] if k >= 0 else " "
                        return ("BOUND", '"') if before in " (\n>" else ("TEXT", '"')
                    return "TEXT", "&"
            if mode == "json":
                if c == "n" and j >= 1 and t[j - 1] == "\\":
                    return "BOUND", "\n"
                if c == '"':
                    return ("TEXT", c) if j >= 1 and t[j - 1] == "\\" else ("BOUND", c)
            if c in "\r\n\t":
                return "BOUND", c
            if c in "\"“" and mode != "json":
                before = t[j - 1] if j >= 1 else " "
                return ("BOUND", c) if before in " (\n\t>" else ("TEXT", c)
            if c in OPENERS:
                return "BOUND", c
            if c in SENTENCE_END:
                return "SENT", c
            if c in CLAUSE_PUNCT:
                return "PUNCT", c
            return "TEXT", c
        return "BOUND", ""

    def right(self, i: int) -> tuple[str, str, str]:
        t, mode = self.t, self.mode
        j, n = i, len(self.t)
        self.crossed_right = False
        while j < n:
            c = t[j]
            if mode == "md" and c == "\n" and (t[j + 1:j + 2] == "\n"
                                               or re.match(r"\n\s*([-*#>]|\d+\.)\s", t[j:j + 6])):
                return "BOUND", "\n", ""
            if _is_space(c, mode):
                j += 1
                continue
            if mode == "html" and c == "<":
                k = t.find(">", j)
                if k == -1:
                    return "TEXT", c, ""
                if _tag_name(t[j:k + 1]) in BLOCK_TAGS:
                    return "BOUND", "<", ""
                self.crossed_right = True
                j = k + 1
                continue
            if mode == "json" and c == "\\" and t[j + 1:j + 2] == "n":
                return "BOUND", "\n", ""
            if mode == "json" and c == "\\" and t[j + 1:j + 2] == '"':
                m = re.match(r'\\"([^\s\\"<]+)', t[j:j + 40])
                return "TEXT", '"', (m.group(1) if m else "")
            if mode == "json" and c == '"':
                return "BOUND", c, ""
            if c in "\r\n\t" or c in CLOSERS:
                return "BOUND", c, ""
            m = re.match(r"[^\s<\"\\]+", t[j:j + 60])
            return "TEXT", c, (m.group(0) if m else c)
        return "BOUND", "", ""


def _segment(t: str, s: int, e: int, mode: str) -> tuple[int, int]:
    """Approximate sentence around a dash, as (start, stop) indices."""
    pattern = r"[.!?。！？।](\s|$)|\n\n|</?(p|li|td|th|div|h\d|br|title|tr)\b"
    if mode == "json":
        pattern += r'|\\n|(?<!\\)"'
    stops = re.compile(pattern)
    left = max(0, s - SEGMENT_REACH)
    for m in stops.finditer(t, max(0, s - SEGMENT_REACH), s):
        left = m.end()
    m = stops.search(t, e, min(len(t), e + SEGMENT_REACH))
    right = m.start() if m else min(len(t), e + SEGMENT_REACH)
    return left, right


def _is_conjunction(t: str, e: int, word: str, left_char: str) -> bool:
    w = word.lower().rstrip(",.;:")
    if w not in CONJUNCTIONS:
        return False
    if JA_CHAR.match(left_char or ""):
        if w in STRONG_CONJUNCTIONS:
            return True
        if w == "not":
            nxt = re.match(r"\S+\s+([^\s,.;:]+)", t[e:e + 60].lstrip())
            return bool(nxt and nxt.group(1).lower() in CLAUSE_AFTER_NOT)
        return False
    return True


def _decide(t: str, s: int, e: int, mode: str, runs: list[tuple[int, int]], scan: _Scan) -> str:
    if (t[max(0, s - 6):s] == "<code>" and t[e:e + 7] == "</code>") or (t[s - 1:s] == "`" and t[e:e + 1] == "`"):
        return "placeholder"
    lk, lc = scan.left(s)
    rk, rc, word = scan.right(e)
    structural = scan.crossed_left or scan.crossed_right
    if lk == "BOUND" and rk == "BOUND":
        return "placeholder"
    if lk == "BOUND":
        return "lead"
    if rk == "BOUND":
        return "trail"
    if word.startswith(SITE_SUFFIX_START) and mode != "json":
        return "title"
    if structural:
        return "colon"   # "label</span> D <span>gloss": a list entry, not prose
    if lk == "SENT":
        before = t[max(0, s - 12):s].rstrip()
        if not (ABBREV_END.search(before) and re.match(r"[a-z]", word)):
            return "after_stop"
    if lk == "PUNCT":
        return "after_punct"
    tight = s > 0 and not t[s - 1].isspace() and e < len(t) and not t[e].isspace()
    if tight and lc.isdigit() and rc.isdigit():
        return "range"
    a, b = _segment(t, s, e, mode)
    inside = [r for r in runs if a <= r[0] < b]
    if len(inside) == 2:
        between = t[inside[0][1]:inside[1][0]]
        if mode == "html":
            # Entities (&#x27; &quot;) end in ";" but are not clause breaks; count
            # each as one character so HTML and JSON copies of a text agree.
            between = HTML_ENTITY.sub("'", between)
        if len(between) <= PAIR_MAX_GAP and not re.search(r" / |;|\||:", between):
            return "pair"
    if _is_conjunction(t, e, word, lc):
        return "conj"
    # Stay inside the same text run: tags and attribute quotes bound it in
    # HTML; in JSON "<" and ">" are literal text and only an unescaped quote
    # ends the string.
    edge = r'(?<!\\)"' if mode == "json" else r"[<>\"]"
    left_near = re.split(edge, t[a:s])[-1]
    right_near = re.split(edge, t[e:min(b, e + COLON_LOOKAHEAD)])[0]
    if re.search(r":\s|：", left_near + " " + right_near):
        return "comma"
    return "colon"


def normalize(text: str, mode: str, stats: Counter | None = None) -> str:
    """Return text with every U+2014 run replaced per the module rules."""
    if EM_DASH not in text:
        return text
    stats = stats if stats is not None else Counter()
    for old, new in DIALOGUE_LINES.items():
        if old in text:
            stats["dialogue"] += text.count(old)
            text = text.replace(old, new)
    runs = [(m.start(), m.end()) for m in re.finditer(EM_DASH + "+", text)]
    scan = _Scan(text, mode)
    out: list[str] = []
    pos = 0
    for s, e in runs:
        kind = _decide(text, s, e, mode, runs, scan)
        stats[kind] += 1
        ls = s - 1 if s > 0 and text[s - 1] in " \u3000" else s
        rs = e + 1 if e < len(text) and text[e] in " \u3000" else e
        if kind in ("placeholder", "range"):
            rep, a, b = "-", s, e
        elif kind == "lead":
            rep, a, b = "", s, rs
        elif kind == "trail":
            rep, a, b = "", ls, e
        elif kind in ("after_stop", "after_punct"):
            rep, a, b = "", s, rs
            if text[e:e + 1] not in (" ", "\u3000"):
                a = ls
        elif kind == "title":
            rep, a, b = " | ", ls, rs
        else:
            sep = SEPARATORS[kind]
            if e < len(text) and text[e] in "\r\n":
                rep, a, b = sep, ls, e
            else:
                rep, a, b = sep + " ", ls, rs
        a = max(a, pos)
        out.append(text[pos:a])
        out.append(rep)
        pos = b
    out.append(text[pos:])
    return "".join(out)


def _run(apply: bool) -> int:
    stats: Counter = Counter()
    remaining: list[tuple[str, int]] = []
    bad_json: list[str] = []
    changed = 0
    for rel in tracked_scope_files():
        path = REPO_ROOT / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        count = text.count(EM_DASH)
        if not count:
            continue
        if not apply:
            remaining.append((rel, count))
            continue
        mode = mode_for(rel)
        new = normalize(text, mode, stats)
        if mode == "json":
            try:
                json.loads(new)
            except json.JSONDecodeError as exc:
                bad_json.append(f"{rel}: {exc}")
                continue
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(new)
        changed += 1
    if apply:
        print(f"rewrote {changed} files; decisions: {dict(stats.most_common())}")
        if bad_json:
            print("NOT written (would break JSON):", *bad_json, sep="\n  ")
            return 1
        return 0
    total = sum(n for _, n in remaining)
    print(f"em dashes in learner-facing files: {total} in {len(remaining)} files")
    for rel, n in sorted(remaining, key=lambda x: -x[1])[:20]:
        print(f"  {n:6d}  {rel}")
    return 1 if total else 0


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="exit 1 if any learner-facing file has an em dash")
    group.add_argument("--apply", action="store_true", help="rewrite learner-facing files in place")
    args = ap.parse_args()
    return _run(apply=args.apply)


if __name__ == "__main__":
    sys.exit(main())
