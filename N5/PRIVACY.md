# Privacy

This app does not collect, transmit, or store any personal data on a remote server.

## What we do NOT do

- **No accounts, no login.** You can use every feature without identifying yourself.
- **No telemetry, no analytics.** No page-view, click, or session data is sent anywhere.
- **No third-party scripts.** The app loads only from this domain (enforced by Content-Security-Policy in `index.html`).
- **No tracking cookies.** Nothing is set in `document.cookie`.
- **No remote API calls during normal use.** Once the page is loaded (or cached by the service worker for offline use), every interaction is handled locally in your browser.

## What stays on your device

All learning state - answers you've given, items you've marked known, your study streak, test results, settings - is held only in your browser's `localStorage`, namespaced under `jlpt-n5-tutor:*`. It never leaves your device.

You can:

- **Export** your progress at any time via Settings → Export progress (downloads a `.json` file you control).
- **Import** a previously exported file to restore state on the same device or transfer to a different one.
- **Wipe** everything by clearing the site's storage in your browser (DevTools → Application → Local Storage), or via Settings → Reset progress.

## Audio

Audio assets (MP3 files for grammar examples, listening drills, reading passages) are static files served from the same origin. They are not streamed from a third party.

## Hosting (what GitHub may log)

This site is hosted on **GitHub Pages** (`github.io` domain). When your browser fetches a page or asset from this site, GitHub's servers receive the standard HTTP request information that any web server receives:

- Your **IP address** (used to route the response back to you)
- The **URL** you requested
- Your browser's **User-Agent** and **Referer** headers (sent automatically by your browser)
- Approximate **request timestamp** and **bytes transferred**

This information is processed and may be retained by GitHub on their servers, governed by [GitHub's Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement), not by us. We (the app authors) do not see, log, or have access to that data.

For GDPR purposes (Articles 13/14 information-obligation), this means:

- **Data controller for hosting-layer logs:** GitHub, Inc. (a US-based provider that participates in the EU-US Data Privacy Framework).
- **Purpose:** delivering the static files of this app to your browser, abuse prevention, and aggregate hosting analytics for GitHub's own service operation.
- **Legal basis:** GitHub's legitimate interests in operating a hosting service; their privacy statement details retention periods and your rights to access, rectify, or delete server-side logs.
- **No data is shared between us and GitHub.** We do not query, request, or receive any user-level data from GitHub's logs.

If this hosting-layer data flow is unacceptable for your use case, you can **self-host** the app (it ships as static files in this repository: see `docs/SELF-HOST.md`). Self-hosted instances eliminate the GitHub hosting layer entirely; the only logs would be whatever your chosen host produces.

## Independently verifiable

Open the browser's Network tab and watch a session. You will see only same-origin requests for the assets the app needs to run (HTML, CSS, JS, JSON, fonts, MP3s, SVGs). No third-party hosts, no analytics endpoints, no tracking pixels. The build does not inject analytics or trackers post-deploy.

## Updates

If this app's privacy posture ever changes, the change will be documented in the `CHANGELOG.md` and announced on the home page before it ships.

---

*Last updated: 2026-05-11 (legal-vetting F-9, added Hosting section disclosing GitHub Pages server-side IP logging per GDPR Art 13/14 information-obligation).*
