export function formatCurrency(amount) {
    return `R${amount.toFixed(2)}`;
}

export function formatDate(date) {
    return new Date(date).toLocaleDateString('en-ZA');
}

export const TAX_RATE = 0.15;

export default function createDriver(name, plate) {
    return {
        name,
        plate, 
        trips: 0,
        addTrip() {
            this.trips++;
        }
    }
}