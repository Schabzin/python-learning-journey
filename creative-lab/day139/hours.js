const HOURS = {
    0: ["08:00", "18:00"],
    1: ["08:00", "19:00"],
    2: ["08:00", "19:00"],
    3: ["08:00", "19:00"],
    4: ["08:00", "19:00"],
    5: ["08:00", "19:00"],
    6: ["08:00", "19:00"],
};

function toMinutes(text) {
    const parts = text.split(":");
    const h = Number(parts[0]);
    const m = Number(parts[1]);
    return h * 60 + m;
}

function isOpenAt(hours, when) {
    const pair = hours[when.getDay()];
    if (pair === undefined) {
        throw new Error("No hours for day " + when.getDay() + ". Check HOURS.");
    }
    if (pair === null) return false;

    const now = when.getHours() * 60 + when.getMinutes();
    const open = toMinutes(pair[0]);
    const close = toMinutes(pair[1]);
    return now >= open && now < close;
}

function validateHours(hours) {
    for (let day = 0; day <= 6; day++) {
        const pair = hours[day];
        if (pair === undefined) {
            throw new Error("Day " + day + " has no hours. Use null if the shop is closed that day.");
        }
        if (pair === null) continue;
        const open = toMinutes(pair[0]);
        const close = toMinutes(pair[1]);
        if (open >= close) {
            throw new Error("Day " + day + " opens at " + pair[0] + " but closes at " + pair[1] + ".");
        }
    }
    return true;
}

const DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function statusMessage(hours, when) {
    const today = when.getDay();
    const pair = hours[today];
    if (isOpenAt(hours, when)) {
        return "Open now - closes at " + pair[1];
    }
    const now = when.getHours() * 60 + when.getMinutes();
    if (pair !== null && now < toMinutes(pair[0])) {
        return "Closed - opens today at " + pair[0];
    }
    for (let ahead = 1; ahead <= 7; ahead++) {
        const day = (today + ahead) % 7;
        const next = hours[day];
        if (next === null) continue;
        const label = ahead === 1 ? "tomorrow" : DAY_NAMES[day];
        return "Closed - opens " + label + " at " + next[0];
    }
    return "Closed";
}

if (typeof module !== "undefined") {
    module.exports = { HOURS, toMinutes, isOpenAt, validateHours, statusMessage };
}