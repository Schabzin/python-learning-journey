const WHATSAPP = "27732239762";


function waLink(message) {
    return `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(message)}`;
}

function abPair(a, b) {
    if (a.code === b.code) {
        throw new Error(`Both variants use code ${a.code} - replies could not be told apart`);
    }
    return [a, b].map((variant) => ({
        code: variant.code,
        line: variant.line,
        link: waLink(`Hi 9EightEight, I saw your ad (${variant.code}). When are you open?`),
    }));
}

module.exports = { waLink, abPair };

if (require.main === module) {
    const pair = abPair(
        { code: "988A", line: "Good vibes" },
        { code: "988B", line: "Pull up, get your ride clean and enjoy our fresh meat" },
    );
    for (const variant of pair) {
        console.log(`${variant.code}: ${variant.line}`);
        console.log(`   ${variant.link}`);
    }
}