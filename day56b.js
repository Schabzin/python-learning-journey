const routes = ['CBD', 'VaalMall', 'River'];
const moreRoutes = ['Mittal', 'Evaton'];

const allRoutes = [...routes, ...moreRoutes];
console.log(allRoutes);

const routesCopy = [...routes];

const updatedRoutes = [...routes, 'Sebokeng'];
console.log(routes);
console.log(updatedRoutes);

const driver = {name: 'Chahane', plate: 'GP123456'};
const extraInfo = {phone: '0711111111', status: 'active'};

const updatedDriver = {...driver, plate: 'GP999999'};
console.log(driver.plate);
console.log(updatedDriver.plate);

const fullDriver = {...driver, ...extraInfo};
console.log(fullDriver);

function logTrips(...trips) {
    trips.forEach(trip => console.log(trip));
}
logTrips('Sharpville', 'Bophelong', 'Golden Gardens', 'Ext.11');

function firstAndRest(first, ...rest) {
    console.log('First:', first);
    console.log('Rest:', rest);
}

firstAndRest('Sharpville', 'Bophelong','Golden Gardens', 'Ext.11' )


