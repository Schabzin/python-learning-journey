function makeNumbers(n) {
    const list = [];
    for (let i = 0; i < n; i++) {
        list.push(Math.floor(Math.random() * 1000));
    }
    return list;
}

function builtInSort(list) {
    let comparisons = 0;
    const copy = [...list];
    copy.sort((a, b) => {
        comparisons = comparisons + 1;
        return a - b;
    });
    return comparisons;
}

function bubbleSort(list) {
    let comparisons = 0;
    const copy = [...list];
    for (let end = copy.length - 1; end > 0; end--) {
        for (let i = 0; i < end; i++) {
            comparisons = comparisons + 1;
            if (copy[i] > copy[i + 1]) {
                const temp = copy[i];
                copy[i] = copy[i + 1];
                copy[i + 1] = temp;
            }
        }
    }
    return comparisons;
}

for (const n of [10, 100, 1000]) {
    const numbers = makeNumbers(n);
    console.log("n =", n, "| built-in:", builtInSort(numbers), "| bubble:", bubbleSort(numbers));
}

const items = [
    { name: "Bread", price: 13 },
    { name: "Milk", price: 18.5 },
    { name: "Eggs", price: 13 },
];
console.log([...items].sort((a, b) => a.price - b.price).map((x) => x.name));
console.log([...items].reverse().sort((a, b) => a.price - b.price).map((x) => x.name));