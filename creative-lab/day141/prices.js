const PRICES = [
    { item: "White bread", cents: 1300, asAt: "2026-10-31" },
];

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const STALE_AFTER_DAYS = 30;

function formatRand(cents) {
    const rands = Math.floor(cents / 100);
    const rest = cents % 100;
    return "R" + rands + "." + String(rest).padStart(2, "0");
}

function toDate(text) {
    const parts = text.split("-");
    return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
}

function formatDate(text) {
    const d = toDate(text);
    return d.getDate() + " " + MONTHS[d.getMonth()] + " " + d.getFullYear();
}

function daysOld(asAt, today) {
    const start = toDate(asAt);
    const end = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    return Math.round((end - start) / (24 * 60 * 60 * 1000));
}

function validatePrices(prices) {
    for (const p of prices) {
        if (!Number.isInteger(p.cents) || p.cents <= 0) {
            throw new Error("'" + p.item + "' price must be whole cents above 0, got " + p.cents);
        }
        if (!/^\d{4}-\d{2}-\d{2}$/.test(p.asAt)) {
            throw new Error("'" + p.item + "' date must look like 2026-10-31, got " + p.asAt);
        }
    }
    return true;
}

function priceLine(p, today) {
    const line = p.item + ": " + formatRand(p.cents);
    if (daysOld(p.asAt, today) > STALE_AFTER_DAYS) {
        return line + " (price as at " + formatDate(p.asAt) + " - may have changed, please check in store)";
    }
    return line + " (as at " + formatDate(p.asAt) + ")";
}

if (typeof module !== "undefined") {
    module.exports = { PRICES, formatRand, formatDate, daysOld, validatePrices, priceLine };
}