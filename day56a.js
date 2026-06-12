const names = ['CBD', 'VaalMall', 'River', 'Mittal', 'Evaton'];
const [first,, third] = names;
console.log(first);
console.log(third);

console.log('CBD','River');
const taxi = {name: 'Oupa', phone: '0711111111', plate: 'GP345678', status: 'active', trips: 4};

const {name, phone, plate, status, trips} = taxi;
console.log(name);
console.log(plate);
console.log(trips);

function showDriver({name, plate, trips}) {
    console.log(`Driver ${name} ${plate} - ${trips} trips today`);
}

showDriver({name: 'oupa', plate: 'GP56789', trips:4});
