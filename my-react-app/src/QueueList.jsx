import { useState, useEffect } from "react";

function QueueList() {
    const [queue, setQueue] = useState([]);

    useEffect(function () {
        const data = [
            { id: 1, plate: "SS23HJ GP", position: 1 },
            { id: 2, plate: "PL12AS GP", position: 2 }
        ];
        setQueue(data);
    }, []);

    return (
        <ul>
            {queue.map(function (entry) {
                return <li key={entry.id}>Position {entry.position}: {entry.plate}</li>;
            })}
        </ul>
    );
}

export default QueueList;