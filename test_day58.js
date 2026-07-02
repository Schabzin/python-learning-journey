export class BaseAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || `Request failed: {response.status}`);
        }
        return data;
    }
}

export class TaxiAPI extends BaseAPI {
    getTaxis() {
        return this.request('/api/taxis');
    }

    logTrip(taxiId, routeId) {
        return this.request('/api/trip', {
            method:"POST",
            headers:{'Content-Type': 'application/json'},
            body:JSON.stringify({taxi_id: taxiId, route_id: routeId})
        });
    }
    static formatPlate(plate) {
        return plate.toUpperCase().replace(/\s/g, '');
    }
}

export class DriverAPI extends BaseAPI {
    getMyTaxi() {
        return this.request('/api/driver/taxi');
    }
}
console.log(TaxiAPI.formatPlate('gp 258 741'));
