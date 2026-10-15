function wrapText(measure, text, maxWidth, font) {
    if (typeof text !== "string" || text.trim() === "")
    return null;
    const words = text.trim().split(/\s+/);
    const lines = [];
    let line = "";

    for (const word of words) {
        if (measure(word, font) > maxWidth) return null;
        const test = line === "" ? word : line + " " + word;
        if (measure(test, font) <= maxWidth) {
            line = test;
        } else {
            lines.push(line);
            line = word;
        }
    }
    if (line !== "") lines.push(line);
    return lines;
}

function fitText(measure, text, opts) {
    for (let size = opts.maxSize; size >= opts.minSize; size -= 2) {
        const font = `${opts.weight} ${size}px Arial`;
        const lines = wrapText(measure, text, opts.maxWidth, font);
        if (lines !== null && lines.length <= opts.maxLines) {
            return { size: size, lines: lines, lineHeight: Math.round(size * 1.15) };
        }
    }
    return null;
}

if (typeof module !== "undefined") {
    module.exports = { wrapText, fitText };
}