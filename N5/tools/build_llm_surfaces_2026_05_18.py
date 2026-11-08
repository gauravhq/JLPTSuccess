"""
build_llm_surfaces_2026_05_18.py
================================

Closes LLM-001..005 (BUG-094, BUG-095, BUG-096, BUG-097, BUG-105).

The N5 SPA shell is hash-routed (#/learn/grammar/n5-008 etc.). LLM web
crawlers (Claude, GPT, Perplexity, Google AI Overviews, Googlebot)
cannot follow fragments and therefore cannot read per-entity content.

Static mirrors for grammar / vocab / kanji / reading / listening
already exist from prior commits (1370 files). What was missing as of
2026-05-18:

  - papers/ static mirrors (28 paper packs + 1 index)
  - data/index.json corpus-discovery file
  - llms.txt (root + N5/)
  - sitemap.xml regeneration (was 10 meta routes; needs 1400+ URLs)
  - 7 LLM-005-style thin summary pages
  - noscript block expansion in N5/index.html + stale-count fix
  - root level-picker dual-link update

This script produces all of the above.
"""
import sys, io, json, os, glob, datetime
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emdash_normalize import mode_for as mode_for_emdash  # noqa: E402
from emdash_normalize import normalize as normalize_emdash  # noqa: E402

REPO_N5 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(REPO_N5)  # JLPTSuccess/
TODAY = "2026-05-18"

BASE_URL = "https://gauravaccentureproducts.github.io/JLPTSuccess"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def write_atomically(path, content):
    # No em dashes on the site (owner decision 2026-11-08): some templates in
    # this file still contain them, so every surface passes through the
    # shared normalizer before it is written.
    content = normalize_emdash(content, mode_for_emdash(path))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, path)

def load_data():
    """Load all corpora and version.json."""
    out = {}
    out["grammar"] = json.load(open(os.path.join(REPO_N5, "data", "grammar.json"), encoding="utf-8"))
    out["vocab"] = json.load(open(os.path.join(REPO_N5, "data", "vocab.json"), encoding="utf-8"))
    out["kanji"] = json.load(open(os.path.join(REPO_N5, "data", "kanji.json"), encoding="utf-8"))
    out["reading"] = json.load(open(os.path.join(REPO_N5, "data", "reading.json"), encoding="utf-8"))
    out["listening"] = json.load(open(os.path.join(REPO_N5, "data", "listening.json"), encoding="utf-8"))
    out["version"] = json.load(open(os.path.join(REPO_N5, "data", "version.json"), encoding="utf-8"))
    out["papers_manifest"] = json.load(open(os.path.join(REPO_N5, "data", "papers", "manifest.json"), encoding="utf-8"))
    return out

