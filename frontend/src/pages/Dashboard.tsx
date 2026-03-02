import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, type User } from '../services/authService';
import { matchmakingService, type LeaderboardPlayer, type MatchQueueStatus } from '../services/matchmakingService';
import { LogOut, Trophy, Target, Activity, Users, ChevronRight, Award, Terminal, Database, Bug, Palette, Code2, Sparkles, Clock } from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardPlayer[]>([]);
  const [queueStatus, setQueueStatus] = useState<MatchQueueStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        
        const lbData = await matchmakingService.getGlobalLeaderboard(10, 0);
        setLeaderboard(lbData.leaderboard);
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const [isPolling, setIsPolling] = useState(false);

  const joinQueue = async () => {
    if (isPolling) return;
    try {
      await matchmakingService.joinQueue();
      setQueueStatus({ in_queue: true, joined_at: new Date().toISOString() });
      setIsPolling(true);
      
      // Real polling for match
      const pollInterval = setInterval(async () => {
        try {
          const status = await matchmakingService.getQueueStatus();
          if (status.match_id) {
            clearInterval(pollInterval);
            navigate('/arena', { state: { matchId: status.match_id } });
            setIsPolling(false);
          } else if (!status.in_queue) {
            // Someone else matched us or we were removed
            clearInterval(pollInterval);
            setQueueStatus(null);
            setIsPolling(false);
          }
        } catch (e) {
          console.error("Polling error", e);
        }
      }, 2000);

      // Timeout safety
      setTimeout(() => {
        clearInterval(pollInterval);
        setIsPolling(false);
      }, 60000);

    } catch (err) {
      console.error("Failed to join queue", err);
    }
  };

  const startPracticeMatch = async () => {
    try {
      setLoading(true);
      const match = await matchmakingService.createPracticeMatch('intermediate');
      navigate('/arena', { state: { matchId: match.id || match.match_id } });
    } catch (err) {
      console.error("Failed to start practice match", err);
      // Fallback
      navigate('/arena');
    } finally {
      setLoading(false);
    }
  };

  if (loading || !user) {
    return (
      <div className="min-h-screen flex-center">
        <div className="animate-pulse-glow p-4 rounded-full bg-primary/20">
          <Activity size={32} className="text-primary animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-6 lg:p-12 animate-fade-in max-w-7xl mx-auto">
      
      {/* Header */}
      <header className="flex-between mb-12 glass-panel p-4 px-6">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-primary to-accent flex-center">
            <Terminal size={20} className="text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white tracking-wide">Code Road</h1>
            <p className="text-xs text-primary uppercase tracking-widest font-mono">Terminal Active</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="text-right hidden sm:block">
            <p className="text-white font-medium">{user.username}</p>
            <p className="text-sm text-success font-mono">Rating: {user.current_rating}</p>
          </div>
          <button onClick={handleLogout} className="text-text-muted hover:text-danger transition-colors p-2 rounded-lg hover:bg-white/5">
            <LogOut size={20} />
          </button>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Main Actions column */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Hero Banner */}
          <div className="glass-panel p-8 md:p-10 relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
               <Target size={120} />
            </div>
            <h2 className="text-3xl md:text-5xl font-bold mb-4 text-white">Enter the <br/><span className="text-gradient">Proving Grounds</span></h2>
            <p className="text-text-secondary mb-8 max-w-md text-lg">
              Compete against other developers in real-time. Our AI engine scales the challenges to your exact skill level.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <button 
                onClick={joinQueue}
                disabled={!!queueStatus?.in_queue}
                className="btn btn-primary text-lg px-8 py-4 flex-1 sm:flex-none flex-between shadow-glow"
              >
                {queueStatus?.in_queue ? 'Finding Opponent...' : 'Competitive (1v1)'}
                {!queueStatus?.in_queue && <ChevronRight size={20} />}
              </button>

              <button 
                onClick={startPracticeMatch}
                className="btn btn-secondary text-lg px-8 py-4 flex-1 sm:flex-none flex items-center justify-center gap-2 border border-white/10"
              >
                <Activity size={20} />
                Solo Training
              </button>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="glass-panel p-5 flex flex-col items-center justify-center text-center">
              <Award className="text-warning mb-2" size={24} />
              <p className="text-3xl font-bold text-white">{user.wins || 0}</p>
              <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Victories</p>
            </div>
            <div className="glass-panel p-5 flex flex-col items-center justify-center text-center">
              <Activity className="text-accent mb-2" size={24} />
              <p className="text-3xl font-bold text-white">{(user.matches_played || 0) > 0 ? Math.round(((user.wins || 0) / (user.matches_played || 1)) * 100) : 0}%</p>
              <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Win Rate</p>
            </div>
            <div className="glass-panel p-5 flex flex-col items-center justify-center text-center">
              <Users className="text-primary mb-2" size={24} />
              <p className="text-3xl font-bold text-white">{user.matches_played || 0}</p>
              <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Matches</p>
            </div>
            <div className="glass-panel p-5 flex flex-col items-center justify-center text-center">
              <Trophy className="text-success mb-2" size={24} />
              <p className="text-3xl font-bold text-white">{user.current_rating}</p>
              <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Elo</p>
            </div>
          </div>
        </div>

        {/* Leaderboard Column */}
        <div className="glass-panel p-6 flex flex-col h-[600px]">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Trophy size={20} className="text-warning" />
            Global Top 10
          </h3>
          
          <div className="flex-1 overflow-y-auto pr-2 space-y-3">
            {leaderboard.length > 0 ? (
               leaderboard.map((player) => (
                 <div key={player.player_id} className={`p-4 rounded-xl border flex items-center justify-between ${player.username === user.username ? 'bg-primary/10 border-primary/30' : 'bg-bg-panel-light/50 border-border-light'}`}>
                   <div className="flex items-center gap-4">
                     <span className={`font-mono font-bold w-6 text-center ${player.rank <= 3 ? 'text-warning' : 'text-text-muted'}`}>
                       #{player.rank}
                     </span>
                     <div>
                       <p className="text-white font-medium">{player.username}</p>
                       <p className="text-xs text-text-secondary">{player.wins}W - {player.losses}L</p>
                     </div>
                   </div>
                   <div className="text-right">
                     <span className="text-primary font-mono font-bold">{player.current_rating}</span>
                   </div>
                 </div>
               ))
            ) : (
               <div className="h-full flex-center flex-col text-text-muted text-center p-6 border border-dashed border-border-light rounded-xl">
                 <Trophy size={48} className="mb-4 opacity-20" />
                 <p>No rankings available yet. Be the first to conquer the board!</p>
               </div>
            )}
          </div>
        </div>

      </div>

      {/* Coming Soon Features */}
      <div className="mt-12 glass-panel p-8">
        <div className="flex items-center gap-3 mb-6">
          <Sparkles size={24} className="text-warning" />
          <h3 className="text-2xl font-bold text-white">Coming Soon</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light hover:border-primary/50 transition-all group">
            <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex-center mb-4 group-hover:scale-110 transition-transform">
              <Database size={24} className="text-white" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">DBMS Arena</h4>
            <p className="text-sm text-text-secondary">Master SQL queries and database optimization in competitive challenges</p>
            <div className="mt-4 flex items-center gap-2 text-xs text-primary">
              <Clock size={14} />
              <span>Q2 2026</span>
            </div>
          </div>

          <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light hover:border-accent/50 transition-all group">
            <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-red-500 to-red-600 flex-center mb-4 group-hover:scale-110 transition-transform">
              <Bug size={24} className="text-white" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">Debug Arena</h4>
            <p className="text-sm text-text-secondary">Race to find and fix bugs in real codebases under time pressure</p>
            <div className="mt-4 flex items-center gap-2 text-xs text-accent">
              <Clock size={14} />
              <span>Q2 2026</span>
            </div>
          </div>

          <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light hover:border-warning/50 transition-all group">
            <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-purple-500 to-purple-600 flex-center mb-4 group-hover:scale-110 transition-transform">
              <Palette size={24} className="text-white" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">UI Arena</h4>
            <p className="text-sm text-text-secondary">Build pixel-perfect interfaces from designs in competitive sprints</p>
            <div className="mt-4 flex items-center gap-2 text-xs text-warning">
              <Clock size={14} />
              <span>Q3 2026</span>
            </div>
          </div>

          <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light hover:border-success/50 transition-all group">
            <div className="h-12 w-12 rounded-lg bg-gradient-to-br from-green-500 to-green-600 flex-center mb-4 group-hover:scale-110 transition-transform">
              <Code2 size={24} className="text-white" />
            </div>
            <h4 className="text-lg font-bold text-white mb-2">Multi-Language</h4>
            <p className="text-sm text-text-secondary">Python, Java, C++, JavaScript, Go, Rust and more languages supported</p>
            <div className="mt-4 flex items-center gap-2 text-xs text-success">
              <Clock size={14} />
              <span>Q3 2026</span>
            </div>
          </div>
        </div>
      </div>

      {/* Match History */}
      <div className="mt-8 glass-panel p-8">
        <div className="flex items-center gap-3 mb-6">
          <Activity size={24} className="text-primary" />
          <h3 className="text-2xl font-bold text-white">Recent Matches</h3>
        </div>
        
        <div className="space-y-3">
          {user.matches_played && user.matches_played > 0 ? (
            <div className="text-center py-12 text-text-muted">
              <Activity size={48} className="mx-auto mb-4 opacity-20" />
              <p>Match history will be available soon!</p>
              <p className="text-sm mt-2">Your {user.matches_played} match{user.matches_played !== 1 ? 'es' : ''} will appear here</p>
            </div>
          ) : (
            <div className="text-center py-12 text-text-muted border border-dashed border-border-light rounded-xl">
              <Target size={48} className="mx-auto mb-4 opacity-20" />
              <p>No matches played yet</p>
              <p className="text-sm mt-2">Start your first match to see your history!</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
