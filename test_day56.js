const plates = ['GP12345', 'GP23456', 'GP34567', 'GP4567', 'GP56789'];
const[first, ...rest] = plates;
const last = rest[rest.length - 1];
console.log(first);
console.log(last);

const taxi = {plate: 'GP12345', driver: 'Neo', trips: 4, status: 'active'};
const{driver,trips} = taxi;
console.log(driver);
console.log(trips);

const routes = ['Evaton'];
const moreRoutes = ['Residentia'];
const allRoutes = [...routes,...moreRoutes];
console.log(allRoutes);

const info = {name: "Lebo", plate: "GP745896", phone: "0697412589"};
const extraInfo = {status: "active"}
const fullInfo = {...info, ...extraInfo};
console.log(fullInfo)

function logAllTrips(...trips) {
    trips.forEach(trip => console.log(trip));
}
logAllTrips('Trip 1', 'Trip 2', 'Trip 3');

function formatCurrency(amount) {
    return `R${amount.toFixed(2)}`;
}

class Taxi {
    constructor(plate,driver) {
        this.driver = driver;
        this.plate = plate;
        this.trips = 0;
        this.collected = 0
    }
    logTrip(amount) {
        this.trips ++;
        this.collected += amount;
        console.log(`Trip logged - ${this.trips} trips, R${this.collected} collected`);
    }
    targetMet() {
        return this.collected >= 750;
    }
}
const taxi1 = new Taxi('GP123456', 'Chahane');
taxi1.logTrip(300);
taxi1.logTrip(300);
taxi1.logTrip(300);
console.log(taxi1.targetMet())
console.log(formatCurrency(taxi1.collected))
