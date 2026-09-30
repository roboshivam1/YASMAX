/*
 * File: web/sw.js
 *
 * The service worker: what makes YASMAX work offline and installable.
 *
 * - On install it downloads every file listed in precache.json (written
 *   by tools/build_site.py: the app, engine.zip and the Pyodide runtime)
 *   into a cache named after the build.
 * - Afterwards every request is answered from that cache first, so the
 *   app starts without internet. Anything not cached goes to the network.
 * - A new deploy has a new BUILD id, so the browser installs a fresh
 *   worker, which fills a new cache and deletes the old ones. The page
 *   then shows "A new version of YASMAX is ready" (main.js).
 * Only registered in published builds (BUILD is stamped, never "dev").
 */

const BUILD = "dev";
const CACHE = `yasmax-${BUILD}`;

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const list = await (await fetch("precache.json", { cache: "no-store" })).json();
      const cache = await caches.open(CACHE);
      await cache.addAll(list);
      await self.skipWaiting();
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      for (const name of await caches.keys()) {
        if (name.startsWith("yasmax-") && name !== CACHE) await caches.delete(name);
      }
      await self.clients.claim();
    })(),
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(
    (async () => {
      const cache = await caches.open(CACHE);
      const hit = await cache.match(event.request, { ignoreSearch: true });
      if (hit) return hit;
      const response = await fetch(event.request);
      if (response.ok && new URL(event.request.url).origin === self.location.origin) {
        cache.put(event.request, response.clone());
      }
      return response;
    })(),
  );
});
