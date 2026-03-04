import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { LogIn, Key, Mail, AlertCircle } from 'lucide-react';

const Login = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.login({ email, password });
      navigate('/dashboard');
    } catch (err: any) {
      if (err.code === 'ERR_NETWORK' || !err.response) {
        setError('Cannot connect to the backend server.');
      } else {
        setError(
          err.response?.data?.detail?.[0]?.msg || 
          err.response?.data?.detail || 
          'Invalid credentials. Please try again.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex-center p-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <h1 className="text-gradient text-4xl mb-2">Code Road</h1>
          <p className="text-secondary">Welcome back to the arena</p>
        </div>

        <div className="glass-panel p-8">
          <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-2">
            <LogIn size={24} className="text-primary" />
            Sign In
          </h2>

          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 flex items-start gap-3 text-sm">
              <AlertCircle size={20} className="shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="form-label" htmlFor="email">Email Address</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-muted">
                  <Mail size={18} />
                </div>
                <input
                  id="email"
                  type="email"
                  required
                  className="input-base pl-10"
                  placeholder="hacker@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="form-label" htmlFor="password">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-muted">
                  <Key size={18} />
                </div>
                <input
                  id="password"
                  type="password"
                  required
                  className="input-base pl-10"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !email || !password}
              className="btn btn-primary w-full mt-4"
            >
              {loading ? 'Authenticating...' : 'Enter System'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-text-secondary">
            Don't have clearance?{' '}
            <Link to="/register" className="text-primary hover:text-primary-hover font-medium">
              Request access
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
