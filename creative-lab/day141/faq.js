const pricesLib = (typeof require !== "undefined") ? require("./prices.js") : { priceLine };

const WHATSAPP_EVATON = "081 065 8453";

function toInternational(local) {
    const digits = local.replace(/\D/g, "");
    if (digits.length !== 10 || digits[0] !== "0") {
        throw new Error("SA number must be 10 digits starting with 0, got " + local);
    }
    return "27" + digits.slice(1);
}

function whatsappLink(localNumber, message) {
    return "https://wa.me/" + toInternational(localNumber) + "?text=" + encodeURIComponent(message);
}

function buildFaq(prices, today) {
    return [
        {
            q: "How much is the white bread?",
            a: pricesLib.priceLine(prices[0], today),
            ask: "Hi, what are today's bread prices?",
        },
        {
            q: "Where are you?",
            a: "Two branches: Evaton (1068 Sakies Adams Road) and Zone 7 (Shop No. 13, Zone 7B, Sebokeng). Tap 'Use my location' to find the nearest.",
            ask: "Hi, which branch is closest to me?",
        },
        {
            q: "How do I invest or join the stokvel?",
            a: "We answer this one personally. Tap below to ask us on WhatsApp.",
            ask: "Hi, I'd like to know how to join or invest in Isicholo Investment Stokvel.",
        },
    ];
}

if (typeof module !== "undefined") {
    module.exports = { WHATSAPP_EVATON, toInternational, whatsappLink, buildFaq };
}