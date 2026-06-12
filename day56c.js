import { formatCurrency, formatDate, TAX_RATE } from './utils.js';

console.log(formatCurrency(750));
console.log(TAX_RATE);

class Taxi {
    constructor(plate, driver) {
        this.plate = plate;
        this.driver = driver;
        this.trips = 0;
        this.collected = 0;
    }

    logTrip(amount) {
        this.trips++;
        this.collected += amount;
        console.log(`Trip logged - ${this.trips} trips, R${this.collected} collected`);
    }

    targetMet() {
        return this.collected >= 750;
    }
}

const taxi1 = new Taxi('GP123456', 'Chahane');
taxi1.logTrip(330);
taxi1.logTrip(330);
taxi1.logTrip(330);
console.log(taxi1.targetMet());
console.log(formatCurrency(taxi1.collected));