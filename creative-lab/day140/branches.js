const hoursLib = (typeof require !== "undefined") ? require("./hours.js") : window;

const UNKNOWN = "unknown";

const BRANCHES = [
    {
        name: "Evaton",
        address: "1068 Sakies Adams Road, Evaton",
        phone: "016 023 0857",
        hours: UNKNOWN,
    },
    {
        name: "Zone 7",
        address: "Shop No. 13, Zone 7B, Sebokeng",
        phone: "016 023 0634",
        hours: hoursLib.HOURS,
    },
];

function validateBranches(branches) {
    if (branches.length === 0) {
        throw new Error("There are no branches.");
    }
    for (const b of branches) {
        if (!b.name || !b.address || !b.phone) {
            throw new Error("Branch '" + (b.name || "?") + "' is missing a name, address or phone.");
        }
        if (typeof b.hours === "string" && b.hours !== UNKNOWN) {
            throw new Error("Branch '" + b.name + "' has hours '" + b.hours + "'. Use UNKNOWN or a timetable.");
        }
        if (b.hours !== UNKNOWN) {
            hoursLib.validateHours(b.hours);
        }
    }
    return true;
}

function branchStatus(branch, when) {
    if (branch.hours === UNKNOWN) {
        return "Hours not confirmed - please call " + branch.phone;
    }
    return hoursLib.statusMessage(branch.hours, when);
}

if (typeof module !== "undefined") {
    module.exports = { UNKNOWN, BRANCHES, validateBranches, branchStatus };
}