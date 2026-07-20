import { useNavigate } from 'react-router-dom';
import { LogOut, Swords, Trophy } from 'lucide-react';
import { authService, type User } from '../services/authService';
import './Header.css';

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
    <header className="app-header">
      <button
        type="button"
        className="app-header__brand"
        onClick={() => navigate('/dashboard')}
        aria-label="Go to dashboard"
      >
        <img src="/logo.svg" alt="" className="app-header__logo" />
        <span>CodeRoad</span>
      </button>

      <nav className="app-header__nav" aria-label="Primary navigation">
        <button
          type="button"
          onClick={() => navigate('/attack-arena')}
          className="app-header__link app-header__link--attack"
        >
          <Swords size={16} />
          <span>Attack</span>
        </button>
        {showLeaderboard && (
          <button
            type="button"
            onClick={() => navigate('/leaderboard')}
            className="app-header__link"
          >
            <Trophy size={16} />
            <span>Rankings</span>
          </button>
        )}

        <button
          type="button"
          onClick={() => navigate('/profile')}
          className="app-header__profile"
        >
          <span className="app-header__identity">
            <strong>{user.username}</strong>
            <small>Profile</small>
          </span>
          {user.profile_picture ? (
            <img
              src={user.profile_picture}
              alt={user.username}
              className="app-header__avatar"
            />
          ) : (
            <span className="app-header__avatar app-header__avatar--fallback">
              {user.username.charAt(0).toUpperCase()}
            </span>
          )}
        </button>

        <button
          type="button"
          onClick={handleLogout}
          className="app-header__logout"
          title="Logout"
          aria-label="Logout"
        >
          <LogOut size={18} />
        </button>
      </nav>
    </header>
  );
};

export default Header;
