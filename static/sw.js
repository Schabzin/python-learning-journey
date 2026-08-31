const CACHE_VERSION = "v2";

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(
                cacheNames.map(function (name) {
                    if (name !== CACHE_VERSION) {
                        return caches.delete(name);
                    }
                })
            );
        })
    );
});

self.addEventListener("fetch", function (event) {
    event.respondWith(fetch(event.request));
});

self.addEventListener("push", function(event) {
    const data = event.data.json();
    self.ServiceWorkerRegistration.showNotification(data.title, {
        body: data.body,
        icon: "/static/icon-192.png"
    });
});