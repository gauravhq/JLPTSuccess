// PWA install prompt + offline indicator + SW update toast (Brief 2 §12.3, §12.4, §12.1).
//
// - Install banner: shown once per user when the browser fires
//   `beforeinstallprompt`. Dismissed banner persists in localStorage.
// - Offline indicator: small chip in the header that appears when
//   `navigator.onLine` becomes false. Hidden when online; in steady state
//   the user shouldn't see anything.
// - Update toast: surfaced when the SW posts a SW_UPDATE_AVAILABLE message
//   (new shell version detected). Click "Reload" to skipWaiting + reload.

import * as storage from './storage.js';
import { assetUrl } from './router.js';

const INSTALL_DISMISSED_KEY = 'pwa.installDismissed';
let deferredPrompt = null;

export function initPwa() {
  // Service worker registration. Previously lived as an inline <script> in
  // index.html, but that violated the CSP `script-src 'self'` directive
  // (CSP blocks inline scripts even when same-origin). Moving it here keeps
  // the strict CSP intact.
  //
  // The script URL is rebased to the SPA root with assetUrl(). A bare
  // './sw.js' resolves against the document URL: fine on index.html (its
  // <base href> is the root) but on a static mirror such as /learn/n5-001/
  // (no <base>) it became /learn/n5-001/sw.js, a 404 that failed the
  // registration and logged a console error on every mirror page.
  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    const swUrl = assetUrl('sw.js');
    if (document.readyState === 'complete') {
      navigator.serviceWorker.register(swUrl).catch(err => {
        console.warn('Service worker registration failed:', err);
      });
    } else {
      window.addEventListener('load', () => {
        navigator.serviceWorker.register(swUrl).catch(err => {
          console.warn('Service worker registration failed:', err);
        });
      });
    }
  }

  // Install banner
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    if (!storage.get(INSTALL_DISMISSED_KEY, false)) showInstallBanner();
  });

  // ISSUE-034 (audit round-4): on-demand install trigger from the home
  // trust band ("Works offline" pill). Wire any element marked
  // [data-trust-install] to fire the same prompt deferred above.
  document.addEventListener('click', async (ev) => {
    const el = ev.target.closest('[data-trust-install]');
    if (!el) return;
    ev.preventDefault();
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const choice = await deferredPrompt.userChoice;
      deferredPrompt = null;
      if (choice && choice.outcome === 'dismissed') {
        // Don't store dismissal - user chose deliberately.
      }
    } else {
      // No prompt available (already installed, or browser doesn't fire
      // beforeinstallprompt - Firefox/iOS Safari). Show a one-shot toast.
      _showOfflineHowToast();
    }
  });

  // Offline indicator
  const updateOnlineState = () => {
    const indicator = ensureOfflineIndicator();
    indicator.hidden = navigator.onLine;
  };
  window.addEventListener('online', updateOnlineState);
  window.addEventListener('offline', updateOnlineState);
  updateOnlineState();

  // SW update toast
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('message', (ev) => {
      if (ev.data?.type === 'SW_UPDATE_AVAILABLE') showUpdateToast();
    });
  }
}

function showInstallBanner() {
  if (document.getElementById('pwa-install-banner')) return;
  const banner = document.createElement('div');
  banner.id = 'pwa-install-banner';
  banner.className = 'pwa-banner';
  banner.setAttribute('role', 'region');
  banner.setAttribute('aria-label', 'Install this app');
  // Trust-band promotion 2026-05-07: install pitch now leads with the
  // niche-N2 differentiators (no login / no tracking / no ads / offline)
  //, these are the precise reasons a learner installs vs sticks with
  // a tab in their browser. Surfacing them on the install CTA itself
  // raises install conversion on first paint.
  banner.innerHTML = `
    <span class="pwa-banner-copy">
      <strong>Install this app to use it offline from your home screen.</strong>
      <small class="pwa-banner-trust">No login. No tracking. No ads. Free, forever.</small>
    </span>
    <button id="pwa-install-yes" class="btn-primary">Install</button>
    <button id="pwa-install-no" class="btn-secondary">Not now</button>
  `;
  document.body.appendChild(banner);
  document.getElementById('pwa-install-yes').addEventListener('click', async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const choice = await deferredPrompt.userChoice;
    storage.set(INSTALL_DISMISSED_KEY, true);
    deferredPrompt = null;
    banner.remove();
  });
  document.getElementById('pwa-install-no').addEventListener('click', () => {
    storage.set(INSTALL_DISMISSED_KEY, true);
    banner.remove();
  });
}

function ensureOfflineIndicator() {
  let el = document.getElementById('offline-indicator');
  if (el) return el;
  el = document.createElement('div');
  el.id = 'offline-indicator';
  el.className = 'offline-indicator';
  el.setAttribute('role', 'status');
  el.setAttribute('aria-live', 'polite');
  el.textContent = 'Offline - cached content only';
  el.hidden = true;
  document.body.appendChild(el);
  return el;
}

// ISSUE-034: fallback toast for browsers that don't fire
// beforeinstallprompt (Firefox / iOS Safari). Tells the user how to
// install via the browser's own UI.
function _showOfflineHowToast() {
  const ua = navigator.userAgent || '';
  let how;
  if (/iPhone|iPad|iPod/i.test(ua)) {
    how = 'iOS: tap the Share button in Safari, then "Add to Home Screen".';
  } else if (/Firefox/i.test(ua)) {
    how = 'Firefox: open the menu, then "Install" or "Add to Home Screen".';
  } else {
    how = 'Look for an install / "Add to home screen" option in your browser menu.';
  }
  const toast = document.createElement('div');
  toast.className = 'pwa-toast';
  toast.setAttribute('role', 'status');
  toast.innerHTML = `<span>${how}</span><button class="btn-secondary" aria-label="Dismiss">×</button>`;
  document.body.appendChild(toast);
  toast.querySelector('button').addEventListener('click', () => toast.remove());
  setTimeout(() => toast.remove(), 8000);
}

function showUpdateToast() {
  if (document.getElementById('sw-update-toast')) return;
  const toast = document.createElement('div');
  toast.id = 'sw-update-toast';
  toast.className = 'pwa-toast';
  toast.setAttribute('role', 'status');
  toast.innerHTML = `
    <span>A new version is available.</span>
    <button id="sw-update-yes" class="btn-primary">Reload</button>
    <button id="sw-update-no" class="btn-secondary" aria-label="Dismiss">×</button>
  `;
  document.body.appendChild(toast);
  document.getElementById('sw-update-yes').addEventListener('click', () => {
    navigator.serviceWorker.controller?.postMessage({ type: 'SKIP_WAITING' });
    location.reload();
  });
  document.getElementById('sw-update-no').addEventListener('click', () => toast.remove());
}
