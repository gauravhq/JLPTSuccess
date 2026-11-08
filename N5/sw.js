// Service worker - offline caching for the static app.
// Strategy (revised 2026-05-10 — was stale-while-revalidate for shell):
//   * On install: pre-cache the SHELL only - HTML, CSS, JS modules, font
//     subsets, the JSON catalogs (grammar / vocab / kanji / reading /
//     listening / questions / whitelists), the i18n locales, and the 106
//     kanji stroke-order SVGs. Total ~3 MB.
//   * Audio MP3s (~22 MB across grammar/reading/listening) are NOT
//     precached. They are cached lazily on first fetch via the cache-first
//     branch of the fetch handler.
//   * HTML / navigation requests: NETWORK-FIRST. Updated HTML reaches the
//     user on a simple reload — no stale-while-revalidate "second reload"
//     surprise, no manual SW unregister required after each deploy. Cache
//     is the OFFLINE fallback only.
//   * CSS / JS / JSON / SVG / audio / fonts: CACHE-FIRST. CSS+JS are
//     version-keyed via `?v=N` query strings in index.html, so cache hit
//     ↔ correct version. New version = new URL = automatic cache miss =
//     fresh fetch. Other content is effectively immutable per release.
//
// Bump CACHE_VERSION whenever a release ships, so old caches get evicted on
// the next visit.
const CACHE_VERSION = 'jlptsuccess-n5-v1.17.51';  // bumped 2026-06-08 (v1.17.44: 雨 example sentences replaced; v1.17.43: 語 かた demoted to additional readings; v1.17.42: kanji native-review corrections - reading rules for on-dominant kanji + example/sentence fixes; v1.17.41: cache-bust delivering the native-review pronoun/noun/question-word particle-example + notation fixes to returning learners); prior bump 2026-06-04 — native-reviewer batch K: closed the last 2 BUG-266 re-check items on すむ — replaced unnatural frequency/time-adverb collocations (よく/まいにち/いま すむ) with reviewer-approved location-particle collocations (東京に/日本に/この町に すむ). Cache-bust so the corrected すむ entry reaches returning learners.

