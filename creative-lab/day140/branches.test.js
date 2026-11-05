const test = require("node:test");
const assert = require("node:assert/strict");
const { UNKNOWN, BRANCHES, validateBranches, branchStatus, distanceKm, branchesByDistance } = require("./branches.js");

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

test("distance from a point to itself is 0", () => {
    assert.equal(distanceKm(-26.5, 27.8, -26.5, 27.8), 0);
});

test("one degree of latitude is about 111.2 km", () => {
    const d = distanceKm(0, 0, 1, 0);
    assert.ok(Math.abs(d - 111.195) < 0.01, "got " + d);
});

test("branches come back nearest first, and the original list is untouched", () => {
    const A = { name: "A", lat: 0, lng: 0 };
    const B = { name: "B", lat: 0, lng: 1 };
    const list = [A, B];
    const sorted = branchesByDistance(list, 0, 0.9);
    assert.equal(sorted[0].branch.name, "B");
    assert.equal(sorted[1].branch.name, "A");
    assert.equal(list[0].name, "A");
});

test("a branch with no map position is refused", () => {
    const broken = [{ ...BRANCHES[1], lat: undefined }];
    assert.throws(() => validateBranches(broken), /no map position/);
});