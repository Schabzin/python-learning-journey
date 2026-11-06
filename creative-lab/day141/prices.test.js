const test = require("node:test");
const assert = require("node:assert/strict");
const { PRICES, formatRand, formatDate, daysOld, validatePrices, priceLine } = require("./prices.js");

test("why we store cents: decimal money goes wrong", () => {
    assert.notEqual(0.1 + 0.2, 0.3);
});

test("formatRand shows rands and two-digit cents", () => {
    assert.equal(formatRand(1300), "R13.00");
    assert.equal(formatRand(1850), "R18.50");
    assert.equal(formatRand(5), "R0.05");
    assert.equal(formatRand(100000), "R1000.00");
});

test("dates read the way people say them", () => {
    assert.equal(formatDate("2026-10-31"), "31 Oct 2026");
});

test("a fresh price shows its date", () => {
    const today = new Date(2026, 10, 6);
    assert.equal(daysOld("2026-10-31", today), 6);
    assert.equal(priceLine(PRICES[0], today), "White bread: R13.00 (as at 31 Oct 2026)");
});

test("the border: 30 days is still fresh, 31 is stale", () => {
    assert.equal(priceLine(PRICES[0], new Date(2026, 10, 30)), "White bread: R13.00 (as at 31 Oct 2026)");
    assert.match(priceLine(PRICES[0], new Date(2026, 11, 1)), /may have changed/);
});

test("bad prices are refused", () => {
    
    assert.equal(validatePrices(PRICES), true);
    assert.throws(() => validatePrices([{ item: "Milk", cents: 18.5, asAt: "2026-10-31" }]), /whole cents/);
    assert.throws(() => validatePrices([{ item: "Milk", cents: 1850, asAt: "31/10/2026" }]), /date must look like/);
});