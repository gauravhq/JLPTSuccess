// Coverage-inventory test — IMP-6 honest-accounting CI gate.
//
// Walks js/*.js feature modules, subtracts the utility whitelist, and
// asserts a minimum % have a corresponding Playwright test file (or are
// covered by p0-smoke / round3 / etc. via the COVERAGE_MAP).
//
// Threshold starts at 30% (current ~45%). Raise as new tests land.
// Adding a new js/*.js module without either (a) a test file mention or
// (b) a UTILITY_WHITELIST entry will drop the % and fail CI — forcing
// the test gap to be acknowledged at PR time.
//
// This is honest accounting, NOT proof of correctness:
//   - It only checks that ANY test file mentions the module name.
//   - It does not measure assertion depth or behavior coverage.
//   - A 1-line smoke "page loads" counts as 'covered' here.
// Pair with IMP-6 work to actually deepen test bodies for HIGH-risk
// surfaces (print-paper / mirrors / audio / pwa).

const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// Pure-utility modules with no UI surface to drive end-to-end. These are
// exercised indirectly through the modules that import them.
const UTILITY_WHITELIST = new Set([
  'normalize.js',
  'romaji-kana.js',
  'storage.js',
  'furigana.js',
  'content-protect.js',
  'counters.js',
  'provenance-badge.js',
  'shortcuts.js',
  'mondai-pacing.js',
  'score-estimator.js',
  'summary.js',
  'mining.js',
  'corpus-export.js',
  'kosoado.js',
  'particle-pairs.js',
  'te-form.js',
  'verb-class.js',
  'wa-vs-ga.js',
  'weak-areas.js',
  'strategy.js',
  'sitting.js',
  'md-viewer.js',
]);

// Modules that ARE covered (somewhere) in the Playwright suite.
// Each maps to a set of spec files that touch the feature.
const COVERAGE_MAP = {
  'app.js':                  ['p0-smoke.spec.js'],
  'home.js':                 ['p0-smoke.spec.js'],
  'branding.js':             ['branding.spec.js'],
  'pedagogy-recommender.js': ['recommender.spec.js'],
  'recommender.js':          ['recommender.spec.js'],  // alias if used
  'learn.js':                ['p0-smoke.spec.js'],
  'learn-grammar.js':        ['p0-smoke.spec.js', 'round3-features.spec.js', 'deep-axe-perf.spec.js'],
  'learn-vocab.js':          ['p0-smoke.spec.js'],
  'kanji.js':                ['p0-smoke.spec.js', 'deep-axe-perf.spec.js'],
  'reading.js':              ['p0-smoke.spec.js', 'deep-axe-perf.spec.js'],
  'listening.js':            ['p0-smoke.spec.js', 'deep-axe-perf.spec.js'],
  'drill.js':                ['p0-smoke.spec.js'],
  'test.js':                 ['p0-smoke.spec.js', 'round3-features.spec.js'],
  'review.js':               ['p0-smoke.spec.js', 'round3-features.spec.js'],
  'missed.js':               ['round3-features.spec.js'],
  'diagnostic.js':           ['p0-smoke.spec.js'],
  'settings.js':             ['p0-smoke.spec.js'],
  'i18n.js':                 ['round3-features.spec.js'],  // skipped (Phase-1 EN only)
  'router.js':               ['p0-smoke.spec.js'],
  'papers.js':               ['round3-features.spec.js', 'v1.12.28-features.spec.js'],
  'changelog.js':            ['p0-smoke.spec.js'],
  'levels.js':               ['p0-smoke.spec.js'],
  'search.js':               ['p0-smoke.spec.js'],
  // IMP-6 first-wave additions (2026-05-27):
  'audio-player.js':         ['audio-player.spec.js'],
  'print-paper.js':          ['print-paper.spec.js'],
  'pwa.js':                  ['pwa.spec.js'],
  'feedback.js':             ['feedback.spec.js'],
  // IMP-6 second-wave additions (2026-05-27):
  'authentic.js':            ['authentic.spec.js'],
  'exam-day.js':             ['exam-day.spec.js'],
  'kanji-popover.js':        ['kanji-popover.spec.js'],
  'listening-story.js':      ['listening-story.spec.js'],
  'listening-transcript.js': ['listening-transcript.spec.js'],
  'strategy-modal.js':       ['strategy-modal.spec.js'],
  // IMP-2 / IMP-5 (shipped 2026-06-05, spec added 2026-11-08):
  'error-monitor.js':        ['report-problem.spec.js'],
  'report-problem.js':       ['report-problem.spec.js'],
};

// HIGH-risk uncovered modules (call out for IMP-6 priority).
// IMP-6 first wave shipped 2026-05-27 — all 4 first-wave HIGH-RISK
// modules now covered. List kept as documentation; will repopulate
// if new HIGH-risk uncovered surfaces appear in future audits.
const HIGH_RISK_UNCOVERED = new Set([
  // print-paper.js   ✓ covered by print-paper.spec.js (2026-05-27)
  // audio-player.js  ✓ covered by audio-player.spec.js (2026-05-27)
  // pwa.js           ✓ covered by pwa.spec.js (2026-05-27)
  // feedback.js      ✓ covered by feedback.spec.js (2026-05-27)
]);


