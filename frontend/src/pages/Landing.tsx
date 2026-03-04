import { useNavigate } from 'react-router-dom';
import { Code, Trophy, Zap, Users, Target, Bug, Sparkles, ArrowRight, Github, Twitter } from 'lucide-react';

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-bg-dark via-bg-panel to-bg-dark overflow-hidden">
      {/* Hero Section */}
      <div className="relative min-h-screen flex flex-col">
        {/* Navigation */}
        <nav className="glass-panel border-b border-white/5 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary via-accent to-success flex-center">
                <Code size={24} className="text-white" />
              </div>
              <span className="text-2xl font-black text-gradient">CodeRoad</span>
            </div>
            
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/login')}
                className="text-text-secondary hover:text-white transition-colors font-semibold"
              >
                Login
              </button>
              <button
                onClick={() => navigate('/register')}
                className="btn btn-primary"
              >
                Get Started
              </button>
            </div>
          </div>
        </nav>

        {/* Hero Content */}
        <div className="flex-1 flex items-center justify-center px-6 py-20">
          <div className="max-w-6xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-8 animate-fade-in">
              <Sparkles size={16} className="text-primary" />
              <span className="text-sm font-semibold text-primary">AI-Powered Competitive Programming</span>
            </div>
            
            <h1 className="text-6xl md:text-8xl font-black mb-6 animate-fade-in">
              <span className="text-white">Master</span>
              <br />
              <span className="text-gradient">Algorithms</span>
              <br />
              <span className="text-white">Through</span>{' '}
              <span className="text-gradient">Battle</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-text-secondary mb-12 max-w-3xl mx-auto animate-fade-in">
              Compete in real-time 1v1 coding battles. Solve AI-generated challenges. 
              Climb the leaderboard. Become a coding champion.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-fade-in">
              <button
                onClick={() => navigate('/register')}
                className="btn btn-primary text-lg px-8 py-4 group"
              >
                Start Your Journey
                <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={() => navigate('/login')}
                className="btn btn-secondary text-lg px-8 py-4"
              >
                Sign In
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 mt-20 max-w-3xl mx-auto">
              <div className="text-center">
                <div className="text-4xl font-black text-gradient mb-2">1000+</div>
                <div className="text-sm text-text-muted uppercase tracking-wider">Challenges</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-black text-gradient mb-2">Real-Time</div>
                <div className="text-sm text-text-muted uppercase tracking-wider">Battles</div>
              </div>
              <div className="text-center">
                <div className="text-4xl font-black text-gradient mb-2">AI-Powered</div>
                <div className="text-sm text-text-muted uppercase tracking-wider">Generation</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-black text-white mb-4">
              Why <span className="text-gradient">CodeRoad</span>?
            </h2>
            <p className="text-xl text-text-secondary">
              The ultimate platform for competitive programmers
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="glass-panel p-8 hover:scale-105 transition-transform cursor-pointer group">
              <div className="h-16 w-16 rounded-xl bg-primary/20 border border-primary/40 flex-center mb-6 group-hover:scale-110 transition-transform">
                <Users size={32} className="text-primary" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">1v1 Battles</h3>
              <p className="text-text-secondary">
                Compete against real opponents in real-time coding duels. Test your skills under pressure.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="glass-panel p-8 hover:scale-105 transition-transform cursor-pointer group">
              <div className="h-16 w-16 rounded-xl bg-accent/20 border border-accent/40 flex-center mb-6 group-hover:scale-110 transition-transform">
                <Zap size={32} className="text-accent" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">AI Generation</h3>
              <p className="text-text-secondary">
                Unlimited unique challenges generated by advanced AI. Never run out of problems to solve.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="glass-panel p-8 hover:scale-105 transition-transform cursor-pointer group">
              <div className="h-16 w-16 rounded-xl bg-success/20 border border-success/40 flex-center mb-6 group-hover:scale-110 transition-transform">
                <Trophy size={32} className="text-success" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">ELO Rankings</h3>
              <p className="text-text-secondary">
                Climb the global leaderboard with our sophisticated ELO rating system. Track your progress.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="glass-panel p-8 hover:scale-105 transition-transform cursor-pointer group">
              <div className="h-16 w-16 rounded-xl bg-warning/20 border border-warning/40 flex-center mb-6 group-hover:scale-110 transition-transform">
                <Target size={32} className="text-warning" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Smart Matching</h3>
              <p className="text-text-secondary">
                Get matched with opponents of similar skill level. Fair and challenging matches every time.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="glass-panel p-8 hover:scale-105 transition-transform cursor-pointer group">
              <div className="h-16 w-16 rounded-xl bg-danger/20 border border-danger/40 flex-center mb-6 group-hover:scale-110 transition-transform">
                <Bug size={32} className="text-danger" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Debug Arena</h3>
              <p className="text-text-secondary">
                Master debugging skills by fixing intentionally broken code. Sharpen your error detection.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="glass-panel p-8 hover:scale-105 transition-transform cursor-pointer group">
              <div className="h-16 w-16 rounded-xl bg-primary/20 border border-primary/40 flex-center mb-6 group-hover:scale-110 transition-transform">
                <Code size={32} className="text-primary" />
              </div>
              <h3 className="text-2xl font-bold text-white mb-3">Practice Mode</h3>
              <p className="text-text-secondary">
                Hone your skills in solo practice mode. No pressure, just pure learning and improvement.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-32 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="glass-panel p-12 border-primary/30">
            <h2 className="text-5xl font-black text-white mb-6">
              Ready to <span className="text-gradient">Compete</span>?
            </h2>
            <p className="text-xl text-text-secondary mb-10">
              Join thousands of developers sharpening their skills through competitive programming
            </p>
            <button
              onClick={() => navigate('/register')}
              className="btn btn-primary text-lg px-12 py-4 group"
            >
              Create Free Account
              <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary via-accent to-success flex-center">
                <Code size={24} className="text-white" />
              </div>
              <span className="text-xl font-black text-gradient">CodeRoad</span>
            </div>
            
            <div className="text-text-muted text-sm">
              © 2026 CodeRoad. Built for competitive programmers.
            </div>
            
            <div className="flex items-center gap-4">
              <a href="#" className="text-text-muted hover:text-primary transition-colors">
                <Github size={20} />
              </a>
              <a href="#" className="text-text-muted hover:text-primary transition-colors">
                <Twitter size={20} />
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
