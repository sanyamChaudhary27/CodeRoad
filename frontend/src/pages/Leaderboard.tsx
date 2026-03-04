import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, type User } from '../services/authService';
import { matchmakingService, type LeaderboardPlayer } from '../services/matchmakingService';
import { Trophy, Medal, Crown, Award, TrendingUp, Users } from 'lucide-react';
import Header from '../components/Header';

const Leaderboard = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [leaderboard, setLeaderboard] = useState<LeaderboardPlayer[]>([]);
  const [loading, setLoading] = useState(true);
  const [arenaType, setArenaType] = useState<'dsa' | 'debug'>('dsa');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        
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
    if (rank === 1) return <Crown size={24} className="text-yellow-400" />;
    if (rank === 2) return <Medal size={24} className="text-gray-300" />;
    if (rank === 3) return <Medal size={24} className="text-amber-600" />;
    return null;
  };

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) return 'from-yellow-500 to-yellow-600';
    if (rank === 2) return 'from-gray-400 to-gray-500';
    if (rank === 3) return 'from-amber-600 to-amber-700';
    return 'from-bg-panel-light to-bg-panel';
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

  return (
    <div className="min-h-screen p-6 lg:p-12 animate-fade-in max-w-7xl mx-auto">
      
      {user && <Header user={user} showLeaderboard={false} />}

      {/* Back to Dashboard Button */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="text-text-muted hover:text-primary transition-colors flex items-center gap-2 text-sm font-semibold uppercase tracking-wider"
        >
          <span>←</span> Back to Dashboard
        </button>
      </div>

      {/* Header */}
      <div className="glass-panel p-8 mb-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-6">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
              <Trophy size={36} className="text-warning" />
              Global Leaderboard
            </h1>
            <p className="text-text-secondary text-lg">Top developers competing worldwide</p>
          </div>
          
          {user && (
            <div className="glass-panel p-4 px-6 border-primary/30">
              <p className="text-text-muted text-sm mb-1">Your Rank</p>
              <div className="flex items-center gap-3">
                <TrendingUp size={20} className="text-primary" />
                <span className="text-2xl font-bold text-white">#{leaderboard.findIndex(p => p.username === user.username) + 1 || '—'}</span>
                <span className="text-primary font-mono font-semibold">
                  {arenaType === 'debug' ? (user.debug_rating || 300) : user.current_rating} ELO
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Arena Type Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setArenaType('dsa')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              arenaType === 'dsa'
                ? 'bg-primary text-white shadow-glow'
                : 'bg-bg-panel-light text-text-secondary hover:text-white'
            }`}
          >
            DSA Arena
          </button>
          <button
            onClick={() => setArenaType('debug')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              arenaType === 'debug'
                ? 'bg-danger text-white shadow-glow'
                : 'bg-bg-panel-light text-text-secondary hover:text-white'
            }`}
          >
            Debug Arena
          </button>
        </div>
      </div>

      {/* Top 3 Podium - Enhanced */}
      {leaderboard.length >= 3 && (
        <div className="mb-8 grid grid-cols-3 gap-6 max-w-5xl mx-auto">
          {/* 2nd Place */}
          <div className="mt-16 animate-fade-in" style={{animationDelay: '0.1s'}}>
            <div className="glass-panel p-8 text-center border-gray-400/40 hover:border-gray-400/60 transition-all hover:scale-105 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-gray-400/10 rounded-full blur-2xl group-hover:scale-150 transition-transform"></div>
              
              <div className="relative">
                <div className="relative inline-block mb-6">
                  <div className="h-24 w-24 rounded-2xl bg-gradient-to-br from-gray-400 to-gray-500 flex-center text-white text-3xl font-bold shadow-glow-md mx-auto">
                    {leaderboard[1].username.charAt(0).toUpperCase()}
                  </div>
                  <div className="absolute -top-3 -right-3 h-10 w-10 rounded-xl bg-gradient-to-br from-gray-400 to-gray-500 flex-center shadow-glow-sm">
                    <Medal size={20} className="text-white" />
                  </div>
                </div>
                <p className="text-white font-bold text-xl mb-2">{leaderboard[1].username}</p>
                <p className="text-gray-300 font-mono font-bold text-lg mb-3">{leaderboard[1].current_rating}</p>
                <p className="text-sm text-text-muted">{leaderboard[1].wins}W - {leaderboard[1].losses}L</p>
              </div>
            </div>
          </div>

          {/* 1st Place */}
          <div className="animate-fade-in">
            <div className="glass-panel p-8 text-center border-yellow-400/40 hover:border-yellow-400/60 transition-all hover:scale-105 relative overflow-hidden group">
              <div className="absolute -top-6 left-1/2 transform -translate-x-1/2 z-10">
                <Crown size={40} className="text-yellow-400 animate-pulse drop-shadow-glow" />
              </div>
              <div className="absolute top-0 right-0 w-48 h-48 bg-yellow-400/10 rounded-full blur-3xl group-hover:scale-150 transition-transform"></div>
              
              <div className="relative mt-6">
                <div className="relative inline-block mb-6">
                  <div className="h-32 w-32 rounded-2xl bg-gradient-to-br from-yellow-500 to-yellow-600 flex-center text-white text-4xl font-bold shadow-glow-lg mx-auto">
                    {leaderboard[0].username.charAt(0).toUpperCase()}
                  </div>
                  <div className="absolute -top-3 -right-3 h-12 w-12 rounded-xl bg-gradient-to-br from-yellow-500 to-yellow-600 flex-center shadow-glow-md">
                    <Trophy size={24} className="text-white" />
                  </div>
                </div>
                <p className="text-white font-black text-2xl mb-2">{leaderboard[0].username}</p>
                <p className="text-yellow-400 font-mono font-black text-2xl mb-3">{leaderboard[0].current_rating}</p>
                <p className="text-base text-text-muted">{leaderboard[0].wins}W - {leaderboard[0].losses}L</p>
              </div>
            </div>
          </div>

          {/* 3rd Place */}
          <div className="mt-16 animate-fade-in" style={{animationDelay: '0.2s'}}>
            <div className="glass-panel p-8 text-center border-amber-600/40 hover:border-amber-600/60 transition-all hover:scale-105 relative overflow-hidden group">
              <div className="absolute top-0 right-0 w-32 h-32 bg-amber-600/10 rounded-full blur-2xl group-hover:scale-150 transition-transform"></div>
              
              <div className="relative">
                <div className="relative inline-block mb-6">
                  <div className="h-24 w-24 rounded-2xl bg-gradient-to-br from-amber-600 to-amber-700 flex-center text-white text-3xl font-bold shadow-glow-md mx-auto">
                    {leaderboard[2].username.charAt(0).toUpperCase()}
                  </div>
                  <div className="absolute -top-3 -right-3 h-10 w-10 rounded-xl bg-gradient-to-br from-amber-600 to-amber-700 flex-center shadow-glow-sm">
                    <Medal size={20} className="text-white" />
                  </div>
                </div>
                <p className="text-white font-bold text-xl mb-2">{leaderboard[2].username}</p>
                <p className="text-amber-600 font-mono font-bold text-lg mb-3">{leaderboard[2].current_rating}</p>
                <p className="text-sm text-text-muted">{leaderboard[2].wins}W - {leaderboard[2].losses}L</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Full Leaderboard Table - Enhanced */}
      <div className="glass-panel p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl"></div>
        
        <div className="relative">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary/20 flex-center">
              <Users size={24} className="text-primary" />
            </div>
            All Rankings
          </h2>
          
          {leaderboard.length > 0 ? (
            <div className="space-y-3">
              {leaderboard.map((player, index) => (
                <div 
                  key={player.player_id} 
                  className={`p-5 rounded-xl border flex items-center justify-between transition-all hover:scale-[1.02] cursor-pointer ${
                    player.username === user?.username 
                      ? 'bg-primary/10 border-primary/40 shadow-glow-sm' 
                      : index < 3
                      ? 'bg-gradient-to-r from-warning/5 to-transparent border-warning/30 hover:border-warning/50'
                      : 'bg-bg-panel-light/50 border-border-light hover:border-primary/30'
                  }`}
                >
                  <div className="flex items-center gap-5 flex-1">
                    {/* Rank */}
                    <div className={`h-14 w-14 rounded-xl bg-gradient-to-br ${getRankBadgeColor(player.rank)} flex-center shrink-0 shadow-md`}>
                      {getRankIcon(player.rank) || (
                        <span className="font-mono font-black text-white text-lg">#{player.rank}</span>
                      )}
                    </div>
                    
                    {/* Avatar */}
                    <div className="h-14 w-14 rounded-xl bg-gradient-to-br from-primary to-accent flex-center text-white font-bold text-xl shrink-0 shadow-md">
                      {player.username.charAt(0).toUpperCase()}
                    </div>
                    
                    {/* Player Info */}
                    <div className="flex-1 min-w-0">
                      <p className="text-white font-bold text-xl truncate">{player.username}</p>
                      <p className="text-sm text-text-secondary">
                        {player.wins}W - {player.losses}L 
                        {player.matches_played > 0 && (
                          <span className="ml-3 text-accent">
                            ({Math.round((player.wins / player.matches_played) * 100)}% WR)
                          </span>
                        )}
                      </p>
                    </div>
                    
                    {/* Rating */}
                    <div className="text-right">
                      <div className="flex items-center gap-3">
                        <Award size={20} className="text-primary" />
                        <span className="text-primary font-mono font-black text-2xl">{player.current_rating}</span>
                      </div>
                      <p className="text-xs text-text-muted uppercase tracking-wider">ELO Rating</p>
                    </div>
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
  );
};

export default Leaderboard;
