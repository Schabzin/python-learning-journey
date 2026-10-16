const LETTERS = "ABCDEFGH";

function buildWaLink(number, message) {
    return `https://wa.me/${number}?text=${encodeURIComponent(message)}`;
}

function makeVariants(brief, propositions, number) {
    return propositions.map((proposition, i) => {
        const code = `AD-${LETTERS[i]}`;
        return {
            code: code,
            brief: { ...brief, proposition: proposition },
            waLink: buildWaLink(number, `Hi, I saw your ad (${code}). I'd like a website.`)
        };
    });
}

function tally(messages, codes) {
    const counts = {};
    for (const code of codes) counts[code] = 0;
    for (const text of messages) {
        for (const code of codes) {
            if (text.toUpperCase().includes(code)) counts[code] += 1;
        }
    }
    return counts;
}

function pickWinner(counts, minTotal = 30, minShare = 0.6) {
    let total = 0;
    let topCode = null;
    let topCount = -1;
    for (const [code, n] of Object.entries(counts)) {
        total += n;
        if (n > topCount) {
            topCode = code;
            topCount = n;
        }
    }
    if (total < minTotal) {
        return { winner: null, reason: `Not enough data: ${total} of ${minTotal} replies.` };
    }
    if (topCount / total < minShare) {
        return { winner: null, reason: "Too close to call." };
    }
    return { winner: topCode, reason: `${topCode} brought ${topCount} of ${total} replies.` };
}

if (typeof module !== "undefined") {
    module.exports = { buildWaLink, makeVariants, tally, pickWinner };
}
