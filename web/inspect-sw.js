// Offline support for the inspection page: pages are fetched from the network first (cached copy when offline);
// sheets, styles, scripts and fonts are served from the cache and refreshed in the background.
const CACHE = 'bridge-inspection-v4';
const SHELL = ['./inspect.html', './ui.css?v=insp3', './inspect.css?v=insp3', './inspect-config.js?v=insp3', './inspect.bundle.js?v=insp3',
  './favicon.svg', './vendor/fonts/ibm-plex-sans-latin.woff2', './vendor/fonts/ibm-plex-mono-400-latin.woff2'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(SHELL.map(u => c.add(u).catch(() => null)))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;   // cloud API calls go straight out
  if (req.mode === 'navigate') {
    e.respondWith(fetch(req).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return r; })
      .catch(() => caches.match(req).then(r => r || caches.match('./inspect.html'))));
    return;
  }
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(req);
    const fresh = fetch(req).then(r => { if (r.ok) c.put(req, r.clone()); return r; }).catch(() => hit);
    return hit || fresh;
  }));
});
