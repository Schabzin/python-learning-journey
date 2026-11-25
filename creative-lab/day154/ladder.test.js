import { test } from "node:test";
import assert from "node:assert/strict";
import { copyProblems } from "./ladder.js";

const GOOD = {
    audience: "Families in the Vaal planning a December day out",
    feature: "Two pools and braai stands",
    benefit: "The kids swim while you braai, all day, for one entry fee",
    proof: "R50 entry, open 09:00 to 18:00, every day in December",
    cta: "Book your braai stand on WhatsApp",
};

test("a complete, specific brief has no problems", () => {
    assert.deepEqual(copyProblems(GOOD), []);
});

test("a missing or blank rung is reported by name", () => {
    assert.deepEqual(copyProblems({ ...GOOD, proof: "  "}), ["proof: missing"]);
});

test("a cliche fails the competitor test", () => {
    assert.deepEqual(copyProblems({ ...GOOD, benefit: "A MEMORABLE day for the family" }),
      ['benefit: "memorable" - any venue could say this']);
});

test("whole words only: bestseller is not best", () => {
    assert.deepEqual(copyProblems({ ...GOOD, proof: "Our bestseller is the R60 platter"}), []);
});

test("a vague call to action is caught twice", () => {
    const problems = copyProblems({ ...GOOD, cta: "Discover what awaits you" });
    assert.equal(problems.length, 2);
    assert.ok(problems[0].startsWith('cta: "awaits"'));
    assert.ok(problems[1].startsWith('cta: starts with "discover"'));
});