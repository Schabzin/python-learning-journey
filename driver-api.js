import { BaseAPI } from './base-api.js';

class DriverAPI extends BaseAPI {
    getMyTaxi() {
        return this.request('/api/driver/taxi');
    }
}