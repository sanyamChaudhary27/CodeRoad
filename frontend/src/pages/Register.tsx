import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authService } from '../services/authService';
import { UserPlus, Mail, Lock, User, AlertCircle, Code, Trophy, Target, Sparkles } from 'lucide-react';

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
        setError('Server Error: Something went wrong. Please try again.');
      } else if (Array.isArray(errMsg)) {
        setError(errMsg[0]?.msg || 'Validation error');
      } else if (errMsg) {
        setError(errMsg);
      } else if (err.code === 'ERR_NETWORK' || !err.response) {
        setError('Network error: Unable to connect. Please check your connection.');
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-bg-dark via-bg-panel to-bg-dark">
      {/* Animated Background Grid */}
      <div className="absolute inset-0 bg-grid-pattern opacity-5"></div>
      
      {/* Floating Orbs */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-pulse" style={{animationDelay: '2s'}}></div>
      <div className="absolute top-1/2 right-1/3 w-96 h-96 bg-warning/5 rounded-full blur-3xl animate-pulse" style={{animationDelay: '4s'}}></div>

      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-6xl">
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            
            {/* Left Side - Branding & Benefits */}
            <div className="hidden lg:block space-y-8 animate-fade-in">
              {/* Logo & Title */}
              <div className="space-y-4">
                <div className="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-accent/10 border border-accent/20">
                  <Sparkles className="text-accent" size={20} />
                  <span className="text-accent font-semibold text-sm">Join the Elite</span>
                </div>
                <h1 className="text-6xl font-bold">
                  <span className="text-white">Start Your</span>
                  <br />
                  <span className="text-gradient">Coding Journey</span>
                </h1>
                <p className="text-xl text-text-secondary">
                  Join thousands of developers competing and improving their skills
                </p>
              </div>

              {/* Benefit Cards */}
              <div className="space-y-4">
                <div className="group p-6 rounded-2xl bg-gradient-to-br from-primary/5 to-transparent border border-primary/10 hover:border-primary/30 transition-all duration-300">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-primary/10 group-hover:bg-primary/20 transition-colors">
                      <Trophy className="text-primary" size={24} />
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-lg mb-1">Compete & Win</h3>
                      <p className="text-text-secondary text-sm">Battle in real-time matches and climb the global leaderboard</p>
                    </div>
                  </div>
                </div>

                <div className="group p-6 rounded-2xl bg-gradient-to-br from-accent/5 to-transparent border border-accent/10 hover:border-accent/30 transition-all duration-300">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-accent/10 group-hover:bg-accent/20 transition-colors">
                      <Target className="text-accent" size={24} />
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-lg mb-1">Skill-Based Matching</h3>
                      <p className="text-text-secondary text-sm">Get matched with opponents of similar skill level</p>
                    </div>
                  </div>
                </div>

                <div className="group p-6 rounded-2xl bg-gradient-to-br from-success/5 to-transparent border border-success/10 hover:border-success/30 transition-all duration-300">
                  <div className="flex items-start gap-4">
                    <div className="p-3 rounded-xl bg-success/10 group-hover:bg-success/20 transition-colors">
                      <Code className="text-success" size={24} />
                    </div>
                    <div>
                      <h3 className="text-white font-bold text-lg mb-1">Practice Mode</h3>
                      <p className="text-text-secondary text-sm">Sharpen your skills with unlimited solo practice sessions</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Side - Register Form */}
            <div className="animate-fade-in" style={{animationDelay: '0.2s'}}>
              {/* Mobile Logo */}
              <div className="lg:hidden text-center mb-8">
                <h1 className="text-4xl font-bold mb-2">
                  <span className="text-white">Code</span>
                  <span className="text-gradient"> Road</span>
                </h1>
                <p className="text-text-secondary">Create your account</p>
              </div>

              {/* Form Card */}
              <div className="relative">
                {/* Glow Effect */}
                <div className="absolute -inset-1 bg-gradient-to-r from-accent via-primary to-accent rounded-3xl blur opacity-20 group-hover:opacity-30 transition duration-1000"></div>
                
                <div className="relative bg-bg-panel border border-border-light rounded-3xl p-8 lg:p-10 shadow-2xl">
                  <div className="mb-8">
                    <h2 className="text-3xl font-bold text-white mb-2">Create Account</h2>
                    <p className="text-text-secondary">Start your competitive coding journey today</p>
                  </div>

                  {error && (
                    <div className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3 animate-shake">
                      <AlertCircle size={20} className="text-red-400 shrink-0 mt-0.5" />
                      <span className="text-red-400 text-sm">{error}</span>
                    </div>
                  )}

                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-2">
                      <label className="text-sm font-medium text-text-secondary" htmlFor="username">
                        Username
                      </label>
                      <div className="relative group">
                        <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                          <User size={20} className="text-text-muted group-focus-within:text-primary transition-colors" />
                        </div>
                        <input
                          id="username"
                          type="text"
                          required
                          className="w-full h-14 pl-12 pr-4 bg-bg-panel-light border border-border-light rounded-xl text-white placeholder-text-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none"
                          placeholder="codewizard"
                          value={username}
                          onChange={(e) => setUsername(e.target.value)}
                        />
                      </div>
                    </div>

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
                      <p className="text-xs text-text-muted mt-1">Minimum 8 characters recommended</p>
                    </div>

                    <button
                      type="submit"
                      disabled={loading || !username || !email || !password}
                      className="w-full h-14 bg-gradient-to-r from-accent to-primary text-white font-semibold rounded-xl hover:shadow-glow transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 group mt-6"
                    >
                      {loading ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                          <span>Creating Account...</span>
                        </>
                      ) : (
                        <>
                          <span>Create Account</span>
                          <UserPlus size={20} className="group-hover:translate-x-1 transition-transform" />
                        </>
                      )}
                    </button>
                  </form>

                  <div className="mt-8 text-center">
                    <p className="text-text-secondary">
                      Already have an account?{' '}
                      <Link 
                        to="/login" 
                        className="text-primary hover:text-primary-hover font-semibold transition-colors inline-flex items-center gap-1 group"
                      >
                        Sign In
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

export default Register;
