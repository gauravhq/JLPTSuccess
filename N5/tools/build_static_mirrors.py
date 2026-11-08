"""Build pre-rendered static HTML mirrors for every SPA route surface.

User-reported BUG-010 (2026-05-16) generalizes BUG-001 (grammar-only)
to every content + meta surface. Each pre-rendered file:

- Mirrors what the SPA would render for that route, as real HTML
  (not a meta refresh, not a noscript placeholder).
- Carries route-specific <title>, <meta name="description">, and OG
  tags (og:title, og:description, og:url, og:image).
- Carries <link rel="canonical"> pointing back to the live SPA hash
  route (so search engines deduplicate static + interactive views).
- Carries a small inline script: when JS is enabled, redirect after
  a short delay so a user landing on the static mirror flows to the
  interactive SPA. Search engines (which render JS but stop before
  redirect delay completes) still index the static content.
- Carries inline CSS sufficient to render readably without JS.

Surfaces (built in stages — see BUG-010 description):
- Stage 1: grammar (/N5/learn/grammar/<id>/index.html × 178 + index)
- Stage 2: vocab (/N5/learn/vocab/<form>/index.html × 1009 + index)
- Stage 3: kanji (/N5/kanji/<glyph>/index.html × 106 + index)
- Stage 4: reading (/N5/reading/<id>/index.html × 54 + index)
- Stage 5: listening (/N5/listening/<id>/index.html × 50 + index)
- Stage 6: meta routes (home / changelog / privacy / notices /
  feedback / settings / test / sitting / missed / summary) +
  /N5/sitemap.xml + /N5/robots.txt

Run from N5/:
  python tools/build_static_mirrors.py
  python tools/build_static_mirrors.py --stages grammar,vocab
  python tools/build_static_mirrors.py --stages all  (default)

WARNING (2026-05-29) - a wholesale run is NOT a no-op; this builder is
out of sync with the committed mirrors in two ways:
  1. ROUTING FORMAT. The committed CONTENT mirrors (learn/, kanji/,
     reading/, listening/) are still in the PRE-2026-05-24 hash-routing
     format (a setTimeout redirect to a "#/" hash route + a "Static
     read-only mirror" banner), hand-patched on top with the global
     app-header (injected 2026-05-27) and a nav merge (2026-05-28). This
     builder emits the NEWER history-mode template. Running it wholesale
     RE-MIGRATES ~1372 content pages' routing/canonical/redirect markup
     (~42k lines) - a deliberate, separately-reviewed migration, not
     routine maintenance.
  2. APP-HEADER. This builder does NOT emit the global brand+nav
     app-header; a SECOND step adds it
     (tools/inject_app_header_into_mirrors_2026_05_27.py). If you run this
     builder you MUST run that injector afterwards, or every mirror it
     wrote renders header-less ("looks broken" on deep-link) - the exact
     regression that hit home/changelog twice (commit 7ce167ff + a
     2026-05-29 rebuild). JA-170 in check_content_integrity.py is the CI
     guard: it fails the build if any mirror is left header-less.

After running, run tools/check_content_integrity.py (JA-113 meta-mirror
freshness + JA-157 paper-mirror staleness + JA-170 app-header presence).
"""
from __future__ import annotations

import argparse
import html
import io
import json
import re
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from emdash_normalize import mode_for as mode_for_emdash  # noqa: E402
from emdash_normalize import normalize as normalize_emdash  # noqa: E402

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
GRAMMAR = DATA_DIR / "grammar.json"
VOCAB = DATA_DIR / "vocab.json"
KANJI = DATA_DIR / "kanji.json"
READING = DATA_DIR / "reading.json"
LISTENING = DATA_DIR / "listening.json"

# Live deploy base — used in canonical + og:url. Trailing slash matters.
SITE_BASE = "https://gauravaccentureproducts.github.io/JLPTSuccess/"
N5_BASE = SITE_BASE + "N5/"

# SPA cache-buster version — must match the `?v=...` in index.html's
# script tag so the mirrors load the same minified bundle the SPA root
# does. Bumped 2026-05-24 with the history-mode migration to v1.17.0.
SPA_VERSION = "1.17.30"


# ----- Common HTML chrome -----

INLINE_CSS = """
  :root { --green: #14452a; --green-soft: #1a5c38; --bg: #ffffff; --bg-soft: #f6f8f6; --text: #1a1a1a; --muted: #555; --border: #ddd; }
  * { box-sizing: border-box; }
  html, body { background: var(--bg); color: var(--text); }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Yu Gothic", "Noto Sans CJK JP", sans-serif; max-width: 760px; margin: 0 auto; padding: 1rem; line-height: 1.6; }
  a { color: var(--green); }
  a:hover { color: var(--green-soft); }
  h1 { font-size: 1.6em; margin: 0.5rem 0; line-height: 1.3; }
  h2 { font-size: 1.18em; border-bottom: 1px solid var(--border); padding-bottom: 0.3em; margin-top: 2rem; }
  h3 { font-size: 1.05em; margin-top: 1.4rem; }
  code { background: #f0f3f0; padding: 0.05em 0.35em; border-radius: 3px; font-size: 0.92em; }
  .meta-banner { background: var(--bg-soft); border-left: 3px solid var(--green); padding: 0.75rem 1rem; font-size: 0.92em; margin: 0 0 1.5rem 0; }
  .meta-banner a { font-weight: 600; }
  .lang-tag { display: inline-block; background: #eef; border: 1px solid #ccd; border-radius: 3px; padding: 0 0.4em; font-size: 0.8em; color: #336; margin-right: 0.45em; vertical-align: 1px; }
  .ex { margin: 0.8em 0; padding: 0.5em 0.7em; background: #fafbfa; border-left: 2px solid #e4ebe5; border-radius: 0 4px 4px 0; }
  .ex .ja { font-size: 1.05em; }
  .ex .en { color: var(--muted); font-size: 0.93em; margin-top: 0.2em; }
  .wrong { color: #a33; }
  .right { color: var(--green-soft); }
  /* BUG-011: register-variant entries — neutral framing (no strike/check) */
  .variant-pair { border-left-color: #a66a1f; }
  .variant-row { display: flex; align-items: baseline; gap: 0.5em; margin: 0.2em 0; }
  .variant-label { display: inline-block; background: #f7efe0; color: #a66a1f; border-radius: 3px; padding: 1px 6px; font-size: 0.78em; font-weight: 500; white-space: nowrap; flex-shrink: 0; }
  @media (prefers-color-scheme: dark) {
    .variant-pair { border-left-color: #d6a062; }
    .variant-label { background: #3a2f1f; color: #f0c890; }
  }
  .muted { color: var(--muted); font-size: 0.92em; }
  .index-section { margin-bottom: 1.4rem; }
  .index-section h3 { margin: 1rem 0 0.4rem 0; color: var(--green-soft); }
  .index-card { display: block; padding: 0.5em 0.7em; border: 1px solid #e0e6e0; border-radius: 4px; margin: 0.3em 0; text-decoration: none; color: inherit; }
  .index-card:hover { background: var(--bg-soft); }
  .index-card .label { font-weight: 600; color: var(--green); }
  .index-card .gloss { color: var(--muted); font-size: 0.9em; }
  footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border); font-size: 0.85em; color: var(--muted); }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #1a1d1b; --bg-soft: #232826; --text: #e7eae8; --muted: #a5aba8; --border: #383d3a; }
    code { background: #2a2f2c; }
    .ex { background: #1f2320; border-left-color: #2c3530; }
    .index-card { border-color: #2c3530; }
    .meta-banner { background: #232826; }
    .lang-tag { background: #2a2f3a; color: #b5bdce; border-color: #3a4150; }
  }
"""

# SPA boot script — loaded at end of <body>. The SPA's app.js reads
# location.pathname (history-mode routing) and renders the route into
# the <main id="app"> wrapper. Crawlers without JS see the static
# pre-rendered content. Users with JS see the same content briefly
# until the SPA boots and replaces #app with the interactive version.
# Single URL serves both audiences — replaces the pre-v1.17 hash-
# routing dual-surface architecture (static mirror + SPA redirect).
SPA_BOOT_SCRIPT_TEMPLATE = '<script type="module" src="{spa_js_path}"></script>'

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title_tag}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{canonical_url}">
{hreflang_links}
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical_url}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{description}">
<meta property="og:site_name" content="JLPT N5 Tutor">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{og_title}">
<meta name="twitter:description" content="{description}">
<style>{inline_css}</style>
<link rel="stylesheet" href="{main_css_path}">
</head>
<body>
<main id="app">
<p class="meta-banner"><a href="{n5_root}">&larr; JLPT N5 home</a></p>
<h1>{h1}</h1>
{body}
<footer>
  <p>{breadcrumb_html}</p>
  <p>Part of <a href="{n5_root}">JLPT N5 Tutor</a>. Content licensed CC BY-SA 4.0 · <a href="{n5_root}CONTENT-LICENSE.md">CONTENT-LICENSE.md</a>.</p>
  {footer_meta}
