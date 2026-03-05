import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { LogIn, Mail, Lock, AlertCircle, Code, Zap, Shield, TrendingUp } from 'lucide-react';

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
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-bg-dark via-bg-panel to-bg-dark">
      {/* Animated Background Grid */}
      <div className="absolute inset-0 bg-animated-grid opacity-5"></div>
      
      {/* Floating Orbs */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-success/5 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>

      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-6xl">
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            
            {/* Left Side - Branding & Features */}
            <div className="hidden lg:block space-y-8 animate-fade-in">
              {/* Logo & Title */}
              <div className="space-y-4">
                <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-primary/10 border border-primary/20">
                  <Code className="text-primary" size={20} />
                  <span className="text-primary font-semibold text-sm">Competitive Coding Platform</span>
                </div>
                <h1 className="text-6xl font-bold">
                  <span className="text-white">Code</span>
                  <span className="text-gradient"> Road</span>
                </h1>
                <p className="text-xl text-text-secondary">
                  Where developers compete, learn, and grow together
                </p>
              </div>

              {/* Feature Cards */}
              <div className="space-y-4">
                <div className="group p-6 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent border border-primary/10 hover:border-primary/30 transition-all duration-300">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-primary/10 group-hover:bg-primary/20 transition-colors">
                      <Zap className="text-primary" size={24} />
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-lg mb-1">Real-Time Battles</h3>
                      <p className="text-text-secondary text-sm">Compete against developers worldwide in live coding challenges</p>
                    </div>
                  </div>
                </div>

                <div className="group p-6 rounded-2xl bg-gradient-to-br from-accent/5 to-transparent border border-accent/10 hover:border-accent/30 transition-all duration-300">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-accent/10 group-hover:bg-accent/20 transition-colors">
                      <Shield className="text-accent" size={24} />
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-lg mb-1">AI-Powered Integrity</h3>
                      <p className="text-text-secondary text-sm">Advanced ML models ensure fair play and detect cheating</p>
                    </div>
                  </div>
                </div>

                <div className="group p-6 rounded-2xl bg-gradient-to-br from-success/5 to-transparent border border-success/10 hover:border-success/30 transition-all duration-300">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-success/10 group-hover:bg-success/20 transition-colors">
                      <TrendingUp className="text-success" size={24} />
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-lg mb-1">ELO Rating System</h3>
                      <p className="text-text-secondary text-sm">Fair matchmaking based on skill level and performance</p>
                    </div>
                  </div>
                </div>
              </div>

            </div>

            {/* Right Side - Login Form */}
            <div className="animate-fade-in" style={{animationDelay: '0.2s'}}>
              {/* Mobile Logo */}
              <div className="lg:hidden text-center mb-8">
                <h1 className="text-4xl font-bold mb-2">
                  <span className="text-white">Code</span>
                  <span className="text-gradient"> Road</span>
                </h1>
                <p className="text-text-secondary">Sign in to continue</p>
              </div>

              {/* Form Card */}
              <div className="relative">
                {/* Glow Effect */}
                <div className="absolute -inset-1 bg-gradient-to-r from-primary via-accent to-primary rounded-3xl blur opacity-20 group-hover:opacity-30 transition duration-1000"></div>
                
                <div className="relative bg-bg-panel border border-border-light rounded-3xl p-8 lg:p-10 shadow-2xl">
                  <div className="mb-8">
                    <h2 className="text-3xl font-bold text-white mb-2">Welcome Back</h2>
                    <p className="text-text-secondary">Enter your credentials to access your account</p>
                  </div>

                  {error && (
                    <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3 animate-shake">
                      <AlertCircle size={20} className="text-red-400 shrink-0 mt-0.5" />
                      <span className="text-red-400 text-sm">{error}</span>
                    </div>
                  )}

                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-text-secondary" htmlFor="email">
                        Email Address
                      </label>
                      <div className="relative group">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                          <Mail size={20} className="text-text-muted group-focus-within:text-primary transition-colors" />
                        </div>
                        <input
                          id="email"
                          type="email"
                          required
                          className="w-full h-14 pl-12 pr-4 bg-bg-panel-light border border-border-light rounded-xl text-white placeholder-text-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                          placeholder="you@example.com"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium text-text-secondary" htmlFor="password">
                        Password
                      </label>
                      <div className="relative group">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                          <Lock size={20} className="text-text-muted group-focus-within:text-primary transition-colors" />
                        </div>
                        <input
                          id="password"
                          type="password"
                          required
                          className="w-full h-14 pl-12 pr-4 bg-bg-panel-light border border-border-light rounded-xl text-white placeholder-text-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                          placeholder="••••••••"
                          value={password}
                          onChange={(e) => setPassword(e.target.value)}
                        />
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={loading || !email || !password}
                      className="w-full h-14 bg-gradient-to-r from-primary to-accent text-white font-semibold rounded-xl hover:shadow-glow transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 group"
                    >
                      {loading ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                          <span>Signing In...</span>
                        </>
                      ) : (
                        <>
                          <span>Sign In</span>
                          <LogIn size={20} className="group-hover:translate-x-1 transition-transform" />
                        </>
                      )}
                    </button>
                  </form>

                  <div className="mt-8 text-center">
                    <p className="text-text-secondary">
                      Don't have an account?{' '}
                      <Link 
                        to="/register" 
                        className="text-primary hover:text-primary-hover font-semibold transition-colors inline-flex items-center gap-1 group"
                      >
                        Create Account
                        <span className="group-hover:translate-x-1 transition-transform">→</span>
                      </Link>
                    </p>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
