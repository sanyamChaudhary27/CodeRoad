import { useNavigate } from 'react-router-dom';
import { Code, Trophy, Zap, Users, Target, Bug, Sparkles, ArrowRight } from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-bg-dark via-bg-panel to-bg-dark overflow-hidden">
      {/* Hero Section - Enhanced */}
      <div className="relative min-h-screen flex flex-col">
        {/* Navigation - Enhanced */}
        <nav className="glass-panel border-b border-white/5 backdrop-blur-xl sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3 group cursor-pointer">
              <div className="h-14 w-20 flex-center group-hover:scale-110 transition-transform">
                <img src="/logo.svg" alt="CodeRoad" className="h-full w-full object-contain" />
              </div>
              <span className="text-xl font-black text-gradient">CodeRoad</span>
            </div>
            
            <div className="flex items-center gap-3">
              <button
                onClick={() => navigate('/login')}
                className="text-text-secondary hover:text-white transition-colors font-semibold px-5 py-2 text-sm"
              >
                Login
              </button>
              <button
                onClick={() => navigate('/register')}
                className="btn btn-primary px-6 py-2 text-sm font-semibold"
              >
                Get Started
              </button>
            </div>
          </div>
        </nav>

        {/* Hero Content - Enhanced */}
        <div className="flex-1 flex items-center justify-center px-6 py-12">
          <div className="max-w-6xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/30 mb-6 animate-fade-in hover:scale-105 transition-transform cursor-pointer">
              <Sparkles size={14} className="text-primary animate-pulse" />
              <span className="text-xs font-bold text-primary">AI-Powered Competitive Programming</span>
            </div>
            
            <h1 className="text-5xl md:text-6xl font-black mb-5 animate-fade-in leading-tight">
              <span className="text-white">Master</span>
              <br />
              <span className="text-gradient">Algorithms</span>
              <br />
              <span className="text-white">Through</span>{' '}
              <span className="text-gradient">Battle</span>
            </h1>
            
            <p className="text-base md:text-lg text-text-secondary mb-8 max-w-3xl mx-auto animate-fade-in leading-relaxed">
              Compete in real-time 1v1 coding battles. Solve AI-generated challenges. 
              Climb the leaderboard. Become a coding champion.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 animate-fade-in mb-12">
              <button
                onClick={() => navigate('/register')}
                className="btn btn-primary text-base px-7 py-3 group shadow-glow-lg hover:shadow-glow-xl transition-all"
              >
                Start Your Journey
                <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => navigate('/login')}
                className="btn btn-secondary text-base px-7 py-3 hover:bg-white/10"
              >
                Sign In
              </button>
            </div>

            {/* Stats - Enhanced */}
            <div className="grid grid-cols-3 gap-6 mt-16 max-w-4xl mx-auto">
              <div className="text-center group cursor-pointer hover:scale-110 transition-transform">
                <div className="text-3xl font-black text-gradient mb-2 group-hover:animate-pulse">Infinite</div>
                <div className="text-xs text-text-muted uppercase tracking-widest">Challenges</div>
              </div>
              <div className="text-center group cursor-pointer hover:scale-110 transition-transform">
                <div className="text-3xl font-black text-gradient mb-2 group-hover:animate-pulse">Real-Time</div>
                <div className="text-xs text-text-muted uppercase tracking-widest">Battles</div>
              </div>
              <div className="text-center group cursor-pointer hover:scale-110 transition-transform">
                <div className="text-3xl font-black text-gradient mb-2 group-hover:animate-pulse">AI-Powered</div>
                <div className="text-xs text-text-muted uppercase tracking-widest">Generation</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section - Enhanced */}
      <div className="py-16 px-6 mb-12">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-black text-white mb-3">
              Why <span className="text-gradient">CodeRoad</span>?
            </h2>
            <p className="text-lg text-text-secondary">
              The ultimate platform for competitive programmers
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 - Enhanced */}
            <div className="glass-panel p-10 hover:scale-105 transition-all cursor-pointer group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-all"></div>
              
              <div className="relative">
                <div className="h-20 w-20 rounded-2xl bg-primary/20 border-2 border-primary/40 flex-center mb-8 group-hover:scale-110 transition-transform shadow-glow-sm">
                  <Users size={36} className="text-primary" />
                </div>
                <h3 className="text-2xl font-black text-white mb-4">1v1 Battles</h3>
                <p className="text-text-secondary leading-relaxed">
                  Compete against real opponents in real-time coding duels. Test your skills under pressure.
                </p>
              </div>
            </div>

            {/* Feature 2 - Enhanced */}
            <div className="glass-panel p-10 hover:scale-105 transition-all cursor-pointer group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-accent/5 rounded-full blur-3xl group-hover:bg-accent/10 transition-all"></div>
              
              <div className="relative">
                <div className="h-20 w-20 rounded-2xl bg-accent/20 border-2 border-accent/40 flex-center mb-8 group-hover:scale-110 transition-transform shadow-glow-sm">
                  <Zap size={36} className="text-accent" />
                </div>
                <h3 className="text-2xl font-black text-white mb-4">AI Generation</h3>
                <p className="text-text-secondary leading-relaxed">
                  Unlimited unique challenges generated by advanced AI. Never run out of problems to solve.
                </p>
              </div>
            </div>

            {/* Feature 3 - Enhanced */}
            <div className="glass-panel p-10 hover:scale-105 transition-all cursor-pointer group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-success/5 rounded-full blur-3xl group-hover:bg-success/10 transition-all"></div>
              
              <div className="relative">
                <div className="h-20 w-20 rounded-2xl bg-success/20 border-2 border-success/40 flex-center mb-8 group-hover:scale-110 transition-transform shadow-glow-sm">
                  <Trophy size={36} className="text-success" />
                </div>
                <h3 className="text-2xl font-black text-white mb-4">ELO Rankings</h3>
                <p className="text-text-secondary leading-relaxed">
                  Climb the global leaderboard with our sophisticated ELO rating system. Track your progress.
                </p>
              </div>
            </div>

            {/* Feature 4 - Enhanced */}
            <div className="glass-panel p-10 hover:scale-105 transition-all cursor-pointer group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-warning/5 rounded-full blur-3xl group-hover:bg-warning/10 transition-all"></div>
              
              <div className="relative">
                <div className="h-20 w-20 rounded-2xl bg-warning/20 border-2 border-warning/40 flex-center mb-8 group-hover:scale-110 transition-transform shadow-glow-sm">
                  <Target size={36} className="text-warning" />
                </div>
                <h3 className="text-2xl font-black text-white mb-4">Smart Matching</h3>
                <p className="text-text-secondary leading-relaxed">
                  Get matched with opponents of similar skill level. Fair and challenging matches every time.
                </p>
              </div>
            </div>

            {/* Feature 5 - Enhanced */}
            <div className="glass-panel p-10 hover:scale-105 transition-all cursor-pointer group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-danger/5 rounded-full blur-3xl group-hover:bg-danger/10 transition-all"></div>
              
              <div className="relative">
                <div className="h-20 w-20 rounded-2xl bg-danger/20 border-2 border-danger/40 flex-center mb-8 group-hover:scale-110 transition-transform shadow-glow-sm">
                  <Bug size={36} className="text-danger" />
                </div>
                <h3 className="text-2xl font-black text-white mb-4">Debug Arena</h3>
                <p className="text-text-secondary leading-relaxed">
                  Master debugging skills by fixing intentionally broken code. Sharpen your error detection.
                </p>
              </div>
            </div>

            {/* Feature 6 - Enhanced */}
            <div className="glass-panel p-10 hover:scale-105 transition-all cursor-pointer group relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-all"></div>
              
              <div className="relative">
                <div className="h-20 w-20 rounded-2xl bg-primary/20 border-2 border-primary/40 flex-center mb-8 group-hover:scale-110 transition-transform shadow-glow-sm">
                  <Code size={36} className="text-primary" />
                </div>
                <h3 className="text-2xl font-black text-white mb-4">Practice Mode</h3>
                <p className="text-text-secondary leading-relaxed">
                  Hone your skills in solo practice mode. No pressure, just pure learning and improvement.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section - Enhanced */}
      <div className="mt-12 pb-16 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="glass-panel p-8 border-primary/40 relative overflow-hidden group hover:border-primary/60 transition-all">
            <div className="absolute top-0 right-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl group-hover:scale-150 transition-transform"></div>
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl group-hover:scale-150 transition-transform"></div>
            
            <div className="relative">
              <h2 className="text-3xl md:text-4xl font-black text-white mb-4 text-center">
                Ready to <span className="text-gradient">Compete</span>?
              </h2>
              <p className="text-base md:text-lg text-text-secondary mb-6 leading-relaxed text-center max-w-3xl mx-auto">
                Join thousands of developers sharpening their skills through competitive programming
              </p>
              <div className="text-center">
                <button
                  onClick={() => navigate('/register')}
                  className="btn btn-primary text-base px-10 py-4 group shadow-glow-xl hover:shadow-glow-2xl transition-all"
                >
                  Create Free Account
                  <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6 mt-12">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="h-10 w-14 flex-center">
                <img src="/logo.svg" alt="CodeRoad" className="h-full w-full object-contain" />
              </div>
              <span className="text-lg font-black text-gradient">CodeRoad</span>
            </div>
            
            <div className="text-text-muted text-sm">
              © 2026 CodeRoad. Built for competitive programmers.
            </div>
            
            <div className="flex items-center gap-4">
              <a href="#" className="text-text-muted hover:text-primary transition-colors">
                <Code size={18} />
              </a>
              <a href="#" className="text-text-muted hover:text-primary transition-colors">
                <Trophy size={18} />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
