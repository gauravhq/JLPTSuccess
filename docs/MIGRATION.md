# Migration history

This repo (`gauravaccentureproducts/JLPTSuccess`) was created on **2026-05-04** by consolidating two previously-separate repos into a single monorepo.

## Predecessor repos and their tags

| Old repo | Status | Pre-migration tag | Maps to |
|---|---|---|---|
| `gauravaccentureproducts/jlpt-n5-tutor` | Archived (read-only backup) | `pre-migration-2026-05-04` | `JLPTSuccess/N5/` (this repo) |
| `gauravaccentureproducts/jlpt-n4-tutor` | Archived (read-only backup) | `v0.2.1-pre-migration` | `JLPTSuccess/N4/` (this repo, currently work-blocked) |

The old repos' commit histories are preserved at those tags. They were not grafted into this monorepo because:

1. The old N5 and N4 repos were independent histories with overlapping authorship metadata; a `git filter-repo` graft would have produced a confusing branched history.
2. Solo + AI authorship - preserving file-level history across the move was lower-value than the simplicity of starting fresh.
3. The pre-migration tags + read-only archives are a sufficient audit trail for any forensic question ("when was item X first introduced?", "what changed between v3 and v3.1?", etc.).

## Live URL changes

| Resource | Pre-migration URL | Post-migration URL |
|---|---|---|
| N5 app | `…github.io/jlpt-n5-tutor/` | `…github.io/JLPTSuccess/N5/` |
| N4 app | `…github.io/jlpt-n4-tutor/` | `…github.io/JLPTSuccess/N4/` |
| Level picker (new) | n/a | `…github.io/JLPTSuccess/` |

The pre-migration URLs continue to serve their last pre-migration build for as long as the backup repos and their Pages deployments remain enabled. They carry a redirect notice pointing to the new URLs. They will not receive further content updates.

## Service worker considerations

Because the live URL changed (`/jlpt-n5-tutor/` → `/JLPTSuccess/N5/`), the SW scope changed too. Returning visitors who had the old SW cached will need to either:

- Visit the new URL (which registers a different SW under a different scope - no conflict, both can coexist while old visitors finish their last cached session).
- Click the redirect notice on the old URL, which sends them to the new URL.

The SW cache version was reset to `jlptsuccess-n5-vN` (mirrors `version.json:version`) so that anyone on the new URL gets a fresh cache stamp.

## localStorage considerations

The localStorage namespace was deliberately preserved across the migration:

- `jlpt-n5-tutor:*` keys - pre-migration N5 progress data is automatically picked up by the new app at the new URL.
- `jlpt-n4-tutor:*` keys - same for N4.

Because the origin (`gauravaccentureproducts.github.io`) is shared between old and new URLs, browser localStorage is the same store. Users moving from the old URL to the new URL keep their study progress. (This also means that clearing site data on `gauravaccentureproducts.github.io` clears progress for both old and new - that's standard web platform behavior, not a bug.)

## What changed at code level

- Brand-link in each level now points to `../` (the JLPTSuccess level picker), not `#/levels` (which used to be an in-app placeholder route).
- In-app routes `#/levels`, `#/n5`, `#/n4`, `#/n3`, `#/n2`, `#/n1` redirect out via `location.replace('../')` for any legacy bookmarks that still hit those.
- The five-bar ladder logo from `assets/logo/` (canonical, top-level) is wired into favicons and PWA manifests across all levels.
- N4 was placed under a project-level work-block (per `.claude/CLAUDE.md`) on 2026-05-04 - its sub-app continues to serve at `/JLPTSuccess/N4/` for legacy bookmarks but receives no further content updates until the user explicitly unblocks it.

## How to inspect the pre-migration state

```bash
git clone https://github.com/gauravaccentureproducts/jlpt-n5-tutor
cd jlpt-n5-tutor
git checkout pre-migration-2026-05-04
# Browse the tree as it was just before the consolidation.
```

Same pattern for `jlpt-n4-tutor` with tag `v0.2.1-pre-migration`.

The backup repos are intentionally left alive (in archived / read-only state on GitHub) so this `git clone` workflow continues to function for any future audit.
