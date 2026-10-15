
const ACTION_VERBS = ["whatsapp", "call", "book", "visit", "order", "register", "get", "join"];

function words(text) {
    return (text || "").toLowerCase().match(/[a-z0-9']+/g) || [];
}

const RULES = [
    {
        id: "complete",
        level: "error",
        check: (b) => ["client", "audience", "insight", "proposition", "proof", "cta"]
          .filter((f) => typeof b[f] !== "string" || b[f].trim() === "")
          .map((f) => `Missing: ${f}`)
    },
    {
        id: "one-idea",
        level: "error",
        check: (b) => words(b.proposition).length >8
          ? ["Proposition over 8 words: one idea only."]
          : []
    },
    {
        id: "you-focus",
        level: "warning",
        check: (b) => {
            const w = words(b.proposition).concat(words(b.support));
            const you = w.filter((x) => x === "you" || x === "your").length;
            const we = w.filter((x) => x === "we" || x === "our" || x === "us").length;
            return we > you ? [`Talks about us (${we}) more than you (${you}).`] : [];
        }

    },
    {
        id: "insight-about-audience",
        level: "warning",
        check: (b) => b.client && (b.insight || "").toLowerCase().includes(b.client.toLowerCase())
          ? ["Insight mentions the client: an insight is a truth about the AUDIENCE."]
          : []
    },
    {
        id: "cta-starts-with-action",
        level: "warning",
        check: (b) => ACTION_VERBS.includes(words(b.cta)[0])
          ? []
          : ["CTA should start with an action: WhatsApp, Call, Book..."]
    }
];

function lintBrief(brief) {
    const result = { errors: [], warnings: [] };
    for (const rule of RULES) {
        const messages = rule.check(brief);
        const bucket = rule.level === "error" ? result.errors : result.warnings;
        bucket.push(...messages);
    }
    return result;
}

if (typeof module !== "undefined") {
    module.exports = { lintBrief, words, RULES };
}