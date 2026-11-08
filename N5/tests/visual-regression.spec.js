// Visual-regression smoke per feedback/ui-testing-plan.md §16 + DEFER-6.
//
// Captures screenshots of the 6 routes that drive the most page-paint risk
// (home / learn hub / grammar TOC / kanji index / reading list / settings).
// Compares against committed baselines in tests/__screenshots__. First run
// after a layout change should be `npx playwright test --update-snapshots`.
//
// Why scoped this narrowly: visual-regression with full coverage breeds
// flakes (font-rendering, scrollbar width, cursor blink). The 6 routes
// here cover every CSS layout shipped (3-col grid, 2-col grid, card
// matrix, list, form, single-pane). New routes don't need a separate
// snapshot unless they introduce a new layout pattern.
//
// Animations are disabled per-test via `prefers-reduced-motion: reduce`
// emulation; the runner waits for `networkidle` so PWA-cache warm-up
// doesn't paint differently between baseline and run.
const { test, expect } = require('@playwright/test');

const ROUTES = [
  { path: '/',                      slug: 'home' },
  { path: '/#/learn',               slug: 'learn-hub' },
  { path: '/#/learn/grammar',       slug: 'learn-grammar-toc' },
  { path: '/#/kanji',               slug: 'kanji-index' },
  { path: '/#/reading',             slug: 'reading-list' },
  { path: '/#/settings',            slug: 'settings' },
  // ISSUE-045 / IMP-065 (audit round-5): coverage for the round-3/4
  // surfaces that previously had zero pixel-drift protection.
  { path: '/#/missed',              slug: 'missed-empty' },
  { path: '/#/sitting',             slug: 'sitting-picker' },
  { path: '/#/test',                slug: 'test-setup' },
  // ISSUE-072 (audit round-9): expanded coverage to highest-traffic
  // surfaces previously uncovered. These three close out the
  // "no visual-regression on home/settings/vocab list" finding.
  { path: '/#/learn/vocab',         slug: 'vocab-list' },
  { path: '/#/listening',           slug: 'listening-list' },
  { path: '/#/papers',              slug: 'papers-list' },
  { path: '/#/drill',               slug: 'drill-setup' },
  { path: '/#/review',              slug: 'review-empty' },
  { path: '/#/summary',             slug: 'summary' },
];

const VIEWPORTS = [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile',  width: 375,  height: 812 },
];

// 2026-05-21: visual-regression suite runs on every platform.
//
// Baselines are committed per-OS:
//   - `<name>-chromium-<project>-win32.png`  (local Windows dev)
//   - `<name>-chromium-<project>-linux.png`  (CI ubuntu-latest)
// Playwright auto-selects the right baseline based on process.platform
// at test time. The Linux baselines were generated via the
// workflow_dispatch input `update_snapshots: true` on
// .github/workflows/playwright.yml (gh workflow run playwright.yml -f
// update_snapshots=true) and committed alongside the win32 ones.
//
// To refresh baselines after intentional layout changes:
//   - Local Windows: `npm run test:visual:update`, commit -win32 PNGs.
//   - CI Linux:     `gh workflow run playwright.yml -f update_snapshots=true`,
//                   download artifact, commit -linux PNGs.
// See procedure-manual §F.40.6 (cross-platform-snapshot class).
test.describe('Visual regression - homepage + canonical routes', () => {
  for (const vp of VIEWPORTS) {
    for (const route of ROUTES) {
      test(`${route.slug} @ ${vp.name}`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.emulateMedia({ reducedMotion: 'reduce' });
        await page.goto(route.path);
        await page.waitForLoadState('networkidle');
        // Mask the streak / daily-status row on home: it changes daily,
        // which would flake the baseline. Mask the footer version label on
        // every route: it changes on every release, so an unmasked label
        // makes every baseline stale at the next version bump (the
        // 2026-05-28 -linux baselines had "v1.17.16" baked in).
        const masks = [page.locator('[data-footer-version]')];
        if (route.slug === 'home') masks.push(page.locator('.syllabus-daily-status'));
        await expect(page).toHaveScreenshot(`${route.slug}-${vp.name}.png`, {
          fullPage: true,
          mask: masks,
          // Pixel-diff threshold: 0.1% of pixels can differ before fail.
          // Calibrated to absorb sub-pixel font rendering between runs
          // while still catching real layout regressions (e.g. a card
          // shifted 4px would blow past 0.1%).
          maxDiffPixelRatio: 0.001,
          animations: 'disabled',
        });
      });
    }
  }
});

