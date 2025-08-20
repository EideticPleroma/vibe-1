import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title } from 'chart.js';

// Import components
import Navigation from './components/Navigation';
import Dashboard from './pages/Dashboard';
import Budget from './pages/Budget';
import BudgetMethodologyPage from './pages/BudgetMethodology';
import Transactions from './pages/Transactions';
import Categories from './pages/Categories';
import Investments from './pages/Investments';
import Analytics from './pages/Analytics';
import Alerts from './pages/Alerts';

// Register Chart.js components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title
);

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main className="pt-16">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/budget" element={<Budget />} />
            <Route path="/budget-methodologies" element={<BudgetMethodologyPage />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/investments" element={<Investments />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/alerts" element={<Alerts />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
