import { BaseAPI } from './base-api.js';

export class TaxiAPI extends BaseAPI {
    getTaxis() {
        return this.request('/api/taxis');
    }
    getRoutes() {
        return this.request('/api/routes');
    }
    logTrip(taxiId, routeId) {
        return this.request('/api/trips', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({taxi_id: taxiId, route_id: routeId})

        });
    }
    getSummary() {
        return this.request('/api/summary');
    }
    static formatPlate(plate) {
        return plate.toUpperCase().replace(/\s/g, '');
    }
}
console.log(TaxiAPI.formatPlate('gp 147 852'));
