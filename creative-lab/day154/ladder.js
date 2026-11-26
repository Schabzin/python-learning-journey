const RUNGS = ["audience", "feature", "benefit", "proof", "cta"];
const CLICHES = ["memorable", "awaits", "unforgettable", "world-class", "best", "like never before"];
const ACTION_VERBS = ["book", "call", "order", "whatsapp", "reserve", "buy", "visit", "come", "pull-up"];


function words(text) {
    return text.toLowerCase().match(/[a-z0-9'-]+/g) || [];
}

function hasPhrase(text, phrase) {
    const padded = " " + words(text).join(" ") + " ";
    return padded.includes(" " + phrase + " ");
}

function copyProblems(brief) {
    const problems = [];
    for (const rung of RUNGS) {
        const value = (brief[rung] || "").trim();
        if (value === "") {
            problems.push(`${rung}: missing`);
        }
    }

    for (const rung of ["benefit", "proof", "cta"]) {
        for (const cliche of CLICHES) {
            if (hasPhrase(brief[rung] || "", cliche)) {
                problems.push(`${rung}: "${cliche}" - any venue could say this`);
            }
        }
    }

    const firstWord = words(brief.cta || "")[0];
    if (firstWord && !ACTION_VERBS.includes(firstWord)) {
        problems.push(`cta: starts with "${firstWord}" - start with something the reader can do`);
    }

    for (const rung of RUNGS) {
        if (hasPhrase(brief[rung] || "", "tbc")) {
            problems.push(`${rung}: TBC - confirm this fact with the client before it ships`);
        }
    }

    return problems;
}

module.exports = { RUNGS, CLICHES, ACTION_VERBS, copyProblems, hasPhrase };

