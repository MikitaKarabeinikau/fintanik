import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <h1>Fintanik</h1>
        <p>Financial Management System</p>
        <Routes>
          <Route path="/" element={<HomePage />} />
          {/* We'll add more routes here (login, dashboard, etc.) */}
        </Routes>
      </div>
    </Router>
  );
}

function HomePage() {
  return (
    <div>
      <h2>Welcome to Fintanik</h2>
      <p>Your personal financial tracking application</p>
    </div>
  );
}

export default App;
