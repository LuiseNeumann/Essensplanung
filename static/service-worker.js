self.addEventListener("install", event => {
    console.log("Service Worker installiert");
});

self.addEventListener("fetch", event => {
    // Hier könntest du Offline-Caching implementieren (optional)
});
