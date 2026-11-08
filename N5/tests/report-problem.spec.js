// IMP-6 coverage for js/error-monitor.js (IMP-5) + js/report-problem.js (IMP-2).
//
// Both modules shipped 2026-06-05 without a spec, which tripped the
// coverage-inventory "no NEW feature module without test" gate on every
// CI run since. They are tested together because report-problem.js reads
// error-monitor.js's ring buffer to pre-fill the GitHub issue.
//
// Tested invariants:
//   error-monitor.js
//     - window.__errorLog is an array and window.__recentErrors() works
//     - an uncaught error and an unhandled rejection are both recorded
//       (kind + message) and persisted to localStorage
//     - the ring buffer is capped (MAX = 25 entries)
//   report-problem.js
//     - the fixed "Report a problem" link renders once, opens a new tab
//       safely (target=_blank + rel=noopener) and points at GitHub
//       issues/new with labels + title + body pre-filled
//     - the title/body carry the current item id (history-mode path)
//     - the body attaches the most recent captured runtime error

const { test, expect } = require('@playwright/test');

const LOG_KEY = 'n5_error_log_v1';
const RING_MAX = 25;

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    try { localStorage.setItem('jlpt-n5-tutor:onboardingSeen', '1'); } catch {}
  });
});

function issueParams(href) {
  const u = new URL(href);
  return {
    host: u.host,
    path: u.pathname,
    labels: u.searchParams.get('labels') || '',
    title: u.searchParams.get('title') || '',
    body: u.searchParams.get('body') || '',
  };
}

test.describe('error-monitor — js/error-monitor.js', () => {

  test('records uncaught errors and unhandled rejections, persisted to localStorage', async ({ page }) => {
    await page.goto('/#/home');
    await page.waitForLoadState('networkidle');
    expect(await page.evaluate(() => Array.isArray(window.__errorLog))).toBe(true);
    expect(await page.evaluate(() => typeof window.__recentErrors)).toBe('function');

    await page.evaluate(() => {
      setTimeout(() => { throw new Error('probe-uncaught-error'); }, 0);
      Promise.reject(new Error('probe-unhandled-rejection'));
    });
    await expect.poll(() => page.evaluate(() => window.__errorLog.length)).toBeGreaterThanOrEqual(2);

    const recent = await page.evaluate(() => window.__recentErrors(5));
    const kinds = recent.map(e => `${e.kind}:${e.message}`).join(' | ');
    expect(kinds).toContain('error:');
    expect(kinds).toContain('probe-uncaught-error');
    expect(kinds).toContain('unhandledrejection:probe-unhandled-rejection');

    const stored = await page.evaluate(k => JSON.parse(localStorage.getItem(k) || '[]'), LOG_KEY);
    expect(stored.map(e => e.message).join(' | ')).toContain('probe-unhandled-rejection');
  });

  test(`ring buffer is capped at ${RING_MAX} entries`, async ({ page }) => {
    await page.goto('/#/home');
    await page.waitForLoadState('networkidle');
    await page.evaluate(n => {
      for (let i = 0; i < n; i++) Promise.reject(new Error(`probe-${i}`));
    }, RING_MAX + 10);
    await expect.poll(() => page.evaluate(() => {
      const log = window.__errorLog;
      return log.length && log[log.length - 1].message;
    })).toBe(`probe-${RING_MAX + 9}`);
    expect(await page.evaluate(() => window.__errorLog.length)).toBe(RING_MAX);
    const stored = await page.evaluate(k => JSON.parse(localStorage.getItem(k) || '[]').length, LOG_KEY);
    expect(stored).toBe(RING_MAX);
  });

});

test.describe('report-problem — js/report-problem.js', () => {

  test('renders one safe "Report a problem" link to a pre-filled GitHub issue', async ({ page }) => {
    await page.goto('/#/home');
    await page.waitForLoadState('networkidle');
    const fab = page.locator('#report-problem-fab');
    await expect(fab).toHaveCount(1);
    await expect(fab).toBeVisible();
    await expect(fab).toHaveText('Report a problem');
    await expect(fab).toHaveAttribute('target', '_blank');
    await expect(fab).toHaveAttribute('rel', /noopener/);
    const p = issueParams(await fab.getAttribute('href'));
    expect(p.host).toBe('github.com');
    expect(p.path).toMatch(/^\/[^/]+\/JLPTSuccess\/issues\/new$/);
    expect(p.labels).toBe('content-error,user-report');
    expect(p.title).toMatch(/^Content\/issue report: /);
    expect(p.body).toContain('**What looks wrong?**');
    expect(p.body).toContain('- Page: ');
  });

  test('issue title + body carry the current item id on a history-mode route', async ({ page }) => {
    await page.goto('/#/learn/n5-017');
    await page.waitForLoadState('networkidle');
    // The router rewrites the legacy hash URL to the clean path.
    await expect(page).toHaveURL(/\/learn\/n5-017\/?$/);
    const fab = page.locator('#report-problem-fab');
    await fab.hover();  // the link refreshes its href on hover / focus
    const p = issueParams(await fab.getAttribute('href'));
    expect(p.title).toBe('Content/issue report: n5-017');
    expect(p.body).toContain('- Item: n5-017');
  });

  test('issue body attaches the most recent runtime error from error-monitor', async ({ page }) => {
    await page.goto('/#/home');
    await page.waitForLoadState('networkidle');
    await page.evaluate(() => { Promise.reject(new Error('probe-for-report')); });
    await expect.poll(() => page.evaluate(() => window.__errorLog.length)).toBeGreaterThanOrEqual(1);
    const fab = page.locator('#report-problem-fab');
    await fab.hover();
    const p = issueParams(await fab.getAttribute('href'));
    expect(p.body).toContain('- Recent runtime errors:');
    expect(p.body).toContain('[unhandledrejection] probe-for-report');
  });

});
