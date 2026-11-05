const test = require("node:test");
const assert = require("node:assert/strict");
const { UNKNOWN, BRANCHES, validateBranches, branchStatus } = require("./branches.js");

test("the real branches pass the check", () => {
    assert.equal(validateBranches(BRANCHES), true);
});

test("Zone 7 uses its hours: open on Wednesday at 10:00", () => {
    const when = new Date(2026, 10, 4, 10, 0);
    assert.equal(branchStatus(BRANCHES[1], when), "Open now - closes at 19:00");
});

test("Evaton's hours are unknown: never guess, ask them to call", () => {
    const when = new Date(2026, 10, 4, 10, 0);
    assert.equal(branchStatus(BRANCHES[0], when), "Hours not confirmed - please call 016 023 0857");
});

test("a branch with no phone is refused", () => {
    const broken = [{ ...BRANCHES[0], phone: "" }];
    assert.throws(() => validateBranches(broken), /missing a name, address or phone/);
});

test("a branch with broken hours is refused", () => {
    const broken = [{ ...BRANCHES[1], hours: {} }];
    assert.throws(() => validateBranches(broken), /Day 0 has no hours/);
});

test("an empty list is refused", () => {
    assert.throws(() => validateBranches([]), /no branches/);
});

test("a mistyped UNKNOWN is refused with a clear message", () => {
    const broken = [{ ...BRANCHES[0], hours: "unknwon" }];
    assert.throws(() => validateBranches(broken), /has hours 'unknwon'/);
});