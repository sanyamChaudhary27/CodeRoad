import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, type User } from '../services/authService';
import { matchmakingService, type LeaderboardPlayer } from '../services/matchmakingService';
import { Trophy, Medal, Crown, Award, TrendingUp, Zap, Target, Flame, Database, Palette, Clock } from 'lucide-react';
import Header from '../components/Header';

const Leaderboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [arenaType, setArenaType] = useState<'dsa' | 'debug' | 'dbms' | 'ui'>('dsa');

  useEffect(() => {
    // Fetch user data on mount
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

  useEffect(() => {
    const fetchData = async () => {
      // Only fetch for active arenas (DSA and Debug)
      if (arenaType === 'dbms' || arenaType === 'ui') {
        setLeaderboard([]);
        setLoading(false);
        return;
      }

      setLoading(true);
      try {
        const lbData = await matchmakingService.getGlobalLeaderboard(50, 0, arenaType);
        setLeaderboard(lbData.leaderboard);
      } catch (err) {
        console.error("Failed to fetch leaderboard", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [arenaType]);

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Crown size={20} className="text-yellow-400" />;
    if (rank === 2) return <Medal size={20} className="text-gray-300" />;
    if (rank === 3) return <Medal size={20} className="text-amber-600" />;
    return null;
  };

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) return 'from-yellow-500 to-yellow-600 border-yellow-400/50';
    if (rank === 2) return 'from-gray-400 to-gray-500 border-gray-400/50';
    if (rank === 3) return 'from-amber-600 to-amber-700 border-amber-600/50';
    return 'from-bg-panel-light to-bg-panel border-white/10';
  };

  if (loading) {
    return (
      <div className="min-h-screen flex-center">
        <div className="animate-pulse-glow p-4 rounded-full bg-primary/20">
          <Trophy size={32} className="text-primary animate-pulse" />
        </div>
      </div>
    );
  }

  const userRank = leaderboard.findIndex(p => p.username === user?.username) + 1;

  return (
    <div className="min-h-screen p-6 lg:p-12 animate-fade-in">
      <div className="max-w-7xl mx-auto">
      
      {user && <Header user={user} showLeaderboard={false} />}
      {/* Back Button */}
      <button
        onClick={() => navigate('/dashboard')}
        className="text-text-muted hover:text-primary transition-colors flex items-center gap-2 text-sm font-semibold uppercase tracking-wider mb-6"
      >
        <span>←</span> Back to Dashboard
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column - Stats & Top 3 */}
          <div className="lg:col-span-4 space-y-6">
            
            {/* Header Card */}
            <div className="glass-panel p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-warning/10 rounded-full blur-3xl"></div>
              
              <div className="relative">
                <div className="flex items-center gap-3 mb-4">
                  <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-warning to-warning/80 flex-center shadow-lg">
                    <Trophy size={24} className="text-white" />
                  </div>
                  <div>
                    <h1 className="text-2xl font-black text-white">Global Leaderboard</h1>
                    <p className="text-xs text-text-muted uppercase tracking-wider">Top Competitors</p>
                  </div>
                </div>

                {/* Arena Tabs */}
                <div className="grid grid-cols-4 gap-2 mb-4">
                  <button
                    onClick={() => setArenaType('dsa')}
                    className={`px-2 py-4 rounded-lg font-bold text-xs transition-all ${
                      arenaType === 'dsa'
                        ? 'bg-primary text-white shadow-lg'
                        : 'bg-bg-panel-light text-text-secondary hover:text-white'
                    }`}
                  >
                    DSA
                  </button>
                  <button
                    onClick={() => setArenaType('debug')}
                    className={`px-2 py-4 rounded-lg font-bold text-xs transition-all ${
                      arenaType === 'debug'
                        ? 'bg-danger text-white shadow-lg'
                        : 'bg-bg-panel-light text-text-secondary hover:text-white'
                    }`}
                  >
                    Debug
                  </button>
                  <button
                    onClick={() => setArenaType('dbms')}
                    className={`px-2 py-4 rounded-lg font-bold text-xs transition-all relative ${
                      arenaType === 'dbms'
                        ? 'bg-yellow-500 text-white shadow-lg'
                        : 'bg-bg-panel-light text-text-secondary hover:text-white'
                    }`}
                  >
                    <div className="flex flex-col items-center justify-center gap-1">
                      <Database size={14} />
                      <span>DBMS</span>
                    </div>
                  </button>
                  <button
                    onClick={() => setArenaType('ui')}
                    className={`px-2 py-4 rounded-lg font-bold text-xs transition-all relative ${
                      arenaType === 'ui'
                        ? 'bg-green-500 text-white shadow-lg'
                        : 'bg-bg-panel-light text-text-secondary hover:text-white'
                    }`}
                  >
                    <div className="flex flex-col items-center justify-center gap-1">
                      <Palette size={14} />
                      <span>UI</span>
                    </div>
                  </button>
                </div>

                {/* Your Rank */}
                {user && userRank > 0 && arenaType !== 'dbms' && arenaType !== 'ui' && (
                  <div className="p-4 rounded-xl bg-primary/10 border border-primary/30">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Your Rank</p>
                        <p className="text-2xl font-black text-white">#{userRank}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Rating</p>
                        <p className="text-2xl font-black text-primary">
                          {arenaType === 'debug' ? (user.debug_rating || 300) : user.current_rating}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Placeholder for DBMS/UI */}
                {user && (arenaType === 'dbms' || arenaType === 'ui') && (
                  <div className="p-4 rounded-xl bg-warning/10 border border-warning/30">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Your Rank</p>
                        <p className="text-2xl font-black text-white">----</p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-text-muted uppercase tracking-wider mb-1">Rating</p>
                        <p className="text-2xl font-black text-warning">----</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Coming Soon Banner for DBMS/UI */}
            {(arenaType === 'dbms' || arenaType === 'ui') && (
              <div className="glass-panel p-6 relative overflow-hidden border-warning/30">
                <div className="absolute top-0 right-0 w-48 h-48 bg-warning/10 rounded-full blur-3xl"></div>
                
                <div className="relative text-center py-8">
                  <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-warning to-warning/80 flex-center mx-auto mb-4 shadow-lg">
                    {arenaType === 'dbms' ? <Database size={32} className="text-white" /> : <Palette size={32} className="text-white" />}
                  </div>
                  <h3 className="text-xl font-bold text-white mb-2">
                    {arenaType === 'dbms' ? 'DBMS Arena' : 'UI Arena'}
                  </h3>
                  <p className="text-text-secondary mb-4">Coming Soon</p>
                  <div className="flex items-center justify-center gap-2 text-sm text-warning">
                    <Clock size={16} />
                    <span>{arenaType === 'dbms' ? 'Q2 2026' : 'Q3 2026'}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Top 3 Podium - Compact */}
            {leaderboard.length >= 3 && arenaType !== 'dbms' && arenaType !== 'ui' && (
              <div className="glass-panel p-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-48 h-48 bg-yellow-400/5 rounded-full blur-3xl"></div>
                
                <div className="relative">
                  <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Crown size={20} className="text-warning" />
                    Top 3 Champions
                  </h2>

                  <div className="space-y-3">
                    {/* 1st Place */}
                    <div className="p-4 rounded-xl bg-gradient-to-r from-yellow-500/20 to-transparent border border-yellow-400/40 hover:border-yellow-400/60 transition-all group">
                      <div className="flex items-center gap-3">
                        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-yellow-500 to-yellow-600 flex-center shadow-lg shrink-0">
                          <Crown size={24} className="text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-bold text-lg truncate">{leaderboard[0].username}</p>
                          <p className="text-xs text-text-muted">{leaderboard[0].wins}W - {leaderboard[0].losses}L</p>
                        </div>
                        <div className="text-right">
                          <p className="text-yellow-400 font-black text-xl">{leaderboard[0].current_rating}</p>
                          <p className="text-[10px] text-text-muted uppercase">ELO</p>
                        </div>
                      </div>
                    </div>

                    {/* 2nd Place */}
                    <div className="p-4 rounded-xl bg-gradient-to-r from-gray-400/20 to-transparent border border-gray-400/40 hover:border-gray-400/60 transition-all group">
                      <div className="flex items-center gap-3">
                        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-gray-400 to-gray-500 flex-center shadow-lg shrink-0">
                          <Medal size={24} className="text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-bold text-lg truncate">{leaderboard[1].username}</p>
                          <p className="text-xs text-text-muted">{leaderboard[1].wins}W - {leaderboard[1].losses}L</p>
                        </div>
                        <div className="text-right">
                          <p className="text-gray-300 font-black text-xl">{leaderboard[1].current_rating}</p>
                          <p className="text-[10px] text-text-muted uppercase">ELO</p>
                        </div>
                      </div>
                    </div>

                    {/* 3rd Place */}
                    <div className="p-4 rounded-xl bg-gradient-to-r from-amber-600/20 to-transparent border border-amber-600/40 hover:border-amber-600/60 transition-all group">
                      <div className="flex items-center gap-3">
                        <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-amber-600 to-amber-700 flex-center shadow-lg shrink-0">
                          <Medal size={24} className="text-white" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-bold text-lg truncate">{leaderboard[2].username}</p>
                          <p className="text-xs text-text-muted">{leaderboard[2].wins}W - {leaderboard[2].losses}L</p>
                        </div>
                        <div className="text-right">
                          <p className="text-amber-600 font-black text-xl">{leaderboard[2].current_rating}</p>
                          <p className="text-[10px] text-text-muted uppercase">ELO</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Stats Card - Only show for active arenas */}
            {arenaType !== 'dbms' && arenaType !== 'ui' && (
            <div className="glass-panel p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-48 h-48 bg-primary/5 rounded-full blur-3xl"></div>
              
              <div className="relative">
                <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Zap size={20} className="text-accent" />
                  Arena Stats
                </h2>

                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-bg-panel-light/50 border border-white/10">
                    <div className="flex items-center gap-2">
                      <Target size={16} className="text-primary" />
                      <span className="text-sm text-text-secondary">Total Players</span>
                    </div>
                    <span className="text-white font-bold">{leaderboard.length}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-bg-panel-light/50 border border-white/10">
                    <div className="flex items-center gap-2">
                      <Flame size={16} className="text-warning" />
                      <span className="text-sm text-text-secondary">Avg Rating</span>
                    </div>
                    <span className="text-white font-bold">
                      {leaderboard.length > 0 
                        ? Math.round(leaderboard.reduce((sum, p) => sum + p.current_rating, 0) / leaderboard.length)
                        : 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between p-3 rounded-lg bg-bg-panel-light/50 border border-white/10">
                    <div className="flex items-center gap-2">
                      <Trophy size={16} className="text-success" />
                      <span className="text-sm text-text-secondary">Top Rating</span>
                    </div>
                    <span className="text-white font-bold">
                      {leaderboard.length > 0 ? leaderboard[0].current_rating : 0}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            )}
          </div>

          {/* Right Column - Full Rankings */}
          <div className="lg:col-span-8">
            <div className="glass-panel p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl"></div>
              
              <div className="relative">
                <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-3">
                  <div className="h-10 w-10 rounded-lg bg-primary/20 flex-center">
                    <TrendingUp size={20} className="text-primary" />
                  </div>
                  Complete Rankings
                </h2>
                
                {arenaType === 'dbms' || arenaType === 'ui' ? (
                  <div className="text-center py-32 text-text-muted">
                    <div className="h-24 w-24 rounded-2xl bg-gradient-to-br from-warning to-warning/80 flex-center mx-auto mb-6 shadow-lg">
                      {arenaType === 'dbms' ? <Database size={48} className="text-white" /> : <Palette size={48} className="text-white" />}
                    </div>
                    <h3 className="text-2xl font-bold text-white mb-3">
                      {arenaType === 'dbms' ? 'DBMS Arena' : 'UI Arena'} Leaderboard
                    </h3>
                    <p className="text-lg mb-2">Coming Soon</p>
                    <div className="flex items-center justify-center gap-2 text-warning mb-8">
                      <Clock size={18} />
                      <span className="font-semibold">{arenaType === 'dbms' ? 'Q2 2026' : 'Q3 2026'}</span>
                    </div>
                    <p className="text-sm text-text-secondary max-w-md mx-auto mb-8">
                      {arenaType === 'dbms' 
                        ? 'Master SQL queries and database optimization in competitive challenges'
                        : 'Build pixel-perfect interfaces from designs in competitive sprints'}
                    </p>
                    <button 
                      onClick={() => navigate('/dashboard')}
                      className="btn btn-primary px-8 py-4"
                    >
                      Back to Dashboard
                    </button>
                  </div>
                ) : leaderboard.length > 0 ? (
                  <div className="space-y-2">
                    {leaderboard.map((player, index) => (
                      <div 
                        key={player.player_id} 
                        className={`p-4 rounded-xl border flex items-center gap-4 transition-all hover:scale-[1.01] cursor-pointer ${
                          player.username === user?.username 
                            ? 'bg-primary/10 border-primary/40 shadow-lg' 
                            : index < 3
                            ? 'bg-gradient-to-r from-warning/5 to-transparent border-warning/20 hover:border-warning/40'
                            : 'bg-bg-panel-light/30 border-white/5 hover:border-primary/20'
                        }`}
                      >
                        {/* Rank Badge */}
                        <div className={`h-11 w-11 rounded-lg bg-gradient-to-br ${getRankBadgeColor(player.rank)} border flex-center shrink-0 shadow-md`}>
                          {getRankIcon(player.rank) || (
                            <span className="font-mono font-black text-white text-sm">#{player.rank}</span>
                          )}
                        </div>
                        
                        {/* Avatar */}
                        <div className="h-11 w-11 rounded-lg bg-gradient-to-br from-primary to-accent flex-center text-white font-bold text-lg shrink-0 shadow-md">
                          {player.username.charAt(0).toUpperCase()}
                        </div>
                        
                        {/* Player Info */}
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-bold text-base truncate">{player.username}</p>
                          <p className="text-xs text-text-secondary">
                            {player.wins}W - {player.losses}L
                            {player.matches_played > 0 && (
                              <span className="ml-2 text-accent font-semibold">
                                {Math.round((player.wins / player.matches_played) * 100)}% WR
                              </span>
                            )}
                          </p>
                        </div>
                        
                        {/* Rating */}
                        <div className="text-right shrink-0">
                          <div className="flex items-center gap-2">
                            <Award size={18} className="text-primary" />
                            <span className="text-primary font-mono font-black text-xl">{player.current_rating}</span>
                          </div>
                          <p className="text-[10px] text-text-muted uppercase tracking-wider">ELO Rating</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-20 text-text-muted">
                    <Trophy size={72} className="mx-auto mb-6 opacity-20" />
                    <p className="text-xl mb-3">No rankings available yet</p>
                    <p className="text-sm mb-8">Be the first to compete and claim the top spot!</p>
                    <button 
                      onClick={() => navigate('/dashboard')}
                      className="btn btn-primary px-8 py-4"
                    >
                      Start Competing
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;