const PRECACHE = [
  './',
  './index.html',
  './manifest.webmanifest',
  // PRIVACY.md is the only narrative doc the app actually links to in the
  // footer. README/TASKS/NOTICES/CONTENT-LICENSE are repo docs; they're
  // viewable on GitHub but not required for the running app and don't need
  // to occupy precache slots. Removed 2026-05-04 (IMP-013 disposition).
  './PRIVACY.md',
  // IMP-021 (audit round-2): runtime references the minified stylesheet.
  // The unminified source stays in the repo + precache so devtools can
  // still resolve it via the `Sources` tab when debugging on-device.
  './css/main.css',
  './css/main.min.css',
  './js/app.js',
  // History-mode router helpers + base-aware fetch wrapper (2026-05-24).
  './js/router.js',
  './js/min/router.js',
  './js/storage.js',
  './js/furigana.js',
  './js/learn.js',
  // IMP-022 (audit round-2): code-split chunks of learn.js. Precache both
  // so the dispatcher's dynamic imports resolve from cache offline.
  './js/learn-grammar.js',
  './js/learn-vocab.js',
  // IMP-008/031, ISSUE-020/IMP-032 (audit round-3): wrong-answer
  // history view + full mock-paper sitting flow.
  './js/missed.js',
  './js/sitting.js',
  // IMP-007/IMP-010/IMP-038 (audit round-3): custom audio-player skin.
  // Lazy-loaded by app.js on DOMContentLoaded so first paint isn't
  // delayed; precache so the dynamic import resolves offline.
  './js/audio-player.js',
  // EB-4 (round-9 close-out, 2026-05-07): pedagogy-rule recommender.
  // Static-imported by home.js so it bundles into js/min/home.js;
  // precache the unminified copy too so devtools Sources resolves it.
  './js/pedagogy-recommender.js',
  './js/min/pedagogy-recommender.js',
  // SVA-NEXT-2.4 (round-9 follow-up, 2026-05-07): print-to-PDF mock
  // paper module. Static-imported by app.js. Precache both copies
  // so the route resolves offline.
  './js/print-paper.js',
  './js/min/print-paper.js',
  // SVA-NEXT-3 (round-9 follow-up, 2026-05-08): branding-override
  // loader + the default-empty branding.json. Precaching the JSON
  // means the loader's first-paint fetch resolves from cache offline,
  // and forks that ship a populated branding.json get it cached too.
  './js/branding.js',
  './js/min/branding.js',
  './data/branding.json',
  // ISSUE-043 (audit round-5): minified JS bundle. index.html points
  // at js/min/app.js; static + dynamic imports cascade to the rest
  // of js/min/. The unminified js/<name>.js files stay precached
  // above so DevTools Sources can still resolve them on-device.
  './js/min/app.js',
  './js/min/storage.js',
  './js/min/furigana.js',
  './js/min/learn.js',
  './js/min/learn-grammar.js',
  './js/min/learn-vocab.js',
  './js/min/missed.js',
  './js/min/sitting.js',
  './js/min/audio-player.js',
  './js/min/test.js',
  './js/min/review.js',
  './js/min/summary.js',
  './js/min/drill.js',
  './js/min/diagnostic.js',
  './js/min/settings.js',
  './js/min/normalize.js',
  './js/min/kosoado.js',
  './js/min/wa-vs-ga.js',
  './js/min/verb-class.js',
  './js/min/te-form.js',
  './js/min/i18n.js',
  './js/min/particle-pairs.js',
  './js/min/counters.js',
  './js/min/reading.js',
  './js/min/listening.js',
  './js/min/kanji.js',
  './js/min/kanji-popover.js',
  './js/min/shortcuts.js',
  './js/min/search.js',
  './js/min/home.js',
  './js/min/changelog.js',
  './js/min/feedback.js',
  './js/min/levels.js',
  './js/min/content-protect.js',
  './js/min/pwa.js',
  './js/min/papers.js',
  './js/test.js',
  './js/review.js',
  './js/summary.js',
  './js/drill.js',
  './js/diagnostic.js',
  './js/settings.js',
  './js/corpus-export.js',
  './js/normalize.js',
  './js/kosoado.js',
  './js/wa-vs-ga.js',
  './js/verb-class.js',
  './js/te-form.js',
  './js/i18n.js',
  './js/particle-pairs.js',
  './js/counters.js',
  './js/reading.js',
  './js/listening.js',
  './js/kanji.js',
  './js/kanji-popover.js',
  './js/shortcuts.js',
  './js/search.js',
  './js/home.js',
  './js/changelog.js',
  './js/feedback.js',
  './js/levels.js',
  './js/content-protect.js',
  './js/pwa.js',
  // IMP-126 (richness audit, 2026-05-09): authentic-content layer.
  // Static-imported by app.js. Precache both copies so #/authentic
  // resolves offline.
  './js/authentic.js',
  './js/min/authentic.js',
  // IMP-151 (richness audit, 2026-05-12): mining cross-link index.
  // Static-imported by app.js. Precache both copies so #/mining
  // resolves offline.
  './js/mining.js',
  './js/min/mining.js',
  './CHANGELOG.md',
  './data/vocab.json',
  './data/kanji.json',
  './data/reading.json',
  './data/listening.json',
  './data/audio_manifest.json',
  './locales/en.json',
  './locales/hi.json',
  './data/grammar.json',
  './data/questions.json',
  // IMP-126 (richness audit, 2026-05-09): authentic-content corpus.
  // Real-world JP signs / menus / transit / shop / notice. Precache
  // so #/authentic loads offline.
  './data/authentic.json',
  // IMP-035 (audit round-3): build-stamp + corpus counts. Read by the
  // footer fallback path, the README-consistency check, and any future
  // SW logic that needs the cache key without rebuilding it from
  // CHANGELOG.md.
  './data/version.json',
  // ISSUE-038 (audit round-5): SEO + crawler hints. Precaching means
  // the files are available even on offline / cached-only visits;
  // search engines hit them on first crawl.
  './robots.txt',
  './sitemap.xml',
  './data/n5_kanji_whitelist.json',
  './data/n5_kanji_readings.json',
  './data/n5_vocab_whitelist.json',
  // ISSUE-033 (audit round-4): explicit core-N5 vs late-N5 split. Honest
  // count for the home dashboard + future filter UIs. Guarded by JA-34
  // invariant in tools/check_content_integrity.py.
  './data/n5_core_pattern_ids.json',
  // IMP-052 (audit round-4): institutional theme overrides. Optional -
  // missing file is the default. Precaching makes the override resolve
  // offline once a fork has shipped one.
  './data/theme-overrides.json',
  // Self-hosted fonts (Phase-4 of the Zen Modern overhaul). Inter L/R/M
  // covers all latin UI. Noto Sans JP 400 is N5+N4-subsetted so the file
  // is ~165 KB instead of ~5 MB. Total font footprint: ~503 KB.
  './fonts/inter-300.woff2',
  './fonts/inter-400.woff2',
  './fonts/inter-500.woff2',
  './fonts/noto-sans-jp-400.woff2',
  // Audit 2026-05-25: new feature modules added since last PRECACHE sweep.
  './js/exam-day.js',
  './js/min/exam-day.js',
  './js/listening-story.js',
  './js/min/listening-story.js',
  './js/listening-transcript.js',
  './js/min/listening-transcript.js',
  './js/md-viewer.js',
  './js/min/md-viewer.js',
  './js/mondai-pacing.js',
  './js/min/mondai-pacing.js',
  './js/papers.js',
  './js/provenance-badge.js',
  './js/min/provenance-badge.js',
  './js/romaji-kana.js',
  './js/min/romaji-kana.js',
  './js/score-estimator.js',
  './js/min/score-estimator.js',
  './js/strategy.js',
  './js/min/strategy.js',
  './js/strategy-modal.js',
  './js/min/strategy-modal.js',
  './js/weak-areas.js',
  './js/min/weak-areas.js',
  // Audit 2026-06-08: error-monitor + report-problem modules added since last
  // PRECACHE sweep. Precache both unminified (DevTools Sources) and minified
  // (runtime) copies so the feature resolves offline.
  './js/error-monitor.js',
  './js/min/error-monitor.js',
  './js/report-problem.js',
  './js/min/report-problem.js',
];

