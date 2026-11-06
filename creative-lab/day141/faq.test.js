const test = require("node:test");
const assert = require("node:assert/strict");
const { WHATSAPP_EVATON, toInternational, whatsappLink, buildFaq } = require("./faq.js");
const { PRICES } = require("./prices.js");

test("a local number becomes the international form WhatsApp needs", () => {
    assert.equal(toInternational("081 065 8453"), "27810658453");
});

test("numbers with the wrong shape are refused", () => {
    assert.throws(() => toInternational("016 023 085"), /10 digits/);
    assert.throws(() => toInternational("27810658453"), /10 digits/);
});

test("the message is sealed so ? & , and space can't break the link", () => {
    assert.equal(
        whatsappLink("081 065 8453", "Hi, how much? R13 & up"),
        "https://wa.me/27810658453?text=Hi%2C%20how%20much%3F%20R13%20%26%20up"
    );
});

test("the price answer comes from prices.js - one source of truth", () => {
    const today = new Date(2026, 10, 6);
    assert.equal(buildFaq(PRICES, today)[0].a, "White bread: R13.00 (as at 31 Oct 2026)");
    const newPrice = [{ ...PRICES[0], cents: 1400 }];
    assert.match(buildFaq(newPrice, today)[0].a, /R14\.00/);
});

test("every question has an answer and a WhatsApp question", () => {
    for (const item of buildFaq(PRICES, new Date(2026, 10, 6))) {
        assert.ok(item.q && item.ask, "incomplete FAQ item: " + item.q);
        assert.ok(whatsappLink(WHATSAPP_EVATON, item.ask).startsWith("https://wa.me/27810658453?text="));
    }
});