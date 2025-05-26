/// <reference lib="webworker" />

const CACHE_NAME = 'web3-trading-cache-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico'
];

const API_CACHE_NAME = 'api-cache-v1';
const WS_CACHE_NAME = 'websocket-cache-v1';

declare const self: ServiceWorkerGlobalScope;

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name.startsWith('web3-trading-'))
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    // API requests caching strategy
    event.respondWith(
      caches.open(API_CACHE_NAME).then((cache) => {
        return fetch(event.request)
          .then((response) => {
            if (response.ok) {
              cache.put(event.request, response.clone());
            }
            return response;
          })
          .catch(() => {
            return cache.match(event.request);
          });
      })
    );
  } else if (event.request.url.includes('/ws/')) {
    // WebSocket fallback when offline
    event.respondWith(
      caches.open(WS_CACHE_NAME).then((cache) => {
        return cache.match(event.request).then((response) => {
          return response || new Response(JSON.stringify({
            type: 'error',
            message: 'You are currently offline'
          }), {
            headers: { 'Content-Type': 'application/json' }
          });
        });
      })
    );
  } else {
    // Static assets caching strategy
    event.respondWith(
      caches.match(event.request).then((response) => {
        if (response) {
          return response;
        }

        return fetch(event.request).then((response) => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });

          return response;
        });
      })
    );
  }
});