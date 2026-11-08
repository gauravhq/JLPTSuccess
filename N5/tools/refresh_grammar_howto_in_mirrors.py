"""Surgically refresh the body of each grammar static mirror so the HOW
TO USE / 使い方 section matches the SPA's rendering.

Why this script exists (BUG-203, 2026-05-31):
    The static mirror at learn/<pid>/index.html previously emitted only
    ``<h2>Attaches to</h2><p>{tokens}</p>`` — a single technical token
    under the section header. Users hitting the mirror with JS-disabled
    or before SPA boot saw what looked like an empty HOW TO USE region.
    The SPA renders a much richer view (top table + conjugation table).
    build_static_mirrors.py was updated to emit the richer markup, but
    running the wholesale rebuild would re-migrate ~1372 hand-patched
    content mirrors. This script does a surgical edit: only the body
    region between ``<h1>...</h1>`` and the trailing ``<footer>...
    </footer>`` is regenerated. Header (app-header + nav + meta tags),
    footer (breadcrumb + license + pattern-id), SPA boot script, and
    canonical URLs are untouched.

What the script does:
    1. Reads data/grammar.json
    2. For each grammar pattern (id starts with "n5-")
    3. Opens learn/<id>/index.html if it exists
    4. Locates the <h1>...</h1> close tag and the next <footer> open tag
    5. Generates the new body via _render_grammar_pattern_body
    6. Substitutes the body region in place
    7. Writes back (preserving line endings and existing surrounding markup)

Run from N5/:
    python tools/refresh_grammar_howto_in_mirrors.py
    python tools/refresh_grammar_howto_in_mirrors.py --dry-run

After running:
    python tools/check_content_integrity.py
    (JA-172 verifies static-mirror parity for HOW TO USE).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Import the shared renderer from build_static_mirrors so the surgical
# edit emits exactly the same markup as a wholesale rebuild.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_static_mirrors import _render_grammar_pattern_body  # type: ignore  # noqa: E402
from emdash_normalize import normalize as normalize_emdash  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GRAMMAR = ROOT / "data" / "grammar.json"
LEARN_DIR = ROOT / "learn"


# Boundary markers used to identify the body region in an existing mirror.
#
# CRITICAL: anchor on the PATTERN TITLE h1 (inside <main id="app">), NOT
# on the first <h1>. The static mirror has TWO <h1> tags — the brand
# wordmark h1 inside <header class="app-header"> (first in document
# order) and the pattern title h1 inside <main id="app"> (second). An
# earlier version of this script regex'd `</h1>` and matched the brand
# h1, gutting <main id="app">, the meta-banner, and the pattern title,
# and planting the new body content INSIDE <header>. Since the header
# uses display:flex on .brand h1, all the body content became flex
# items and rendered as narrow vertical columns (user-caught 2026-05-31
# minutes after the BUG-243 push; root cause logged in F.48 of the
# procedure manual). The two-anchor pattern below makes the bug
# unrepresentable: we first locate `<main id="app">`, then the FIRST
# `</h1>` inside main (the pattern title's close), then the FIRST
# `<footer>` after that (the inner footer with the breadcrumb).
_MAIN_OPEN_RE = re.compile(r'<main\s+id="app"[^>]*>', re.MULTILINE)
_H1_CLOSE_RE = re.compile(r"</h1>\s*", re.MULTILINE)
_FOOTER_OPEN_RE = re.compile(r"<footer[^>]*>", re.MULTILINE)


def _refresh_one(p: dict, dry_run: bool = False) -> str:
    """Return one of: 'rewrote', 'unchanged', 'missing', 'unparseable'."""
    pid = p.get("id")
    if not pid:
        return "missing"
    fp = LEARN_DIR / pid / "index.html"
    if not fp.exists():
        return "missing"
    src = fp.read_text(encoding="utf-8")
    mainm = _MAIN_OPEN_RE.search(src)
    if not mainm:
        return "unparseable"
    # First </h1> *after* <main id="app"> = the pattern title's close.
    h1m = _H1_CLOSE_RE.search(src, mainm.end())
    if not h1m:
        return "unparseable"
    # First <footer> *after* the pattern title = the inner breadcrumb footer.
    footm = _FOOTER_OPEN_RE.search(src, h1m.end())
    if not footm:
        return "unparseable"
    new_body, _desc = _render_grammar_pattern_body(p)
    # Preserve the newline after </h1> that the original template uses
    # (line-break separates header from body), and a newline before
    # <footer> for cleanliness.
    new_section = src[: h1m.end()] + "\n" + new_body + "\n" + src[footm.start():]
    # No em dashes on the site (owner decision 2026-11-08).
    new_section = normalize_emdash(new_section, "html")
    if new_section == src:
        return "unchanged"
    if not dry_run:
        fp.write_text(new_section, encoding="utf-8")
    return "rewrote"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Report what would change, don't write.")
    ap.add_argument("--ids", default="",
                    help="Comma-separated pattern IDs to refresh (default: all).")
    args = ap.parse_args()

    g = json.loads(GRAMMAR.read_text(encoding="utf-8"))
    patterns = g.get("patterns", [])
    if args.ids:
        wanted = set(s.strip() for s in args.ids.split(",") if s.strip())
        patterns = [p for p in patterns if p.get("id") in wanted]
        if not patterns:
            print(f"No patterns matched --ids={args.ids!r}")
            return 1

    counts = {"rewrote": 0, "unchanged": 0, "missing": 0, "unparseable": 0}
    unparseable_ids: list[str] = []
    missing_ids: list[str] = []
    for p in patterns:
        status = _refresh_one(p, dry_run=args.dry_run)
        counts[status] = counts.get(status, 0) + 1
        if status == "unparseable":
            unparseable_ids.append(p.get("id") or "?")
        elif status == "missing":
            missing_ids.append(p.get("id") or "?")

    print("=" * 60)
    print(f"Grammar mirrors HOW TO USE refresh{' (DRY RUN)' if args.dry_run else ''}")
    print("=" * 60)
    print(f"  Rewrote:      {counts['rewrote']}")
    print(f"  Unchanged:    {counts['unchanged']}")
    print(f"  Missing:      {counts['missing']} {missing_ids[:5]}{'...' if len(missing_ids)>5 else ''}")
    print(f"  Unparseable:  {counts['unparseable']} {unparseable_ids[:5]}{'...' if len(unparseable_ids)>5 else ''}")
    if counts["unparseable"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
