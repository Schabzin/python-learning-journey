const test = require("node:test");
const assert = require("node:assert/strict");
const { HOURS, toMinutes, isOpenAt, validateHours, statusMessage } = require("./hours.js");

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

test("edges on Wednesday: 07:59 closed, 08:00 open, 18:59 open, 19:00 closed", () => {
    assert.equal(isOpenAt(HOURS, new Date(2026, 10, 4, 7, 59)), false);
    assert.equal(isOpenAt(HOURS, new Date(2026, 10, 4, 8, 0)), true);
    assert.equal(isOpenAt(HOURS, new Date(2026, 10, 4, 18, 59)), true);
    assert.equal(isOpenAt(HOURS, new Date(2026, 10, 4, 19, 0)), false);
});

test("Sunday closes at 18:00, not 19:00", () => {
    assert.equal(isOpenAt(HOURS, new Date(2026, 10, 8, 17, 59)), true);
    assert.equal(isOpenAt(HOURS, new Date(2026, 10, 8, 18, 30)), false);
});

test("the real HOURS pass the check", () => {
    assert.equal(validateHours(HOURS), true);
});

test("a missing day is refused, not treated as closed", () => {
    const broken = { ...HOURS };
    delete broken[3];
    assert.throws(() => validateHours(broken), /Day 3 has no hours/);
});

test("a day that opens after it closes is refused", () => {
    const broken = { ...HOURS, 2: ["19:00", "08:00"] };
    assert.throws(() => validateHours(broken), /Day 2 opens at 19:00/);
});

test("a closed day (null) is allowed and reads as closed", () => {
    const closedSunday = { ...HOURS, 0: null };
    assert.equal(validateHours(closedSunday), true);
    assert.equal(isOpenAt(closedSunday, new Date(2026, 10, 8, 10, 0)), false);
})

test("open: says when it closes (Sunday closes earlier)", () => {
    assert.equal(statusMessage(HOURS, new Date(2026, 10, 4, 10, 0)), "Open now - closes at 19:00");
    assert.equal(statusMessage(HOURS, new Date(2026, 10, 8, 10, 0)), "Open now - closes at 18:00");
});

test("early morning: opens today", () => {
    assert.equal(statusMessage(HOURS, new Date(2026, 10, 4, 6, 30)), "Closed - opens today at 08:00");
});

test("Saturday night wraps round to Sunday", () => {
    assert.equal(statusMessage(HOURS, new Date(2026, 10, 7, 20, 0)), "Closed - opens tomorrow at 08:00");
})

test("a closed Sunday is skipped: opens Monday, by name", () => {
    const closedSunday = { ...HOURS, 0: null };
    assert.equal(statusMessage(closedSunday, new Date(2026, 10, 7, 20, 0)), "Closed - opens Monday at 08:00");
}); 