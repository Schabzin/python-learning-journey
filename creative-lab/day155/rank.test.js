const test = require("node:test");
const assert = require("node:assert/strict");
const { lineProblems, rankLines } = require("./rank.js");

test("a specific line inside the budget has no problems", () => {
    assert.deepEqual(lineProblems("Your car gets washed while you eat", 10), []);
});

test("an abstract word is flagged", () => {
    assert.deepEqual(lineProblems("Quality you can trust", 10),
      ['abstract: "quality" - show it, don\'t name it']);
});

test("a line over the word budget budget is flagged", () => {
    assert.deepEqual(lineProblems("one two three four five six", 5),
      ["too long: 6 words, budget 5"]);
});

test("fewest problems ranks first", () => {
    const ranked = rankLines(["The best quality kota", "Kota hot from the pot"], 10);
    assert.equal(ranked[0].line, "Kota hot from the pot");
    assert.equal(ranked[1].problems.length, 2);
});

test("a tie goes to the shorter line", () => {
    const ranked = rankLines(["Washed while you eat at 9EightEight", "Washed while you eat"], 10);
    assert.equal(ranked[0].line, "Washed while you eat");
});

test("ranking does not change the original list", () => {
    const lines = ["The best kota", "Kota hot from the pot"];
    rankLines(lines, 10);
    assert.deepEqual(lines, ["The best kota", "Kota hot from the pot"]);
});