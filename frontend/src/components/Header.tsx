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
    <header className="flex-between mb-12 glass-panel p-4 px-6">
      <div className="flex items-center gap-4">
        <img 
          src="/logo.svg" 
          alt="Code Road Logo" 
          className="h-12 w-12 cursor-pointer hover:scale-105 transition-transform"
          onClick={() => navigate('/dashboard')}
        />
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight cursor-pointer" onClick={() => navigate('/dashboard')}>Code Road</h1>
          <p className="text-xs text-primary/80 uppercase tracking-wider font-mono">Competitive Coding Arena</p>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        {showLeaderboard && (
          <button 
            onClick={() => navigate('/leaderboard')}
            className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg bg-warning/10 border border-warning/20 hover:bg-warning/20 transition-all text-warning font-medium"
          >
            <Trophy size={18} />
            <span>Leaderboard</span>
          </button>
        )}
        
        <button 
          onClick={() => navigate('/profile')}
          className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/5 transition-all"
        >
          <div className="text-right hidden sm:block">
            <p className="text-white font-medium text-sm">{user.username}</p>
          </div>
          {user.profile_picture ? (
            <img 
              src={user.profile_picture} 
              alt={user.username}
              className="h-10 w-10 rounded-full object-cover shadow-md border-2 border-primary/30"
            />
          ) : (
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary to-accent flex-center text-white font-bold shadow-md border-2 border-primary/30">
              {user.username.charAt(0).toUpperCase()}
            </div>
          )}
        </button>
        
        <button 
          onClick={handleLogout} 
          className="text-text-muted hover:text-danger transition-colors p-2 rounded-lg hover:bg-white/5"
          title="Logout"
        >
          <LogOut size={20} />
        </button>
      </div>
    </header>
  );
};

export default Header;
