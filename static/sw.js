if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/sw.js")
        .then(function () { console.log("Service worker registered"); })
        .catch(function (error) { console.error("Service worker registration failed:", error); });
}