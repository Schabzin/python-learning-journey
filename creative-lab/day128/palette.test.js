const test = require("node:test");
const assert = require("node:assert/strict");
const { pickTextColour, checkPalette } = require("./palette.js");

test("dark text wins on orange", () => {
    assert.equal(pickTextColour("#fca311").colour, "#111111");
});

test("light text wins on navy", () => {
    assert.equal(pickTextColour("#14213d").colour, "#ffffff");
});

test("the Separaka palette passes every check", () => {
    assert.deepEqual(checkPalette({ background: "#14213d", accent: "#fca311", text: "#f5f0e1" }), []);
});

test("orange text on white fails twice, and suggests dark text", () => {
    const problems = checkPalette({ background: "#ffffff", accent: "#14213d", text: "#fca311" });
    assert.equal(problems.length, 2);
    assert.match(problems[0], /Try #111111/);
});

test("a bad colour gives a clear message, not a crash", () => {
    const problems = checkPalette({ background: "#14213d", accent: "orange", text: "#f5f0e1" });
    assert.equal(problems.length, 1);
    assert.match(problems[0], /not a valid colour/);
});