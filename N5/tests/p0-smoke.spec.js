// P0 smoke tests per feedback/ui-testing-plan.md §17.1.
//
// Goal: catch regressions in core navigation, the Learn hub, key
// detail pages, settings flow, and accessibility on the home route.
// Runs in <60s on a clean machine. Wired into CI as a release gate.

const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

// IMP-044 (2026-05-11) added first-run onboarding that auto-redirects
// hash-less visits with no history/results/streak to #/diagnostic. In
// CI every test launches a fresh browser context (no localStorage), so
// every page.goto('/') trips the redirect and the title becomes "JLPT
// N5 placement diagnostic" instead of the home title. Mark the
// onboarding sentinel as "seen" before navigation to bypass the
// redirect — tests that actually exercise the diagnostic surface
// navigate to /#/diagnostic explicitly and clear this sentinel locally.
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    try { localStorage.setItem('jlpt-n5-tutor:onboardingSeen', '1'); } catch {}
  });
});

test.describe('P0 smoke - core navigation', () => {
  // Note: Playwright gives each test a fresh browser context with empty
  // storage by default, so no beforeEach storage cleanup is needed. An
  // earlier `addInitScript(() => localStorage.clear())` broke the
  // 'persists across reload' test because it cleared storage on the
  // reload too.

  test('home loads as syllabus dashboard with 6 cards, no console errors', async ({ page }) => {
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });

    // 2026-05-27: navigate via explicit #/home rather than `/`. The
    // beforeEach addInitScript that sets `onboardingSeen=1` to bypass
    // the IMP-044 first-run diagnostic redirect was unreliable on CI —
    // tests had been failing on .syllabus-card count for ≥5 commits
    // before this test edit, with the page resolving to the
    // /diagnostic surface instead of /home. Explicit hash navigation
    // bypasses the bare-/ onboarding redirect entirely and lands on
    // the actual home renderer regardless of localStorage state.
    await page.goto('/#/home');
    // app.js applyRouteMeta() rewrites the title from the static
    // "JLPT N5" to the home-route-specific title once the SPA initialises.
    // We assert against the prefix so future copy edits to the route
    // descriptor don't break the test — the JLPT N5 brand anchor must
    // remain intact.
    await expect(page).toHaveTitle(/^JLPT N5/);
    // Brand-link visible wordmark is just "N5" + SVG mark since
    // commit a91bb68 (2026-05-04 "unify brand mark with landing page").
    // The "JLPT" branding lives in the page <title> + aria-label.
    // The header has TWO .brand-link anchors since the 2026-05-04 levels
    // feature: the JLPTSuccess level-home mark (aria-label "JLPTSuccess
    // home, …") and the "N5" wordmark (aria-label "N5 home"). Target each
    // explicitly so the strict-mode locator resolves to a single element.
    await expect(page.locator('.brand-link[aria-label="N5 home"]')).toContainText('N5');
    await expect(page.locator('.brand-link[aria-label*="JLPTSuccess"]')).toHaveAttribute('aria-label', /JLPT/i);
    // Homepage was restructured ~2026-05-09: marketing-style hero
    // dropped; section affordances now lead with `.section-label-text`
    // chips. v1.17.10 (2026-05-27) further dropped the lower three
    // sections per user: Recommended Study Order, Progress overview,
    // and the "Not sure where to start?" CTA. Test was updated to
    // assert the structural invariants that remain (6 syllabus cards
    // in canonical order + their indices). The removed sections'
    // assertions (.study-order-item, .study-order-link, .progress-row)
    // were dropped in the same edit — those classes are no longer
    // rendered.

    // Six syllabus cards in canonical order.
    await expect(page.locator('.syllabus-card')).toHaveCount(6);
    const titles = page.locator('.syllabus-card-title');
    await expect(titles.nth(0)).toContainText('Grammar');
    await expect(titles.nth(1)).toContainText('Vocabulary');
    await expect(titles.nth(2)).toContainText('Kanji');
    await expect(titles.nth(3)).toContainText('Reading');
    await expect(titles.nth(4)).toContainText('Listening');
    await expect(titles.nth(5)).toContainText('Mock Test');
    // 01..06 indices on every card.
    await expect(page.locator('.syllabus-card-index').first()).toContainText('01');
    await expect(page.locator('.syllabus-card-index').nth(5)).toContainText('06');
    // Fullscreen toggle exists in header (top-right cluster). CSS
    // hides it on mobile (display:none at <901px viewport), so check
    // for DOM presence rather than visibility — the button is wired
    // for desktop where it's reachable, mobile relies on the OS.
    await expect(page.locator('#fullscreen-toggle')).toHaveCount(1);
    expect(errors, `console errors: ${errors.join('\n')}`).toEqual([]);
  });

  test('Learn hub shows 5 numbered cards in two section-label groups', async ({ page }) => {
    await page.goto('/#/learn');
    // v1.8.0 design overhaul replaced .hub-group-title <h3> dividers with
    // .section-label components (ALL-CAPS text + flex-1 hairline rule).
    await expect(page.locator('.section-label-text')).toHaveCount(2);
    await expect(page.locator('.section-label-text').nth(0)).toContainText('Reference');
    await expect(page.locator('.section-label-text').nth(1)).toContainText('Practice');
    await expect(page.locator('.hub-card')).toHaveCount(5);
    // Numbered indices 01..05 added in v1.8.0 (replaced removed emoji icons).
    const indices = page.locator('.hub-card .card-index');
    await expect(indices).toHaveCount(5);
    await expect(indices.nth(0)).toContainText('01');
    await expect(indices.nth(4)).toContainText('05');
    const cards = page.locator('.hub-card h3');
    await expect(cards.nth(0)).toContainText('Grammar');
    await expect(cards.nth(1)).toContainText('Vocabulary');
    await expect(cards.nth(2)).toContainText('Kanji');
    await expect(cards.nth(3)).toContainText(/Dokkai|Reading/);
    await expect(cards.nth(4)).toContainText('Listening');
  });

  test('Grammar TOC has 177 cards across 5 super-sections', async ({ page }) => {
    // 32 fine-grained categories were collapsed into 5 super-sections
    // (Sentence Basics / Verbs / Adjectives and Comparison / Quantity,
    // Time and Connectives / Functional and Upper-N5) at render time.
    // The data file (data/grammar.json) is unchanged; the mapping is in
    // js/learn.js GRAMMAR_SUPERCATS. Each super-section is a collapsible
    // <details>; click to expand and see the pattern cards.
    await page.goto('/#/learn/grammar');
    await expect(page.locator('h2')).toContainText('Grammar');
    await expect(page.locator('details.toc-category')).toHaveCount(5);
    // Pattern count drifts as new entries land or duplicates retire.
    // Source of truth: data/grammar.json. Read it at runtime so the
    // assertion tracks the data rather than a hardcoded number.
    const expectedCount = await page.evaluate(async () => {
      const r = await fetch('data/grammar.json');
      const d = await r.json();
      return (d.patterns || []).length;
    });
    await expect(page.locator('.grammar-card')).toHaveCount(expectedCount);
  });

  test('pattern detail (n5-001) shows pattern, EN + JA meaning, examples', async ({ page }) => {
    await page.goto('/#/learn/n5-001');
    await expect(page.locator('h2.pattern-name')).toBeVisible();
    await expect(page.locator('.meaning-en')).toBeVisible();
    await expect(page.locator('.example-list li')).not.toHaveCount(0);
    // Japanese-meaning section heading is rendered with full-width parens
    await expect(page.getByText('意味')).toBeVisible();
  });

  test('Vocab list collapses 40 categories into 6 super-sections, all closed', async ({ page }) => {
    // 40 fine-grained sections collapsed into 6 super-sections
    // (changed 2026-05-01) following the same pattern as Grammar TOC.
    // All sections collapsed by default; chip jump menu removed.
    await page.goto('/#/learn/vocab');
    await expect(page.locator('h2')).toContainText('Vocabulary');
    await expect(page.locator('details.vocab-section')).toHaveCount(6);
    // No chip menu anymore
    await expect(page.locator('.cat-chip')).toHaveCount(0);
    // No section default-open
    const open = await page.locator('details.vocab-section[open]').count();
    expect(open).toBe(0);
  });

  test('Kanji index has 106 cards, each linking to a glyph detail', async ({ page }) => {
    // Corpus is 106 entries since Pass-13 build-pipeline fix recovered 9 missing
    // kanji (手/力/口/目/足/号/員/社/私). Was 97 pre-Pass-13.
    await page.goto('/#/kanji');
    await expect(page.locator('h2')).toContainText('Kanji');
    await expect(page.locator('.kanji-card')).toHaveCount(106);
    const firstHref = await page.locator('.kanji-card').first().getAttribute('href');
    expect(firstHref).toMatch(/^#\/kanji\/%E[0-9A-F]/);
  });

  test('Test setup -> start -> first question renders with 4 choices', async ({ page }) => {
    await page.goto('/#/test');
    await page.locator('#start-test').click();
    await expect(page.locator('.choice-grid, .sentence-order, .text-input-wrap')).toBeVisible({ timeout: 5_000 });
  });

  test('Diagnostic Start button is visible (regression guard for white-on-white CSS bug)', async ({ page }) => {
    await page.goto('/#/diagnostic');
    const btn = page.locator('#start-diagnostic');
    await expect(btn).toBeVisible();
    await expect(btn).toContainText(/Start|Re-take/);
    // Background must NOT be white (regression of the white-on-white bug)
    const bg = await btn.evaluate(el => getComputedStyle(el).backgroundColor);
    expect(bg).not.toBe('rgb(255, 255, 255)');
  });

  test('Settings: audio speed + reset confirm box', async ({ page }) => {
    // Note: the 3-mode furigana radios were removed in Pass 13 (auto-furigana
    // feature was killed because single-primary lookup tables couldn't
    // disambiguate context-dependent kanji readings). Test now covers the
    // remaining persistent settings.
    await page.goto('/#/settings');
    await expect(page.locator('#set-audio-rate option')).toHaveCount(3);
    await expect(page.locator('#reset-confirm')).toBeAttached();
    // Reset confirm box hidden until clicked
    await expect(page.locator('#reset-confirm')).toBeHidden();
  });

  test('Settings audio rate persists across reload', async ({ page }) => {
    await page.goto('/#/settings');
    await page.locator('#set-audio-rate').selectOption('1.25');
    await page.reload();
    await page.waitForLoadState('domcontentloaded');
    await expect(page.locator('#set-audio-rate')).toHaveValue('1.25');
  });
});

