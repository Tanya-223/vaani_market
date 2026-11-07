// Minimal service worker — enough to make the app installable (PWA).
// Network-first; no aggressive caching so live data stays fresh.
self.addEventListener("install", (e) => self.skipWaiting());
self.addEventListener("activate", (e) => self.clients.claim());
self.addEventListener("fetch", (e) => { /* pass through to network */ });
