import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, type User as AuthUser } from '../services/authService';
import { matchmakingService, type MatchQueueStatus } from '../services/matchmakingService';
import { LogOut, Trophy, Activity, Users, ChevronRight, Award, Terminal, Database, Bug, Palette, Code2, User, Clock } from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [queueStatus, setQueueStatus] = useState<MatchQueueStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
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

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
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

      {/* Arena Selection Title */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Choose Your Arena</h2>
        <p className="text-text-secondary text-lg">Select a challenge type and compete in 1v1 battles or practice solo</p>
      </div>

      {/* Arena Cards - Full Width */}
      <div className="space-y-4 mb-12">
        
        {/* DSA Arena Card */}
        <div className="glass-panel p-6 hover:border-primary/50 transition-all relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl"></div>
          <div className="relative flex items-center gap-6">
            <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex-center shrink-0">
              <Code2 size={32} className="text-white" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-white mb-2">DSA Arena</h3>
              <p className="text-text-secondary mb-4">Data Structures & Algorithms challenges - Test your problem-solving skills</p>
              
              <div className="flex items-center gap-3">
                <button 
                  onClick={joinQueue}
                  disabled={!!queueStatus?.in_queue}
                  className="btn btn-primary px-6 py-3 flex items-center gap-2"
                >
                  {queueStatus?.in_queue ? 'Finding Opponent...' : '1v1 Battle'}
                  {!queueStatus?.in_queue && <ChevronRight size={18} />}
                </button>
                <button 
                  onClick={startPracticeMatch}
                  className="btn btn-secondary px-6 py-3 flex items-center gap-2 border border-white/10"
                >
                  <Activity size={18} />
                  Solo Practice
                </button>
                <div className="ml-auto flex items-center gap-2 text-sm">
                  <span className="text-text-muted">Difficulty:</span>
                  <span className="text-success font-semibold">Dynamic</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* DBMS Arena Card */}
        <div className="glass-panel p-6 hover:border-blue-500/50 transition-all relative overflow-hidden opacity-60">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full blur-2xl"></div>
          <div className="relative flex items-center gap-6">
            <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex-center shrink-0">
              <Database size={32} className="text-white" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-white mb-2">DBMS Arena</h3>
              <p className="text-text-secondary mb-4">SQL queries and database optimization challenges</p>
              
              <div className="flex items-center gap-3">
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed">
                  1v1 Battle
                </button>
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed border border-white/10">
                  Solo Practice
                </button>
                <div className="ml-auto flex items-center gap-2 text-sm text-warning">
                  <Clock size={16} />
                  <span>Coming Q2 2026</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Debug Arena Card */}
        <div className="glass-panel p-6 hover:border-red-500/50 transition-all relative overflow-hidden opacity-60">
          <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/5 rounded-full blur-2xl"></div>
          <div className="relative flex items-center gap-6">
            <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-red-500 to-red-600 flex-center shrink-0">
              <Bug size={32} className="text-white" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-white mb-2">Debug Arena</h3>
              <p className="text-text-secondary mb-4">Find and fix bugs in code under time pressure</p>
              
              <div className="flex items-center gap-3">
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed">
                  1v1 Battle
                </button>
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed border border-white/10">
                  Solo Practice
                </button>
                <div className="ml-auto flex items-center gap-2 text-sm text-accent">
                  <Clock size={16} />
                  <span>Coming Q2 2026</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* UI Arena Card */}
        <div className="glass-panel p-6 hover:border-purple-500/50 transition-all relative overflow-hidden opacity-60">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full blur-2xl"></div>
          <div className="relative flex items-center gap-6">
            <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex-center shrink-0">
              <Palette size={32} className="text-white" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-white mb-2">UI Arena</h3>
              <p className="text-text-secondary mb-4">Build pixel-perfect interfaces from designs in competitive sprints</p>
              
              <div className="flex items-center gap-3">
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed">
                  1v1 Battle
                </button>
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed border border-white/10">
                  Solo Practice
                </button>
                <div className="ml-auto flex items-center gap-2 text-sm text-warning">
                  <Clock size={16} />
                  <span>Coming Q3 2026</span>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <button 
          onClick={() => navigate('/leaderboard')}
          className="glass-panel p-6 hover:border-warning/50 transition-all group text-left"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-warning to-warning/60 flex-center group-hover:scale-110 transition-transform">
              <Trophy size={24} className="text-white" />
            </div>
            <ChevronRight size={24} className="text-text-muted group-hover:text-warning transition-colors" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Global Leaderboard</h3>
          <p className="text-sm text-text-secondary">See where you rank among the best developers worldwide</p>
        </button>

        <button 
          onClick={() => navigate('/profile')}
          className="glass-panel p-6 hover:border-primary/50 transition-all group text-left"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex-center group-hover:scale-110 transition-transform">
              <User size={24} className="text-white" />
            </div>
            <ChevronRight size={24} className="text-text-muted group-hover:text-primary transition-colors" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">Your Profile</h3>
          <p className="text-sm text-text-secondary">View your stats, achievements, and match history</p>
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
