import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, type User } from '../services/authService';
import { ArrowLeft, Trophy, Target, Activity, Award, TrendingUp, Calendar, Zap, Shield } from 'lucide-react';

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);
      } catch (err) {
        console.error("Failed to fetch user", err);
        navigate('/login');
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, [navigate]);

  if (loading || !user) {
    return (
      <div className="min-h-screen flex-center">
        <div className="animate-pulse-glow p-4 rounded-full bg-primary/20">
          <Activity size={32} className="text-primary animate-pulse" />
        </div>
      </div>
    );
  }

  const winRate = (user.matches_played || 0) > 0 ? Math.round(((user.wins || 0) / (user.matches_played || 1)) * 100) : 0;
  const losses = (user.matches_played || 0) - (user.wins || 0);

  return (
    <div className="min-h-screen p-6 lg:p-12 animate-fade-in max-w-7xl mx-auto">
      
      {/* Back Button */}
      <button 
        onClick={() => navigate('/dashboard')}
        className="mb-6 flex items-center gap-2 text-text-secondary hover:text-primary transition-colors group"
      >
        <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
        <span>Back to Dashboard</span>
      </button>

      {/* Profile Header */}
      <div className="glass-panel p-8 mb-8">
        <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
          {/* Avatar */}
          <div className="relative">
            <div className="h-24 w-24 rounded-2xl bg-gradient-to-br from-primary via-accent to-success flex-center text-white text-4xl font-bold shadow-glow">
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div className="absolute -bottom-2 -right-2 h-10 w-10 rounded-lg bg-warning flex-center shadow-lg">
              <Trophy size={20} className="text-white" />
            </div>
          </div>

          {/* User Info */}
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-white mb-2">{user.username}</h1>
            <p className="text-text-secondary mb-4">{user.email}</p>
            
            <div className="flex flex-wrap gap-3">
              <div className="px-4 py-2 rounded-lg bg-primary/10 border border-primary/20 flex items-center gap-2">
                <TrendingUp size={16} className="text-primary" />
                <span className="text-primary font-semibold">{user.current_rating} ELO</span>
              </div>
              <div className="px-4 py-2 rounded-lg bg-success/10 border border-success/20 flex items-center gap-2">
                <Award size={16} className="text-success" />
                <span className="text-success font-semibold">{user.wins || 0} Wins</span>
              </div>
              <div className="px-4 py-2 rounded-lg bg-accent/10 border border-accent/20 flex items-center gap-2">
                <Activity size={16} className="text-accent" />
                <span className="text-accent font-semibold">{winRate}% Win Rate</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Stats Column */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Performance Stats */}
          <div className="glass-panel p-6">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <Target size={24} className="text-primary" />
              Performance Statistics
            </h2>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-bg-panel-light/50 p-5 rounded-xl border border-border-light text-center">
                <Activity className="text-primary mb-2 mx-auto" size={24} />
                <p className="text-3xl font-bold text-white">{user.matches_played || 0}</p>
                <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Total Matches</p>
              </div>
              
              <div className="bg-bg-panel-light/50 p-5 rounded-xl border border-border-light text-center">
                <Award className="text-success mb-2 mx-auto" size={24} />
                <p className="text-3xl font-bold text-white">{user.wins || 0}</p>
                <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Victories</p>
              </div>
              
              <div className="bg-bg-panel-light/50 p-5 rounded-xl border border-border-light text-center">
                <Target className="text-danger mb-2 mx-auto" size={24} />
                <p className="text-3xl font-bold text-white">{losses}</p>
                <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Defeats</p>
              </div>
              
              <div className="bg-bg-panel-light/50 p-5 rounded-xl border border-border-light text-center">
                <TrendingUp className="text-accent mb-2 mx-auto" size={24} />
                <p className="text-3xl font-bold text-white">{winRate}%</p>
                <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Win Rate</p>
              </div>
            </div>
          </div>

          {/* Match History */}
          <div className="glass-panel p-6">
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <Calendar size={24} className="text-accent" />
              Recent Matches
            </h2>
            
            {user.matches_played && user.matches_played > 0 ? (
              <div className="text-center py-12 text-text-muted">
                <Activity size={48} className="mx-auto mb-4 opacity-20" />
                <p className="text-lg mb-2">Match history coming soon!</p>
                <p className="text-sm">Your {user.matches_played} match{user.matches_played !== 1 ? 'es' : ''} will appear here</p>
              </div>
            ) : (
              <div className="text-center py-12 text-text-muted border border-dashed border-border-light rounded-xl">
                <Target size={48} className="mx-auto mb-4 opacity-20" />
                <p className="text-lg mb-2">No matches played yet</p>
                <p className="text-sm">Start your first match to build your history!</p>
                <button 
                  onClick={() => navigate('/dashboard')}
                  className="mt-6 btn btn-primary"
                >
                  Enter Arena
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Achievements & Info Column */}
        <div className="space-y-8">
          
          {/* Rank Card */}
          <div className="glass-panel p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Trophy size={20} className="text-warning" />
              Current Rank
            </h3>
            
            <div className="text-center py-6">
              <div className="text-6xl font-bold text-gradient mb-2">{user.current_rating}</div>
              <p className="text-text-secondary">ELO Rating</p>
            </div>
            
            <div className="mt-6 space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-bg-panel-light/50 border border-border-light">
                <span className="text-text-secondary text-sm">Peak Rating</span>
                <span className="text-white font-semibold">{user.current_rating}</span>
              </div>
              <div className="flex items-center justify-between p-3 rounded-lg bg-bg-panel-light/50 border border-border-light">
                <span className="text-text-secondary text-sm">Starting Rating</span>
                <span className="text-white font-semibold">1200</span>
              </div>
            </div>
          </div>

          {/* Achievements */}
          <div className="glass-panel p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Zap size={20} className="text-warning" />
              Achievements
            </h3>
            
            <div className="space-y-3">
              {user.wins && user.wins > 0 && (
                <div className="p-4 rounded-xl bg-gradient-to-r from-success/10 to-transparent border border-success/20">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-success/20 flex-center">
                      <Award size={20} className="text-success" />
                    </div>
                    <div>
                      <p className="text-white font-semibold">First Victory</p>
                      <p className="text-xs text-text-secondary">Won your first match</p>
                    </div>
                  </div>
                </div>
              )}
              
              {user.matches_played && user.matches_played >= 10 && (
                <div className="p-4 rounded-xl bg-gradient-to-r from-primary/10 to-transparent border border-primary/20">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-primary/20 flex-center">
                      <Activity size={20} className="text-primary" />
                    </div>
                    <div>
                      <p className="text-white font-semibold">Veteran</p>
                      <p className="text-xs text-text-secondary">Played 10+ matches</p>
                    </div>
                  </div>
                </div>
              )}
              
              {(!user.wins || user.wins === 0) && (!user.matches_played || user.matches_played < 10) && (
                <div className="text-center py-8 text-text-muted">
                  <Shield size={48} className="mx-auto mb-4 opacity-20" />
                  <p className="text-sm">Complete matches to unlock achievements!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