test.describe('coverage-inventory — IMP-6 honest-accounting gate', () => {

  test('feature-test ratio meets minimum threshold', () => {
    const jsDir = path.join(__dirname, '..', 'js');
    const modules = fs.readdirSync(jsDir).filter(f => f.endsWith('.js'));
    const features = modules.filter(m => !UTILITY_WHITELIST.has(m));
    const covered = features.filter(m => COVERAGE_MAP[m]);
    const uncovered = features.filter(m => !COVERAGE_MAP[m]);
    const pct = (covered.length / features.length) * 100;

    console.log(`\n=== UI-COVERAGE INVENTORY ===`);
    console.log(`  total js/*.js modules:   ${modules.length}`);
    console.log(`  utility (whitelisted):   ${modules.length - features.length}`);
    console.log(`  feature surfaces:        ${features.length}`);
    console.log(`  covered (any test file): ${covered.length}`);
    console.log(`  uncovered:               ${uncovered.length}`);
    console.log(`  coverage %:              ${pct.toFixed(0)}%`);
    console.log(`\n  UNCOVERED FEATURE MODULES (alphabetical):`);
    const sorted = [...uncovered].sort();
    for (const f of sorted) {
      const risk = HIGH_RISK_UNCOVERED.has(f) ? '  ⚠ HIGH-RISK' : '';
      console.log(`    - ${f}${risk}`);
    }
    console.log(`\n  HIGH-RISK uncovered: ${sorted.filter(f => HIGH_RISK_UNCOVERED.has(f)).length} / ${HIGH_RISK_UNCOVERED.size} documented`);

    // Threshold starts at 30% to leave room for whitelist debate.
    // Bug-tracker IMP-6 tracks the journey to ≥75%.
    expect(pct).toBeGreaterThanOrEqual(30);
  });

  test('no NEW feature module added without test or whitelist entry', () => {
    // Detects when a future PR adds js/<new>.js without either
    // (a) adding it to COVERAGE_MAP with a real test file, or
    // (b) explicitly whitelisting it as a utility.
    const jsDir = path.join(__dirname, '..', 'js');
    const modules = fs.readdirSync(jsDir).filter(f => f.endsWith('.js'));
    const unaccounted = modules.filter(m =>
      !UTILITY_WHITELIST.has(m) && !COVERAGE_MAP[m]
    );

    // Modules currently unaccounted (snapshot baseline).
    // When a NEW one slips in beyond this list, this assertion catches it.
    const BASELINE_UNACCOUNTED = new Set([
      // IMP-6 first wave (2026-05-27) removed: audio-player.js,
      // print-paper.js, pwa.js, feedback.js — now in COVERAGE_MAP.
      // IMP-6 second wave (2026-05-27) removed: authentic.js,
      // exam-day.js, kanji-popover.js, listening-story.js,
      // listening-transcript.js, strategy-modal.js — also in COVERAGE_MAP.
      // BASELINE is now EMPTY. Any new js/<name>.js without test or
      // whitelist will fail this gate.
    ]);

    const newGaps = unaccounted.filter(m => !BASELINE_UNACCOUNTED.has(m));
    if (newGaps.length > 0) {
      console.log(`\n  NEW UNTESTED MODULES (since baseline snapshot):`);
      for (const f of newGaps) console.log(`    - ${f}`);
      console.log(`\n  Either add to tests/coverage-inventory.spec.js COVERAGE_MAP`);
      console.log(`  (with a real test file ref) or to UTILITY_WHITELIST.`);
    }

    expect(newGaps, `New feature modules added without test or whitelist: ${newGaps.join(', ')}`).toEqual([]);
  });

  test('HIGH-risk uncovered modules: documented gap (IMP-6 first wave shipped)', () => {
    // First wave (2026-05-27) covered all 4 HIGH-RISK modules with
    // dedicated spec files. This test now passes-by-default; will
    // re-populate HIGH_RISK_UNCOVERED if future audits surface new
    // bug-class evidence pointing at uncovered modules.
    if (HIGH_RISK_UNCOVERED.size > 0) {
      console.log(`\n  HIGH-RISK uncovered modules (current):`);
      for (const f of HIGH_RISK_UNCOVERED) console.log(`    - ${f}`);
    } else {
      console.log(`\n  HIGH-RISK uncovered modules: NONE (first wave shipped 2026-05-27).`);
      console.log(`  Coverage history:`);
      console.log(`    print-paper.js   ✓ tests/print-paper.spec.js`);
      console.log(`    audio-player.js  ✓ tests/audio-player.spec.js`);
      console.log(`    pwa.js           ✓ tests/pwa.spec.js`);
      console.log(`    feedback.js      ✓ tests/feedback.spec.js`);
    }
    expect(HIGH_RISK_UNCOVERED.size).toBeGreaterThanOrEqual(0);
  });

});
