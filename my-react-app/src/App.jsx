import QueueList from "./QueueList";

function TaxiCard({ plate, driverName, collected, target}) {
  return (
    <div className="card">
      <h2>{plate}</h2>
      <p>{driverName}</p>
      <p>Collected: R{collected} / R{target}</p>
    </div>
  );
}

function App() {
  return (
    <div>
      <TaxiCard plate="MT64TP GP" driverName="Chahane" collected={900} target={900} />
      <TaxiCard plate="FG09KL GP" driverName="Jake" collected={700} target={900} />
      <TaxiCard plate="LK65XB GP" driverName="Madela" collected={500} target={900} />
      <QueueList />
    </div>
  );
}

export default App;


