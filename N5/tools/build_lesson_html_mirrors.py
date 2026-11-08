"""Build static HTML mirrors of each grammar pattern at /lessons/<id>.html.

User-reported BUG-001 (2026-05-16): Claude chat (and any non-JS fetcher)
cannot access SPA hash routes like
  https://gauravaccentureproducts.github.io/JLPTSuccess/N5/#/learn/n5-008
because GitHub Pages strips the `#` fragment server-side and returns
the unrendered SPA shell. Without JS execution, the lesson content is
invisible to:
  - LLM web-fetch tools (Claude API, GPT, etc.)
  - Search-engine crawlers (Googlebot DOES run JS but with budget;
    static HTML is faster + more reliable)
  - Read-only mirrors / archive.org snapshots
  - Users behind JS-disabled environments

This tool generates one crawlable HTML file per grammar pattern at
  N5/lessons/<pattern-id>.html
mirroring the on-screen content (pattern title, meaning_en, meaning_ja,
form_rules, examples, common_mistakes, contrasts). Each page carries:
  - <link rel="canonical" href="../#/learn/<id>"> — points back to the
    SPA route (the live, interactive version), so search engines
    deduplicate against the SPA.
  - <meta name="robots" content="index,follow">
  - Minimal CSS for legibility (no JS, no fancy fonts).

The mirrors are read-only. Users who land here from a crawler see a
"Open interactive version" link to the SPA route at the top.

This tool is idempotent — re-running on unchanged grammar.json produces
no diff. Re-run after any grammar.json content change.

Run from N5/:
  python tools/build_lesson_html_mirrors.py
"""
import json
import html
import sys
import io
from pathlib import Path

from emdash_normalize import normalize as normalize_emdash

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
GRAMMAR = ROOT / "data" / "grammar.json"
OUT_DIR = ROOT / "lessons"

