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
    let title = "Separaka";
    let body = "You have a new alert";
    try {
        const data = event.data.json();
        title = data.title || title;
        body = data.body || body;
    } catch (e) {
        body = event.data.text();
    }
    self.ServiceWorkerRegistration.showNotification(title, {
        body: body,
        icon: "/static/icon-192.png"
    });
});