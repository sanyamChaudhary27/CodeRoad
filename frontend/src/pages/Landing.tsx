import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
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
    const targets = { players: 10, matches: 120, challenges: 999 };
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
    { step: '01', title: 'Queue Up', description: 'Hit "Find Match" and enter the matchmaking queue. We\'ll find an opponent within your ELO range.', icon: '🎯' },
    { step: '02', title: 'Get Matched', description: 'Our algorithm pairs you with a worthy opponent (±200 ELO). The challenge is revealed simultaneously.', icon: '🤝' },
    { step: '03', title: 'Battle', description: 'Code your solution in a real-time editor. Submit as many times as you want before the timer runs out.', icon: '⌨️' },
    { step: '04', title: 'Climb', description: 'Win to gain ELO. Lose to learn. Track your progress, earn badges, and dominate the leaderboard.', icon: '🏆' },
  ];

  return (
    <div className={`landing-page ${isVisible ? 'visible' : ''}`}>
      {/* Background Effects */}
      <div className="landing-bg">
        <div className="grid-overlay"></div>
        <div className="glow-orb glow-orb-1"></div>
        <div className="glow-orb glow-orb-2"></div>
        <div className="glow-orb glow-orb-3"></div>
        <div className="floating-code">
          <span className="code-line">{'const battle = await matchmaker.find();'}</span>
          <span className="code-line">{'if (player.elo > opponent.elo) {'}</span>
          <span className="code-line">{'  return solve(challenge);'}</span>
          <span className="code-line">{'}'}</span>
        </div>
      </div>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-brand">⚡ CodeRoad</div>
          <div className="hero-badge">
            <span className="badge-dot"></span>
            <span>RANKED COMPETITIVE CODING</span>
          </div>
          <h1 className="hero-title">
            <span className="title-line">Code.</span>
            <span className="title-line">Compete.</span>
            <span className="title-line title-accent">Conquer.</span>
          </h1>
          <p className="hero-subtitle">
            Battle opponents in real-time 1v1 coding duels. <br/>
            Our AI generates unique challenges matched to your skill level - solve them faster, climb the
            ELO leaderboard & earn your place among the best.
          </p>
          <div className="hero-actions">
            <button className="btn-primary" onClick={() => navigate('/register')}>
              <span className="btn-text">Start Battling</span>
              <span className="btn-icon">→</span>
            </button>
            <button className="btn-secondary" onClick={() => navigate('/login')}>
              Sign In
            </button>
          </div>
          <div className="hero-stats">
            <div className="stat-item">
              <span className="stat-number">{counters.players.toLocaleString()}+</span>
              <span className="stat-label">Players</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-number">{counters.matches.toLocaleString()}+</span>
              <span className="stat-label">Battles Fought</span>
            </div>
            <div className="stat-divider"></div>
            <div className="stat-item">
              <span className="stat-number">∞</span>
              <span className="stat-label">AI-Generated Challenges</span>
            </div>
          </div>
        </div>

        <div className="hero-visual">
          <div className="battle-card">
            <div className="battle-card-header">
              <span className="live-badge">● LIVE</span>
              <span className="match-type">RANKED 1v1</span>
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
                <div className="player-avatar">🧑</div>
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
      </section>

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

        <div className="arenas-grid">
          <div className="arena-card arena-dsa">
            <div className="arena-glow"></div>
            <div className="arena-icon">⚔️</div>
            <h3 className="arena-title">DSA Arena</h3>
            <p className="arena-description">
              Solve algorithmic problems from scratch. Data structures, dynamic programming,
              graphs, sorting — the classic competitive programming experience.
            </p>
            <div className="arena-meta">
              <span className="arena-rating">Starting ELO: 1200</span>
              <span className="arena-domains">8 Domains</span>
            </div>
            <button className="btn-arena" onClick={() => navigate('/register')}>
              Enter Arena →
            </button>
          </div>

          <div className="arena-card arena-debug">
            <div className="arena-glow"></div>
            <div className="arena-icon">🐛</div>
            <h3 className="arena-title">Debug Arena</h3>
            <p className="arena-description">
              Find and fix bugs in broken code. Race against your opponent to identify
              issues and submit the correct fix. Speed and precision matter.
            </p>
            <div className="arena-meta">
              <span className="arena-rating">Starting ELO: 300</span>
              <span className="arena-domains">Bug Hunting</span>
            </div>
            <button className="btn-arena" onClick={() => navigate('/register')}>
              Enter Arena →
            </button>
          </div>
        </div>
      </section>

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
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <span className="footer-logo">⚡ CodeRoad</span>
            <p className="footer-tagline">Where code meets competition.</p>
          </div>
          <div className="footer-links">
            <span>© 2026 CodeRoad</span>
            <span className="footer-sep">•</span>
            <span>Built with 🔥 for competitive coders</span>
          </div>
        </div>
        <div className="footer-contributors" style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid rgba(255,255,255,0.1)', textAlign: 'center' }}>
          <p style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.875rem', marginBottom: '0.75rem' }}>Contributors</p>
          <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <a href="https://github.com/sanyamChaudhary27" target="_blank" rel="noopener noreferrer" style={{ color: 'rgba(255,255,255,0.8)', textDecoration: 'none', fontSize: '0.875rem', transition: 'color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = '#fff'} onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255,255,255,0.8)'}>Sanyam Chaudhary</a>
            <a href="https://github.com/pennedbyv" target="_blank" rel="noopener noreferrer" style={{ color: 'rgba(255,255,255,0.8)', textDecoration: 'none', fontSize: '0.875rem', transition: 'color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = '#fff'} onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255,255,255,0.8)'}>Vedratna Bura</a>
            <a href="https://github.com/GajananDhangude" target="_blank" rel="noopener noreferrer" style={{ color: 'rgba(255,255,255,0.8)', textDecoration: 'none', fontSize: '0.875rem', transition: 'color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = '#fff'} onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255,255,255,0.8)'}>Gajanan Dhangude</a>
            <a href="https://github.com/RAVIKUMAR-CEO" target="_blank" rel="noopener noreferrer" style={{ color: 'rgba(255,255,255,0.8)', textDecoration: 'none', fontSize: '0.875rem', transition: 'color 0.2s' }} onMouseEnter={(e) => e.currentTarget.style.color = '#fff'} onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255,255,255,0.8)'}>RK Reddy</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
