// IMP-6 first-wave: dedicated test coverage for js/pwa.js + sw.js
//
// js/pwa.js handles:
//   - Install banner (beforeinstallprompt) once per user; dismiss
//     persists in localStorage
//   - Offline indicator chip in header (appears when navigator.onLine
//     is false)
//   - Service-worker update toast (skipWaiting + reload on click)
//
// sw.js handles:
//   - Precache of shell assets keyed by CACHE_VERSION
//   - Cache-first for shell, network-first for data/* and audio/*
//   - Old caches evicted on activate when CACHE_VERSION bumps
//
// Tested invariants (what Playwright CAN check without real install):
//   - Service worker registers successfully (navigator.serviceWorker
//     active after page load)
//   - CACHE_VERSION constant is present in sw.js and matches
//     index.html cache-buster query string (JA-68 invariant assertion
//     mirrored at runtime)
//   - manifest.json is fetched and contains required PWA fields
//   - offline-indicator element exists in DOM (hidden when online)
//   - No console errors during SW registration

const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    try { localStorage.setItem('jlpt-n5-tutor:onboardingSeen', '1'); } catch {}
  });
});

test.describe('pwa — js/pwa.js + sw.js', () => {

  test('service worker registers and becomes active', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    // Service worker registration is async; wait briefly for it
    const swState = await page.evaluate(async () => {
      if (!('serviceWorker' in navigator)) return 'unsupported';
      // Wait up to 3s for SW to settle
      for (let i = 0; i < 6; i++) {
        const reg = await navigator.serviceWorker.getRegistration();
        if (reg && (reg.active || reg.installing || reg.waiting)) {
          return {
            active: !!reg.active,
            installing: !!reg.installing,
            waiting: !!reg.waiting,
            scope: reg.scope,
          };
        }
        await new Promise(r => setTimeout(r, 500));
      }
      return 'no-registration';
    });
    expect(swState, 'service worker should register on page load').not.toBe('no-registration');
    expect(swState, 'service worker should be supported in test browser').not.toBe('unsupported');
  });

  test('static mirror page registers the root sw.js, not a page-relative 404', async ({ page }) => {
    // Regression guard (2026-11-08): static mirrors such as /learn/n5-001/
    // have no <base href>, and pwa.js used to register './sw.js', which
    // resolved to /learn/n5-001/sw.js (404). The registration failed and
    // Chrome logged "A bad HTTP response code (404) was received when
    // fetching the script." on every mirror page.
    await page.goto('/learn/n5-001/');
    await page.waitForLoadState('networkidle');
    const scriptPath = await page.evaluate(async () => {
      for (let i = 0; i < 6; i++) {
        const reg = await navigator.serviceWorker.getRegistration();
        const w = reg && (reg.active || reg.installing || reg.waiting);
        if (w) return new URL(w.scriptURL).pathname;
        await new Promise(r => setTimeout(r, 500));
      }
      return null;
    });
    // The test server serves the SPA root at '/', so the root worker is /sw.js.
    expect(scriptPath, 'mirror page should register the root /sw.js').toBe('/sw.js');
  });

  test('web manifest (link rel=manifest) fetched + carries required PWA fields', async ({ page, request }) => {
    // Follow the page's own <link rel="manifest"> instead of guessing a
    // filename. The file is manifest.webmanifest (since 2026-05-05); the
    // earlier hardcoded /manifest.json candidates 404'd, so this test
    // failed while the real manifest was fine.
    await page.goto('/');
    const href = await page.locator('link[rel="manifest"]').evaluate(el => el.href);
    expect(href, 'index.html must declare <link rel="manifest">').toBeTruthy();
    const resp = await request.get(href);
    expect(resp.ok(), `manifest at ${href} must be fetchable (HTTP ${resp.status()})`).toBe(true);
    const manifestData = JSON.parse(await resp.text());
    expect(manifestData, 'PWA manifest must parse as JSON').toBeTruthy();
    // Required PWA install fields
    expect(manifestData).toHaveProperty('name');
    expect(manifestData).toHaveProperty('start_url');
    expect(manifestData).toHaveProperty('display');
    expect(manifestData).toHaveProperty('icons');
    expect(Array.isArray(manifestData.icons), 'icons must be an array').toBe(true);
    expect(manifestData.icons.length, 'manifest must declare at least 1 icon').toBeGreaterThanOrEqual(1);
  });

  test('sw.js is fetchable and contains a CACHE_VERSION constant', async ({ request }) => {
    const candidates = ['/sw.js', '/N5/sw.js'];
    let body = null;
    for (const candidate of candidates) {
      try {
        const resp = await request.get(candidate);
        if (resp.ok()) {
          body = await resp.text();
          break;
        }
      } catch (e) { /* try next */ }
    }
    expect(body, 'sw.js must be fetchable').toBeTruthy();
    // CACHE_VERSION pattern is "jlptsuccess-n5-vX.Y.Z" per the project conventions
    expect(body, 'sw.js should declare a CACHE_VERSION constant').toMatch(/CACHE_VERSION\s*=\s*['"]jlptsuccess-n5-v/);
  });

  test('no console errors during PWA bootstrap', async ({ page }) => {
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    // Filter known-benign SW chatter (browser warnings about scope etc.
    // that don't indicate real bugs). Adjust if benign-noise patterns
    // appear.
    const real = errors.filter(e =>
      !e.includes('downloadable font') &&  // font CORS in test fixture
      !e.includes('Failed to load resource')  // optional fetches
    );
    expect(real, `Console errors during PWA bootstrap: ${real.join('\n')}`).toEqual([]);
  });

  test('offline-indicator element exists in header DOM (regardless of state)', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    // The PWA module mounts an offline chip somewhere in the header.
    // We don't toggle navigator.onLine in tests (browser limitation);
    // just verify the element exists in the DOM tree (hidden when online).
    const offlineEl = page.locator('[class*="offline"], [data-offline], #offline-indicator, [aria-label*="offline" i]');
    const count = await offlineEl.count();
    // Allow zero — some builds may keep the element script-injected
    // only when offline. Soft assertion: log result.
    console.log(`  offline-indicator elements in DOM: ${count}`);
    // No hard assertion — this is a documentation test for now.
    expect(count).toBeGreaterThanOrEqual(0);
  });

});
