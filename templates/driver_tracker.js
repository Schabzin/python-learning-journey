const PING_URL = "/api/taxi/ping";
const MIN_INTERVAL_MS = 30000;
const MAX_ACCURACY_M = 100;

let watchId = null;
let lastSentAt = 0;
let sending = false;

const button = document.getElementById("tracking-btn");
const statusLine = document.getElementById("tracking-status");

function showStatus(message) {
    statusLine.textContent = message;
}

function stopTracking(message) {
    if (watchId !== null) {
        navigator.geolocation.clearWatch(watchId);
        watchId = null;
    }
    button.textContent = "Start shift tracking";
    showStatus(message);
}

async function sendPing(position) {
    const now = Date.now();
    if (sending || now - lastSentAt < MIN_INTERVAL_MS) {
        return;
    }
    if (position.coords.accuracy > MAX_ACCURACY_M) {
        showStatus(`Weak GPS signal (±${Math.round(position.coords.accuracy)} m). waiting for a better reading...`);
        return;
    }

    const body = {
        lat: position.coords.latitude,
        lon: position.coords.longitude,
        recorded_at: new Date(position.timestamp).toISOString(),
        accuracy_m: position.coords.accuracy,
    };

    sending = true;
    lastSentAt = now;
    try {
        const response = await fetch(PING_URL, {
          method: "POST",
          headers: {"Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const result = await response.json().catch(() => ({ error: `HTTP ${response.status}` }));

        if (response.status === 401 || response.status === 403) {
            stopTracking(`Tracking stopped: ${result.error}`);
            return;
        }
        if (!response.ok) {
            showStatus(`Ping rejected: ${result.error}`);
            return;
        }
        const time = new Date().toLocaleTimeString("en-ZA");
        showStatus(`Tracking ON. Last ping sent at ${time}.`);
    } catch (err) {
        showStatus("No connection. Will try again on the next reading.");
    } finally {
        sending = false;
    }
}

function handleGpsError(error) {
    if (error.code === error.PERMISSION_DENIED) {
        stopTracking("Location permission denied. Allow location for this site to track.");
    } else {
        showStatus(`GPS problem: ${error.message}`);
    }
}

function startTracking() {
    if (!("geolocation" in navigator)) {
        showStatus("This phone's browser cannot share location.");
        return;
    }
    watchId = navigator.geolocation.watchPosition(sendPing, handleGpsError, {
        enableHighAccuracy: true,
        maximumAge: 10000,
        timeout: 20000,
    });
    button.textContent = "Stop shift tracking";
    showStatus("Starting GPS...");
}

button.addEventListener("click", () => {
    if (watchId === null) {
        startTracking();
    } else {
        startTracking("Tracking OFF.");
    }
});