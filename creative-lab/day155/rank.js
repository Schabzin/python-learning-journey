const { CLICHES, hasPhrase } = require("../day154/ladder.js");
const ABSTRACT = ["assurance", "certainty", "quality", "experience", "excellence", "convenience"];


function wordCount(line) {
    return line.trim().split(/\s+/).length;
}

function lineProblems(line, maxWords) {
    if (line.trim() === "") {
        return ["empty line"];
    }
    const problems = [];
    for (const cliche of CLICHES) {
        if (hasPhrase(line, cliche)) {
            problems.push(`cliche: "${cliche}"`);
        }
    }
    for (const word of ABSTRACT) {
        if (hasPhrase(line, word)) {
            problems.push(`abstract: "${word}" - show it, don't name it`);
        }
    }
    const count = wordCount(line);
    if (count > maxWords) {
        problems.push(`too long: ${count} words, budget ${maxWords}`);
    }
    return problems;
}

function rankLines(lines, maxWords) {
    const results = lines.map((line) => ({ line, problems: lineProblems(line, maxWords) }));
    results.sort((a, b) => {
        if (a.problems.length !== b.problems.length) {
            return a.problems.length - b.problems.length;
        }
        return wordCount(a.line) - wordCount(b.line);
    });
    return results;
}

module.exports = { ABSTRACT, lineProblems, rankLines };