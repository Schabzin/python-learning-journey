const test = require("node:test");
const assert = require("node:assert/strict");
const { hexToRgb, contrastRatio, isReadable } = require("./colour.js");

function near(actual, expected, tolerance = 0.01) {
    return Math.abs(actual - expected) <= tolerance;
}

test("hex becomes three numbers", () => {
    assert.deepEqual(hexToRgb("#fca311"), { r: 252, g: 163, b: 17 });
    assert.equal(hexToRgb("orange"), null);
});

test("black on white is the maximum, 21", () => {
    assert.ok(near(contrastRatio("#000000", "#ffffff"), 21));
});

test("a colour on itself is 1: invisible", () => {
    assert.ok(near(contrastRatio("#fca311", "#fca311"), 1));
});

test("order doesn't matter", () => {
    assert.ok(near(contrastRatio("#14213d", "#fca311"), contrastRatio("#fca311", "#14213d")));
});

test("the Day 126 bug would have been caught", () => {
    assert.equal(isReadable("#fca311", "#fca311"), false);
    assert.equal(isReadable("#14213d", "#fca311"), true);
});

test("white text on orange is NOT readable", () => {
    assert.equal(isReadable("#ffffff", "#fca311"), false);
});