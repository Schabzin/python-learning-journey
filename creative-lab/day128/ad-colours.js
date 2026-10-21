const colourTools = (typeof require !== "undefined") ? require("./colour.js") : window;
const paletteTools = (typeof require !== "undefined") ? require("./palette.js") : window;

function decideColours(colours) {
    if (!colours) {
        return { ok: false, problems: ["No colours in the brief: add a background and an accent."] };
    }

    const text = paletteTools.pickTextColour(colours.background);
    const ctaText = paletteTools.pickTextColour(colours.accent);

    const problems = [];
    if (text === null) problems.push("Background is not a valid colour (use #RRGGBB).");
    if (ctaText === null) problems.push("Accent is not a valid colour (use #RRGGBB).");
    if (problems.length > 0) return { ok: false, problems: problems };

    if (text.ratio < 4.5) {
        problems.push(`Text only reaches ${text.ratio.toFixed(1)}:1 on this background (needs 4.5). Pick a darker or lighter background.`);
    }
    if (ctaText.ratio < 4.5) {
        problems.push(`Button text only reaches ${ctaText.ratio.toFixed(1)}:1 on this accent (needs 4.5). Pick a darker or lighter accent.`);
    }
    const buttonOnPage = colourTools.contrastRatio(colours.accent, colours.background);
    if (buttonOnPage < 3) {
        problems.push(`The button disappears into the page: ${buttonOnPage.toFixed(1)}:1 (needs 3).`);
    }

    return problems.length > 0
        ? { ok: false, problems: problems }
        : { ok: true, text: text.colour, ctaText: ctaText.colour };
}

if (typeof module !== "undefined") {
    module.exports = { decideColours };
}