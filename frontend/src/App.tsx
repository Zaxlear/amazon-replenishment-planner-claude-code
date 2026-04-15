import { Routes, Route, Navigate } from 'react-router-dom';
import ErrorBoundary from './components/common/ErrorBoundary';
import AppLayout from './components/common/Layout';
import ShipmentPlanPage from './pages/ShipmentPlanPage';
import SalesPlanPage from './pages/SalesPlanPage';
import ChartDashboard from './pages/ChartDashboard';
import TurnoverAnalysis from './pages/TurnoverAnalysis';

function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/shipments/*" element={<ShipmentPlanPage />} />
          <Route path="/sales/*" element={<SalesPlanPage />} />
          <Route path="/charts" element={<ChartDashboard />} />
          <Route path="/turnover" element={<TurnoverAnalysis />} />
          <Route path="/" element={<Navigate to="/shipments" replace />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  );
}

export default App;
