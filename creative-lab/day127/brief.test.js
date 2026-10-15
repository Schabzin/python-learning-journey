const test = require("node:test");
const assert = require("node:assert/strict");
const { lintBrief } = require("./brief.js");

const GOOD = {
    client: "Separaka Holdings",
    audience: "Creche owners in Evaton",
    insight: "Parents choose a creche on their phones before they ever visit.",
    proposition: "Be found before they visit.",
    support: "Your creche online in 7 days.",
    proof: "Mobile-first: loads fast on any cheap phone.",
    cta: "whatsApp 073 223 9762"
};

test("a sharp brief has no errors and no warnings", () => {
    assert.deepEqual(lintBrief(GOOD), { errors: [], warnings: [] });
});

test("missing insight is an error", () => {
    const r = lintBrief({ ...GOOD, insight: "" });
    assert.deepEqual(r.errors, ["Missing: insight"]);
});

test("we-talk is a warning, not an error", () => {
    const r = lintBrief({ ...GOOD, proposition: "We build our websites fast.", support: "We are the best."});
    assert.equal(r.errors.length, 0);
    assert.equal(r.warnings.length, 1);
});

test("an insight about the client is flagged", () => {
    const r = lintBrief({ ...GOOD, insight: "Separaka Holdings builds great websites." });
    assert.equal(r.warnings.length, 1);
    assert.match(r.warnings[0], /AUDIENCE/);
});

test ("a CTA without an action word is flagged", () => {
    const r = lintBrief({ ...GOOD, cta: "073 223 9762" });
    assert.equal(r.warnings.length, 1);
}); 

test("yesterday's brief is missing insight and proof", () => {
    const r = lintBrief({
        client: "Separaka Holdings",
        audience: "Creche and small business owners in the Vaal",
        proposition: "Your business online in 7 days.",
        support: "Mobile-first websites from R3,500.",
        cta: "WhatsApp 073 223 9762"
    });
    assert.deepEqual(r.errors, ["Missing: insight", "Missing: proof"]);
    assert.deepEqual(r.warnings, []);
});