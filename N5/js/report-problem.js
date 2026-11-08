/*
 * report-problem.js - IMP-2: in-app "Report a problem" affordance.
 *
 * WHY THIS EXISTS
 * There was no in-app channel for a real learner to flag a wrong answer /
 * content error / UI bug; all changes were reviewer-driven. One real user
 * spotting a wrong answer is worth many audit cycles. This adds a small fixed
 * "Report a problem" button that opens a PRE-FILLED GitHub issue with the
 * current page URL + route/item id + recent runtime errors (from IMP-5's
 * error-monitor.js), so the maintainer can reproduce.
 *
 * CSP / behaviour
 * Same-origin script (script-src 'self'); builds a plain https link to
 * github.com and opens it in a new tab (link navigation is not blocked by CSP).
 * No inline script, no external fetch, no third-party SDK. The button is styled
 * via CSSStyleDeclaration property writes (not an inline <style> element or a
 * source style="" attribute), which CSP permits. GitHub prompts for login only
 * at submit time; the prefilled link itself needs no account.
 */
(function () {
  "use strict";
  var REPO = "gauravaccentureproducts/JLPTSuccess";

  function currentItem() {
    // Routes are history-mode paths since v1.17 (/JLPTSuccess/N5/learn/n5-017/,
    // .../reading/n5.read.003/); the router rewrites legacy #/... hashes to that
    // form on boot, so reading only location.hash reported "(home)" for every
    // page. Strip the SPA root (same /N5/ marker as router.js getBasePath())
    // and keep the hash as a fallback for a pre-boot legacy URL.
    var route = (location.pathname || "").replace(/^.*\/N5\//, "/") + (location.hash || "");
    var m = route.match(/(n5[-.][a-z0-9.\-]+)/i);
    if (m) return m[1];
    route = route.replace(/^[\/#]+/, "").replace(/\/+$/, "").replace(/\/?index\.html$/, "");
    return route || "(home)";
  }

  function issueUrl() {
    var item = currentItem();
    var lines = [
      "**What looks wrong?** (the error / typo / wrong answer / UI bug)",
      "",
      "",
      "---",
      "_Auto-filled - please keep:_",
      "- Page: " + location.href,
      "- Item: " + item,
      "- When: " + new Date().toISOString()
    ];
    try {
      var errs = (window.__recentErrors && window.__recentErrors(2)) || [];
      if (errs.length) {
        lines.push("- Recent runtime errors:");
        errs.forEach(function (e) { lines.push("  - [" + e.kind + "] " + e.message); });
      }
    } catch (e) { /* error-monitor not present: skip */ }
    return "https://github.com/" + REPO + "/issues/new"
      + "?labels=" + encodeURIComponent("content-error,user-report")
      + "&title=" + encodeURIComponent("Content/issue report: " + item)
      + "&body=" + encodeURIComponent(lines.join("\n"));
  }

  function build() {
    if (document.getElementById("report-problem-fab")) return;
    var a = document.createElement("a");
    a.id = "report-problem-fab";
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.textContent = "Report a problem";
    a.setAttribute("aria-label", "Report a problem with this page (opens GitHub)");
    // Style via CSSStyleDeclaration writes (CSP-permitted). Zen-Modern-aligned:
    // brand dark, weight 500, small radius, no shadow; 44px min touch target.
    var s = a.style;
    s.position = "fixed"; s.right = "12px"; s.bottom = "12px"; s.zIndex = "9998";
    s.background = "#14452a"; s.color = "#ffffff";
    s.font = "500 13px/1.1 system-ui, -apple-system, sans-serif";
    s.padding = "11px 14px"; s.borderRadius = "8px"; s.textDecoration = "none";
    s.minHeight = "44px"; s.display = "inline-flex"; s.alignItems = "center";
    s.boxSizing = "border-box"; s.opacity = "0.92";
    a.href = issueUrl();
    // Refresh the prefilled link to reflect the current route at click time.
    a.addEventListener("focus", function () { a.href = issueUrl(); });
    a.addEventListener("mouseenter", function () { a.href = issueUrl(); });
    document.body.appendChild(a);
    window.addEventListener("hashchange", function () { a.href = issueUrl(); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
