import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

function Dashboard() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Fintanik Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </header>

      <main className="dashboard-content">
        <div className="welcome-card">
          <h2>Welcome to Fintanik!</h2>
          <p>Your financial management dashboard</p>
          <p className="status">Authentication successful</p>
        </div>

        <div className="feature-grid">
          <div className="feature-card">
            <h3>Transactions</h3>
            <p>Coming soon...</p>
          </div>
          <div className="feature-card">
            <h3>Budget</h3>
            <p>Coming soon...</p>
          </div>
          <div className="feature-card">
            <h3>Analytics</h3>
            <p>Coming soon...</p>
          </div>
          <div className="feature-card">
            <h3>Reports</h3>
            <p>Coming soon...</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default Dashboard;