# ---------------------------------------------------------------------------
# Stage 1: Papers static mirrors (LLM-001 paper coverage)
# ---------------------------------------------------------------------------
def html_escape(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&#39;"))

def render_paper_mirror(paper, category_label, paper_id):
    """Render one paper pack as a static HTML mirror page."""
    name = paper.get("name", paper_id)
    name_ja = paper.get("name_ja", "")
    qcount = paper.get("questionCount", 0)
    questions = paper.get("questions", [])
    canonical = f"{BASE_URL}/N5/#/test/papers/{paper_id}"
    static_url = f"{BASE_URL}/N5/papers/{paper_id}/"
    desc = f"JLPT N5 {category_label} mock-test paper pack {paper.get('paperNumber','?')} — {qcount} questions, static page for crawler / no-JS access."

    parts = []
    parts.append(f'<!DOCTYPE html>\n<html lang="en">\n<head>\n')
    parts.append(f'<meta charset="utf-8">\n')
    parts.append(f'<meta name="viewport" content="width=device-width, initial-scale=1">\n')
    parts.append(f'<title>{html_escape(name)} — JLPT N5 (static mirror)</title>\n')
    parts.append(f'<meta name="description" content="{html_escape(desc)}">\n')
    parts.append(f'<meta name="robots" content="index,follow">\n')
    parts.append(f'<link rel="canonical" href="{canonical}">\n')
    parts.append(f'<meta property="og:type" content="article">\n')
    parts.append(f'<meta property="og:url" content="{static_url}">\n')
    parts.append(f'<meta property="og:title" content="{html_escape(name)}">\n')
    parts.append(f'<meta property="og:description" content="{html_escape(desc)}">\n')
    parts.append(f'<meta property="og:site_name" content="JLPT N5 Tutor">\n')
    parts.append('<style>\n')
    parts.append('  :root { --green:#14452a; --green-soft:#1a5c38; --bg:#fff; --bg-soft:#f6f8f6; --text:#1a1a1a; --muted:#555; --border:#ddd; }\n')
    parts.append('  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans", "Yu Gothic", sans-serif; max-width: 760px; margin: 0 auto; padding: 1rem; line-height: 1.6; color: var(--text); background: var(--bg); }\n')
    parts.append('  a { color: var(--green); }\n')
    parts.append('  h1 { font-size: 1.6em; margin: 0.5rem 0; }\n')
    parts.append('  h2 { font-size: 1.18em; border-bottom: 1px solid var(--border); padding-bottom: 0.3em; margin-top: 1.6rem; }\n')
    parts.append('  .meta-banner { background: var(--bg-soft); border-left: 3px solid var(--green); padding: 0.75rem 1rem; font-size: 0.92em; margin: 0 0 1.5rem 0; }\n')
    parts.append('  .question { margin: 1em 0; padding: 0.75em; background: #fafbfa; border-left: 2px solid #e4ebe5; border-radius: 0 4px 4px 0; }\n')
    parts.append('  .stem { font-size: 1.05em; }\n')
    parts.append('  .choices { margin: 0.4em 0 0 1.2em; padding-left: 0; }\n')
    parts.append('  .choices li { margin: 0.2em 0; list-style: none; }\n')
    parts.append('  .rationale { color: var(--muted); font-size: 0.92em; margin-top: 0.4em; }\n')
    parts.append('  .muted { color: var(--muted); font-size: 0.92em; }\n')
    parts.append('  .correct-marker { color: var(--green-soft); font-weight: 600; }\n')
    parts.append('</style>\n</head>\n<body>\n')

    parts.append('<div class="meta-banner">\n')
    parts.append(f'  <strong>Static mirror</strong> — this page exists so search engines and LLM crawlers can read the paper without running JavaScript.\n')
    parts.append(f'  The interactive timed-test version is at <a href="../../#/test/papers/{paper_id}">the SPA</a>.\n')
    parts.append('</div>\n')

    parts.append(f'<h1>{html_escape(name)}</h1>\n')
    if name_ja:
        parts.append(f'<p class="muted">{html_escape(name_ja)}</p>\n')
    parts.append(f'<p>{html_escape(desc)}</p>\n')

    parts.append('<h2>Questions</h2>\n')
    for q in questions:
        qid = q.get("id", "?")
        stem = q.get("stem_html", q.get("stem", ""))
        choices = q.get("choices", [])
        correct_idx = q.get("correctIndex", -1)
        rationale = q.get("rationale", "")
        mondai = q.get("mondai", "")
        parts.append('<div class="question">\n')
        parts.append(f'  <div class="muted">{html_escape(qid)} (Mondai {mondai})</div>\n')
        parts.append(f'  <div class="stem">{stem}</div>\n')
        if choices:
            parts.append('  <ol class="choices">\n')
            for i, ch in enumerate(choices):
                marker = ' <span class="correct-marker">✓</span>' if i == correct_idx else ''
                parts.append(f'    <li>{i+1}. {ch}{marker}</li>\n')
            parts.append('  </ol>\n')
        if rationale:
            parts.append(f'  <div class="rationale"><strong>Rationale:</strong> {html_escape(rationale)}</div>\n')
        parts.append('</div>\n')

    parts.append('<hr>\n')
    parts.append(f'<p class="muted">↩ <a href="../">All paper packs</a> · <a href="../../">JLPT N5 home</a></p>\n')
    parts.append('</body>\n</html>\n')
    return "".join(parts)

def render_papers_index(manifest):
    """Render the papers/index.html landing page."""
    total_papers = manifest.get("totalPapers", 28)
    total_questions = manifest.get("totalQuestions", 402)
    parts = ['<!DOCTYPE html>\n<html lang="en">\n<head>\n']
    parts.append('<meta charset="utf-8">\n')
    parts.append('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
    parts.append('<title>N5 Mock Test Papers — JLPT N5 (static mirror)</title>\n')
    parts.append(f'<meta name="description" content="All {total_papers} N5 mock-test paper packs ({total_questions} questions) across 4 categories. Static index for crawlers and no-JS clients.">\n')
    parts.append('<meta name="robots" content="index,follow">\n')
    parts.append(f'<link rel="canonical" href="{BASE_URL}/N5/#/test">\n')
    parts.append('<style>body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;max-width:760px;margin:0 auto;padding:1rem;line-height:1.6;color:#1a1a1a}a{color:#14452a}h1{font-size:1.6em}h2{font-size:1.18em;border-bottom:1px solid #ddd;padding-bottom:.3em;margin-top:1.6rem}.meta-banner{background:#f6f8f6;border-left:3px solid #14452a;padding:.75rem 1rem;font-size:.92em;margin-bottom:1.5rem}.card{display:block;padding:.5em .7em;border:1px solid #e0e6e0;border-radius:4px;margin:.3em 0;text-decoration:none;color:inherit}.muted{color:#555;font-size:.92em}</style>\n')
    parts.append('</head>\n<body>\n')
    parts.append('<div class="meta-banner"><strong>Static mirror</strong> — interactive timed-test version at <a href="../#/test">the SPA</a>.</div>\n')
    cat_count = len(manifest.get("categories", []))
    parts.append(f'<h1>N5 Mock Test Papers</h1>\n')
    parts.append(f'<p>{total_papers} paper packs · {total_questions} questions · {cat_count} categories.</p>\n')

    for cat in manifest.get("categories", []):
        label = cat.get("label", "?")
        label_ja = cat.get("label_ja", "")
        desc = cat.get("description", "")
        cid = cat.get("id", "")
        parts.append(f'<h2>{html_escape(label)} ({html_escape(label_ja)})</h2>\n')
        parts.append(f'<p class="muted">{html_escape(desc)}</p>\n')
        for n in range(1, 8):  # 7 papers per category
            paper_id = f"{cid}-{n}"
            parts.append(f'<a class="card" href="{paper_id}/"><strong>Paper {n}</strong> — {html_escape(label)} (15 questions)</a>\n')

    parts.append('<hr><p class="muted">↩ <a href="../">JLPT N5 home</a></p>\n')
    parts.append('</body>\n</html>\n')
    return "".join(parts)

def stage_papers_mirrors(data):
    """Emit papers/<id>/index.html + papers/index.html."""
    manifest = data["papers_manifest"]
    written = 0

    # Per-paper-pack mirrors
    paper_files = sorted(glob.glob(os.path.join(REPO_N5, "data", "papers", "*", "*.json")))
    for fp in paper_files:
        if "manifest" in os.path.basename(fp):
            continue
        paper = json.load(open(fp, encoding="utf-8"))
        paper_id = paper.get("id")
        category = os.path.basename(os.path.dirname(fp))  # bunpou / dokkai / goi / moji
        cat_label = next((c["label"] for c in manifest.get("categories",[]) if c["id"] == category), category)
        html = render_paper_mirror(paper, cat_label, paper_id)
        out_path = os.path.join(REPO_N5, "papers", paper_id, "index.html")
        write_atomically(out_path, html)
        written += 1

    # Index page
    index_html = render_papers_index(manifest)
    write_atomically(os.path.join(REPO_N5, "papers", "index.html"), index_html)
    written += 1

    print(f"  papers mirrors: {written} files (28 paper packs + 1 index)")
    return written

# ---------------------------------------------------------------------------
# Stage 2: data/index.json (LLM-003)
# ---------------------------------------------------------------------------
def stage_data_index(data):
    """Emit data/index.json — corpus-discovery file enumerating every data
    file with URL, size, content-type, schema-version, description."""
    version = data["version"]
    counts = version.get("counts", {})

    entries = []
    DATA_DIR = os.path.join(REPO_N5, "data")
    file_specs = [
        ("grammar.json", "application/json", "N5 grammar patterns (178 entries; particles, verb conjugations, adjectives, conditionals)", counts.get("grammar")),
        ("vocab.json", "application/json", f"N5 vocabulary ({counts.get('vocab','?')} entries; pitch-accent, PoS, frequency, collocations)", counts.get("vocab")),
        ("kanji.json", "application/json", f"N5 kanji ({counts.get('kanji','?')} entries; on/kun readings, stroke order, vocab examples)", counts.get("kanji")),
        ("reading.json", "application/json", f"N5 dokkai reading passages ({counts.get('reading','?')} entries; with vocab + grammar footnotes)", counts.get("reading")),
        ("listening.json", "application/json", f"N5 choukai listening drills ({counts.get('listening','?')} entries; VOICEVOX audio, line-level seek)", counts.get("listening")),
        ("questions.json", "application/json", f"N5 drill / paraphrase / kanji-writing questions ({counts.get('questions','?')} entries)", counts.get("questions")),
        ("authentic.json", "application/json", "Authentic source-citation index for grammar patterns", None),
        ("drills_auto.json", "application/json", "Auto-generated mixed-skill drill sets", None),
        ("audio_manifest.json", "application/json", "Audio asset manifest (paths, durations, speaker assignment)", None),
        ("version.json", "application/json", "Build version, cacheVersion, builtAt, content-count claims", None),
        ("papers/manifest.json", "application/json", f"Mock paper test manifest ({counts.get('papers','?')} papers, {counts.get('paperQuestions','?')} questions)", None),
    ]

    def _lf_normalized_size(path: str) -> int:
        """Return byte-size of the file with CRLF normalized to LF.
        Matches git's storage representation (LF) so the recorded size
        agrees with what CI sees on Linux — even when the script runs
        on Windows where the working-tree has CRLF endings (JA-125
        guard fix, 2026-05-21)."""
        with open(path, "rb") as fh:
            data = fh.read()
        return len(data.replace(b"\r\n", b"\n"))

    for rel, content_type, desc, count in file_specs:
        full = os.path.join(DATA_DIR, rel.replace("/", os.sep))
        if not os.path.exists(full):
            continue
        size = _lf_normalized_size(full)
        entries.append({
            "path": f"data/{rel}",
            "url": f"{BASE_URL}/N5/data/{rel}",
            "content_type": content_type,
            "size_bytes": size,
            "schema_version": "1.0",
            "description": desc,
            "item_count": count,
        })

    # Papers per-category files
    paper_files = sorted(glob.glob(os.path.join(DATA_DIR, "papers", "*", "*.json")))
    for fp in paper_files:
        if "manifest" in os.path.basename(fp):
            continue
        rel = os.path.relpath(fp, DATA_DIR).replace(os.sep, "/")
        size = _lf_normalized_size(fp)
        try:
            d = json.load(open(fp, encoding="utf-8"))
            qcount = d.get("questionCount", 0)
            name = d.get("name", os.path.basename(fp))
        except Exception:
            qcount = 0
            name = os.path.basename(fp)
        entries.append({
            "path": f"data/{rel}",
            "url": f"{BASE_URL}/N5/data/{rel}",
            "content_type": "application/json",
            "size_bytes": size,
            "schema_version": "1.0",
            "description": f"{name} — {qcount} questions",
            "item_count": qcount,
        })

    index = {
        "_meta": {
            "schema_version": "1.0",
            "generator": "tools/build_llm_surfaces_2026_05_18.py",
            # `generated_at` removed 2026-05-21 — caused regen-llm-surfaces
            # CI to fail on every push because the timestamp updates on
            # every regen even when no content changed. Same noise-pattern
            # as the per-entry `last_modified` field that was dropped the
            # same day. The build-tag is captured in `version` below from
            # data/version.json.
            "license_code": "MIT",
            "license_content": "CC-BY-SA-4.0",
            "level": "N5",
            "site": "JLPTSuccess",
            "purpose": "Corpus-discovery index for programmatic / LLM access. Every entry here is a publicly-served static file. No CORS or auth required; any client can fetch.",
            "version": version.get("version", "?"),
        },
        "files": entries,
        "totals": {
            "files": len(entries),
            "total_bytes": sum(e["size_bytes"] for e in entries),
            "counts": counts,
        },
    }

    out_path = os.path.join(DATA_DIR, "index.json")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(normalize_emdash(json.dumps(index, ensure_ascii=False, indent=2), "json"))
    print(f"  data/index.json: {len(entries)} entries · {index['totals']['total_bytes']:,} bytes total")
    return len(entries)

# ---------------------------------------------------------------------------
# Stage 3: llms.txt (LLM-005)
# ---------------------------------------------------------------------------
def stage_llms_txt(data):
    """Emit /JLPTSuccess/llms.txt (root) + /JLPTSuccess/N5/llms.txt."""
    counts = data["version"].get("counts", {})
    text_root = f"""# JLPTSuccess
> Free, on-device, privacy-preserving JLPT (Japanese Language Proficiency Test) study material.
> Bilingual (English + Hindi). No login. No tracking. Works offline.
> Open source: https://github.com/gauravaccentureproducts/JLPTSuccess

## Levels
- **N5** (live): {BASE_URL}/N5/  ·  static syllabus summary: {BASE_URL}/N5/home.html
- N4..N1: planned (work paused)

## What is JLPTSuccess?
A hash-routed Progressive Web App that bundles a complete N5 study corpus:
grammar (178 patterns), vocabulary ({counts.get('vocab','?')} entries), kanji
({counts.get('kanji','?')} characters), reading ({counts.get('reading','?')}
dokkai passages), listening ({counts.get('listening','?')} drills with
VOICEVOX audio), and mock papers ({counts.get('papers','?')} packs,
{counts.get('paperQuestions','?')} questions). Content licensed CC BY-SA 4.0;
code MIT.

## How to read this site programmatically
- **Static per-entity HTML mirrors** at `/N5/learn/grammar/<id>/`,
  `/N5/learn/vocab/<form>/`, `/N5/learn/kanji/<glyph>/`, `/N5/reading/<id>/`,
  `/N5/listening/<id>/`, `/N5/papers/<paper-id>/`. Server-rendered HTML; no
  JS required.
- **Static summary pages**: `/N5/home.html`, `/N5/grammar.html`,
  `/N5/vocabulary.html`, `/N5/kanji.html`, `/N5/reading.html`,
  `/N5/listening.html`, `/N5/test.html`.
- **Corpus JSON** at `/N5/data/*.json`. Catalog: `/N5/data/index.json`.
- **Sitemap**: `/N5/sitemap.xml` (≥1400 URLs).
- **Robots**: `/N5/robots.txt`.

## Canonical URLs
The SPA hash routes (e.g. `/N5/#/learn/grammar/n5-008`) and the
path-routed static mirrors (e.g. `/N5/learn/grammar/n5-008/`) deliver
the same content. The hash-route is canonical for human users (linked
via `<link rel="canonical">` from each mirror); the static path is
canonical for crawler / LLM access.

## License
- Code: MIT.
- Content (corpus): CC BY-SA 4.0.
- See {BASE_URL}/N5/CONTENT-LICENSE.md and {BASE_URL}/N5/NOTICES.md.

## Contact
GitHub Issues: https://github.com/gauravaccentureproducts/JLPTSuccess/issues
"""
    write_atomically(os.path.join(REPO_ROOT, "llms.txt"), text_root)
    # Also emit at N5/ root for crawlers that probe per-subdirectory
    text_n5 = text_root.replace("# JLPTSuccess\n", "# JLPTSuccess — N5\n")
    write_atomically(os.path.join(REPO_N5, "llms.txt"), text_n5)
    print(f"  llms.txt: written at /JLPTSuccess/llms.txt + /JLPTSuccess/N5/llms.txt")

# ---------------------------------------------------------------------------
# Stage 4: 7 LLM-005 thin summary pages
# ---------------------------------------------------------------------------
# Brand chrome so the static summary pages match the rest of the site. The
# header mirrors the one tools/inject_app_header_into_mirrors_2026_05_27.py
# injects into the per-entity mirrors (those run over index.html only, so the
# *.html summary pages were never branded). Absolute URLs + no JS so it stays
# crawler-readable at any depth.
SUMMARY_CSS_LINK = '<link rel="stylesheet" href="/JLPTSuccess/N5/css/main.min.css?v=1.17.30">'
SUMMARY_BRAND_HEADER = """<header class="app-header" role="banner">
<div class="brand"><h1><a href="/JLPTSuccess/" class="brand-link" aria-label="JLPTSuccess home, choose a level">
<svg class="brand-mark" viewBox="0 0 100 57" role="img" aria-hidden="true" focusable="false"><g fill="currentColor">
<rect x="1" y="0" width="98" height="9" rx="4.5"/><rect x="1" y="12" width="84" height="9" rx="4.5"/>
<rect x="1" y="24" width="64" height="9" rx="4.5"/><rect x="1" y="36" width="44" height="9" rx="4.5"/>
<rect x="1" y="48" width="22" height="9" rx="4.5"/></g></svg></a>
<a href="/JLPTSuccess/N5/" class="brand-link" aria-label="N5 home"><span class="brand-wordmark">N5</span></a></h1></div>
<nav class="primary-nav" aria-label="Primary">
<a href="/JLPTSuccess/N5/learn/grammar/">Grammar</a>
<a href="/JLPTSuccess/N5/learn/vocab/">Vocabulary</a>
<a href="/JLPTSuccess/N5/kanji/">Kanji</a>
<a href="/JLPTSuccess/N5/reading/">Reading</a>
<a href="/JLPTSuccess/N5/listening/">Listening</a>
<a href="/JLPTSuccess/N5/test/">Test</a>
<a href="/JLPTSuccess/N5/missed/">Missed</a>
<a href="/JLPTSuccess/N5/summary/">Progress</a>
</nav>
</header>"""

# Same site footer the inject script adds to the per-entity mirrors, so the
# summary pages carry the identical footer menu. Keep in sync with FOOTER_HTML
# in tools/inject_app_header_into_mirrors_2026_05_27.py.
SUMMARY_PAGE_FOOTER = """<footer class="app-footer" role="contentinfo">
<nav class="footer-nav" aria-label="Footer">
<a href="/JLPTSuccess/N5/changelog/">What's new</a>
<a href="/JLPTSuccess/N5/privacy/">Privacy</a>
<a href="/JLPTSuccess/N5/notices/">Notices</a>
<a href="/JLPTSuccess/N5/home.html">N5 syllabus overview</a>
<a href="/JLPTSuccess/N5/feedback/">Feedback</a>
<a href="https://github.com/gauravaccentureproducts/JLPTSuccess/blob/master/N5/docs/TRANSLATING.md" target="_blank" rel="noopener">Help translate</a>
</nav>
<small class="footer-disclaimer">JLPT® and the Japanese-Language Proficiency Test® are trademarks of the Japan Foundation and JEES. This independent study site is not affiliated with, endorsed by, or sponsored by them.</small>
</footer>"""


def render_summary_page(slug, title, desc, count_field, count, hash_route, dir_route, body_extra=""):
    """Render one of the 7 LLM-005 summary pages."""
    spa_url = f"{BASE_URL}/N5/#{hash_route}"
    dir_url = f"{BASE_URL}/N5/{dir_route}/"
    # Plain-language call-to-action for the per-module pages. home.html has the
    # Modules cards instead, so it gets no CTA.
    cta = "" if body_extra else f'<p class="cta"><a href="{dir_url}">Open {title} →</a></p>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — JLPT N5</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{spa_url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{title} — JLPT N5">
<meta property="og:description" content="{desc}">
<meta property="og:site_name" content="JLPT N5 Tutor">
{SUMMARY_CSS_LINK}
<style>:root{{--green:#14452a;--green-soft:#1a5c38;--bg:#fff;--bg-soft:#f6f8f6;--text:#1a1a1a;--muted:#555;--border:#ddd}}*{{box-sizing:border-box}}html,body{{background:var(--bg);color:var(--text)}}body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Hiragino Sans","Yu Gothic","Noto Sans CJK JP",sans-serif;line-height:1.6;margin:0}}.page{{max-width:760px;margin:0 auto;padding:1rem}}.page a{{color:var(--green)}}.page a:hover{{color:var(--green-soft)}}h1.page-title{{font-size:1.6em;margin:.5rem 0}}.page h2{{font-size:1.18em;border-bottom:1px solid var(--border);padding-bottom:.3em;margin-top:1.6rem}}.count{{font-size:2em;color:var(--green);font-weight:600}}.muted{{color:var(--muted);font-size:.92em}}.cta{{margin:1.6rem 0;font-size:1.05em}}@media (prefers-color-scheme:dark){{:root{{--bg:#1a1d1b;--bg-soft:#232826;--text:#e7eae8;--muted:#a5aba8;--border:#383d3a}}}}</style>
</head>
<body>
{SUMMARY_BRAND_HEADER}
<div class="page">
<h1 class="page-title">{title}</h1>
<p class="muted">JLPT N5 module summary</p>
<p class="count">{count}</p>
<p>{desc}</p>
{body_extra}
{cta}
</div>
{SUMMARY_PAGE_FOOTER}
</body>
</html>
"""

def stage_summary_pages(data):
    """Emit the 7 LLM-005 summary pages."""
    counts = data["version"].get("counts", {})
    pages = [
        ("home", "JLPT N5 — Free Bilingual Study Material",
         "Free, on-device JLPT N5 study material covering grammar, vocabulary, kanji, reading, and listening. Bilingual English + Hindi. No login. No tracking. Works offline.",
         "version", f"{counts.get('grammar','?')} grammar · {counts.get('vocab','?')} vocab · {counts.get('kanji','?')} kanji · {counts.get('reading','?')} reading · {counts.get('listening','?')} listening · {counts.get('papers','?')} papers",
         "/home", "home",
         """<h2>Modules</h2>
<ul>
<li><a href="grammar.html">Grammar</a> — {grammar} patterns</li>
<li><a href="vocabulary.html">Vocabulary</a> — {vocab} entries</li>
<li><a href="kanji.html">Kanji</a> — {kanji} characters</li>
<li><a href="reading.html">Reading (Dokkai)</a> — {reading} passages</li>
<li><a href="listening.html">Listening (Choukai)</a> — {listening} drills</li>
<li><a href="test.html">Mock Tests</a> — {papers} paper packs ({pq} questions)</li>
</ul>""".format(
             grammar=counts.get('grammar','?'),
             vocab=counts.get('vocab','?'),
             kanji=counts.get('kanji','?'),
             reading=counts.get('reading','?'),
             listening=counts.get('listening','?'),
             papers=counts.get('papers','?'),
             pq=counts.get('paperQuestions','?'),
         )),
        ("grammar", "N5 Grammar",
         f"All {counts.get('grammar','?')} JLPT N5 grammar patterns: particles, verb conjugations, adjectives, copulas, conditionals, request/permission forms, comparison, time expressions, and more.",
         "grammar", counts.get("grammar","?"), "/learn/grammar", "learn/grammar"),
        ("vocabulary", "N5 Vocabulary",
         f"All {counts.get('vocab','?')} JLPT N5 vocabulary entries with pitch-accent annotation, part-of-speech tags, frequency rank, collocations, and curated example sentences.",
         "vocab", counts.get("vocab","?"), "/learn/vocab", "learn/vocab"),
        ("kanji", "N5 Kanji",
         f"All {counts.get('kanji','?')} JLPT N5 kanji with KanjiVG stroke-order SVGs, on/kun readings, primary meanings, vocab examples, and confusable cluster cross-references.",
         "kanji", counts.get("kanji","?"), "/kanji", "kanji"),
        ("reading", "N5 Reading (Dokkai)",
         f"All {counts.get('reading','?')} JLPT N5 reading (dokkai) passages with vocab + grammar footnotes, paragraph segmentation, cultural context, and inline glossary.",
         "reading", counts.get("reading","?"), "/reading", "reading"),
        ("listening", "N5 Listening (Choukai)",
         f"All {counts.get('listening','?')} JLPT N5 listening (choukai) drills with VOICEVOX-rendered audio, slow-version variants, inline vocab glossary, and line-level seek timestamps.",
         "listening", counts.get("listening","?"), "/listening", "listening"),
        ("test", "N5 Mock Tests",
         f"All {counts.get('papers','?')} JLPT N5 mock-test paper packs ({counts.get('paperQuestions','?')} questions) covering moji, goi, bunpou, and dokkai sections. Full timed mock sittings supported in the interactive app.",
         "papers/manifest", f"{counts.get('papers','?')} papers / {counts.get('paperQuestions','?')} questions", "/test", "papers"),
    ]
    written = 0
    for slug, title, desc, count_field, count, hash_route, dir_route, *extra in pages:
        body_extra = extra[0] if extra else ""
        html = render_summary_page(slug, title, desc, count_field, count, hash_route, dir_route, body_extra)
        out_path = os.path.join(REPO_N5, f"{slug}.html")
        write_atomically(out_path, html)
        written += 1
    print(f"  Summary pages: {written} files written")
    return written

# ---------------------------------------------------------------------------
# Stage 5: sitemap.xml regeneration (LLM-002)
# ---------------------------------------------------------------------------
def stage_sitemap(data):
    """Regenerate /N5/sitemap.xml to include every static mirror."""
    urls = []

    # Meta routes (existing)
    for r in ["", "home", "changelog", "privacy", "notices", "feedback", "missed", "settings", "sitting", "summary", "test"]:
        urls.append(f"{BASE_URL}/N5/{r}/" if r else f"{BASE_URL}/N5/")

    # 7 summary pages
    for slug in ["home", "grammar", "vocabulary", "kanji", "reading", "listening", "test"]:
        urls.append(f"{BASE_URL}/N5/{slug}.html")

    # Per-entity static mirrors (read from disk)
    for d, prefix in [
        ("learn/grammar", "learn/grammar"),
        ("learn/vocab", "learn/vocab"),
        ("kanji", "kanji"),
        ("reading", "reading"),
        ("listening", "listening"),
        ("papers", "papers"),
        ("lessons", "lessons"),
    ]:
        full_dir = os.path.join(REPO_N5, d)
        if not os.path.isdir(full_dir):
            continue
        for entry in sorted(os.listdir(full_dir)):
            sub = os.path.join(full_dir, entry)
            if os.path.isdir(sub):
                urls.append(f"{BASE_URL}/N5/{prefix}/{entry}/")
            elif sub.endswith(".html") and entry != "index.html":
                urls.append(f"{BASE_URL}/N5/{prefix}/{entry}")

    urls = sorted(set(urls))

    parts = ['<?xml version="1.0" encoding="UTF-8"?>\n']
    # Browser-only presentation: a same-origin XSL stylesheet renders the
    # sitemap as a branded, readable table. Search-engine crawlers ignore the
    # stylesheet PI and parse the raw <urlset>, so SEO is unaffected.
    parts.append('<?xml-stylesheet type="text/xsl" href="sitemap.xsl"?>\n')
    parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for url in urls:
        parts.append(f'  <url><loc>{url}</loc></url>\n')
    parts.append('</urlset>\n')
    write_atomically(os.path.join(REPO_N5, "sitemap.xml"), "".join(parts))
    print(f"  sitemap.xml: {len(urls)} URLs")
    return len(urls)

# ---------------------------------------------------------------------------
# Stage 6: noscript expansion + count fix in index.html (LLM-004)
# ---------------------------------------------------------------------------
def stage_noscript_update(data):
    """Update <noscript> block in N5/index.html with path-routed nav + fix counts."""
    counts = data["version"].get("counts", {})
    fp = os.path.join(REPO_N5, "index.html")
    src = open(fp, "r", encoding="utf-8").read()

    import re
    new_noscript = f'''<noscript>
      <article style="max-width:680px;margin:24px auto;padding:0 16px;">
        <h2>JLPT N5 — Free study material (English + Hindi)</h2>
        <p>This site is a Progressive Web App and works best with JavaScript enabled.
           Below is the syllabus outline + links to crawler-readable static pages.</p>

        <h3>Module summaries (static, no-JS)</h3>
        <ul>
          <li><a href="home.html">JLPT N5 overview</a></li>
          <li><a href="grammar.html">Grammar</a> — {counts.get("grammar","?")} patterns</li>
          <li><a href="vocabulary.html">Vocabulary</a> — {counts.get("vocab","?")} entries</li>
          <li><a href="kanji.html">Kanji</a> — {counts.get("kanji","?")} characters</li>
          <li><a href="reading.html">Reading (Dokkai)</a> — {counts.get("reading","?")} passages</li>
          <li><a href="listening.html">Listening (Choukai)</a> — {counts.get("listening","?")} drills</li>
          <li><a href="test.html">Mock Tests</a> — {counts.get("papers","?")} paper packs ({counts.get("paperQuestions","?")} questions)</li>
        </ul>

        <h3>Per-entity static indexes</h3>
        <ul>
          <li><a href="learn/grammar/">All {counts.get("grammar","?")} grammar patterns</a></li>
          <li><a href="learn/vocab/">All {counts.get("vocab","?")} vocabulary entries</a></li>
          <li><a href="kanji/">All {counts.get("kanji","?")} kanji</a></li>
          <li><a href="reading/">All {counts.get("reading","?")} reading passages</a></li>
          <li><a href="listening/">All {counts.get("listening","?")} listening drills</a></li>
          <li><a href="papers/">All {counts.get("papers","?")} mock paper packs</a></li>
        </ul>

        <h3>Data / Developers</h3>
        <ul>
          <li><a href="data/index.json">Corpus discovery index (JSON)</a></li>
          <li><a href="data/grammar.json">grammar.json</a> ·
              <a href="data/vocab.json">vocab.json</a> ·
              <a href="data/kanji.json">kanji.json</a> ·
              <a href="data/reading.json">reading.json</a> ·
              <a href="data/listening.json">listening.json</a></li>
          <li><a href="sitemap.xml">sitemap.xml</a> ·
              <a href="/JLPTSuccess/llms.txt">llms.txt</a></li>
        </ul>

        <h3>Site meta</h3>
        <ul>
          <li><a href="changelog/">Changelog</a></li>
          <li><a href="privacy/">Privacy</a></li>
          <li><a href="notices/">Notices &amp; licenses</a></li>
          <li><a href="https://github.com/gauravaccentureproducts/JLPTSuccess/issues">Feedback (GitHub Issues)</a></li>
        </ul>

        <p>Open source on
          <a href="https://github.com/gauravaccentureproducts/JLPTSuccess">GitHub</a>.
          MIT licensed code, CC BY-SA 4.0 content. No login, no tracking, works offline.</p>
      </article>
    </noscript>'''

    new_src = re.sub(r'<noscript>.*?</noscript>', new_noscript, src, count=1, flags=re.DOTALL)
    write_atomically(fp, new_src)
    print(f"  N5/index.html noscript: expanded with path-routed nav + counts {counts.get('grammar','?')}/{counts.get('vocab','?')}/{counts.get('kanji','?')}/{counts.get('reading','?')}/{counts.get('listening','?')}")
    return True

# ---------------------------------------------------------------------------
# Stage 7: Root level-picker dual-link update (LLM-005)
# ---------------------------------------------------------------------------
def stage_root_picker():
    """The root level-picker landing page intentionally carries NO crawler-link
    row. (Removed 2026-05-30 per user request: the 'N5 syllabus overview ·
    sitemap.xml · llms.txt' row read as belonging to a different site on the
    human landing page.) The N5 syllabus-overview link now lives in the N5
    footer instead; the sitemap stays discoverable via robots.txt. This stage
    strips the legacy block if an older build left it behind, and adds nothing."""
    fp = os.path.join(REPO_ROOT, "index.html")
    if not os.path.exists(fp):
        print(f"  root index.html not found at {fp}; skipping")
        return False
    src = open(fp, "r", encoding="utf-8").read()
    import re
    # Idempotent cleanup: drop the legacy LLM-005 crawler-links block if present.
    new_src = re.sub(
        r'\n*<!-- LLM-005 \(BUG-105\): static-summary link for crawlers / LLM access -->.*?</p>\n*',
        '\n', src, count=1, flags=re.DOTALL)
    if new_src != src:
        write_atomically(fp, new_src)
        print(f"  root index.html: removed legacy crawler-links row")
    else:
        print(f"  root index.html: no crawler-links row (ok)")
    return True

# ---------------------------------------------------------------------------
# Stage 8: robots.txt update (cross-level sitemap reference)
# ---------------------------------------------------------------------------
def stage_robots_root():
    """Ensure /JLPTSuccess/robots.txt exists with sitemap reference."""
    fp = os.path.join(REPO_ROOT, "robots.txt")
    content = f"""User-agent: *
Allow: /

# JLPTSuccess — JLPT study app (static, no tracking, no auth)
# N5 is the active level.
Sitemap: {BASE_URL}/N5/sitemap.xml
Sitemap: {BASE_URL}/llms.txt
"""
    if os.path.exists(fp):
        existing = open(fp, encoding="utf-8").read()
        if "sitemap" in existing.lower() and "N5/sitemap.xml" in existing:
            print(f"  root robots.txt already has sitemap reference")
            return True
    write_atomically(fp, content)
    print(f"  root robots.txt: written")

def main():
    data = load_data()
    print()
    print("=== Stage 1: Papers static mirrors (LLM-001) ===")
    stage_papers_mirrors(data)
    print()
    print("=== Stage 2: data/index.json (LLM-003) ===")
    stage_data_index(data)
    print()
    print("=== Stage 3: llms.txt (LLM-005) ===")
    stage_llms_txt(data)
    print()
    print("=== Stage 4: 7 LLM-005 summary pages ===")
    stage_summary_pages(data)
    print()
    print("=== Stage 5: sitemap.xml (LLM-002) ===")
    stage_sitemap(data)
    print()
    print("=== Stage 6: noscript expansion (LLM-004) ===")
    stage_noscript_update(data)
    print()
    print("=== Stage 7: root index.html dual-link ===")
    stage_root_picker()
    print()
    print("=== Stage 8: root robots.txt ===")
    stage_robots_root()
    print()
    print("=== Done ===")

if __name__ == "__main__":
    main()