test.describe('P0 smoke - syllabus dashboard features (v1.10.0)', () => {
  // Regression coverage for the homepage redesign + 4 new features
  // shipped in v1.10.0: daily-goal badge, mock-test reading toggle,
  // completion tracking propagated to homepage Progress, full study-
  // order link routing.

  test('daily-goal badge: hidden for first-time visitor', async ({ page }) => {
    // Fresh storage = no streak record = no daily-status row at all.
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.syllabus-daily-status')).toHaveCount(0);
  });

  test('daily-goal badge: returning user, practiced today shows ✓', async ({ page }) => {
    // Seed a streak record dated today, then reload home.
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.evaluate(() => {
      const today = new Date();
      const key = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}-${String(today.getDate()).padStart(2,'0')}`;
      localStorage.setItem('jlpt-n5-tutor:streak', JSON.stringify({
        current: 5, longest: 5, lastStudyDate: key, days: [key],
      }));
      localStorage.setItem('jlpt-n5-tutor:results', JSON.stringify([
        { correct: 12, total: 15, percent: 80, incorrect: 3 },
      ]));
    });
    // Force re-render of home
    await page.evaluate(() => { location.hash = '#/learn'; });
    await page.waitForTimeout(400);
    await page.evaluate(() => { location.hash = '#/home'; });
    await page.waitForTimeout(600);
    await expect(page.locator('.syllabus-daily-status')).toBeVisible();
    await expect(page.locator('.syllabus-daily-streak')).toContainText('5 days');
    await expect(page.locator('.syllabus-daily-today')).toHaveClass(/is-met/);
    await expect(page.locator('.syllabus-daily-today')).toContainText('Practiced today');
  });

  test('daily-goal badge: returning user, NOT practiced today shows ○', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await page.evaluate(() => {
      // Streak from yesterday - not today.
      const yesterday = new Date(Date.now() - 86400_000);
      const key = `${yesterday.getFullYear()}-${String(yesterday.getMonth()+1).padStart(2,'0')}-${String(yesterday.getDate()).padStart(2,'0')}`;
      localStorage.setItem('jlpt-n5-tutor:streak', JSON.stringify({
        current: 3, longest: 3, lastStudyDate: key, days: [key],
      }));
      localStorage.setItem('jlpt-n5-tutor:history', JSON.stringify({
        'n5-001': { reps: 1, isMastered: true, isManuallyKnown: false },
      }));
    });
    await page.evaluate(() => { location.hash = '#/learn'; });
    await page.waitForTimeout(400);
    await page.evaluate(() => { location.hash = '#/home'; });
    await page.waitForTimeout(600);
    await expect(page.locator('.syllabus-daily-today')).toHaveClass(/is-pending/);
    await expect(page.locator('.syllabus-daily-today')).toContainText('Not yet practiced today');
  });

  test.skip('study-order links: all 9 route to the right surface', async ({ page }) => {
    // 2026-05-27: SKIPPED. The home-page "Recommended Study Order"
    // section (with the 9 `.study-order-link` anchors) was removed in
    // v1.17.10 per user request. The helper functions in js/home.js
    // (studyOrder(), the renderer) are retained for an easy revert,
    // and the i18n keys (home.study_order_*) remain in locales/*.json
    // (JA-108 parity). If the section is ever re-instated, change
    // `test.skip(...)` back to `test(...)` and this assertion should
    // pass again unchanged.
    //
    // Equivalent navigation coverage (Grammar / Vocab / Kanji / Drill
    // / Reading / Listening / Test / Review / Authentic) is still
    // exercised through:
    //   - The primary nav (.primary-nav a[data-route]) — clicked in
    //     the "Primary nav routes to all 6 main surfaces" test below.
    //   - The 6 syllabus cards on the home — covered by the
    //     "home loads as syllabus dashboard" test above.
    //   - The 5 hub-cards on /#/learn — covered by the
    //     "Learn hub shows 5 numbered cards" test below.
  });

  test('reading mock-test mode toggle: persists + filters questions', async ({ page }) => {
    await page.goto('/#/reading');
    await page.waitForLoadState('networkidle');
    const toggle = page.locator('#reading-mock-mode');
    await expect(toggle).toBeVisible();
    await expect(toggle).not.toBeChecked();
    await toggle.check();
    await expect(toggle).toBeChecked();
    // Page re-renders; check setting persisted to localStorage.
    const stored = await page.evaluate(() => {
      const s = JSON.parse(localStorage.getItem('jlpt-n5-tutor:settings') || '{}');
      return s.readingMockTestMode;
    });
    expect(stored).toBe(true);
    // MOB-017 (BUG-126, 2026-05-19) simplified the reading-list rows
    // to <a class="reading-pick"> wrapping just the passage title;
    // per-row question counts are no longer rendered, so the older
    // "contains もん" content-comparison was dropped. The persistence
    // check above is the meaningful assertion — it verifies the
    // toggle round-trips through storage and the re-render is wired.
    await expect(page.locator('.reading-list .reading-pick').first()).toBeVisible();
  });

  test.skip('homepage Progress reflects completion-state localStorage', async ({ page }) => {
    // 2026-05-27: SKIPPED. The home-page Progress section (6 progress
    // rows for Grammar / Vocab / Kanji / Reading / Listening / Mock
    // Test) was removed in v1.17.10 per user request. The renderer
    // helpers (computeProgress(), renderProgressRow()) in js/home.js
    // are retained, and the i18n keys (home.progress_*) remain in
    // locales/*.json (JA-108 parity). If the section is ever
    // re-instated, flip `test.skip` back to `test`.
    //
    // The completion-state localStorage shape this test seeds
    // (completedReading, completedListening, knownKanji) is still
    // written by the relevant route renderers (reading.js, listening.js,
    // kanji.js); only the home-page READ side is gone. Equivalent
    // coverage for the home-page renderer's count math, were it ever
    // useful, would now need a different surface (e.g., the syllabus
    // forecast section for returning users).
  });
});

test.describe('P0 smoke - keyboard shortcuts', () => {
  test('? opens shortcuts cheatsheet, Esc closes', async ({ page }) => {
    await page.goto('/#/learn');
    await page.waitForLoadState('networkidle');
    // The shortcuts handler is wired in app.js DOMContentLoaded chain;
    // wait until it's bound before dispatching.
    await page.waitForFunction(() => typeof window !== 'undefined');
    await page.evaluate(() => {
      document.body.focus();
      document.dispatchEvent(new KeyboardEvent('keydown', { key: '?', bubbles: true }));
    });
    await expect(page.locator('.shortcuts-overlay')).toBeVisible({ timeout: 3_000 });
    await page.evaluate(() => document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true })));
    await expect(page.locator('.shortcuts-overlay')).toBeHidden({ timeout: 3_000 });
  });

  test('/ focuses search input', async ({ page, isMobile }) => {
    // Conceptually a desktop power-user shortcut; on mobile the search
    // input may be reflowed off-viewport and there's no real keyboard
    // anyway. Skip on mobile rather than test something the user won't do.
    test.skip(isMobile, 'desktop-only shortcut');
    await page.goto('/#/learn');
    // waitForLoadState('networkidle') is more reliable than
    // domcontentloaded for SPA bundles — the keydown handler is
    // attached after the SPA boots, not at DOMContentLoaded.
    await page.waitForLoadState('networkidle');
    await page.evaluate(() => document.activeElement && document.activeElement.blur && document.activeElement.blur());
    // Use page.keyboard.press() rather than dispatchEvent(). Playwright's
    // keyboard simulation routes through the browser's input pipeline
    // (which matches a real user) instead of synthesising a JS-side
    // KeyboardEvent that some handlers may not fully process. This
    // closes the 2026-05-21 flake reported in CI run 26257997871.
    await page.keyboard.press('/');
    await expect(page.locator('#search-input')).toBeFocused();
  });
});

test.describe('P0 smoke - no third-party requests during steady state', () => {
  test('first-load network requests are all same-origin', async ({ page }) => {
    const thirdParty = [];
    page.on('request', req => {
      const u = new URL(req.url());
      if (u.hostname !== 'localhost' && u.hostname !== '127.0.0.1') {
        thirdParty.push(req.url());
      }
    });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    expect(thirdParty, `unexpected third-party requests: ${thirdParty.join(', ')}`).toEqual([]);
  });
});

test.describe('P0 smoke - accessibility (axe-core)', () => {
  // Per testing-plan §5.1: zero serious / critical violations on every route.
  // Cover the 6 routes most users actually touch.
  for (const route of ['/', '/#/learn', '/#/learn/grammar', '/#/test', '/#/settings', '/#/kanji']) {
    test(`axe-core: no serious/critical violations on ${route}`, async ({ page }) => {
      await page.goto(route);
      await page.waitForLoadState('networkidle');
      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
        .disableRules([
          // Skip rules that have known acceptable behavior on this app:
          // 'page-has-heading-one' is enforced site-wide; per-route h1
          // would duplicate the brand h1 unnecessarily.
          'page-has-heading-one',
        ])
        .analyze();
      const blocking = results.violations.filter(v =>
        v.impact === 'serious' || v.impact === 'critical'
      );
      expect(
        blocking,
        blocking.length
          ? `serious/critical a11y violations on ${route}:\n` +
            blocking.map(v => `  ${v.id}: ${v.help}`).join('\n')
          : ''
      ).toEqual([]);
    });
  }
});
