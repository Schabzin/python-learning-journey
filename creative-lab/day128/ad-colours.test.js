const test = require("node:test");
const assert = require("node:assert/strict");
const { decideColours } = require("./ad-colours.js");

test("Separaka navy + orange: allowed, colours chosen", () => {
    const result = decideColours({ background: "#14213d", accent: "#fca311" });
    assert.equal(result.ok, true);
    assert.equal(result.text, "#ffffff");
    assert.equal(result.ctaText, "#111111");
});

test("orange button on a white page: refused, button disappears", () => {
    const result = decideColours({ background: "#ffffff", accent: "#fca311" });
    assert.equal(result.ok, false);
    assert.match(result.problems[0], /disappears/);
});

test("no colours at all: refused, no crash", () => {
    const result = decideColours(undefined);
    assert.equal(result.ok, false);
});