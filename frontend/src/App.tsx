import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Arena from './pages/Arena';
import DebugArena from './pages/DebugArena';
import Profile from './pages/Profile';
import Leaderboard from './pages/Leaderboard';

function App() {
  return (
    <BrowserRouter>
      <div className="bg-mesh"></div>
      
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Splash screen redirect logic */}
        <Route path="/" element={
           <div className="min-h-screen flex-center flex-col p-8">
             <h1 className="text-gradient mb-4 text-4xl">Code Road</h1>
             <p className="text-secondary mb-8 text-lg">Premium Hacker Arena</p>
             <a href="/login" className="btn btn-primary">Enter the Arena</a>
           </div>
        } />
        
        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/arena" element={<Arena />} />
          <Route path="/debug-arena" element={<DebugArena />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