</footer>
</main>
{spa_boot_script}
</body>
</html>
"""


# ----- Helpers -----


def _esc(s: object) -> str:
    return html.escape(str(s) if s is not None else "")


def _relative_root_from(depth: int) -> str:
    """Path from a static mirror back up to /N5/. e.g. depth=3 -> '../../../'"""
    return "../" * depth if depth > 0 else "./"


def _build_page(
    *,
    lang: str = "en",
    title_tag: str,
    h1: str,
    description: str,
    canonical_url: str,
    spa_url: str,
    body_html: str,
    depth: int,
    og_title: str | None = None,
    breadcrumb: list[tuple[str, str]] | None = None,
    footer_meta_html: str = "",
    interactive_note: str = " (audio playback, drills, cross-references require JavaScript).",
    hreflang_alt_url: str | None = None,
    hreflang_lang: str | None = None,
    self_hreflang_lang: str | None = None,
) -> str:
    """Render the full HTML for one static mirror page."""
    n5_root = _relative_root_from(depth)
    og_img = N5_BASE + "icons/icon-512.png"  # static OG image; doesn't need per-page generation in this iteration

    hreflang_links = ""
    if hreflang_alt_url and hreflang_lang:
        self_lang = self_hreflang_lang or lang
        hreflang_links = (
            f'<link rel="alternate" hreflang="{self_lang}" href="{canonical_url}">\n'
            f'<link rel="alternate" hreflang="{hreflang_lang}" href="{hreflang_alt_url}">'
        )

    breadcrumb_html = ""
    if breadcrumb:
        parts = []
        for label, href in breadcrumb:
            if href:
                parts.append(f'<a href="{_esc(href)}">{_esc(label)}</a>')
            else:
                parts.append(_esc(label))
        breadcrumb_html = " · ".join(parts)

    main_css_path = n5_root + f"css/main.min.css?v={SPA_VERSION}"
    spa_js_path = n5_root + f"js/min/app.js?v={SPA_VERSION}"
    spa_boot_script = SPA_BOOT_SCRIPT_TEMPLATE.format(spa_js_path=spa_js_path)

    return PAGE_TEMPLATE.format(
        lang=lang,
        title_tag=_esc(title_tag),
        description=_esc(description),
        canonical_url=_esc(canonical_url),
        hreflang_links=hreflang_links,
        og_title=_esc(og_title or title_tag),
        og_image=_esc(og_img),
        inline_css=INLINE_CSS,
        main_css_path=main_css_path,
        spa_boot_script=spa_boot_script,
        h1=_esc(h1),
        body=body_html,
        n5_root=n5_root,
        breadcrumb_html=breadcrumb_html,
        footer_meta=footer_meta_html,
    )


def _write_if_changed(path: Path, content: str) -> bool:
    """Write content to path only if it differs. Returns True if written.

    Every page passes through tools/emdash_normalize.py first: the site shows
    no em dashes (owner decision 2026-11-08) and some templates below still
    contain them, so the filter keeps a rebuild from adding them back.
    """
    content = normalize_emdash(content, mode_for_emdash(path.name))
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


# ----- Grammar renderer (Stage 1) -----


def _render_examples(examples: list) -> str:
    if not examples:
        return ""
    out = ["<h2>Examples</h2>"]
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        ja = ex.get("ja") or ""
        en = ex.get("en") or ex.get("translation_en") or ""
        if not ja:
            continue
        out.append('<div class="ex">')
        out.append(f'<div class="ja" lang="ja"><span class="lang-tag">JA</span>{_esc(ja)}</div>')
        if en:
            out.append(f'<div class="en"><span class="lang-tag">EN</span>{_esc(en)}</div>')
        out.append("</div>")
    return "\n".join(out)


def _render_common_mistakes(cms: list) -> str:
    """Render common_mistakes section.

    BUG-011 (2026-05-16): entries with `kind: "register_variant"` are NOT
    errors — both forms are grammatically valid, differing in register /
    formality / pragmatic context. They render with neutral framing
    (no ✗/✓, no strike-through), using `label_a` / `label_b` as register
    tags. Other entries render as the legacy wrong/right pair.
    """
    if not cms:
        return ""

    # Split into traditional errors vs register variants for clearer section
    # presentation.
    errors = [c for c in cms if isinstance(c, dict) and c.get("kind") != "register_variant"]
    variants = [c for c in cms if isinstance(c, dict) and c.get("kind") == "register_variant"]

    out: list[str] = []

    if errors:
        out.append("<h2>Common mistakes</h2>")
        for cm in errors:
            wrong = cm.get("wrong") or ""
            right = cm.get("right") or ""
            why = cm.get("why") or ""
            if not (wrong or right):
                continue
            out.append('<div class="ex">')
            if wrong:
                out.append(f'<div class="wrong" lang="ja">✗ {_esc(wrong)}</div>')
            if right:
                out.append(f'<div class="right" lang="ja">✓ {_esc(right)}</div>')
            if why:
                out.append(f'<div class="en">{_esc(why)}</div>')
            out.append("</div>")

    if variants:
        out.append("<h2>Register variants — both forms are correct</h2>")
        out.append('<p class="muted">These forms differ in register, formality, or pragmatic context — not in grammaticality. Pick by context.</p>')
        for cm in variants:
            # BUG-013 (2026-05-16): the schema migration is complete —
            # register-variant entries now carry `form_a` / `form_b`
            # keys (not `wrong` / `right`). Fall back to legacy keys
            # if a stale entry hasn't migrated yet.
            form_a = cm.get("form_a") or cm.get("wrong") or ""
            form_b = cm.get("form_b") or cm.get("right") or ""
            label_a = cm.get("label_a") or "Form A"
            label_b = cm.get("label_b") or "Form B"
            why = cm.get("why") or ""
            if not (form_a or form_b):
                continue
            out.append('<div class="ex variant-pair">')
            if form_a:
                out.append(
                    f'<div class="variant-row"><span class="variant-label">{_esc(label_a)}</span> '
                    f'<span lang="ja">{_esc(form_a)}</span></div>'
                )
            if form_b:
                out.append(
                    f'<div class="variant-row"><span class="variant-label">{_esc(label_b)}</span> '
                    f'<span lang="ja">{_esc(form_b)}</span></div>'
                )
            if why:
                out.append(f'<div class="en">{_esc(why)}</div>')
            out.append("</div>")

    return "\n".join(out)


def _render_wcp(wcps: list) -> str:
    if not wcps:
        return ""
    out = ["<h2>Wrong / corrected pairs</h2>"]
    for wcp in wcps:
        if not isinstance(wcp, dict):
            continue
        wrong = wcp.get("wrong") or ""
        correct = wcp.get("correct") or wcp.get("right") or ""
        why = wcp.get("why") or ""
        if not (wrong or correct):
            continue
        out.append('<div class="ex">')
        if wrong:
            out.append(f'<div class="wrong" lang="ja">✗ {_esc(wrong)}</div>')
        if correct:
            out.append(f'<div class="right" lang="ja">✓ {_esc(correct)}</div>')
        if why:
            out.append(f'<div class="en">{_esc(why)}</div>')
        out.append("</div>")
    return "\n".join(out)


def _render_grammar_pattern_body(p: dict) -> tuple[str, str]:
    """Returns (body_html, description) for one grammar pattern."""
    title = p.get("pattern") or p.get("id")
    meaning_en = p.get("meaning_en") or ""
    meaning_ja = p.get("meaning_ja") or ""
    explanation_en = p.get("explanation_en") or ""

    desc = (meaning_en or title)[:155]

    parts: list[str] = []
    if meaning_en:
        parts.append(f'<p><span class="lang-tag">EN</span>{_esc(meaning_en)}</p>')
    if meaning_ja:
        parts.append(f'<p lang="ja"><span class="lang-tag">JA</span>{_esc(meaning_ja)}</p>')
    if explanation_en and explanation_en != meaning_en:
        parts.append(f'<h2>Explanation</h2><p>{_esc(explanation_en)}</p>')

    # HOW TO USE / 使い方 — render the SAME content the SPA renders
    # (`renderHowToUseTable` in js/learn-grammar.js). The earlier static
    # mirror rendered only `<h2>Attaches to</h2><p>{tokens}</p>`, which
    # left users hitting the mirror with JS-disabled / slow-boot seeing a
    # single technical token like "question_word" under what the SPA
    # labels "HOW TO USE / 使い方". The richer fallback below pairs each
    # attaches_to slot with the pattern itself, then (when present)
    # adds the conjugation table — same shape the SPA emits, just
    # noscript-ready. BUG-203, JA-172 enforces parity on rebuild.
    fr = p.get("form_rules") or {}
    if isinstance(fr, dict):
        atts = fr.get("attaches_to") or []
        conjs = fr.get("conjugations") or []
        # Top "attach points → pattern" table is rendered only when there
        # are ≥2 attach points. A single attach point just re-states the
        # title (e.g. "Before a noun → こんな / そんな / あんな / どんな +
        # Noun") — the SPA renderer hides it for the same reason. Section
        # itself only renders when at least one of the sub-tables would.
        # Keep in sync with `renderHowToUseTable` in js/learn-grammar.js;
        # JA-173 invariant assumes this rule. UI polish 2026-05-31.
        show_top = isinstance(atts, list) and len(atts) >= 2
        show_conj = isinstance(conjs, list) and len(conjs) >= 2
        if show_top or show_conj:
            usage: list[str] = []
            usage.append('<section class="pattern-usage">')
            usage.append(
                '<div class="pattern-usage-header">'
                '<h2 class="section-title">How to use</h2>'
                '<span class="pattern-usage-chip" lang="ja">使い方</span>'
                '</div>'
            )
            if show_top:
                # Map slot keys to human-readable labels. Must stay in
                # sync with ATTACHES_TO_LABEL in js/learn-grammar.js.
                # When a key is missing, fall back to title-cased key.
                _LABELS = {
                    "noun": "Noun",
                    "noun_subject": "Noun (subject)",
                    "noun_location": "Noun (location)",
                    "noun_time": "Noun (time)",
                    "noun_quantity": "Noun (quantity)",
                    "noun_or_adj": "Noun or adjective",
                    "na_adjective": "な-adjective",
                    "i_adjective": "い-adjective",
                    "verb": "Verb",
                    "verb_stem": "Verb stem (ます-base)",
                    "verb_stem_i": "Verb i-stem",
                    "verb_root": "Verb root",
                    "verb_dictionary": "Verb (dictionary form)",
                    "verb_plain": "Verb (plain form)",
                    "verb_te": "Verb (て-form)",
                    "verb_ta": "Verb (た-form)",
                    "verb_nai": "Verb (ない-form)",
                    "verb_mashita": "Verb (ました form)",
                    "verb_te_imasu_neg": "Verb (て-いません)",
                    "verb_or_adj_stem": "Verb or adjective stem",
                    "pronoun": "Pronoun",
                    "question_word": "Question word",
                    "before_noun": "Before a noun",
                    "adverbial": "Adverbial position",
                    "sentence_end": "Sentence end",
                    "sentence_pattern": "Full sentence",
                    "clause": "Clause",
                    "clause_start": "Clause-initial",
                    "clause_end": "Clause-final",
                    "plain_clause": "Plain-form clause",
                    "plain_or_polite_clause": "Plain or polite clause",
                    "quoted_clause": "Quoted clause",
                    "quantity": "Quantity expression",
                    "number": "Number",
                    "set_phrase": "Set phrase",
                    "standalone": "Standalone",
                    "dialogue": "Dialogue line",
                    "after_name": "After a name",
                }
                usage.append(
                    '<table class="pattern-usage-table" '
                    f'aria-label="Attach points for {_esc(title)}">'
                    '<tbody>'
                )
                for i, a in enumerate(atts):
                    label = _LABELS.get(a) or str(a).replace("_", " ").capitalize()
                    usage.append("<tr>")
                    usage.append(f'<td class="pattern-usage-pos">{_esc(label)}</td>')
                    if i == 0:
                        usage.append(
                            '<td class="pattern-usage-form" '
                            f'rowspan="{len(atts)}" lang="ja">{_esc(title)}</td>'
                        )
                    usage.append("</tr>")
                usage.append("</tbody></table>")
            if show_conj:
                usage.append(
                    '<table class="pattern-conjugation-table" '
                    'aria-label="Conjugation forms">'
                    '<thead><tr><th scope="col">Form</th>'
                    '<th scope="col">Example</th></tr></thead><tbody>'
                )
                for c in conjs:
                    if not isinstance(c, dict):
                        continue
                    label = c.get("label") or c.get("form") or ""
                    example = c.get("example") or ""
                    usage.append(
                        "<tr>"
                        f'<td>{_esc(label)}</td>'
                        f'<td lang="ja">{_esc(example)}</td>'
                        "</tr>"
                    )
                usage.append("</tbody></table>")
            usage.append("</section>")
            parts.append("\n".join(usage))

    parts.append(_render_examples(p.get("examples") or []))
    parts.append(_render_common_mistakes(p.get("common_mistakes") or []))
    parts.append(_render_wcp(p.get("wrong_corrected_pair") or []))

    body = "\n".join(x for x in parts if x)
    return body, desc


def build_grammar(sitemap_urls: list[str]) -> tuple[int, int, int]:
    """Stage 1 — grammar pattern mirrors.

    History-mode (2026-05-24 onward): each pattern lives at
    learn/<pid>/index.html (not learn/grammar/<pid>/) — clean URL =
    SPA URL = single source of truth. The mirror boots the SPA in
    place rather than redirecting after 1.5s.

    Returns (written, unchanged, total).
    """
    g = json.loads(GRAMMAR.read_text(encoding="utf-8"))
    patterns = g.get("patterns", [])

    out_root = ROOT / "learn"
    written = 0
    unchanged = 0

    for p in patterns:
        pid = p.get("id")
        if not pid:
            continue
        title = p.get("pattern") or pid
        body, desc = _render_grammar_pattern_body(p)
        tier = p.get("tier") or ""
        category = p.get("category") or ""

        # New layout: learn/<pid>/index.html (depth=2 from N5 root)
        out_path = out_root / pid / "index.html"
        canonical = f"{N5_BASE}learn/{pid}/"
        spa_url = canonical

        footer_meta = (
            f'<p>Pattern ID: <code>{_esc(pid)}</code>'
            + (f' · Tier: <code>{_esc(tier)}</code>' if tier else "")
            + (f' · Category: <code>{_esc(category)}</code>' if category else "")
            + "</p>"
        )

        breadcrumb = [
            ("Home", _relative_root_from(2)),
            ("Grammar", "../grammar/"),
            (title, ""),
        ]

        html_text = _build_page(
            lang="en",
            title_tag=f"{title} — JLPT N5 Grammar",
            h1=title,
            description=desc,
            canonical_url=canonical,
            spa_url=spa_url,
            body_html=body,
            depth=2,
            og_title=f"{title} — JLPT N5 Grammar",
            breadcrumb=breadcrumb,
            footer_meta_html=footer_meta,
        )

        if _write_if_changed(out_path, html_text):
            written += 1
        else:
            unchanged += 1

        # Sitemap: the static mirror IS the canonical URL now
        # (history-mode = single URL per pattern).
        mirror_url = canonical
        sitemap_urls.append(mirror_url)

    # Grammar index page
    idx_items = sorted(patterns, key=lambda x: (x.get("categoryOrder", 999), x.get("patternOrder", 999)))
    by_cat: dict[str, list[dict]] = {}
    cat_order: list[str] = []
    for p in idx_items:
        cat = p.get("category") or "Other"
        if cat not in by_cat:
            by_cat[cat] = []
            cat_order.append(cat)
        by_cat[cat].append(p)

    idx_parts: list[str] = []
    idx_parts.append('<p>Static index of all N5 grammar patterns. Each entry links to a read-only mirror; the interactive version (audio, drills, cross-references) is at the SPA route.</p>')
    for cat in cat_order:
        idx_parts.append(f'<section class="index-section">')
        idx_parts.append(f'<h3>{_esc(cat)}</h3>')
        for p in by_cat[cat]:
            pid = p.get("id")
            title = p.get("pattern") or pid
            gloss = (p.get("meaning_en") or "")[:80]
            # Pattern mirrors live one level up at learn/<pid>/ in
            # history-mode (post-migration 2026-05-24). From this
            # listing at learn/grammar/index.html, the relative path
            # is ../<pid>/.
            idx_parts.append(
                f'<a class="index-card" href="../{_esc(pid)}/">'
                f'<span class="label" lang="ja">{_esc(title)}</span> — '
                f'<span class="gloss">{_esc(gloss)}</span>'
                f'</a>'
            )
        idx_parts.append("</section>")
    idx_body = "\n".join(idx_parts)

    # Grammar listing page stays at learn/grammar/index.html (the SPA
    # route /learn/grammar/ matches). Pattern mirrors moved to
    # learn/<pid>/ per the history-mode migration. The listing's
    # per-pattern links point UP one level to ../<pid>/.
    idx_canonical = f"{N5_BASE}learn/grammar/"
    idx_path = ROOT / "learn" / "grammar" / "index.html"
    idx_html = _build_page(
        lang="en",
        title_tag="N5 Grammar — All Patterns (static index)",
        h1="N5 Grammar — All Patterns",
        description=f"All {len(patterns)} N5 grammar patterns, organized by category. Static index for non-JS clients; SPA enhances on hydration.",
        canonical_url=idx_canonical,
        spa_url=idx_canonical,
        body_html=idx_body,
        depth=2,
        og_title="N5 Grammar — All Patterns",
        breadcrumb=[("Home", "../../"), ("Grammar", "")],
        footer_meta_html=f"<p>{len(patterns)} patterns indexed.</p>",
    )
    if _write_if_changed(idx_path, idx_html):
        written += 1
    else:
        unchanged += 1
    sitemap_urls.append(idx_canonical)

    return written, unchanged, len(patterns)


# ----- Vocab renderer (Stage 2) -----


def _encode_url_segment(s: str) -> str:
    """Percent-encode a single URL path segment (e.g. a vocab form)."""
    return urllib.parse.quote(s or "", safe="")


def _render_vocab_examples(examples: list) -> str:
    if not examples:
        return ""
    out = ["<h2>Examples</h2>"]
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        ja = ex.get("ja") or ""
        en = ex.get("translation_en") or ex.get("en") or ""
        if not ja:
            continue
        out.append('<div class="ex">')
        out.append(f'<div class="ja" lang="ja"><span class="lang-tag">JA</span>{_esc(ja)}</div>')
        if en:
            out.append(f'<div class="en"><span class="lang-tag">EN</span>{_esc(en)}</div>')
        out.append("</div>")
    return "\n".join(out)


def _render_vocab_entry_block(e: dict) -> str:
    """Render one vocab entry (one sense). Multiple senses share a form page."""
    form = e.get("form") or ""
    reading = e.get("reading") or ""
    gloss = e.get("gloss") or ""
    gloss_hi = e.get("gloss_hi") or ""
    pos = e.get("pos") or ""
    section = e.get("section") or ""
    register = e.get("register") or ""
    counter = e.get("counter") or ""

    parts: list[str] = ['<article class="vocab-sense">']
    # Sense heading: pos · reading
    head_bits = []
    if pos:
        head_bits.append(f'<code>{_esc(pos)}</code>')
    if reading and reading != form:
        head_bits.append(f'<span class="lang-tag">読</span><span lang="ja">{_esc(reading)}</span>')
    if head_bits:
        parts.append(f'<p class="muted">{" · ".join(head_bits)}</p>')

    if gloss:
        parts.append(f'<p><span class="lang-tag">EN</span>{_esc(gloss)}</p>')
    if gloss_hi:
        parts.append(f'<p><span class="lang-tag">HI</span><span lang="hi">{_esc(gloss_hi)}</span></p>')

    meta_bits = []
    if section:
        meta_bits.append(f"Section: {_esc(section)}")
    if register and register != "neutral":
        meta_bits.append(f"Register: {_esc(register)}")
    if counter:
        meta_bits.append(f"Counter: <code lang=\"ja\">{_esc(counter)}</code>")
    pa = e.get("pitch_accent") or {}
    if isinstance(pa, dict) and pa.get("mora") is not None and pa.get("drop") is not None:
        meta_bits.append(
            f"Pitch: mora={_esc(pa.get('mora'))}, drop={_esc(pa.get('drop'))}"
        )
    if meta_bits:
        parts.append('<p class="muted">' + " · ".join(meta_bits) + "</p>")

    cols = e.get("collocations") or []
    if cols:
        parts.append("<h3>Common collocations</h3><ul>")
        for c in cols[:10]:
            if isinstance(c, str) and c:
                parts.append(f'<li lang="ja">{_esc(c)}</li>')
        parts.append("</ul>")

    parts.append(_render_vocab_examples(e.get("examples") or []))

    fp = e.get("frequent_patterns") or []
    if isinstance(fp, list) and fp:
        links = []
        for pid in fp[:8]:
            if isinstance(pid, str) and pid:
                links.append(
                    f'<a href="../../grammar/{_esc(pid)}/"><code>{_esc(pid)}</code></a>'
                )
        if links:
            parts.append("<h3>Often appears with</h3><p>" + " · ".join(links) + "</p>")

    parts.append("</article>")
    return "\n".join(parts)


def build_vocab(sitemap_urls: list[str]) -> tuple[int, int, int]:
    """Stage 2 — vocab mirrors. One static page per unique form.

    36 forms in the corpus have multiple sense entries (e.g., か, は, あの,
    人). All senses for a given form land on the same static page so a
    learner / reader sees every meaning.

    Returns (written, unchanged, total_forms).
    """
    v = json.loads(VOCAB.read_text(encoding="utf-8"))
    entries = v.get("entries", [])

    # Group entries by form (preserves first-seen order for stable index)
    by_form: dict[str, list[dict]] = {}
    form_order: list[str] = []
    for e in entries:
        form = e.get("form")
        if not form:
            continue
        if form not in by_form:
            by_form[form] = []
            form_order.append(form)
        by_form[form].append(e)

    out_root = ROOT / "learn" / "vocab"
    written = 0
    unchanged = 0

    for form in form_order:
        senses = by_form[form]
        # Use the first sense's reading + gloss as page summary
        primary = senses[0]
        reading = primary.get("reading") or form
        gloss = primary.get("gloss") or ""
        # If multiple senses, append a count hint to title
        sense_hint = f" ({len(senses)} senses)" if len(senses) > 1 else ""

        # Page body: render each sense in sequence
        body_parts: list[str] = []
        body_parts.append(
            f'<p class="muted">Reading: <span lang="ja">{_esc(reading)}</span></p>'
        )
        if len(senses) > 1:
            body_parts.append(
                f'<p class="muted">This form has {len(senses)} sense entries in the corpus. All shown below.</p>'
            )
        for idx, e in enumerate(senses):
            if len(senses) > 1:
                body_parts.append(f'<h2>Sense {idx + 1}</h2>')
            body_parts.append(_render_vocab_entry_block(e))
        body = "\n".join(body_parts)

        form_encoded = _encode_url_segment(form)
        canonical = f"{N5_BASE}#/learn/vocab/{form_encoded}"
        mirror_url = f"{N5_BASE}learn/vocab/{form_encoded}/"

        desc = (gloss or form)[:155]

        breadcrumb = [
            ("Home", "../../../#/home"),
            ("Vocab", "../index.html"),
            (form, ""),
        ]
        footer_meta = ""
        if primary.get("section"):
            footer_meta = (
                f'<p>Section: <code>{_esc(primary.get("section"))}</code>'
                + (f' · POS: <code>{_esc(primary.get("pos") or "")}</code>' if primary.get("pos") else "")
                + "</p>"
            )

        html_text = _build_page(
            lang="en",
            title_tag=f"{form} ({reading}) — JLPT N5 Vocab{sense_hint}",
            h1=f"{form}" + (f" — {reading}" if reading != form else ""),
            description=desc,
            canonical_url=canonical,
            spa_url=canonical,
            body_html=body,
            depth=3,
            og_title=f"{form} — JLPT N5 Vocab",
            breadcrumb=breadcrumb,
            footer_meta_html=footer_meta,
        )

        # Path on disk uses raw form chars (modern filesystems handle Unicode).
        out_path = out_root / form / "index.html"
        if _write_if_changed(out_path, html_text):
            written += 1
        else:
            unchanged += 1

        sitemap_urls.append(mirror_url)

    # Vocab index, grouped by section
    by_section: dict[str, list[str]] = {}
    section_order: list[str] = []
    for form in form_order:
        primary = by_form[form][0]
        section = primary.get("section") or "Other"
        if section not in by_section:
            by_section[section] = []
            section_order.append(section)
        by_section[section].append(form)

    # Sort sections by the leading integer when present
    def _section_sort_key(s: str) -> tuple:
        m = re.match(r"^\s*(\d+)\s*[.\-]", s)
        return (0, int(m.group(1))) if m else (1, s)

    section_order_sorted = sorted(section_order, key=_section_sort_key)

    idx_parts: list[str] = []
    idx_parts.append(
        f'<p>Static index of all {len(form_order)} unique vocabulary forms ({len(entries)} sense entries) for JLPT N5. Forms with multiple senses share one page; the interactive version (drills, SRS, audio) is at the SPA route.</p>'
    )
    for section in section_order_sorted:
        idx_parts.append('<section class="index-section">')
        idx_parts.append(f'<h3>{_esc(section)}</h3>')
        for form in by_section[section]:
            primary = by_form[form][0]
            reading = primary.get("reading") or form
            gloss = (primary.get("gloss") or "")[:60]
            form_encoded = _encode_url_segment(form)
            label_reading = f" ({reading})" if reading != form else ""
            idx_parts.append(
                f'<a class="index-card" href="{form_encoded}/">'
                f'<span class="label" lang="ja">{_esc(form)}</span>'
                f'<span class="muted">{_esc(label_reading)}</span> — '
                f'<span class="gloss">{_esc(gloss)}</span>'
                f'</a>'
            )
        idx_parts.append("</section>")
    idx_body = "\n".join(idx_parts)

    idx_canonical = f"{N5_BASE}#/learn/vocab"
    idx_path = out_root / "index.html"
    idx_html = _build_page(
        lang="en",
        title_tag="N5 Vocabulary — All Words (static index)",
        h1="N5 Vocabulary — All Words",
        description=f"All {len(form_order)} unique N5 vocabulary forms ({len(entries)} sense entries), grouped by section.",
        canonical_url=idx_canonical,
        spa_url=idx_canonical,
        body_html=idx_body,
        depth=2,
        og_title="N5 Vocabulary — All Words",
        breadcrumb=[("Home", "../../#/home"), ("Vocab", "")],
        footer_meta_html=f"<p>{len(form_order)} forms / {len(entries)} sense entries indexed.</p>",
    )
    if _write_if_changed(idx_path, idx_html):
        written += 1
    else:
        unchanged += 1
    sitemap_urls.append(f"{N5_BASE}learn/vocab/")

    return written, unchanged, len(form_order)


# ----- Kanji renderer (Stage 3) -----


def _render_kanji_examples(examples: list) -> str:
    if not examples:
        return ""
    out = ["<h2>Compound examples</h2><ul>"]
    seen = set()
    for ex in examples:
        if not isinstance(ex, dict):
            continue
        form = ex.get("form") or ex.get("lemma") or ""
        reading = ex.get("reading") or ""
        gloss = ex.get("gloss") or ""
        if not form or form in seen:
            continue
        seen.add(form)
        bits = [f'<span lang="ja"><strong>{_esc(form)}</strong></span>']
        if reading:
            bits.append(f'<span class="muted" lang="ja">({_esc(reading)})</span>')
        if gloss:
            bits.append(f'— {_esc(gloss)}')
        out.append(f'<li>{" ".join(bits)}</li>')
    out.append("</ul>")
    return "\n".join(out)


def _render_kanji_sentences(sentences: list) -> str:
    if not sentences:
        return ""
    out = ["<h2>Example sentences</h2>"]
    for s in sentences:
        if not isinstance(s, dict):
            continue
        ja = s.get("ja") or ""
        en = s.get("translation_en") or s.get("en") or ""
        if not ja:
            continue
        out.append('<div class="ex">')
        out.append(f'<div class="ja" lang="ja"><span class="lang-tag">JA</span>{_esc(ja)}</div>')
        if en:
            out.append(f'<div class="en"><span class="lang-tag">EN</span>{_esc(en)}</div>')
        out.append("</div>")
    return "\n".join(out)


def build_kanji(sitemap_urls: list[str]) -> tuple[int, int, int]:
    """Stage 3 — kanji mirrors at /kanji/<glyph>/index.html.

    Returns (written, unchanged, total).
    """
    k = json.loads(KANJI.read_text(encoding="utf-8"))
    entries = k.get("entries", [])

    out_root = ROOT / "kanji"
    written = 0
    unchanged = 0

    for e in entries:
        glyph = e.get("glyph")
        if not glyph:
            continue
        meanings = e.get("meanings") or []
        meanings_hi = e.get("meanings_hi") or []
        on_yomi = e.get("on") or []
        kun_yomi = e.get("kun") or []
        stroke_count = e.get("stroke_count")
        primary_reading = e.get("primary_reading") or ""
        radical = e.get("radical") or {}
        mnemonic = e.get("mnemonic") or {}

        gloss_summary = ", ".join(meanings[:3]) if meanings else glyph
        desc = (f"Kanji {glyph} — " + gloss_summary)[:155]

        body_parts: list[str] = []
        # Glyph display block
        body_parts.append(
            f'<p style="text-align:center; font-size:5em; line-height:1; margin:0.5rem 0;" lang="ja">{_esc(glyph)}</p>'
        )
        if meanings:
            body_parts.append(
                f'<p style="text-align:center; font-size:1.1em;"><span class="lang-tag">EN</span>{_esc(", ".join(meanings))}</p>'
            )
        if meanings_hi:
            body_parts.append(
                f'<p style="text-align:center;" lang="hi"><span class="lang-tag">HI</span>{_esc(", ".join(meanings_hi))}</p>'
            )

        # Readings
        readings_parts: list[str] = []
        if on_yomi:
            readings_parts.append(
                f'<p><strong>On (音読み):</strong> <span lang="ja">{_esc("、 ".join(on_yomi))}</span></p>'
            )
        if kun_yomi:
            readings_parts.append(
                f'<p><strong>Kun (訓読み):</strong> <span lang="ja">{_esc("、 ".join(kun_yomi))}</span></p>'
            )
        if readings_parts:
            body_parts.append("<h2>Readings</h2>" + "\n".join(readings_parts))

        # Stroke count + radical
        meta_lines: list[str] = []
        if stroke_count is not None:
            meta_lines.append(f"Stroke count: <strong>{_esc(stroke_count)}</strong>")
        if isinstance(radical, dict):
            r_g = radical.get("glyph") or radical.get("form") or ""
            r_m = radical.get("meaning") or ""
            if r_g:
                meta_lines.append(
                    f'Radical: <span lang="ja">{_esc(r_g)}</span>'
                    + (f" ({_esc(r_m)})" if r_m else "")
                )
        if meta_lines:
            body_parts.append(
                "<h2>Stroke / radical</h2><p>" + " · ".join(meta_lines) + "</p>"
            )

        # Mnemonic (multi-locale dict)
        if isinstance(mnemonic, dict):
            mn_en = mnemonic.get("en") or ""
            mn_hi = mnemonic.get("hi") or ""
            if mn_en or mn_hi:
                body_parts.append("<h2>Mnemonic</h2>")
                if mn_en:
                    body_parts.append(f'<p><span class="lang-tag">EN</span>{_esc(mn_en)}</p>')
                if mn_hi:
                    body_parts.append(f'<p lang="hi"><span class="lang-tag">HI</span>{_esc(mn_hi)}</p>')

        # Examples / compounds
        body_parts.append(_render_kanji_examples(e.get("examples") or []))
        body_parts.append(_render_kanji_sentences(e.get("sentences") or []))

        # Lookalikes (visually similar kanji)
        lookalikes = e.get("lookalikes") or []
        if lookalikes:
            body_parts.append("<h2>Visually similar</h2>")
            for la in lookalikes[:6]:
                if not isinstance(la, dict):
                    continue
                la_g = la.get("glyph") or la.get("kanji") or ""
                la_note = la.get("note") or la.get("difference") or ""
                if la_g:
                    la_encoded = _encode_url_segment(la_g)
                    body_parts.append(
                        f'<p>'
                        f'<a href="../{la_encoded}/" style="font-size:1.4em;" lang="ja">{_esc(la_g)}</a>'
                        + (f" — {_esc(la_note)}" if la_note else "")
                        + "</p>"
                    )

        body = "\n".join(x for x in body_parts if x)
        glyph_encoded = _encode_url_segment(glyph)
        canonical = f"{N5_BASE}#/kanji/{glyph_encoded}"
        mirror_url = f"{N5_BASE}kanji/{glyph_encoded}/"

        title_tag = f"{glyph} — JLPT N5 Kanji ({gloss_summary})"
        breadcrumb = [("Home", "../../#/home"), ("Kanji", "../index.html"), (glyph, "")]
        footer_meta = ""
        if primary_reading:
            footer_meta = f'<p>Primary reading: <span lang="ja">{_esc(primary_reading)}</span></p>'

        html_text = _build_page(
            lang="en",
            title_tag=title_tag,
            h1=f"{glyph} — {gloss_summary}",
            description=desc,
            canonical_url=canonical,
            spa_url=canonical,
            body_html=body,
            depth=2,
            og_title=f"{glyph} — JLPT N5 Kanji",
            breadcrumb=breadcrumb,
            footer_meta_html=footer_meta,
        )

        out_path = out_root / glyph / "index.html"
        if _write_if_changed(out_path, html_text):
            written += 1
        else:
            unchanged += 1
        sitemap_urls.append(mirror_url)

    # Kanji index — order by lesson_order
    idx_items = sorted(entries, key=lambda x: (x.get("lesson_order") or 999, x.get("frequency_rank") or 999))
    idx_parts: list[str] = []
    idx_parts.append(
        f'<p>Static index of all {len(entries)} JLPT N5 kanji, in lesson order. Each entry links to a read-only mirror; the interactive version (stroke-order animation, drills, SRS) is at the SPA route.</p>'
    )
    idx_parts.append('<div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:0.5em; margin:1em 0;">')
    for e in idx_items:
        glyph = e.get("glyph")
        if not glyph:
            continue
        gloss_summary = ", ".join((e.get("meanings") or [])[:2])
        glyph_encoded = _encode_url_segment(glyph)
        idx_parts.append(
            f'<a class="index-card" href="{glyph_encoded}/" style="text-align:center;">'
            f'<span class="label" style="font-size:1.8em; display:block;" lang="ja">{_esc(glyph)}</span>'
            f'<span class="gloss">{_esc(gloss_summary)}</span>'
            f'</a>'
        )
    idx_parts.append("</div>")
    idx_body = "\n".join(idx_parts)

    idx_canonical = f"{N5_BASE}#/kanji"
    idx_path = out_root / "index.html"
    idx_html = _build_page(
        lang="en",
        title_tag="N5 Kanji — All 106 Characters (static index)",
        h1="N5 Kanji — All 106 Characters",
        description=f"All {len(entries)} JLPT N5 kanji in lesson order. Static index for non-JS clients.",
        canonical_url=idx_canonical,
        spa_url=idx_canonical,
        body_html=idx_body,
        depth=1,
        og_title="N5 Kanji — All 106 Characters",
        breadcrumb=[("Home", "../#/home"), ("Kanji", "")],
        footer_meta_html=f"<p>{len(entries)} kanji indexed.</p>",
    )
    if _write_if_changed(idx_path, idx_html):
        written += 1
    else:
        unchanged += 1
    sitemap_urls.append(f"{N5_BASE}kanji/")

    return written, unchanged, len(entries)


# ----- Reading renderer (Stage 4) -----


def _render_reading_questions(questions: list) -> str:
    if not questions:
        return ""
    out = ["<h2>Comprehension questions</h2>"]
    for i, q in enumerate(questions, 1):
        if not isinstance(q, dict):
            continue
        prompt_ja = q.get("prompt_ja") or q.get("prompt") or ""
        choices = q.get("choices") or []
        correct = q.get("correctAnswer") or ""
        expl_en = q.get("explanation_en") or ""
        expl_hi = q.get("explanation_hi") or ""
        out.append(f'<div class="ex">')
        out.append(f'<p><strong>Q{i}.</strong> <span lang="ja">{_esc(prompt_ja)}</span></p>')
        if choices:
            out.append("<ol>")
            for c in choices:
                marker = " ✓" if c == correct else ""
                cls = ' class="right"' if c == correct else ""
                out.append(f'<li{cls} lang="ja">{_esc(c)}{marker}</li>')
            out.append("</ol>")
        if expl_en:
            out.append(f'<p class="en"><span class="lang-tag">EN</span>{_esc(expl_en)}</p>')
        if expl_hi:
            out.append(f'<p lang="hi"><span class="lang-tag">HI</span>{_esc(expl_hi)}</p>')
        out.append("</div>")
    return "\n".join(out)


def build_reading(sitemap_urls: list[str]) -> tuple[int, int, int]:
    """Stage 4 — reading-passage mirrors at /reading/<id>/index.html.

    Returns (written, unchanged, total).
    """
    r = json.loads(READING.read_text(encoding="utf-8"))
    passages = r.get("passages", [])

    out_root = ROOT / "reading"
    written = 0
    unchanged = 0

    for p in passages:
        pid = p.get("id")
        if not pid:
            continue
        title_ja = p.get("title_ja") or pid
        topic = p.get("topic") or ""
        level = p.get("level") or ""
        mondai = p.get("mondai")
        ja_text = p.get("ja") or ""
        summary = p.get("summary") or ""
        summary_hi = p.get("summary_hi") or ""
        translation_natural = p.get("translation_natural") or ""
        translation_literal = p.get("translation_literal") or ""
        cultural_context = p.get("cultural_context") or ""

        body_parts: list[str] = []
        # Meta
        meta_bits: list[str] = []
        if topic:
            meta_bits.append(f"Topic: {_esc(topic)}")
        if level:
            meta_bits.append(f"Level: {_esc(level)}")
        if mondai is not None:
            meta_bits.append(f"Mondai: {_esc(mondai)}")
        if meta_bits:
            body_parts.append('<p class="muted">' + " · ".join(meta_bits) + "</p>")

        if summary:
            body_parts.append(f'<p><span class="lang-tag">EN</span>{_esc(summary)}</p>')
        if summary_hi:
            body_parts.append(f'<p lang="hi"><span class="lang-tag">HI</span>{_esc(summary_hi)}</p>')

        # Passage text
        body_parts.append("<h2>Passage</h2>")
        body_parts.append(f'<div class="ex" lang="ja" style="font-size:1.08em; line-height:1.85;">{_esc(ja_text)}</div>')

        # Translations
        if translation_natural:
            body_parts.append("<h2>Translation (natural)</h2>")
            body_parts.append(f'<p>{_esc(translation_natural)}</p>')
        if translation_literal and translation_literal != translation_natural:
            body_parts.append("<h3>Translation (literal)</h3>")
            body_parts.append(f'<p class="muted">{_esc(translation_literal)}</p>')

        # Cultural context
        if cultural_context:
            body_parts.append("<h2>Cultural context</h2>")
            body_parts.append(f'<p>{_esc(cultural_context)}</p>')

        # Questions
        body_parts.append(_render_reading_questions(p.get("questions") or []))

        # Vocab used (cross-links)
        vocab_used = p.get("vocab_used") or []
        if vocab_used:
            body_parts.append("<h2>Vocab used</h2><p>")
            links = []
            for vid in vocab_used[:30]:
                if not isinstance(vid, str):
                    continue
                # vid shape: "n5.vocab.<section>.<form>" — extract form (last segment)
                form = vid.rsplit(".", 1)[-1] if "." in vid else vid
                form_encoded = _encode_url_segment(form)
                links.append(
                    f'<a href="../../learn/vocab/{form_encoded}/" lang="ja">{_esc(form)}</a>'
                )
            body_parts.append(" · ".join(links))
            body_parts.append("</p>")

        # Kanji used (cross-links)
        kanji_used = p.get("kanji_used") or []
        if kanji_used:
            body_parts.append("<h2>Kanji used</h2><p>")
            links = []
            for g in kanji_used[:30]:
                if not isinstance(g, str):
                    continue
                g_encoded = _encode_url_segment(g)
                links.append(
                    f'<a href="../../kanji/{g_encoded}/" lang="ja" style="font-size:1.2em; margin-right:0.4em;">{_esc(g)}</a>'
                )
            body_parts.append(" ".join(links))
            body_parts.append("</p>")

        body = "\n".join(x for x in body_parts if x)

        canonical = f"{N5_BASE}#/reading/{_encode_url_segment(pid)}"
        mirror_url = f"{N5_BASE}reading/{_encode_url_segment(pid)}/"

        desc = (summary or topic or title_ja)[:155]

        breadcrumb = [("Home", "../../#/home"), ("Reading", "../index.html"), (title_ja, "")]
        footer_meta = f'<p>Passage ID: <code>{_esc(pid)}</code></p>'

        html_text = _build_page(
            lang="en",
            title_tag=f"{title_ja} — JLPT N5 Reading ({topic or 'Passage'})",
            h1=title_ja,
            description=desc,
            canonical_url=canonical,
            spa_url=canonical,
            body_html=body,
            depth=2,
            og_title=f"{title_ja} — JLPT N5 Reading",
            breadcrumb=breadcrumb,
            footer_meta_html=footer_meta,
        )

        out_path = out_root / pid / "index.html"
        if _write_if_changed(out_path, html_text):
            written += 1
        else:
            unchanged += 1
        sitemap_urls.append(mirror_url)

    # Reading index — group by mondai
    by_mondai: dict[int | str, list[dict]] = {}
    mondai_order: list[int | str] = []
    for p in passages:
        m = p.get("mondai") if p.get("mondai") is not None else "Other"
        if m not in by_mondai:
            by_mondai[m] = []
            mondai_order.append(m)
        by_mondai[m].append(p)
    mondai_order_sorted = sorted(mondai_order, key=lambda x: (isinstance(x, str), x))

    idx_parts: list[str] = []
    idx_parts.append(
        f'<p>Static index of all {len(passages)} JLPT N5 reading (dokkai) passages, grouped by mondai. Each links to a read-only mirror; the interactive version (audio playback, timed mode) is at the SPA route.</p>'
    )
    for m in mondai_order_sorted:
        idx_parts.append('<section class="index-section">')
        idx_parts.append(f'<h3>Mondai {_esc(m)}</h3>')
        for p in by_mondai[m]:
            pid = p.get("id")
            title = p.get("title_ja") or pid
            topic = p.get("topic") or ""
            idx_parts.append(
                f'<a class="index-card" href="{_esc(pid)}/">'
                f'<span class="label" lang="ja">{_esc(title)}</span> — '
                f'<span class="gloss">{_esc(topic)}</span>'
                f'</a>'
            )
        idx_parts.append("</section>")
    idx_body = "\n".join(idx_parts)

    idx_canonical = f"{N5_BASE}#/reading"
    idx_path = out_root / "index.html"
    idx_html = _build_page(
        lang="en",
        title_tag="N5 Reading — All Passages (static index)",
        h1="N5 Reading — All Passages",
        description=f"All {len(passages)} JLPT N5 reading passages (dokkai), grouped by mondai.",
        canonical_url=idx_canonical,
        spa_url=idx_canonical,
        body_html=idx_body,
        depth=1,
        og_title="N5 Reading — All Passages",
        breadcrumb=[("Home", "../#/home"), ("Reading", "")],
        footer_meta_html=f"<p>{len(passages)} passages indexed.</p>",
    )
    if _write_if_changed(idx_path, idx_html):
        written += 1
    else:
        unchanged += 1
    sitemap_urls.append(f"{N5_BASE}reading/")

    return written, unchanged, len(passages)


# ----- Listening renderer (Stage 5) -----


def _render_listening_questions(questions: list) -> str:
    """Listening items may have a `question` (single) or `questions` (list)."""
    if not questions:
        return ""
    out = ["<h2>Question</h2>"]
    for q in questions if isinstance(questions, list) else [questions]:
        if not isinstance(q, dict):
            continue
        prompt = q.get("prompt_ja") or q.get("prompt") or q.get("question") or ""
        choices = q.get("choices") or []
        correct = q.get("correctAnswer") or q.get("correct") or ""
        expl_en = q.get("explanation_en") or q.get("explanation") or ""
        expl_hi = q.get("explanation_hi") or ""
        if prompt:
            out.append(f'<p><span lang="ja">{_esc(prompt)}</span></p>')
        if choices:
            out.append("<ol>")
            for c in choices:
                marker = " ✓" if c == correct else ""
                cls = ' class="right"' if c == correct else ""
                out.append(f'<li{cls} lang="ja">{_esc(c)}{marker}</li>')
            out.append("</ol>")
        if expl_en:
            out.append(f'<p class="en"><span class="lang-tag">EN</span>{_esc(expl_en)}</p>')
        if expl_hi:
            out.append(f'<p lang="hi"><span class="lang-tag">HI</span>{_esc(expl_hi)}</p>')
    return "\n".join(out)


def build_listening(sitemap_urls: list[str]) -> tuple[int, int, int]:
    """Stage 5 — listening drill mirrors at /listening/<id>/index.html."""
    L = json.loads(LISTENING.read_text(encoding="utf-8"))
    items = L.get("items", []) or L.get("drills", []) or L.get("entries", [])

    out_root = ROOT / "listening"
    written = 0
    unchanged = 0

    for it in items:
        iid = it.get("id")
        if not iid:
            continue
        title_ja = it.get("title_ja") or it.get("title") or iid
        topic = it.get("topic") or it.get("format") or it.get("format_type") or ""
        mondai = it.get("mondai")
        level = it.get("level") or ""
        # listening.json uses `script_ja` for the transcript; reading.json uses `ja`.
        transcript = (
            it.get("script_ja")
            or it.get("transcript")
            or it.get("script")
            or it.get("ja")
            or ""
        )
        summary = it.get("summary") or it.get("description") or it.get("cultural_context") or ""
        summary_hi = it.get("summary_hi") or ""

        body_parts: list[str] = []
        meta_bits: list[str] = []
        fmt_bits = []
        for f in (it.get("format"), it.get("format_type")):
            if f and f not in fmt_bits:
                fmt_bits.append(f)
        if fmt_bits:
            meta_bits.append(f"Format: {_esc(' · '.join(fmt_bits))}")
        if topic and topic not in (it.get("format"), it.get("format_type")):
            meta_bits.append(f"Topic: {_esc(topic)}")
        if level:
            meta_bits.append(f"Level: {_esc(level)}")
        if mondai is not None:
            meta_bits.append(f"Mondai: {_esc(mondai)}")
        if meta_bits:
            body_parts.append('<p class="muted">' + " · ".join(meta_bits) + "</p>")

        if summary:
            body_parts.append(f'<p><span class="lang-tag">EN</span>{_esc(summary)}</p>')
        if summary_hi:
            body_parts.append(f'<p lang="hi"><span class="lang-tag">HI</span>{_esc(summary_hi)}</p>')

        # Audio: link only — static mirror won't auto-play.
        audio = it.get("audio") or ""
        if audio:
            body_parts.append(
                f'<p class="muted">Audio: <a href="../../{_esc(audio)}">{_esc(audio)}</a> (open in the SPA for embedded player + replay UI).</p>'
            )

        if transcript:
            body_parts.append("<h2>Transcript</h2>")
            body_parts.append(f'<div class="ex" lang="ja" style="font-size:1.05em; line-height:1.85;">{_esc(transcript)}</div>')

        # Question: listening.json uses INLINE prompt_ja/choices/correctAnswer
        # (single question per drill). reading.json uses a `questions` list.
        # Handle both shapes.
        qs = it.get("questions")
        if not qs:
            inline_q = {
                k: v for k, v in {
                    "prompt_ja": it.get("prompt_ja"),
                    "choices": it.get("choices"),
                    "correctAnswer": it.get("correctAnswer"),
                    "explanation_en": it.get("explanation_en"),
                    "explanation_hi": it.get("explanation_hi"),
                }.items() if v
            }
            qs = [inline_q] if inline_q else []
        body_parts.append(_render_listening_questions(qs))

        # Cross-links
        vocab_used = it.get("vocab_used") or []
        if vocab_used:
            body_parts.append("<h2>Vocab used</h2><p>")
            links = []
            for vid in vocab_used[:20]:
                if not isinstance(vid, str):
                    continue
                form = vid.rsplit(".", 1)[-1] if "." in vid else vid
                links.append(
                    f'<a href="../../learn/vocab/{_encode_url_segment(form)}/" lang="ja">{_esc(form)}</a>'
                )
            body_parts.append(" · ".join(links))
            body_parts.append("</p>")

        body = "\n".join(x for x in body_parts if x)

        canonical = f"{N5_BASE}#/listening/{_encode_url_segment(iid)}"
        mirror_url = f"{N5_BASE}listening/{_encode_url_segment(iid)}/"
        desc = (summary or topic or title_ja)[:155]
        breadcrumb = [("Home", "../../#/home"), ("Listening", "../index.html"), (title_ja, "")]
        footer_meta = f'<p>Item ID: <code>{_esc(iid)}</code></p>'

        html_text = _build_page(
            lang="en",
            title_tag=f"{title_ja} — JLPT N5 Listening",
            h1=title_ja,
            description=desc,
            canonical_url=canonical,
            spa_url=canonical,
            body_html=body,
            depth=2,
            og_title=f"{title_ja} — JLPT N5 Listening",
            breadcrumb=breadcrumb,
            footer_meta_html=footer_meta,
        )

        out_path = out_root / iid / "index.html"
        if _write_if_changed(out_path, html_text):
            written += 1
        else:
            unchanged += 1
        sitemap_urls.append(mirror_url)

    # Listening index — group by mondai
    by_mondai: dict[int | str, list[dict]] = {}
    mondai_order: list[int | str] = []
    for it in items:
        m = it.get("mondai") if it.get("mondai") is not None else "Other"
        if m not in by_mondai:
            by_mondai[m] = []
            mondai_order.append(m)
        by_mondai[m].append(it)
    mondai_order_sorted = sorted(mondai_order, key=lambda x: (isinstance(x, str), x))

    idx_parts: list[str] = []
    idx_parts.append(
        f'<p>Static index of all {len(items)} JLPT N5 listening drills, grouped by mondai. Audio playback requires the SPA route.</p>'
    )
    for m in mondai_order_sorted:
        idx_parts.append('<section class="index-section">')
        idx_parts.append(f'<h3>Mondai {_esc(m)}</h3>')
        for it in by_mondai[m]:
            iid = it.get("id")
            title = it.get("title_ja") or it.get("title") or iid
            topic = it.get("topic") or ""
            idx_parts.append(
                f'<a class="index-card" href="{_esc(iid)}/">'
                f'<span class="label" lang="ja">{_esc(title)}</span> — '
                f'<span class="gloss">{_esc(topic)}</span>'
                f'</a>'
            )
        idx_parts.append("</section>")
    idx_body = "\n".join(idx_parts)

    idx_canonical = f"{N5_BASE}#/listening"
    idx_path = out_root / "index.html"
    idx_html = _build_page(
        lang="en",
        title_tag="N5 Listening — All Drills (static index)",
        h1="N5 Listening — All Drills",
        description=f"All {len(items)} JLPT N5 listening drills, grouped by mondai.",
        canonical_url=idx_canonical,
        spa_url=idx_canonical,
        body_html=idx_body,
        depth=1,
        og_title="N5 Listening — All Drills",
        breadcrumb=[("Home", "../#/home"), ("Listening", "")],
        footer_meta_html=f"<p>{len(items)} drills indexed.</p>",
    )
    if _write_if_changed(idx_path, idx_html):
        written += 1
    else:
        unchanged += 1
    sitemap_urls.append(f"{N5_BASE}listening/")

    return written, unchanged, len(items)


# ----- Meta-route renderer (Stage 6) -----


def _markdown_to_html(text: str) -> str:
    """Minimal Markdown→HTML for static meta pages.

    Handles: headings (#..######), unordered lists (-, *), ordered lists (1.),
    paragraphs, inline links [text](url), inline code `..`, bold **..**,
    italic *..*, horizontal rules ---, and code fences ```.

    Doesn't try to be a full Markdown engine — just renders the meta-page
    .md files (CHANGELOG / PRIVACY / NOTICES) readably for non-JS clients.
    """
    lines = text.split("\n")
    out: list[str] = []
    in_code = False
    in_ul = False
    in_ol = False
    para_lines: list[str] = []

    def flush_para():
        nonlocal para_lines
        if para_lines:
            joined = " ".join(p.strip() for p in para_lines if p.strip())
            if joined:
                out.append(f"<p>{_render_inline(joined)}</p>")
            para_lines = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def _render_inline(s: str) -> str:
        # Escape first, then re-introduce markdown markers
        s = html.escape(s)
        # links [text](url)
        s = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
            s,
        )
        # inline code
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        # bold
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        # italics (single *)
        s = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
        return s

    for raw in lines:
        line = raw.rstrip()
        # Code fences
        if line.startswith("```"):
            flush_para()
            close_lists()
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append('<pre><code>')
                in_code = True
            continue
        if in_code:
            out.append(html.escape(raw))
            continue

        # Horizontal rule
        if line.strip() in ("---", "***", "___"):
            flush_para()
            close_lists()
            out.append("<hr>")
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            flush_para()
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{_render_inline(m.group(2))}</h{level}>")
            continue

        # Unordered list
        m = re.match(r"^[-*]\s+(.+)$", line)
        if m:
            flush_para()
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{_render_inline(m.group(1))}</li>")
            continue

        # Ordered list
        m = re.match(r"^\d+[.)]\s+(.+)$", line)
        if m:
            flush_para()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{_render_inline(m.group(1))}</li>")
            continue

        # Blank line ends paragraph + lists
        if not line.strip():
            flush_para()
            close_lists()
            continue

        # Otherwise accumulate paragraph text
        close_lists()
        para_lines.append(line)

    flush_para()
    close_lists()
    if in_code:
        out.append("</code></pre>")
    return "\n".join(out)


# Per-meta-route config:
#   slug = the on-disk dir name (also the URL segment)
#   spa_route = the SPA hash route (canonical target)
#   source_md = optional .md file in /N5/ to render as body
#   depth = directory depth from /N5/ (always 1 for these top-level routes)
#   title = HTML <title>
#   description = meta description
#   interactive_note = override for the meta-banner sub-text
#   stub_body_html = optional pre-rendered HTML for routes without an .md source
META_ROUTES: list[dict] = [
    {
        "slug": "home",
        "spa_route": "#/home",
        "source_md": "README.md",
        "title": "JLPT N5 Tutor — Home",
        "description": "Browser-based static web app for JLPT N5: grammar, vocab, kanji, reading, and listening. No server. No accounts. No third-party scripts.",
    },
    {
        "slug": "changelog",
        "spa_route": "#/changelog",
        "source_md": "CHANGELOG.md",
        "title": "Changelog — JLPT N5 Tutor",
        "description": "Version history and release notes for the JLPT N5 Tutor app.",
    },
    {
        "slug": "privacy",
        "spa_route": "#/privacy",
        "source_md": "PRIVACY.md",
        "title": "Privacy — JLPT N5 Tutor",
        "description": "Privacy posture for JLPT N5 Tutor: no telemetry, no third-party scripts, no accounts.",
    },
    {
        "slug": "notices",
        "spa_route": "#/notices",
        "source_md": "NOTICES.md",
        "title": "Attribution & Notices — JLPT N5 Tutor",
        "description": "Open-source dependencies, content attribution, and licence notices for JLPT N5 Tutor.",
    },
    {
        "slug": "feedback",
        "spa_route": "#/feedback",
        "title": "Feedback — JLPT N5 Tutor",
        "description": "Send feedback about JLPT N5 Tutor. The interactive feedback form is in the SPA route.",
        "interactive_note": " — the in-app feedback form requires JavaScript. You can also email feedback directly via the link below.",
        "stub_body_html": (
            "<p>The interactive feedback form lives in the SPA route at "
            '<a href="../#/feedback">/N5/#/feedback</a>. It collects no telemetry; '
            "submissions are stored on-device until you choose to send them.</p>"
            "<p>If JavaScript is disabled, you can still reach the maintainer:</p>"
            "<ul>"
            "<li>GitHub issues: <a href=\"https://github.com/gauravaccentureproducts/JLPTSuccess/issues\">github.com/gauravaccentureproducts/JLPTSuccess/issues</a></li>"
            "<li>Repository discussions: <a href=\"https://github.com/gauravaccentureproducts/JLPTSuccess/discussions\">github.com/gauravaccentureproducts/JLPTSuccess/discussions</a></li>"
            "</ul>"
        ),
    },
    {
        "slug": "settings",
        "spa_route": "#/settings",
        "title": "Settings — JLPT N5 Tutor",
        "description": "Settings for JLPT N5 Tutor: locale (EN / HI), audio voice, theme, accessibility.",
        "interactive_note": " — settings are stored in your browser's localStorage and require JavaScript to apply.",
        "stub_body_html": (
            "<p>Settings live in the SPA route at <a href=\"../#/settings\">/N5/#/settings</a>. They include:</p>"
            "<ul>"
            "<li>Locale: English / हिन्दी</li>"
            "<li>Audio voice (where multiple speakers are available)</li>"
            "<li>Theme (system / light / dark)</li>"
            "<li>Accessibility: font size, motion-reduction, contrast</li>"
            "<li>Reset (clears localStorage / SRS state)</li>"
            "</ul>"
            "<p class=\"muted\">Settings cannot be modified from this static mirror — JavaScript is required to read / write localStorage.</p>"
        ),
    },
    {
        "slug": "test",
        "spa_route": "#/test",
        "title": "Test mode — JLPT N5 Tutor",
        "description": "Interactive test mode for JLPT N5: timed drills, MCQ + sentence-order + cloze.",
        "interactive_note": " — test mode is interactive (timed, scored) and requires JavaScript.",
        "stub_body_html": (
            "<p>The interactive test mode lives at <a href=\"../#/test\">/N5/#/test</a>. It supports:</p>"
            "<ul>"
            "<li>Timed drills (configurable per-mondai time budget)</li>"
            "<li>Mixed question types: MCQ, sentence-order, cloze, listening</li>"
            "<li>Wrong-answer review (linked to <a href=\"../#/missed\">/N5/#/missed</a>)</li>"
            "<li>Full mock-test sittings (linked to <a href=\"../#/sitting\">/N5/#/sitting</a>)</li>"
            "</ul>"
            "<p>The content (questions, choices, explanations) is fully static in <code>data/questions.json</code> and <code>data/drills_auto.json</code> — only the test-running UI requires JavaScript.</p>"
        ),
    },
    {
        "slug": "sitting",
        "spa_route": "#/sitting",
        "title": "Mock-test sitting — JLPT N5 Tutor",
        "description": "Full mock-test sitting for JLPT N5: simulated 105-minute exam with mondai 1-5.",
        "interactive_note": " — mock-test sittings require JavaScript for the timer, score tracking, and pause/resume.",
        "stub_body_html": (
            "<p>Mock-test sittings live at <a href=\"../#/sitting\">/N5/#/sitting</a>. A sitting simulates the real JLPT N5 exam timing and mondai mix.</p>"
            "<p>For per-passage / per-drill content browsing without JavaScript, see "
            "<a href=\"../reading/\">/N5/reading/</a> and <a href=\"../listening/\">/N5/listening/</a>.</p>"
        ),
    },
    {
        "slug": "missed",
        "spa_route": "#/missed",
        "title": "Wrong-answer review — JLPT N5 Tutor",
        "description": "Browse and re-attempt questions you got wrong. Personal SRS history, stored on-device only.",
        "interactive_note": " — your missed-answer history is in localStorage and requires JavaScript to read.",
        "stub_body_html": (
            "<p>The wrong-answer-review surface at <a href=\"../#/missed\">/N5/#/missed</a> reads your personal history from browser localStorage.</p>"
            "<p>The history is stored on-device only — never sent to any server, never visible to anyone outside your browser. A static mirror cannot show it for that reason.</p>"
        ),
    },
    {
        "slug": "summary",
        "spa_route": "#/summary",
        "title": "Progress dashboard — JLPT N5 Tutor",
        "description": "Personal progress dashboard for JLPT N5: SRS state, recent attempts, mastery estimates.",
        "interactive_note": " — your progress data is in localStorage and requires JavaScript to read.",
        "stub_body_html": (
            "<p>The progress dashboard at <a href=\"../#/summary\">/N5/#/summary</a> reads your personal SRS state from browser localStorage.</p>"
            "<p>The data is stored on-device only — never sent to any server. A static mirror cannot show it for that reason.</p>"
            "<p>For raw content statistics (corpus counts, lesson coverage), see the <a href=\"../README.md\">README</a> and the per-surface indexes:</p>"
            "<ul>"
            "<li><a href=\"../learn/grammar/\">/N5/learn/grammar/</a> — 178 patterns</li>"
            "<li><a href=\"../learn/vocab/\">/N5/learn/vocab/</a> — 970 unique forms / 1009 sense entries</li>"
            "<li><a href=\"../kanji/\">/N5/kanji/</a> — 106 kanji</li>"
            "<li><a href=\"../reading/\">/N5/reading/</a> — 54 passages</li>"
            "<li><a href=\"../listening/\">/N5/listening/</a> — 50 drills</li>"
            "</ul>"
        ),
    },
]


def build_meta(sitemap_urls: list[str]) -> tuple[int, int, int]:
    """Stage 6 — meta-route mirrors at /N5/<slug>/index.html.

    Returns (written, unchanged, total).
    """
    written = 0
    unchanged = 0

    for cfg in META_ROUTES:
        slug = cfg["slug"]
        spa_route = cfg["spa_route"]
        body_html = ""
        if cfg.get("source_md"):
            md_path = ROOT / cfg["source_md"]
            if md_path.exists():
                md_text = md_path.read_text(encoding="utf-8")
                body_html = _markdown_to_html(md_text)
        if not body_html and cfg.get("stub_body_html"):
            body_html = cfg["stub_body_html"]
        if not body_html:
            body_html = f'<p class="muted">No static content available for this route. <a href="../{spa_route}">Open in the SPA</a>.</p>'

        # The HTML emitted by _markdown_to_html uses h1..h6; if it leads with
        # an h1, we don't want to duplicate it via the page-template h1. Strip
        # a leading h1 from body_html and use it as the page h1.
        h1_match = re.match(r"\s*<h1>(.*?)</h1>\s*", body_html, re.S)
        page_h1 = cfg.get("title", slug)
        if h1_match:
            page_h1 = re.sub(r"<.*?>", "", h1_match.group(1))
            body_html = body_html[h1_match.end():]

        canonical = N5_BASE + spa_route
        spa_url = canonical
        mirror_url = f"{N5_BASE}{slug}/"

        breadcrumb = [("Home", "../#/home"), (cfg.get("title", slug).split(" — ")[0], "")]

        html_text = _build_page(
            lang="en",
            title_tag=cfg.get("title", slug),
            h1=page_h1,
            description=cfg.get("description", ""),
            canonical_url=canonical,
            spa_url=spa_url,
            body_html=body_html,
            depth=1,
            og_title=cfg.get("title", slug),
            breadcrumb=breadcrumb,
            interactive_note=cfg.get(
                "interactive_note",
                " (the interactive version offers additional features that require JavaScript).",
            ),
        )

        out_path = ROOT / slug / "index.html"
        if _write_if_changed(out_path, html_text):
            written += 1
        else:
            unchanged += 1
        sitemap_urls.append(mirror_url)

    return written, unchanged, len(META_ROUTES)


# ----- Sitemap + robots.txt -----


def write_sitemap(sitemap_urls: list[str]) -> bool:
    """Write /N5/sitemap.xml from accumulated URLs. Returns True if file changed.

    2026-05-18 — LLM-002 (BUG-095) close-out wired the full per-entity
    sitemap (1589 URLs) via tools/build_llm_surfaces_2026_05_18.py.
    To avoid this script overwriting the larger sitemap when run with
    only a subset of stages (e.g. --stages meta), we merge in the
    existing sitemap rather than overwriting unconditionally. This
    preserves URLs from stages that weren't run in the current call.
    """
    # Sort + dedupe for deterministic output (idempotent re-runs).
    urls = set(sitemap_urls)

    # Merge in existing URLs from the on-disk sitemap, so a partial-stages
    # run doesn't truncate URLs from stages that weren't requested this call.
    sitemap_path = ROOT / "sitemap.xml"
    if sitemap_path.exists():
        import re as _re
        existing = sitemap_path.read_text(encoding="utf-8")
        for m in _re.finditer(r"<loc>(.*?)</loc>", existing):
            urls.add(m.group(1))

    urls = sorted(urls)
    # Browser-only branded view via sitemap.xsl (crawlers ignore the PI). Kept in
    # sync with tools/build_llm_surfaces_2026_05_18.py, the other sitemap writer.
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<?xml-stylesheet type="text/xsl" href="sitemap.xsl"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append(f"  <url><loc>{_esc(u)}</loc></url>")
    lines.append("</urlset>")
    lines.append("")
    content = "\n".join(lines)
    return _write_if_changed(sitemap_path, content)


def write_robots() -> bool:
    """Write /N5/robots.txt pointing at the sitemap."""
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {N5_BASE}sitemap.xml\n"
    )
    return _write_if_changed(ROOT / "robots.txt", content)


