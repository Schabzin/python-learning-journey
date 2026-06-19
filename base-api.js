
export class BaseAPI {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }

    async request(endpoint, options = {}) {
        const response = await fetch(`${this.baseUrl}${endpoint}`, options);
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || `Request failed: ${response.status}`);
        }
        return data;
    }
}
