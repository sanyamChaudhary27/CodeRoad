import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { UserPlus, Key, Mail, Terminal, AlertCircle } from 'lucide-react';

const Register = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authService.register({ username, email, password });
      navigate('/dashboard');
    } catch (err: any) {
      console.error('Registration error:', err);
      const status = err.response?.status;
      const errMsg = err.response?.data?.detail;
      
      if (status === 500) {
        setError('Server Error: Something went wrong on our end while processing your registration. Our engineers are on it!');
      } else if (Array.isArray(errMsg)) {
        setError(errMsg[0]?.msg || 'Validation error');
      } else if (errMsg) {
        setError(errMsg);
      } else if (err.code === 'ERR_NETWORK' || !err.response) {
        setError('Cannot connect to the backend server.');
      } else {
        setError('Registration failed. Please try a stronger password or check your details.');
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
          <p className="text-secondary">Initialize your hacker profile</p>
        </div>

        <div className="glass-panel p-8">
          <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-2">
            <UserPlus size={24} className="text-primary" />
            Registration
          </h2>

          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 flex items-start gap-3 text-sm">
              <AlertCircle size={20} className="shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="form-label" htmlFor="username">Alias (Username)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-muted">
                  <Terminal size={18} />
                </div>
                <input
                  id="username"
                  type="text"
                  required
                  className="input-base pl-10"
                  placeholder="zero_cool"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="form-label" htmlFor="email">Secure Comm (Email)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-text-muted">
                  <Mail size={18} />
                </div>
                <input
                  id="email"
                  type="email"
                  required
                  className="input-base pl-10"
                  placeholder="crash@override.net"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="form-label" htmlFor="password">Passphrase (Min 8 chars, mixed case, number, symbol)</label>
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
              disabled={loading || !email || !password || !username}
              className="btn btn-primary w-full mt-6"
            >
              {loading ? 'Allocating Profile...' : 'Initialize'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-text-secondary">
            Already in the database?{' '}
            <Link to="/login" className="text-primary hover:text-primary-hover font-medium">
              Authenticate here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