# ----- Entry point -----


STAGES_AVAILABLE = ["grammar", "vocab", "kanji", "reading", "listening", "meta"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Build static HTML mirrors for non-JS clients.")
    parser.add_argument(
        "--stages",
        default="all",
        help=f"Comma-separated stages to build (default: all). Available: {','.join(STAGES_AVAILABLE)},all",
    )
    args = parser.parse_args()

    stages = (
        STAGES_AVAILABLE
        if args.stages == "all"
        else [s.strip() for s in args.stages.split(",") if s.strip()]
    )

    sitemap_urls: list[str] = []

    summary: list[tuple[str, int, int, int]] = []

    if "grammar" in stages:
        w, u, t = build_grammar(sitemap_urls)
        summary.append(("grammar", w, u, t))
        print(f"Stage 1 (grammar): wrote {w}, unchanged {u}, total {t} patterns (+1 index).")

    if "vocab" in stages:
        w, u, t = build_vocab(sitemap_urls)
        summary.append(("vocab", w, u, t))
        print(f"Stage 2 (vocab): wrote {w}, unchanged {u}, total {t} unique forms (+1 index).")

    if "kanji" in stages:
        w, u, t = build_kanji(sitemap_urls)
        summary.append(("kanji", w, u, t))
        print(f"Stage 3 (kanji): wrote {w}, unchanged {u}, total {t} kanji (+1 index).")

    if "reading" in stages:
        w, u, t = build_reading(sitemap_urls)
        summary.append(("reading", w, u, t))
        print(f"Stage 4 (reading): wrote {w}, unchanged {u}, total {t} passages (+1 index).")

    if "listening" in stages:
        w, u, t = build_listening(sitemap_urls)
        summary.append(("listening", w, u, t))
        print(f"Stage 5 (listening): wrote {w}, unchanged {u}, total {t} drills (+1 index).")

    if "meta" in stages:
        w, u, t = build_meta(sitemap_urls)
        summary.append(("meta", w, u, t))
        print(f"Stage 6 (meta): wrote {w}, unchanged {u}, total {t} meta routes.")

    # Always rebuild sitemap + robots from the accumulated urls of the
    # stages we built. (When more stages are added, their URLs will be
    # included automatically.)
    if write_sitemap(sitemap_urls):
        print(f"Wrote sitemap.xml ({len(set(sitemap_urls))} URLs).")
    else:
        print(f"sitemap.xml unchanged ({len(set(sitemap_urls))} URLs).")
    if write_robots():
        print("Wrote robots.txt.")
    else:
        print("robots.txt unchanged.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
