const { wrapText, fitText } = require("../day127/layout");

let calls = 0;
const measure = (text, font) => {
    calls += 1;
    const size = Number(font.match(/(\d+)px/)[1]);
    return text.length * size * 0.5;
};

for (const n of [5, 10, 20, 40]) {
    const text = Array(n).fill("word").join(" ");

    calls = 0;
    wrapText(measure, text, 100000, "bold 40px Arial");
    const wrapCalls = calls;

    calls = 0;
    const result = fitText(measure, text, { maxWidth: 920, maxLines: 3, maxSize: 110, minSize: 56, weight: "bold" });
    console.log(`${n} words: wrapText ${wrapCalls} calls, fitText ${calls} calls, fits: ${result !== null}`);
}