const hoursLib = (typeof require !== "undefined") ? require("./hours.js") : { HOURS, validateHours, statusMessage };

const UNKNOWN = "unknown";

const BRANCHES = [
    {
        name: "Evaton",
        address: "1068 Sakies Adams Road, Evaton",
        phone: "016 023 0857",
        hours: UNKNOWN,
        lat: -26.525,
        lng: 27.852,
    },
    {
        name: "Zone 7",
        address: "Shop No. 13, Zone 7B, Sebokeng",
        phone: "016 023 0634",
        hours: hoursLib.HOURS,
        lat: -26.588,
        lng: 27.838,
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
        if (typeof b.lat !== "number" || typeof b.lng !== "number") {
            throw new Error("Branch '" + b.name + "' has no map position (lat, lng).");
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

const EARTH_RADIUS_KM = 6371;

function toRadians(degrees) {
    return degrees * Math.PI / 180;
}
 
function distanceKm(lat1, lng1, lat2, lng2) {
    const dLat = toRadians(lat2 - lat1);
    const dLng = toRadians(lng2 - lng1);
    const a = Math.sin(dLat / 2) ** 2 +
              Math.cos(toRadians(lat1)) * Math.cos(toRadians(lat2)) * Math.sin(dLng / 2) ** 2;
    return 2 * EARTH_RADIUS_KM * Math.asin(Math.sqrt(a));
}

function branchesByDistance(branches, lat, lng) {
    const withDistance = branches.map((b) => ({ branch: b, km: distanceKm(lat, lng, b.lat, b.lng) }));
    withDistance.sort((x, y) => x.km - y.km);
    return withDistance;
}

if (typeof module !== "undefined") {
    module.exports = { UNKNOWN, BRANCHES, validateBranches, branchStatus, distanceKm, branchesByDistance };
}