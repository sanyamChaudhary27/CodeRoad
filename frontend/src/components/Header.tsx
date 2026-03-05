import { useNavigate } from 'react-router-dom';
import { LogOut, Trophy } from 'lucide-react';
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
    <header className="flex-between mb-8 glass-panel px-6 py-3 relative overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-r from-primary/10 via-accent/5 to-primary/10 animate-gradient"></div>
      
      {/* Left side - Logo + Brand */}
      <div className="flex items-center relative z-10">
        <div 
          className="relative cursor-pointer group/logo flex items-center gap-3"
          onClick={() => navigate('/dashboard')}
        >
          {/* Logo container - Perfect square */}
          <div className="relative h-12 w-12 flex-center group-hover/logo:scale-110 transition-transform">
            <img src="/logo.svg" alt="CodeRoad" className="h-full w-full object-contain drop-shadow-lg" />
          </div>
          {/* Brand name */}
          <span className="text-2xl font-black text-gradient group-hover/logo:text-primary transition-colors">
            CodeRoad
          </span>
        </div>
      </div>
      
      {/* Right side - Actions */}
      <div className="flex items-center gap-4 relative z-10">
        {showLeaderboard && (
          <button 
            onClick={() => navigate('/leaderboard')}
            className="flex items-center gap-3 px-10 py-4 rounded-xl bg-gradient-to-r from-warning/20 to-warning/10 border border-warning/40 hover:border-warning/60 hover:from-warning/30 hover:to-warning/20 transition-all text-warning font-bold shadow-lg hover:shadow-warning/20 hover:scale-105 group min-w-[200px] justify-center"
          >
            <Trophy size={20} className="group-hover:rotate-12 transition-transform" />
            <span>Leaderboard</span>
          </button>
        )}
        
        <button 
          onClick={() => navigate('/profile')}
          className="flex items-center gap-4 px-6 py-4 rounded-xl hover:bg-white/10 transition-all border border-white/10 hover:border-primary/40 group"
        >
          <div className="text-right">
            <p className="text-white font-bold text-sm group-hover:text-primary transition-colors">{user.username}</p>
            <p className="text-xs text-text-muted">View Profile</p>
          </div>
          {user.profile_picture ? (
            <img 
              src={user.profile_picture} 
              alt={user.username}
              style={{ width: '36px', height: '36px', minWidth: '36px', minHeight: '36px', maxWidth: '36px', maxHeight: '36px' }}
              className="rounded-full object-cover shadow-lg border-2 border-primary/50 group-hover:border-primary transition-all shrink-0 group-hover:scale-110"
            />
          ) : (
            <div 
              style={{ width: '36px', height: '36px', minWidth: '36px', minHeight: '36px' }}
              className="rounded-full bg-gradient-to-br from-primary to-accent flex-center text-white font-bold shadow-lg border-2 border-primary/50 group-hover:border-primary transition-all shrink-0 group-hover:scale-110"
            >
              {user.username.charAt(0).toUpperCase()}
            </div>
          )}
        </button>
        
        <button 
          onClick={handleLogout} 
          className="text-text-muted hover:text-danger transition-all p-4 rounded-xl hover:bg-danger/10 border border-transparent hover:border-danger/40 group"
          title="Logout"
        >
          <LogOut size={22} className="group-hover:scale-110 transition-transform" />
        </button>
      </div>
    </header>
  );
};

export default Header;
