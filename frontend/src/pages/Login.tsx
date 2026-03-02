import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { LogIn, Key, Mail, AlertCircle, Terminal, Code2, Trophy, Zap } from 'lucide-react';

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
      setError(
        err.response?.data?.detail?.[0]?.msg || 
        err.response?.data?.detail || 
        'Invalid credentials. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-pulse" style={{animationDelay: '1s'}}></div>
      </div>

      <div className="w-full max-w-6xl animate-fade-in relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          
          {/* Left side - Branding */}
          <div className="hidden lg:block space-y-8">
            <div className="flex items-center gap-4 mb-8">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary to-accent flex-center shadow-glow">
                <Terminal size={32} className="text-white" />
              </div>
              <div>
                <h1 className="text-5xl font-bold text-gradient">Code Road</h1>
                <p className="text-text-secondary text-lg">Competitive Coding Arena</p>
              </div>
            </div>

            <div className="space-y-6">
              <div className="flex items-start gap-4 glass-panel p-6 hover:border-primary/50 transition-all">
                <div className="h-12 w-12 rounded-lg bg-primary/20 flex-center shrink-0">
                  <Trophy size={24} className="text-primary" />
                </div>
                <div>
                  <h3 className="text-white font-bold mb-1">Real-time Competition</h3>
                  <p className="text-text-secondary text-sm">Battle against developers worldwide in live coding challenges</p>
                </div>
              </div>

              <div className="flex items-start gap-4 glass-panel p-6 hover:border-accent/50 transition-all">
                <div className="h-12 w-12 rounded-lg bg-accent/20 flex-center shrink-0">
                  <Zap size={24} className="text-accent" />
                </div>
                <div>
                  <h3 className="text-white font-bold mb-1">AI-Powered Challenges</h3>
                  <p className="text-text-secondary text-sm">Dynamic problems that adapt to your skill level</p>
                </div>
              </div>

              <div className="flex items-start gap-4 glass-panel p-6 hover:border-success/50 transition-all">
                <div className="h-12 w-12 rounded-lg bg-success/20 flex-center shrink-0">
                  <Code2 size={24} className="text-success" />
                </div>
                <div>
                  <h3 className="text-white font-bold mb-1">Skill-Based Matchmaking</h3>
                  <p className="text-text-secondary text-sm">Fair matches with ELO rating system</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right side - Login Form */}
          <div className="w-full">
            <div className="lg:hidden text-center mb-8">
              <div className="flex items-center justify-center gap-3 mb-4">
                <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex-center">
                  <Terminal size={24} className="text-white" />
                </div>
                <h1 className="text-gradient text-4xl font-bold">Code Road</h1>
              </div>
              <p className="text-text-secondary">Welcome back to the arena</p>
            </div>

            <div className="glass-panel p-8 lg:p-10">
              <h2 className="text-3xl font-bold mb-2 text-white flex items-center gap-3">
                <LogIn size={28} className="text-primary" />
                Sign In
              </h2>
              <p className="text-text-secondary mb-8">Enter your credentials to access the arena</p>

              {error && (
                <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 flex items-start gap-3 text-sm animate-shake">
                  <AlertCircle size={20} className="shrink-0 mt-0.5" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <label className="form-label" htmlFor="email">Email Address</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-muted">
                      <Mail size={20} />
                    </div>
                    <input
                      id="email"
                      type="email"
                      required
                      className="input-base pl-12 h-14 text-lg"
                      placeholder="hacker@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>
                </div>

                <div>
                  <label className="form-label" htmlFor="password">Password</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-text-muted">
                      <Key size={20} />
                    </div>
                    <input
                      id="password"
                      type="password"
                      required
                      className="input-base pl-12 h-14 text-lg"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading || !email || !password}
                  className="btn btn-primary w-full mt-6 h-14 text-lg shadow-glow"
                >
                  {loading ? 'Authenticating...' : 'Enter Arena'}
                </button>
              </form>

              <div className="mt-8 text-center">
                <p className="text-text-secondary">
                  Don't have an account?{' '}
                  <Link to="/register" className="text-primary hover:text-primary-hover font-semibold transition-colors">
                    Create Account
                  </Link>
                </p>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Login;
