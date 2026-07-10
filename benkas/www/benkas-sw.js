/* Copyright (c) 2026, Benkas and Contributors — GPL-3.0
 *
 * App service worker for the /benkas PWA.
 *
 * Purpose: make the app INSTALLABLE (Chromium needs a service worker with a
 * fetch handler that controls the manifest scope, and the push SW lives at the
 * /assets scope so it cannot). Served at the site root (/benkas-sw.js) so it
 * can legally claim scope "/benkas".
 *
 * Strategy: NETWORK-FIRST for navigations + same-origin GETs, so online users
 * ALWAYS get the freshest shell/bundle (deliberately the opposite of a precache
 * SW that serves stale shells). /api is never touched by the SW. Cache is only
 * an offline fallback. No stale-shell risk.
 */
var SW_VERSION = "benkas-app-v1";
var SHELL_CACHE = "benkas-shell-" + SW_VERSION;
var OFFLINE_URL = "/benkas";

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(SHELL_CACHE)
      .then(function (c) { return c.add(OFFLINE_URL).catch(function () {}); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.map(function (k) {
        if (k.indexOf("benkas-shell-") === 0 && k !== SHELL_CACHE) return caches.delete(k);
      }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // only same-origin
  if (url.pathname.indexOf("/api/") === 0) return;    // never intercept API calls

  // Network-first: try the network, fall back to cache only when offline.
  e.respondWith(
    fetch(req).then(function (res) {
      if (res && res.status === 200 && res.type === "basic") {
        var copy = res.clone();
        caches.open(SHELL_CACHE).then(function (c) { c.put(req, copy); }).catch(function () {});
      }
      return res;
    }).catch(function () {
      return caches.match(req).then(function (cached) {
        return cached || (req.mode === "navigate" ? caches.match(OFFLINE_URL) : undefined);
      });
    })
  );
});
