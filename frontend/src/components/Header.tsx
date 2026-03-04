import { useNavigate } from 'react-router-dom';
import { LogOut, Trophy, Code } from 'lucide-react';
import { authService, type User } from '../services/authService';

interface HeaderProps {
  user: User;
  showLeaderboard?: boolean;
}

const Header = ({ user, showLeaderboard = true }: HeaderProps) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <header className="flex-between mb-8 glass-panel p-4 px-6 relative overflow-hidden group">
      {/* Subtle gradient background */}
      <div className="absolute inset-0 bg-gradient-to-r from-primary/5 via-transparent to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      <div className="flex items-center gap-4 relative z-10">
        <div 
          className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary via-accent to-success flex-center cursor-pointer hover:scale-110 transition-transform shadow-lg"
          onClick={() => navigate('/dashboard')}
        >
          <Code size={24} className="text-white" />
        </div>
        <div>
          <h1 
            className="text-2xl font-black text-gradient tracking-tight cursor-pointer hover:scale-105 transition-transform inline-block" 
            onClick={() => navigate('/dashboard')}
          >
            CodeRoad
          </h1>
          <p className="text-xs text-text-muted uppercase tracking-[0.2em] font-semibold">Competitive Arena</p>
        </div>
      </div>
      
      <div className="flex items-center gap-3 relative z-10">
        {showLeaderboard && (
          <button 
            onClick={() => navigate('/leaderboard')}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-warning/10 border border-warning/30 hover:bg-warning/20 hover:border-warning/40 transition-all text-warning font-semibold shadow-sm hover:shadow-glow hover:scale-105"
          >
            <Trophy size={18} />
            <span className="hidden sm:inline">Leaderboard</span>
          </button>
        )}
        
        <button 
          onClick={() => navigate('/profile')}
          className="flex items-center gap-3 px-3 py-2 rounded-xl hover:bg-white/5 transition-all border border-transparent hover:border-primary/20"
        >
          <div className="text-right hidden sm:block">
            <p className="text-white font-semibold text-sm">{user.username}</p>
            <p className="text-xs text-text-muted">View Profile</p>
          </div>
          {user.profile_picture ? (
            <img 
              src={user.profile_picture} 
              alt={user.username}
              className="h-11 w-11 rounded-full object-cover shadow-lg border-2 border-primary/40 hover:border-primary/60 transition-all"
            />
          ) : (
            <div className="h-11 w-11 rounded-full bg-gradient-to-br from-primary to-accent flex-center text-white font-bold shadow-lg border-2 border-primary/40 hover:border-primary/60 transition-all">
              {user.username.charAt(0).toUpperCase()}
            </div>
          )}
        </button>
        
        <button 
          onClick={handleLogout} 
          className="text-text-muted hover:text-danger transition-all p-2.5 rounded-xl hover:bg-danger/10 border border-transparent hover:border-danger/30 group"
          title="Logout"
        >
          <LogOut size={20} className="group-hover:scale-110 transition-transform" />
        </button>
      </div>
    </header>
  );
};

export default Header;
