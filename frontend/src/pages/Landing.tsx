import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { Code, Trophy, Zap, Users, Target, Bug, Sparkles, ArrowRight } from 'lucide-react';
import './Landing.css';

const Landing = () => {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);
  const [activeFeature, setActiveFeature] = useState(0);
  const [counters, setCounters] = useState({ players: 0, matches: 0, challenges: 0 });
  const [timerSeconds, setTimerSeconds] = useState(84); // starts at 01:24

  useEffect(() => {
    setIsVisible(true);

    // Animate counters
    const duration = 2000;
    const steps = 60;
    const interval = duration / steps;
    const targets = { players: 1200, matches: 8500, challenges: 350 };
    let step = 0;

    const timer = setInterval(() => {
      step++;
      const progress = step / steps;
      const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
      setCounters({
        players: Math.floor(targets.players * eased),
        matches: Math.floor(targets.matches * eased),
        challenges: Math.floor(targets.challenges * eased),
      });
      if (step >= steps) clearInterval(timer);
    }, interval);

    // Auto-rotate features
    const featureTimer = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % 4);
    }, 3000);

    // Ticking battle timer
    const battleTimer = setInterval(() => {
      setTimerSeconds((prev) => (prev <= 0 ? 84 : prev - 1));
    }, 1000);

    return () => {
      clearInterval(timer);
      clearInterval(featureTimer);
      clearInterval(battleTimer);
    };
  }, []);

  const formatTimer = (s: number) => {
    const min = Math.floor(s / 60).toString().padStart(2, '0');
    const sec = (s % 60).toString().padStart(2, '0');
    return `${min}:${sec}`;
  };

  const features = [
    {
      icon: '⚔️',
      title: '1v1 Ranked Battles',
      description: 'Face off against opponents matched to your skill level. Solve AI-generated challenges under pressure and climb the ranks.',
    },
    {
      icon: '🐛',
      title: 'Debug Arena',
      description: 'Find and fix bugs in broken code before your opponent does. A unique twist on competitive programming.',
    },
    {
      icon: '🤖',
      title: 'AI-Generated Challenges',
      description: 'Every problem is unique. Our AI crafts challenges tailored to your rating across 8 different coding domains.',
    },
    {
      icon: '🛡️',
      title: 'Integrity Verified',
      description: 'Advanced stylometric analysis and LLM detection ensure fair play. Your rank means something here.',
    },
  ];

  const howItWorks = [
    { step: '01', title: 'Queue Up', description: 'Hit "Find Match" and enter the matchmaking queue. We\'ll find an opponent within your ELO range.', icon: '🎮' },
    { step: '02', title: 'Get Matched', description: 'Our algorithm pairs you with a worthy opponent (±200 ELO). The challenge is revealed simultaneously.', icon: '🤝' },
    { step: '03', title: 'Battle', description: 'Code your solution in a real-time editor. Submit as many times as you want before the timer runs out.', icon: '⌨️' },
    { step: '04', title: 'Climb', description: 'Win to gain ELO. Lose to learn. Track your progress, earn badges, and dominate the leaderboard.', icon: '🏆' },
  ];

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
            <div className="battle-card-players">
              <div className="player-side player-left">
                <div className="player-avatar">👨‍💻</div>
                <span className="player-name">You</span>
                <span className="player-elo">1450 ELO</span>
                <div className="player-progress">
                  <div className="progress-bar" style={{ width: '75%' }}></div>
                </div>
              </div>
              <div className="vs-badge">VS</div>
              <div className="player-side player-right">
                <div className="player-avatar">🧠</div>
                <span className="player-name">Opponent</span>
                <span className="player-elo">1380 ELO</span>
                <div className="player-progress">
                  <div className="progress-bar" style={{ width: '45%' }}></div>
                </div>
              </div>
            </div>
            <div className="battle-card-timer">
              <span className="timer-icon">⏱️</span>
              <span className={`timer-value ${timerSeconds <= 10 ? 'timer-urgent' : ''}`}>{formatTimer(timerSeconds)}</span>
            </div>
            <div className="battle-card-challenge">
              <span className="challenge-tag">Dynamic Programming</span>
              <span className="challenge-difficulty difficulty-medium">Medium</span>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <section className="features-section">
        <div className="section-header">
          <span className="section-tag">FEATURES</span>
          <h2 className="section-title">Built for Competitive Coders</h2>
          <p className="section-subtitle">
            Everything you need to sharpen your skills and prove your worth in ranked battles.
          </p>
        </div>

        <div className="features-grid">
          {features.map((feature, index) => (
            <div
              key={index}
              className={`feature-card ${activeFeature === index ? 'feature-active' : ''}`}
              onMouseEnter={() => setActiveFeature(index)}
            >
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
              <div className="feature-glow"></div>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-section">
        <div className="section-header">
          <span className="section-tag">HOW IT WORKS</span>
          <h2 className="section-title">From Queue to Victory</h2>
          <p className="section-subtitle">
            Four steps. One winner. Are you ready?
          </p>
        </div>

        <div className="steps-container">
          <div className="steps-line"></div>
          {howItWorks.map((item, index) => (
            <div key={index} className="step-card" style={{ animationDelay: `${index * 0.15}s` }}>
              <div className="step-number">{item.step}</div>
              <div className="step-icon">{item.icon}</div>
              <h3 className="step-title">{item.title}</h3>
              <p className="step-description">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Arenas Section */}
      <section className="arenas-section">
        <div className="section-header">
          <span className="section-tag">ARENAS</span>
          <h2 className="section-title">Choose Your Battleground</h2>
          <p className="section-subtitle">Two arenas. Two rating systems. Double the competition.</p>
        </div>
      </section>

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
            <button className="btn-arena" onClick={() => navigate('/register')}>
              Enter Arena →
            </button>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="cta-content">
          <h2 className="cta-title">Ready to Prove Yourself?</h2>
          <p className="cta-subtitle">
            Join the arena. Every match is a new challenge. Every win takes you higher.
          </p>
          <button className="btn-primary btn-large" onClick={() => navigate('/register')}>
            <span className="btn-text">Create Account & Battle</span>
            <span className="btn-icon">⚡</span>
          </button>
        </div>
      </section>

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
