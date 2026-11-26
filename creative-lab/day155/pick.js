const { rankLines } = require("./rank.js");
const BUDGET = 12;

const benefits = [
    "Cars and food, best of both worlds",
    "Nobody values your time like we do",
    "Do you want to play with us?",
    "Chill with us, you know we got you",
    "Xava the rides, spotless and shiny",
    "Enjoy yourself by listening to good music",
    "Good vibes",
    "A place of connection",
    "Everything in one place",
    "Come thru",
    "Pull up, get your ride clean and enjoy our fresh meat",
];

const ranked = rankLines(benefits, BUDGET);

ranked.forEach((result, index) => {
    const mark = result.problems.length === 0 ? "clean" : result.problems.join("; ");
    console.log(`${index + 1}. ${result.line} [${mark}]`);
});