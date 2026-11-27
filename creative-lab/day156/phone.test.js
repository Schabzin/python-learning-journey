const test = require("node:test");
const assert = require("node:assert/strict");
const { toWhatsApp } = require("./phone.js");

test("a local number with spaces becomes 27...", () => {
    assert.equal(toWhatsApp("073 223 9762"), "27732239762");
});

test("+27 and dashes give the same answer", () => {
    assert.equal(toWhatsApp("+27 73-223-9762"), "27732239762");
});

test("a missing digit is refused with the count", () => {
    assert.throws(() => toWhatsApp("073 223 976"), /9 digits - a local number has 10/);
});

test("a number without 0 or +27 is refused", () => {
    assert.throws(() => toWhatsApp("732239762"), /must start with 0 or \+27/);
});

test("too many digits after +27 is refused", () => {
    assert.throws(() => toWhatsApp("+27 073 223 9762"), /12 digits - a \+27 number has 11/);
});