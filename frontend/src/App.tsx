import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Arena from './pages/Arena';
// import DebugArena from './pages/DebugArena'; // Not needed - going directly to Arena
import Profile from './pages/Profile';
import Leaderboard from './pages/Leaderboard';

function App() {
  return (
    <BrowserRouter>
      <div className="bg-mesh"></div>
      
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/arena" element={<Arena />} />
          {/* <Route path="/debug-arena" element={<DebugArena />} /> */}
          <Route path="/profile" element={<Profile />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
