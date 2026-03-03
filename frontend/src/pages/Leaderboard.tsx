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

  useEffect(() => {
    const fetchData = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
        
        const lbData = await matchmakingService.getGlobalLeaderboard(50, 0);
        setLeaderboard(lbData.leaderboard);
      } catch (err) {
        console.error("Failed to fetch leaderboard", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

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

      {/* Header */}
      <div className="glass-panel p-8 mb-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
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
                <span className="text-primary font-mono font-semibold">{user.current_rating} ELO</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Top 3 Podium */}
      {leaderboard.length >= 3 && (
        <div className="mb-8 grid grid-cols-3 gap-4 max-w-4xl mx-auto">
          {/* 2nd Place */}
          <div className="mt-12 animate-fade-in" style={{animationDelay: '0.1s'}}>
            <div className="glass-panel p-6 text-center border-gray-400/30 hover:border-gray-400/50 transition-all">
              <div className="relative inline-block mb-4">
                <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-gray-400 to-gray-500 flex-center text-white text-2xl font-bold shadow-lg mx-auto">
                  {leaderboard[1].username.charAt(0).toUpperCase()}
                </div>
                <div className="absolute -top-2 -right-2 h-8 w-8 rounded-lg bg-gradient-to-br from-gray-400 to-gray-500 flex-center shadow-lg">
                  <Medal size={16} className="text-white" />
                </div>
              </div>
              <p className="text-white font-bold text-lg mb-1">{leaderboard[1].username}</p>
              <p className="text-gray-300 font-mono font-semibold mb-2">{leaderboard[1].current_rating}</p>
              <p className="text-xs text-text-muted">{leaderboard[1].wins}W - {leaderboard[1].losses}L</p>
            </div>
          </div>

          {/* 1st Place */}
          <div className="animate-fade-in">
            <div className="glass-panel p-6 text-center border-yellow-400/30 hover:border-yellow-400/50 transition-all relative">
              <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                <Crown size={32} className="text-yellow-400 animate-pulse" />
              </div>
              <div className="relative inline-block mb-4 mt-4">
                <div className="h-24 w-24 rounded-2xl bg-gradient-to-br from-yellow-500 to-yellow-600 flex-center text-white text-3xl font-bold shadow-glow mx-auto">
                  {leaderboard[0].username.charAt(0).toUpperCase()}
                </div>
                <div className="absolute -top-2 -right-2 h-10 w-10 rounded-lg bg-gradient-to-br from-yellow-500 to-yellow-600 flex-center shadow-lg">
                  <Trophy size={20} className="text-white" />
                </div>
              </div>
              <p className="text-white font-bold text-xl mb-1">{leaderboard[0].username}</p>
              <p className="text-yellow-400 font-mono font-bold text-lg mb-2">{leaderboard[0].current_rating}</p>
              <p className="text-sm text-text-muted">{leaderboard[0].wins}W - {leaderboard[0].losses}L</p>
            </div>
          </div>

          {/* 3rd Place */}
          <div className="mt-12 animate-fade-in" style={{animationDelay: '0.2s'}}>
            <div className="glass-panel p-6 text-center border-amber-600/30 hover:border-amber-600/50 transition-all">
              <div className="relative inline-block mb-4">
                <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-amber-600 to-amber-700 flex-center text-white text-2xl font-bold shadow-lg mx-auto">
                  {leaderboard[2].username.charAt(0).toUpperCase()}
                </div>
                <div className="absolute -top-2 -right-2 h-8 w-8 rounded-lg bg-gradient-to-br from-amber-600 to-amber-700 flex-center shadow-lg">
                  <Medal size={16} className="text-white" />
                </div>
              </div>
              <p className="text-white font-bold text-lg mb-1">{leaderboard[2].username}</p>
              <p className="text-amber-600 font-mono font-semibold mb-2">{leaderboard[2].current_rating}</p>
              <p className="text-xs text-text-muted">{leaderboard[2].wins}W - {leaderboard[2].losses}L</p>
            </div>
          </div>
        </div>
      )}

      {/* Full Leaderboard Table */}
      <div className="glass-panel p-6">
        <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
          <Users size={24} className="text-primary" />
          All Rankings
        </h2>
        
        {leaderboard.length > 0 ? (
          <div className="space-y-2">
            {leaderboard.map((player, index) => (
              <div 
                key={player.player_id} 
                className={`p-4 rounded-xl border flex items-center justify-between transition-all hover:scale-[1.01] ${
                  player.username === user?.username 
                    ? 'bg-primary/10 border-primary/30 shadow-lg' 
                    : index < 3
                    ? 'bg-gradient-to-r from-warning/5 to-transparent border-warning/20'
                    : 'bg-bg-panel-light/50 border-border-light hover:border-primary/20'
                }`}
              >
                <div className="flex items-center gap-4 flex-1">
                  {/* Rank */}
                  <div className={`h-12 w-12 rounded-xl bg-gradient-to-br ${getRankBadgeColor(player.rank)} flex-center shrink-0`}>
                    {getRankIcon(player.rank) || (
                      <span className="font-mono font-bold text-white">#{player.rank}</span>
                    )}
                  </div>
                  
                  {/* Avatar */}
                  <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex-center text-white font-bold text-lg shrink-0">
                    {player.username.charAt(0).toUpperCase()}
                  </div>
                  
                  {/* Player Info */}
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-semibold text-lg truncate">{player.username}</p>
                    <p className="text-xs text-text-secondary">
                      {player.wins}W - {player.losses}L 
                      {player.matches_played > 0 && (
                        <span className="ml-2">
                          ({Math.round((player.wins / player.matches_played) * 100)}% WR)
                        </span>
                      )}
                    </p>
                  </div>
                  
                  {/* Rating */}
                  <div className="text-right">
                    <div className="flex items-center gap-2">
                      <Award size={18} className="text-primary" />
                      <span className="text-primary font-mono font-bold text-xl">{player.current_rating}</span>
                    </div>
                    <p className="text-xs text-text-muted">ELO Rating</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 text-text-muted">
            <Trophy size={64} className="mx-auto mb-4 opacity-20" />
            <p className="text-lg mb-2">No rankings available yet</p>
            <p className="text-sm">Be the first to compete and claim the top spot!</p>
            <button 
              onClick={() => navigate('/dashboard')}
              className="mt-6 btn btn-primary"
            >
              Start Competing
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Leaderboard;
