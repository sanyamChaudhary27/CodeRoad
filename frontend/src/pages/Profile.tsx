import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, type User } from '../services/authService';
import { Trophy, Target, Activity, Award, TrendingUp, Calendar, Zap, Shield, Camera } from 'lucide-react';
import Header from '../components/Header';
import MatchHistory from '../components/MatchHistory';

const Profile = () => {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploadingPicture, setUploadingPicture] = useState(false);

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

  const handleProfilePictureChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }

    // Validate file size (max 500KB)
    if (file.size > 500000) {
      alert('Image too large. Please select an image under 500KB');
      return;
    }

    setUploadingPicture(true);

    try {
      // Convert to base64
      const reader = new FileReader();
      reader.onloadend = async () => {
        try {
          const base64String = reader.result as string;
          await authService.updateProfilePicture(base64String);
          
          // Refresh user data
          const updatedUser = await authService.getCurrentUser();
          setUser(updatedUser);
          setUploadingPicture(false);
        } catch (err) {
          console.error('Failed to upload profile picture', err);
          alert('Failed to upload profile picture');
          setUploadingPicture(false);
        }
      };
      reader.onerror = () => {
        alert('Failed to read image file');
        setUploadingPicture(false);
      };
      reader.readAsDataURL(file);
    } catch (err) {
      console.error('Failed to process image', err);
      alert('Failed to process image');
      setUploadingPicture(false);
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

  const winRate = (user.matches_played || 0) > 0 ? Math.round(((user.wins || 0) / (user.matches_played || 1)) * 100) : 0;
  const losses = (user.matches_played || 0) - (user.wins || 0);
  
  const debugWinRate = (user.debug_matches_played || 0) > 0 ? Math.round(((user.debug_wins || 0) / (user.debug_matches_played || 1)) * 100) : 0;
  const debugLosses = (user.debug_matches_played || 0) - (user.debug_wins || 0);

  return (
    <div className="min-h-screen p-6 lg:p-12 animate-fade-in max-w-7xl mx-auto">
      
      <Header user={user} />

      {/* Back to Dashboard Button */}
      <div className="mb-6">
        <button
          onClick={() => navigate('/dashboard')}
          className="text-text-muted hover:text-primary transition-colors flex items-center gap-2 text-sm font-semibold uppercase tracking-wider"
        >
          <span>←</span> Back to Dashboard
        </button>
      </div>

      {/* Profile Header - Enhanced */}
      <div className="glass-panel p-8 mb-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-accent/5 rounded-full blur-3xl"></div>
        
        <div className="relative flex flex-col md:flex-row items-start md:items-center gap-6">
          {/* Avatar with Upload - Enhanced */}
          <div className="relative group">
            {user.profile_picture ? (
              <img 
                src={user.profile_picture} 
                alt={user.username}
                style={{ width: '96px', height: '96px', minWidth: '96px', minHeight: '96px', maxWidth: '96px', maxHeight: '96px' }}
                className="rounded-2xl object-cover shadow-lg border-2 border-primary/30 transition-transform group-hover:scale-105"
              />
            ) : (
              <div 
                style={{ width: '96px', height: '96px', minWidth: '96px', minHeight: '96px' }}
                className="rounded-2xl bg-gradient-to-br from-primary via-accent to-success flex-center text-white text-4xl font-bold shadow-lg border-2 border-primary/30 transition-transform group-hover:scale-105"
              >
                {user.username.charAt(0).toUpperCase()}
              </div>
            )}
            
            {/* Upload Button Overlay */}
            <label 
              htmlFor="profile-picture-upload"
              className="absolute inset-0 rounded-2xl bg-black/60 flex-center opacity-0 group-hover:opacity-100 transition-all cursor-pointer"
            >
              {uploadingPicture ? (
                <Activity size={24} className="text-white animate-spin" />
              ) : (
                <Camera size={24} className="text-white" />
              )}
            </label>
            <input
              id="profile-picture-upload"
              type="file"
              accept="image/*"
              onChange={handleProfilePictureChange}
              className="hidden"
              disabled={uploadingPicture}
            />
          </div>

          {/* User Info - Enhanced */}
          <div className="flex-1">
            <h1 className="text-5xl font-black text-white mb-2 tracking-tight">{user.username}</h1>
            <p className="text-text-secondary mb-6 text-lg">{user.email}</p>
            
            <div className="flex flex-wrap gap-3">
              <div className="px-5 py-3 rounded-xl bg-primary/10 border border-primary/30 flex items-center gap-2 hover:bg-primary/20 transition-all hover:scale-105">
                <Activity size={18} className="text-primary" />
                <span className="text-primary font-bold text-lg">{user.matches_played || 0} Total Matches</span>
              </div>
              <div className="px-5 py-3 rounded-xl bg-success/10 border border-success/30 flex items-center gap-2 hover:bg-success/20 transition-all hover:scale-105">
                <Award size={18} className="text-success" />
                <span className="text-success font-bold text-lg">{user.wins || 0} Total Wins</span>
              </div>
              <div className="px-5 py-3 rounded-xl bg-accent/10 border border-accent/30 flex items-center gap-2 hover:bg-accent/20 transition-all hover:scale-105">
                <TrendingUp size={18} className="text-accent" />
                <span className="text-accent font-bold text-lg">{winRate}% Win Rate</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Stats Column */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* DSA Performance Stats - Enhanced */}
          <div className="glass-panel p-6 relative overflow-hidden group hover:border-primary/40 transition-all">
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-all"></div>
            
            <div className="relative">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-primary/20 flex-center">
                  <Target size={24} className="text-primary" />
                </div>
                DSA Arena Statistics
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light text-center hover:border-primary/30 transition-all hover:scale-105 cursor-pointer">
                  <Activity className="text-primary mb-3 mx-auto" size={28} />
                  <p className="text-4xl font-black text-white mb-1">{user.matches_played || 0}</p>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Total Matches</p>
                </div>
                
                <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light text-center hover:border-success/30 transition-all hover:scale-105 cursor-pointer">
                  <Award className="text-success mb-3 mx-auto" size={28} />
                  <p className="text-4xl font-black text-white mb-1">{user.wins || 0}</p>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Victories</p>
                </div>
                
                <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light text-center hover:border-danger/30 transition-all hover:scale-105 cursor-pointer">
                  <Target className="text-danger mb-3 mx-auto" size={28} />
                  <p className="text-4xl font-black text-white mb-1">{losses}</p>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Defeats</p>
                </div>
                
                <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light text-center hover:border-accent/30 transition-all hover:scale-105 cursor-pointer">
                  <TrendingUp className="text-accent mb-3 mx-auto" size={28} />
                  <p className="text-4xl font-black text-white mb-1">{winRate}%</p>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Win Rate</p>
                </div>
              </div>
            </div>
          </div>

          {/* Debug Arena Performance Stats - Enhanced */}
          <div className="glass-panel p-6 border-danger/20 relative overflow-hidden group hover:border-danger/40 transition-all">
            <div className="absolute top-0 right-0 w-64 h-64 bg-danger/5 rounded-full blur-3xl group-hover:bg-danger/10 transition-all"></div>
            
            <div className="relative">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-danger/20 flex-center">
                  <Shield size={24} className="text-danger" />
                </div>
                Debug Arena Statistics
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light text-center hover:border-danger/30 transition-all hover:scale-105 cursor-pointer">
                  <Activity className="text-danger mb-3 mx-auto" size={28} />
                  <p className="text-4xl font-black text-white mb-1">{user.debug_matches_played || 0}</p>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Total Matches</p>
                </div>
                
                <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light text-center hover:border-success/30 transition-all hover:scale-105 cursor-pointer">
                  <Award className="text-success mb-3 mx-auto" size={28} />
                  <p className="text-4xl font-black text-white mb-1">{user.debug_wins || 0}</p>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Victories</p>
                </div>
                
                <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light text-center hover:border-danger/30 transition-all hover:scale-105 cursor-pointer">
                  <Target className="text-danger mb-3 mx-auto" size={28} />
                  <p className="text-4xl font-black text-white mb-1">{debugLosses}</p>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Defeats</p>
                </div>
                
                <div className="bg-bg-panel-light/50 p-6 rounded-xl border border-border-light text-center hover:border-accent/30 transition-all hover:scale-105 cursor-pointer">
                  <TrendingUp className="text-accent mb-3 mx-auto" size={28} />
                  <p className="text-4xl font-black text-white mb-1">{debugWinRate}%</p>
                  <p className="text-xs text-text-muted uppercase tracking-wider">Win Rate</p>
                </div>
              </div>
            </div>
          </div>

          {/* Match History - Enhanced */}
          <div className="glass-panel p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-accent/5 rounded-full blur-3xl"></div>
            
            <div className="relative">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-accent/20 flex-center">
                  <Calendar size={24} className="text-accent" />
                </div>
                Recent Matches
              </h2>
              
              {user && user.id ? (
                <MatchHistory userId={user.id} limit={10} />
              ) : (
                <div className="text-center py-16 text-text-muted">
                  <Activity size={56} className="mx-auto mb-4 opacity-20 animate-pulse" />
                  <p className="text-lg">Loading match history...</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Achievements & Info Column */}
        <div className="space-y-8">
          
          {/* Rank Cards */}
          <div className="space-y-4">
            {/* DSA Rank Card - Enhanced */}
            <div className="glass-panel p-6 relative overflow-hidden group hover:border-primary/40 transition-all">
              <div className="absolute top-0 right-0 w-48 h-48 bg-primary/10 rounded-full blur-3xl group-hover:scale-110 transition-transform"></div>
              
              <div className="relative">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <div className="h-8 w-8 rounded-lg bg-primary/20 flex-center">
                    <Trophy size={18} className="text-primary" />
                  </div>
                  DSA Arena Rank
                </h3>
                
                <div className="text-center py-8">
                  <div className="text-7xl font-black text-gradient mb-3 animate-pulse-glow">{user.current_rating}</div>
                  <p className="text-text-secondary text-lg">ELO Rating</p>
                </div>
                
                <div className="mt-6 space-y-3">
                  <div className="flex items-center justify-between p-4 rounded-xl bg-bg-panel-light/50 border border-border-light hover:border-primary/30 transition-all">
                    <span className="text-text-secondary">Peak Rating</span>
                    <span className="text-white font-bold text-lg">{user.current_rating}</span>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-xl bg-bg-panel-light/50 border border-border-light hover:border-primary/30 transition-all">
                    <span className="text-text-secondary">Starting Rating</span>
                    <span className="text-white font-bold text-lg">300</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Debug Rank Card - Enhanced */}
            <div className="glass-panel p-6 border-danger/20 relative overflow-hidden group hover:border-danger/40 transition-all">
              <div className="absolute top-0 right-0 w-48 h-48 bg-danger/10 rounded-full blur-3xl group-hover:scale-110 transition-transform"></div>
              
              <div className="relative">
                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                  <div className="h-8 w-8 rounded-lg bg-danger/20 flex-center">
                    <Trophy size={18} className="text-danger" />
                  </div>
                  Debug Arena Rank
                </h3>
                
                <div className="text-center py-8">
                  <div className="text-7xl font-black text-danger mb-3 animate-pulse">{user.debug_rating || 300}</div>
                  <p className="text-text-secondary text-lg">ELO Rating</p>
                </div>
                
                <div className="mt-6 space-y-3">
                  <div className="flex items-center justify-between p-4 rounded-xl bg-bg-panel-light/50 border border-border-light hover:border-danger/30 transition-all">
                    <span className="text-text-secondary">Peak Rating</span>
                    <span className="text-white font-bold text-lg">{user.debug_rating || 300}</span>
                  </div>
                  <div className="flex items-center justify-between p-4 rounded-xl bg-bg-panel-light/50 border border-border-light hover:border-danger/30 transition-all">
                    <span className="text-text-secondary">Starting Rating</span>
                    <span className="text-white font-bold text-lg">300</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Achievements - Enhanced */}
          <div className="glass-panel p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-48 h-48 bg-warning/5 rounded-full blur-3xl"></div>
            
            <div className="relative">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-warning/20 flex-center">
                  <Zap size={18} className="text-warning" />
                </div>
                Achievements
              </h3>
              
              <div className="space-y-3">
                {user.wins && user.wins > 0 && (
                  <div className="p-5 rounded-xl bg-gradient-to-r from-success/10 to-transparent border border-success/30 hover:border-success/50 transition-all hover:scale-105 cursor-pointer">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-xl bg-success/20 flex-center">
                        <Award size={24} className="text-success" />
                      </div>
                      <div>
                        <p className="text-white font-bold text-lg">First Victory</p>
                        <p className="text-xs text-text-secondary">Won your first match</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {user.matches_played && user.matches_played >= 10 && (
                  <div className="p-5 rounded-xl bg-gradient-to-r from-primary/10 to-transparent border border-primary/30 hover:border-primary/50 transition-all hover:scale-105 cursor-pointer">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-xl bg-primary/20 flex-center">
                        <Activity size={24} className="text-primary" />
                      </div>
                      <div>
                        <p className="text-white font-bold text-lg">Veteran</p>
                        <p className="text-xs text-text-secondary">Played 10+ matches</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {(!user.wins || user.wins === 0) && (!user.matches_played || user.matches_played < 10) && (
                  <div className="text-center py-12 text-text-muted">
                    <Shield size={56} className="mx-auto mb-4 opacity-20" />
                    <p className="text-sm">Complete matches to unlock achievements!</p>
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

export default Profile;
