export const RUNGS = ["audience", "feature", "benefit", "proof", "cta"];
export const CLICHES = ["memorable", "awaits", "unforgettable", "world-class", "best", "like never before"];
export const ACTION_VERBS = ["book", "call", "order", "whatsapp", "reserve", "buy", "visit", "come"];


function words(text) {
    return text.toLowerCase().match(/[a-z0-9'-]+/g) || [];
}

function hasPhrase(text, phrase) {
    const padded = " " + words(text).join(" ") + " ";
    return padded.includes(" " + phrase + " ");
}

export function copyProblems(brief) {
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

    return problems;
}