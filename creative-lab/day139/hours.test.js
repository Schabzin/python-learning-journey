const test = require("node:test");
const assert = require("node:assert/strict");
const { HOURS, toMinutes, isOpenAt } = require("./hours.js");

test("toMinutes turns a time into minutes since midnight", () => {
    assert.equal(toMinutes("00:00"), 0);
    assert.equal(toMinutes("08:30"), 510);
    assert.equal(toMinutes("19:00"), 1140);
});

test("open on Wednesday at 10:00", () => {
    const when = new Date(2026, 10, 4, 10, 0);
    assert.equal(isOpenAt(HOURS, when), true);
});

test("closed on Wednesday at 21:00", () => {
    const when = new Date(2026, 10, 4, 21, 0);
    assert.equal(isOpenAt(HOURS, when), false);
});