# Minimal page chrome — no JS, no external CSS, no fonts beyond system.
# The CSS is inline to keep the mirror self-contained for crawlers.
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title} — JLPT N5 Grammar</title>
<meta name="description" content="{description}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="../#/learn/{id}">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Yu Gothic", sans-serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #222; }}
  a {{ color: #14452a; }}
  .meta {{ background: #f6f8f6; border-left: 3px solid #14452a; padding: 0.75rem 1rem; font-size: 0.92em; margin: 1.5rem 0; }}
  h1 {{ font-size: 1.6em; margin: 0.5rem 0; }}
  h2 {{ font-size: 1.15em; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; margin-top: 2rem; }}
  .lang-tag {{ display: inline-block; background: #eef; border: 1px solid #ccd; border-radius: 3px; padding: 0 0.4em; font-size: 0.8em; color: #336; margin-right: 0.5em; }}
  .ex {{ margin: 0.8em 0; }}
  .ex .ja {{ font-size: 1.05em; }}
  .ex .en {{ color: #555; font-size: 0.93em; margin-top: 0.2em; }}
  .wrong {{ color: #a33; }}
  .right {{ color: #1a5c38; }}
  footer {{ margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: 0.85em; color: #666; }}
</style>
</head>
<body>
<p class="meta">
  <strong>Static read-only mirror.</strong>
  <a href="../#/learn/{id}">Open the interactive version</a> (audio playback, furigana toggle, cross-references, etc. require JavaScript).
</p>
<h1>{title}</h1>
{body}
<footer>
  <p>Part of <a href="../">JLPT N5 Tutor</a>. Content licensed CC BY-SA 4.0 — see <a href="../CONTENT-LICENSE.md">CONTENT-LICENSE.md</a>.</p>
  <p>Pattern ID: <code>{id}</code> · Tier: <code>{tier}</code> · Category: <code>{category}</code></p>
</footer>
</body>
</html>
"""


def render_examples(examples):
    if not examples:
        return ""
    out = ["<h2>Examples</h2>"]
    for i, ex in enumerate(examples):
        if not isinstance(ex, dict):
            continue
        ja = ex.get("ja") or ""
        en = ex.get("en") or ex.get("translation_en") or ""
        if not ja:
            continue
        out.append('<div class="ex">')
        out.append(f'<div class="ja"><span class="lang-tag">JA</span>{html.escape(ja)}</div>')
        if en:
            out.append(f'<div class="en"><span class="lang-tag">EN</span>{html.escape(en)}</div>')
        out.append('</div>')
    return "\n".join(out)


def render_common_mistakes(cms):
    """Render common_mistakes.

    BUG-011 (2026-05-16): entries with kind='register_variant' are NOT
    grammar errors — both forms are valid; they differ in register /
    formality / pragmatic context. Render with neutral framing using
    label_a / label_b register tags. Other entries render as legacy
    wrong/right pair with ✗/✓ markers.
    """
    if not cms:
        return ""
    errors = [c for c in cms if isinstance(c, dict) and c.get("kind") != "register_variant"]
    variants = [c for c in cms if isinstance(c, dict) and c.get("kind") == "register_variant"]
    out = []

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
                out.append(f'<div class="wrong">✗ {html.escape(wrong)}</div>')
            if right:
                out.append(f'<div class="right">✓ {html.escape(right)}</div>')
            if why:
                out.append(f'<div class="en">{html.escape(why)}</div>')
            out.append('</div>')

    if variants:
        out.append("<h2>Register variants — both forms are correct</h2>")
        for cm in variants:
            # BUG-013: register-variant entries now use form_a/form_b
            # keys, not wrong/right. Legacy fallback for safety.
            form_a = cm.get("form_a") or cm.get("wrong") or ""
            form_b = cm.get("form_b") or cm.get("right") or ""
            label_a = cm.get("label_a") or "Form A"
            label_b = cm.get("label_b") or "Form B"
            why = cm.get("why") or ""
            if not (form_a or form_b):
                continue
            out.append('<div class="ex">')
            if form_a:
                out.append(f'<div><strong>[{html.escape(label_a)}]</strong> {html.escape(form_a)}</div>')
            if form_b:
                out.append(f'<div><strong>[{html.escape(label_b)}]</strong> {html.escape(form_b)}</div>')
            if why:
                out.append(f'<div class="en">{html.escape(why)}</div>')
            out.append('</div>')

    return "\n".join(out)


def render_wcp(wcps):
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
            out.append(f'<div class="wrong">✗ {html.escape(wrong)}</div>')
        if correct:
            out.append(f'<div class="right">✓ {html.escape(correct)}</div>')
        if why:
            out.append(f'<div class="en">{html.escape(why)}</div>')
        out.append('</div>')
    return "\n".join(out)


def render_pattern(p):
    pid = p["id"]
    title = p.get("pattern") or pid
    meaning_en = p.get("meaning_en") or ""
    meaning_ja = p.get("meaning_ja") or ""
    explanation_en = p.get("explanation_en") or ""
    tier = p.get("tier") or ""
    category = p.get("category") or ""

    desc = (meaning_en or title)[:155]

    parts = []
    if meaning_en:
        parts.append(f'<p><span class="lang-tag">EN</span>{html.escape(meaning_en)}</p>')
    if meaning_ja:
        parts.append(f'<p><span class="lang-tag">JA</span>{html.escape(meaning_ja)}</p>')
    if explanation_en and explanation_en != meaning_en:
        parts.append(f'<h2>Explanation</h2><p>{html.escape(explanation_en)}</p>')

    fr = p.get("form_rules") or {}
    if isinstance(fr, dict) and fr:
        atts = fr.get("attaches_to") or []
        if atts:
            parts.append(f'<h2>Attaches to</h2><p>{html.escape(", ".join(atts))}</p>')

    parts.append(render_examples(p.get("examples") or []))
    parts.append(render_common_mistakes(p.get("common_mistakes") or []))
    parts.append(render_wcp(p.get("wrong_corrected_pair") or []))

    body = "\n".join(x for x in parts if x)
    return PAGE_TEMPLATE.format(
        id=pid,
        title=html.escape(title),
        description=html.escape(desc),
        body=body,
        tier=html.escape(tier),
        category=html.escape(category),
    )


def main() -> int:
    if not GRAMMAR.exists():
        print(f"ERROR: missing {GRAMMAR}")
        return 1
    g = json.loads(GRAMMAR.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    written = 0
    unchanged = 0
    for p in g.get("patterns", []):
        pid = p.get("id")
        if not pid:
            continue
        out = OUT_DIR / f"{pid}.html"
        # No em dashes on the site (owner decision 2026-11-08): templates still
        # hold some, so every page passes through the shared normalizer.
        new_content = normalize_emdash(render_pattern(p), "html")
        if out.exists() and out.read_text(encoding="utf-8") == new_content:
            unchanged += 1
            continue
        out.write_text(new_content, encoding="utf-8")
        written += 1

    # Build an index page for the lesson mirrors (helps crawlers find them).
    idx_items = sorted(g.get("patterns", []), key=lambda x: (x.get("categoryOrder", 999), x.get("patternOrder", 999)))
    idx_links = []
    current_cat = None
    for p in idx_items:
        cat = p.get("category") or "Other"
        if cat != current_cat:
            idx_links.append(f'<h2>{html.escape(cat)}</h2>')
            current_cat = cat
        title = p.get("pattern") or p["id"]
        idx_links.append(f'<p><a href="{p["id"]}.html">{html.escape(title)}</a> — <span class="en">{html.escape((p.get("meaning_en") or "")[:60])}</span></p>')

    index_html = PAGE_TEMPLATE.format(
        id="index",
        title="All N5 grammar patterns (static index)",
        description="Static index of all 178 N5 grammar patterns. Each entry links to a read-only mirror; the interactive version is at the SPA route.",
        body="\n".join(idx_links),
        tier="",
        category="index",
    ).replace('<link rel="canonical" href="../#/learn/index">', '<link rel="canonical" href="../#/learn/grammar">')
    index_html = normalize_emdash(index_html, "html")

    idx_out = OUT_DIR / "index.html"
    if not idx_out.exists() or idx_out.read_text(encoding="utf-8") != index_html:
        idx_out.write_text(index_html, encoding="utf-8")
        print(f"Wrote {idx_out}")

    print(f"Lesson mirrors: {written} written, {unchanged} unchanged. Total: {len(g.get('patterns', []))} patterns.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
