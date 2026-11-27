const { copyProblems } = require("../day154/ladder.js");
const { rankLines } = require("../day155/rank.js");

const brief = {
    audience: "Youngins, around the Vaal",
    feature: "Fresh Kotas",
    benefit: "Get fancy kota delivered to your door",
    proof: "We Deliver the whole Vaal. Delivery fee by area TBC",
    cta: "WhatsApp your order",
}

const headlines = [
    "Hot, fresh, and on the way to your door!",
    "Delicious, tasty and straight to your door",
    "Served with love, to your door",
    "Great taste, delivered while it's hot",
    "Fancy Kota, since 2020",
    "If you see the red bike, you know it's hot",
    "If you see the red bike, it's hot",
];

const BUDGET = 8;

function caption(cta, number, code) {
    const message = `Hi FTS, I saw your ad (${code}). I'd like to order.`;
    const link = `https://wa.me/${number}?text=${encodeURIComponent(message)}`;
    return `${cta}: ${link}`;
}

console.log("Brief:", copyProblems(brief));
rankLines(headlines, BUDGET).forEach((result, index) => {
    const mark = result.problems.length === 0 ? "clean" : result.problems.join(": ");
    console.log(`${index + 1}. ${result.line} [${mark}]`);
});
console.log(caption(brief.cta, "27732239762", "FTS1"));