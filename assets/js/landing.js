// Landing-page bootstrap. The level-picker LP at JLPTSuccess/index.html
// is mostly static, so this script is intentionally minimal — only the
// fullscreen toggle currently. Mirrors initFullscreenToggle() in
// N5/js/app.js so the two surfaces behave identically.
//
// Loaded via <script src="assets/js/landing.js?v=N"> at body-end (CSP allows
// script-src 'self' but not inline scripts).

(function () {
  'use strict';

  function initFullscreenToggle() {
    const btn = document.getElementById('fullscreen-toggle');
    if (!btn) return;
    const targetEl = () => document.documentElement;
    const isFullscreen = () =>
      !!(document.fullscreenElement || document.webkitFullscreenElement);
    const updateLabel = () => {
      const fs = isFullscreen();
      btn.setAttribute('aria-label', fs ? 'Exit fullscreen' : 'Toggle fullscreen');
      btn.setAttribute('title', fs ? 'Exit fullscreen' : 'Toggle fullscreen');
      btn.classList.toggle('is-fullscreen', fs);
    };
    btn.addEventListener('click', async () => {
      try {
        if (isFullscreen()) {
          if (document.exitFullscreen) await document.exitFullscreen();
          else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
        } else {
          const el = targetEl();
          if (el.requestFullscreen) await el.requestFullscreen();
          else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
        }
      } catch (err) {
        // Permissions-Policy or user-gesture issues — fail silently;
        // the button is opportunistic and shouldn't break the LP.
        console.warn('Fullscreen toggle failed:', err);
      }
    });
    document.addEventListener('fullscreenchange', updateLabel);
    document.addEventListener('webkitfullscreenchange', updateLabel);
    updateLabel();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFullscreenToggle);
  } else {
    initFullscreenToggle();
  }
})();