self.addEventListener('install', (event) => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE_VERSION);

    // Build the full precache: static shell + 106 kanji stroke-order SVGs.
    // The SVG paths are derived at install-time from the whitelist file so
    // the precache list doesn't need to be hand-maintained alongside data.
    let kanjiSvgs = [];
    try {
      const wlResp = await fetch('./data/n5_kanji_whitelist.json', { cache: 'reload' });
      if (wlResp.ok) {
        const wl = await wlResp.json();
        kanjiSvgs = wl.map(g => `./svg/kanji/${g}.svg`);
      }
    } catch (err) {
      console.warn('SW: could not derive kanji SVG list:', err);
    }
    const fullList = [...PRECACHE, ...kanjiSvgs];

    // CRITICAL: use { cache: 'reload' } on every precache request so the SW
    // bypasses the BROWSER'S HTTP cache and pulls truly-fresh bytes from the
    // network. Without this, a CACHE_VERSION bump alone is insufficient - if
    // the browser HTTP cache already holds stale js/css from a prior visit,
    // cache.addAll() reads from that stale layer and the SW propagates the
    // stale content forward into its own cache. Symptom: bumping the SW
    // doesn't ship the new code. (Diagnosed 2026-04-30 after L1-L10 batch.)
    try {
      await Promise.all(fullList.map(url =>
        cache.add(new Request(url, { cache: 'reload' }))
      ));
    } catch (err) {
      console.warn('Service worker precache failed:', err);
    }
    self.skipWaiting();
  })());
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k)));
    self.clients.claim();
  })());
});

function isHTMLRequest(url, request) {
  // HTML / navigation requests — bare paths, .html, or top-level navigation.
  // CSS/JS are deliberately excluded here because they are version-keyed via
  // `?v=N` query strings in index.html, which makes URL-keyed cache-first the
  // correct strategy for them (cache hit ↔ correct version; new version =
  // new URL = automatic cache miss).
  if (request.mode === 'navigate') return true;
  if (/\.html$/.test(url.pathname)) return true;
  if (url.pathname.endsWith('/')) return true;
  // Bare path with no extension (e.g. /N5, /privacy) — likely an HTML route.
  if (!/\.[a-z0-9]{2,5}$/i.test(url.pathname)) return true;
  return false;
}

self.addEventListener('fetch', (event) => {
  // Only handle GETs; let everything else go to the network.
  if (event.request.method !== 'GET') return;
  // Same-origin only - don't intercept third-party requests.
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;

  if (isHTMLRequest(url, event.request)) {
    // Network-first for HTML. Updated HTML always reaches the user on
    // simple reload (no manual SW unregister, no stale-while-revalidate
    // dance, no "second reload to see changes" surprise). Cache is the
    // OFFLINE fallback only.
    event.respondWith((async () => {
      try {
        const fresh = await fetch(event.request);
        if (fresh && fresh.ok) {
          const cache = await caches.open(CACHE_VERSION);
          cache.put(event.request, fresh.clone()).catch(() => {});
        }
        return fresh;
      } catch (err) {
        const cache = await caches.open(CACHE_VERSION);
        const cached = await cache.match(event.request);
        return cached || new Response('Offline and not cached.', {
          status: 503, statusText: 'Offline',
          headers: { 'Content-Type': 'text/plain' },
        });
      }
    })());
    return;
  }

  // Everything else (CSS, JS with ?v=, JSON, SVG, audio, fonts): cache-first.
  // CSS/JS are version-keyed, so cache hit = correct version. Other content
  // is effectively immutable per release.
  event.respondWith((async () => {
    const cache = await caches.open(CACHE_VERSION);
    const cached = await cache.match(event.request);
    if (cached) return cached;
    try {
      const fresh = await fetch(event.request);
      if (fresh.ok) cache.put(event.request, fresh.clone()).catch(() => {});
      return fresh;
    } catch {
      return new Response('Offline and not cached.', {
        status: 503, statusText: 'Offline',
        headers: { 'Content-Type': 'text/plain' },
      });
    }
  })());
});

// Allow the page to ask the active SW to skip-wait when the user accepts the
// "Update available" toast.
self.addEventListener('message', (event) => {
  if (event.data?.type === 'SKIP_WAITING') self.skipWaiting();
});