// ISSUE-072 (audit round-9) — Hindi locale visual regression coverage.
// Catches Devanagari-rendering regressions (font-fallback, line-height,
// reflow with Hindi glyphs which have a taller base box than Latin
// fonts) on the highest-traffic surfaces. Localised UI strings ship
// in N5/locales/hi.json; the actual Devanagari rendering depends on
// the system font stack, so a baseline locks the rendered look.
const HINDI_ROUTES = [
  { path: '/',                      slug: 'home-hi' },
  { path: '/#/learn',               slug: 'learn-hub-hi' },
  { path: '/#/settings',            slug: 'settings-hi' },
  { path: '/#/learn/vocab',         slug: 'vocab-list-hi' },
];

// 2026-05-27 RE-SKIP after F1 attempt (commit ab19c25a). The `?lc=hi`
// URL param IS now wired in js/i18n.js initI18n() — and it works for
// any future-enabled locale — but Hindi specifically remains gated:
//
//   js/i18n.js line 30:  const ENABLED_LOCALES = ['en'];
//   js/i18n.js line 25-29 comment:
//     "Phase-1 launch (2026-05-24): Hindi UI is temporarily disabled
//      to focus the first public launch on English-medium learners.
//      hi.json data is retained in the build so JA-108 (locale
//      key-set parity) still passes and Phase 2 re-enables Hindi
//      without a data migration. To re-enable: widen ENABLED_LOCALES
//      to include 'hi' (must be a subset of SUPPORTED)."
//
// So the SPA's initI18n() (both the new URL-param path AND the
// existing saved-settings path) clamps any 'hi' selection back to
// DEFAULT_LOCALE ('en'). document.documentElement.lang never becomes
// 'hi'; waitForFunction times out. This isn't a test-infra issue —
// it's the intended Phase-1 product behavior.
//
// Un-skip path (Phase 2):
//   1. Set ENABLED_LOCALES = ['en', 'hi'] in js/i18n.js
//   2. Flip `test.describe.skip(...)` back to `test.describe(...)`
//   3. Run `gh workflow run playwright.yml -f update_snapshots=true`
//      to regenerate the 8 Hindi -linux.png baselines
//   4. Commit baselines + locale-enable change in one batch
test.describe.skip('Visual regression - Hindi locale (Devanagari) [SKIPPED — ENABLED_LOCALES gates hi off in Phase-1; un-skip when widened]', () => {
  // Runs on every platform — Linux baselines were generated via the
  // workflow_dispatch update_snapshots run alongside the main suite
  // (2026-05-21). See file header for the cross-platform pattern.
  for (const vp of VIEWPORTS) {
    for (const route of HINDI_ROUTES) {
      test(`${route.slug} @ ${vp.name}`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.emulateMedia({ reducedMotion: 'reduce' });
        // v1.17.19 (2026-05-27): navigate with `?lc=hi` URL param so the
        // SPA's initI18n() picks up the locale synchronously at boot.
        // route.path may already contain `#/...` (hash), so insert the
        // query string BEFORE the hash. Empty paths get a bare `/?lc=hi`.
        const [base, hash] = route.path.split('#');
        const url = `${base}${base.includes('?') ? '&' : '?'}lc=hi${hash ? '#' + hash : ''}`;
        await page.goto(url);
        await page.waitForLoadState('networkidle');
        // Confirm the locale switch landed before snapshotting. i18n.js
        // setLocale() writes document.documentElement.lang = 'hi'. With
        // the URL-param approach this is essentially instantaneous (no
        // localStorage round-trip), but keeping waitForFunction with a
        // generous 15s timeout as a safety net.
        await page.waitForFunction(
          () => document.documentElement.lang === 'hi',
          null,
          { timeout: 15000 }
        );
        const masks = route.slug === 'home-hi'
          ? [page.locator('.syllabus-daily-status')]
          : [];
        await expect(page).toHaveScreenshot(`${route.slug}-${vp.name}.png`, {
          fullPage: true,
          mask: masks,
          maxDiffPixelRatio: 0.002,  // slightly more tolerance for
                                     // Devanagari font-rendering variation
          animations: 'disabled',
        });
      });
    }
  }
});
