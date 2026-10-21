const colourLib = (typeof require !== "undefined") ? require("./colour.js") : window;

const DARK = "#111111";
const LIGHT = "#ffffff";

function pickTextColour(backgroundHex, choices = [DARK, LIGHT]) {
    let best = null;
    for (const colour of choices) {
        const ratio = colourLib.contrastRatio(colour, backgroundHex);
        if (ratio === null) continue;
        if (best === null || ratio > best.ratio) {
            best = { colour: colour, ratio: ratio };
        }
    }
    return best;
}

function buttonTextFor(accentHex) {
    const best = pickTextColour(accentHex);
    return best === null ? null : best.colour;
}

function checkPalette(colours) {
    const pairs = [
        { name: "Body text on background", text: colours.text,       on: colours.background, large: false },
        { name: "Headline on background",  text: colours.text,       on: colours.background, large: true},
        { name: "Button text on accent",   text: buttonTextFor(colours.accent), on: colours.accent,     large: false}
    ];
    const problems = [];
    for (const p of pairs) {
        if (!colourLib.isReadable(p.text, p.on, p.large)) {
            const ratio = colourLib.contrastRatio(p.text, p.on);

            if (ratio === null) {
                problems.push(`${p.name}: not a valid colour (use #RRGGBB).`);
                continue;
            }

            const better = pickTextColour(p.on);
            problems.push(`${p.name}: ${ratio.toFixed(1)}:1 is too low. Try ${better.colour} (${better.ratio.toFixed(1)}:1).`);
        }
    }
    return problems;
}

if (typeof module !== "undefined") {
    module.exports = { pickTextColour, checkPalette };
}