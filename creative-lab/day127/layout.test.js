const test = require("node:test");
const assert = require("node:assert/strict");
const { wrapText, fitText } = require("./layout");

function fakeMeasure(text, font) {
    const size = Number(font.match(/(\d+)px/)[1]);
    return text.length * size * 0.5;
}

const FONT_20 = "bold 20px Arial";

test("short text stays on one line", () => {
    assert.deepEqual(wrapText(fakeMeasure, "Hi there", 200, FONT_20), ["Hi there"]);
});

test("text break at the width limit", () => {
    const lines = wrapText(fakeMeasure, "Your business online", 150, FONT_20);
    assert.deepEqual(lines, ["Your business", "online"]);
});

test("one word wider than the box returns null", () => {
    assert.equal(wrapText(fakeMeasure, "Supercalifragilistic", 100, FONT_20), null);
});

test("fitText shrinks to the biggest size that fits", () => {
    const result = fitText(fakeMeasure, "Your business online in 7 days.", {
        maxWidth: 300, maxLines: 2, maxSize: 40, minSize: 20, weight: "bold"
    });
    assert.equal(result.size, 34);
    assert.deepEqual(result.lines, ["Your business", "online in 7 days."]);
});

test("fitText returns null when nothing fits", () => {
    const result = fitText(fakeMeasure, "Supercalifragilisticexpialidocious", {
        maxWidth: 100, maxLines: 1, maxSize: 40, minSize: 20, weight: "bold"
    });
    assert.equal(result, null);
});

test("empty text returns null, not an empty success", () => {
    const result = fitText(fakeMeasure, "", {
        maxWidth: 300, maxLines: 2, maxSize: 40, minSize: 20, weight: "bold"
    });
    assert.equal(result, null);
});