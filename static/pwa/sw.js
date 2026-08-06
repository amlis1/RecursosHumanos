/* Service Worker - Gestor RRHH (PWA)
 * Estrategia:
 *  - Precarga del "app shell" (núcleo visual + páginas clave).
 *  - Navegaciones: network-first con fallback a caché y a /offline.
 *  - Estáticos (same-origin y CDNs conocidos): cache-first con respaldo de red.
 * Bump CACHE_VERSION para forzar la actualización tras cada despliegue.
 */
const CACHE_VERSION = '__PWA_VERSION__';
const PRECACHE = 'rrhh-precache-' + CACHE_VERSION;
const RUNTIME = 'rrhh-runtime-' + CACHE_VERSION;

const OFFLINE_URL = '/static/pwa/offline.html';

const APP_SHELL = [
  OFFLINE_URL,
  '/static/pwa/manifest.json',
  '/static/pwa/icon-192.png',
  '/static/pwa/icon-512.png',
  '/static/pwa/icon-512-maskable.png',
  '/static/pwa/apple-touch-icon.png',
  '/static/assets/css/bootstrap.min.css',
  '/static/assets/css/fontawesome-all.min.css',
  '/static/assets/css/style.css',
  '/static/assets/js/vendor/modernizr-3.5.0.min.js',
  '/static/assets/js/popper.min.js',
  '/static/assets/js/bootstrap.min.js',
  '/static/assets/js/plugins.js',
  '/static/assets/js/main.js'
];

self.addEventListener('install', function (event) {
  event.waitUntil(
    caches.open(PRECACHE)
      .then(function (cache) {
        // Precarga tolerante: si un recurso falla no se rompe la instalación
        // del Service Worker (necesario para que el navegador ofrezca instalar).
        return Promise.all(
          APP_SHELL.map(function (url) {
            return cache.add(url).catch(function () {});
          })
        );
      })
      .then(function () {
        return self.skipWaiting();
      })
  );
});

self.addEventListener('activate', function (event) {
  event.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(
          keys
            .filter(function (key) {
              return key.startsWith('rrhh-') && key !== PRECACHE && key !== RUNTIME;
            })
            .map(function (key) {
              return caches.delete(key);
            })
        );
      })
      .then(function () {
        return self.clients.claim();
      })
  );
});

function isKnownCdn(hostname) {
  return [
    'cdn.jsdelivr.net',
    'cdn.datatables.net',
    'code.jquery.com',
    'cdnjs.cloudflare.com'
  ].some(function (cdn) {
    return hostname === cdn || hostname.endsWith('.' + cdn);
  });
}

self.addEventListener('message', function (event) {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', function (event) {
  var request = event.request;

  if (request.method !== 'GET') {
    return;
  }

  var url = new URL(request.url);

  // Solo manejamos peticiones a nuestro origen y a los CDNs conocidos.
  if (url.origin !== self.location.origin && !isKnownCdn(url.hostname)) {
    return;
  }

  // Navegaciones a páginas: network-first con fallback offline.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then(function (response) {
          if (response && response.status === 200) {
            var copy = response.clone();
            caches.open(RUNTIME).then(function (cache) {
              cache.put(request, copy);
            });
          }
          return response;
        })
        .catch(function () {
          return caches.match(request).then(function (cached) {
            return cached || caches.match(OFFLINE_URL);
          });
        })
    );
    return;
  }

  // Assets estáticos: cache-first.
  event.respondWith(
    caches.match(request).then(function (cached) {
      if (cached) {
        return cached;
      }
      return fetch(request).then(function (response) {
        if (response && response.status === 200) {
          var copy = response.clone();
          caches.open(RUNTIME).then(function (cache) {
            cache.put(request, copy);
          });
        }
        return response;
      });
    })
  );
});
