class TaxiAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async getTaxis() {
        const response = await fetch(`${this.baseUrl}/api/taxis`);
        if (!response.ok) {
            throw new Error(`Failed to load taxis: ${response.status}`);
        }
        return await response.json();
    }

    async getRoutes() {
        const response = await fetch(`${this.baseUrl}/api/routes`);
        if (!response.ok) {
            throw new Error(`Failed to load routes: ${response.status}`);
        }
        return await response.json();
    }

    async logTrip(taxiId, routeId) {
        const response = await fetch(`${this.baseUrl}/api/trips`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({taxi_id: taxiId, route_id: routeId})
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to log trip');
        }
        return data;
    }

    async getSummary() {
        const response = await fetch(`${this.baseUrl}/api/summary`);
        if (!response.ok) {
            throw new Error(`Failed to load summary: ${response.status}`);
        }
        return await response.json();
    }
    static formatPlate(plate) {
        return plate.toUpperCase().replace(/\s/g, '');
    }
}
console.log(TaxiAPI.formatPlate('gp 147 852'));

