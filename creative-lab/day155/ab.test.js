const test = require("node:test");
const assert = require("node:assert/strict");
const { waLink, abPair } = require("./ab.js");

const A = { code: "988A", line: "Good vibes" };
const B = { code: "988B", line: "Pull up, get your ride clean and enjoy our fresh meat" };

test("a link goes to the right WhatsApp number", () => {
    assert.ok(waLink("Hi").startsWith("https://wa.me/27732239762?text="));
});

test("each variant's message carries its own code", () => {
    const [first, second] = abPair(A, B);
    const message = decodeURIComponent(second.link.split("text=")[1]);
    assert.ok(message.includes("(988B)"));
    assert.ok(!first.link.includes("988B"));
});

test("the two messages differ ONLY by the code", () => {
    const [first, second] = abPair(A, B);
    const one = decodeURIComponent(first.link.split("text=")[1]).replace("988A", "CODE");
    const two = decodeURIComponent(second.link.split("text=")[1]).replace("988B", "CODE");
    assert.equal(one, two);
});

test("the same code twice is refused", () => {
    assert.throws(() => abPair(A, { ...B, code: "988A" }), /could not be told apart/);
});