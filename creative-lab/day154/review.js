const { copyProblems } = require("./ladder.js");
const draft = {
    audience: "",
    feature: "A day of relaxation, good food and beautiful surroundings",
    benefit: "Make your next escape memorable. Leave the routine behind",
    proof: "",
    cta: "Discover what awaits you at Stonehill Lodge",
};

const v2 = {
    audience: "A professional worker.",
    feature: " A Lodge",
    benefit: "Gives assurance",
    proof: "Picnics, Venue, Accommodation, Spa, 09:00 to 16:00",
    cta: "Discover",
};

const v3 = {
    audience: "Office workers, in the Vaal, weekend get away",
    feature: "Picnics, A Spa, Accommodation, Venue",
    benefit: "Picnics on the lawn, unwind at the spa,leave your week behind",
    proof: "Picnics 09:00 to 18:00",
    cta: "WhatsApp us for a booking",
};

const brief988 = {
    audience: "Young car owners in the Vaal",
    feature: "Carwash, Shisanyama, Music",
    benefit: "Get your car washed(spotless), Fresh meat(shisanyama) and enjoy good music",
    proof: "3020 Amatolo Street, Boipatong. December events TBC on Computicket",
    cta: "Pull-up",
};

function review(name, brief) {
    const problems = copyProblems(brief);
    console.log(`\n${name}: ${problems.length} problem(s)`);
    for (const problem of problems) {
        console.log(" - " + problem);
    }
    if (problems.length === 0) {
        console.log("  passes the red pen");
    }
}

review("Draft v1", draft);
review("Draft v2", v2);
review("Draft v3", v3);
review("9EightEight December", brief988);