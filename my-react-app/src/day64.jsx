function TaxiCard({ plate, driverName, weekCollected }) {
    return (
        <div className="card">
            <h2>{plate}</h2>
            <p>{driverName}</p>
            <p>Week collected:R{weekCollected}</p>
        </div>

    );
}
export default TaxiCard;