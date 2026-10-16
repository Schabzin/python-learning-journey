const test = require("node:test");
const assert = require("node:assert/strict");
const { buildWaLink, makeVariants, tally, pickWinner } = require("./variants.js");

const BRIEF = { client: "Separaka Holdings", cta: "WhatsApp 073 223 9762" };
const NUMBER = "27732239762";

test("WhatsApp link makes the message safe", () => {
    assert.equal(buildWaLink(NUMBER, "Hi (AD-A)"), "https://wa.me/27732239762?text=Hi%20(AD-A)");
});

test("each variant gets its own code and keeps the rest of the brief", () => {
    const v = makeVariants(BRIEF, ["Be found before they visit.", "Parents search before they visit."], NUMBER);
    assert.equal(v.length, 2);
    assert.equal(v[0].code, "AD-A");
    assert.equal(v[1].code, "AD-B");
    assert.equal(v[1].brief.client, "Separaka Holdings");
    assert.match(v[1].waLink, /AD-B/);
});

test("tally counts codes, ignoring upper and lower case", () => {
    const counts = tally(["Hi I saw AD-A", "hello ad-b", "AD-A please", "just hi"], ["AD-A", "AD-B"]);
    assert.deepEqual(counts, { "AD-A": 2, "AD-B": 1 });
});

test("no winner on too little data", () => {
    assert.equal(pickWinner({"AD-A": 3, "AD-B": 1 }).winner, null);
});

test("a clear winner on enough data", () => {
    assert.equal(pickWinner({ "AD-A": 25, "AD-B": 10 }).winner, "AD-A");
});