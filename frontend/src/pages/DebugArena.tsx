import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Bug, Play, Users, Clock } from 'lucide-react';
import { authService, type User } from '../services/authService';
import { matchmakingService } from '../services/matchmakingService';

const DebugArena = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedMode, setSelectedMode] = useState<'solo' | '1v1' | null>(location.state?.mode || null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      } catch (err) {
        console.error("Failed to fetch user", err);
      }
    };
    fetchUser();
  }, []);

  const startSoloMatch = async () => {
    if (!user) return;
    
    try {
      setLoading(true);
      // Create a debug solo practice match
      const match = await matchmakingService.createPracticeMatch('intermediate', 'debug');
      navigate('/arena', { state: { matchId: match.id || match.match_id, challengeType: 'debug' } });
    } catch (err) {
      console.error("Failed to start debug solo match", err);
      alert("Failed to start match. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const start1v1Match = () => {
    // TODO: Implement 1v1 debug matchmaking
    alert("1v1 Debug Arena coming soon! For now, try Solo Practice.");
  };

  if (!user) {
    return (
      <div className="min-h-screen flex-center">
        <div className="animate-pulse-glow p-4 rounded-full bg-danger/20">
          <Bug size={32} className="text-danger animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-bg-dark via-bg-panel to-bg-dark p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Bug size={48} className="text-danger animate-pulse" />
            <h1 className="text-5xl md:text-7xl font-black italic tracking-tighter text-white uppercase">
              Debug Arena
            </h1>
          </div>
          <p className="text-text-secondary text-sm md:text-base tracking-wider uppercase font-bold">
            Fix the bugs. Beat the clock. Dominate the leaderboard.
          </p>
        </div>

        {/* Mode Selection */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Solo Practice */}
          <div 
            className={`glass-panel p-8 cursor-pointer transition-all hover:scale-105 hover:shadow-glow ${
              selectedMode === 'solo' ? 'border-primary shadow-glow' : 'border-white/10'
            }`}
            onClick={() => setSelectedMode('solo')}
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="bg-primary/20 p-4 rounded-xl border border-primary/40">
                <Play size={32} className="text-primary" />
              </div>
              <div>
                <h2 className="text-2xl font-black text-white uppercase">Solo Practice</h2>
                <p className="text-text-muted text-sm">Train your debugging skills</p>
              </div>
            </div>
            
            <div className="space-y-2 text-sm text-text-secondary">
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-primary" />
                <span>5 minutes per challenge</span>
              </div>
              <div className="flex items-center gap-2">
                <Bug size={16} className="text-danger" />
                <span>1-3 bugs to fix</span>
              </div>
              <div className="text-text-muted">
                • No rating impact<br />
                • Unlimited retries<br />
                • Perfect for learning
              </div>
            </div>

            {selectedMode === 'solo' && (
              <button
                onClick={startSoloMatch}
                disabled={loading}
                className="btn btn-primary w-full mt-6 py-3 font-black uppercase tracking-wider"
              >
                {loading ? 'Starting Match...' : 'Start Solo Match'}
              </button>
            )}
          </div>

          {/* 1v1 Competitive */}
          <div 
            className={`glass-panel p-8 cursor-pointer transition-all hover:scale-105 hover:shadow-glow ${
              selectedMode === '1v1' ? 'border-danger shadow-glow' : 'border-white/10'
            }`}
            onClick={() => setSelectedMode('1v1')}
          >
            <div className="flex items-center gap-4 mb-4">
              <div className="bg-danger/20 p-4 rounded-xl border border-danger/40">
                <Users size={32} className="text-danger" />
              </div>
              <div>
                <h2 className="text-2xl font-black text-white uppercase">1v1 Competitive</h2>
                <p className="text-text-muted text-sm">Battle other debuggers</p>
              </div>
            </div>
            
            <div className="space-y-2 text-sm text-text-secondary">
              <div className="flex items-center gap-2">
                <Clock size={16} className="text-danger" />
                <span>2.5 minutes per challenge</span>
              </div>
              <div className="flex items-center gap-2">
                <Bug size={16} className="text-danger" />
                <span>1-3 bugs to fix</span>
              </div>
              <div className="text-text-muted">
                • ELO rating impact<br />
                • Real-time opponent tracking<br />
                • Competitive rankings
              </div>
            </div>

            {selectedMode === '1v1' && (
              <button
                onClick={start1v1Match}
                className="btn btn-danger w-full mt-6 py-3 font-black uppercase tracking-wider"
              >
                Find Opponent
              </button>
            )}
          </div>
        </div>

        {/* Stats Section */}
        <div className="glass-panel p-6">
          <h3 className="text-xl font-black text-white uppercase mb-4">Your Debug Stats</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-3xl font-black text-danger">{user.debug_rating || 300}</div>
              <div className="text-xs text-text-muted uppercase tracking-wider">Rating</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-white">{user.debug_matches_played || 0}</div>
              <div className="text-xs text-text-muted uppercase tracking-wider">Matches</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-success">{user.debug_wins || 0}</div>
              <div className="text-xs text-text-muted uppercase tracking-wider">Wins</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-black text-text-secondary">
                {user.debug_matches_played ? Math.round((user.debug_wins || 0) / user.debug_matches_played * 100) : 0}%
              </div>
              <div className="text-xs text-text-muted uppercase tracking-wider">Win Rate</div>
            </div>
          </div>
        </div>

        {/* Back Button */}
        <div className="text-center mt-8">
          <button
            onClick={() => navigate('/dashboard')}
            className="text-text-muted hover:text-white transition-colors uppercase tracking-wider text-sm font-bold"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default DebugArena;
