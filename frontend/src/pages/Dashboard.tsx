import { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authService, type User as AuthUser } from '../services/authService';
import { matchmakingService, type MatchQueueStatus } from '../services/matchmakingService';
import { Activity, Users, ChevronRight, Award, Database, Bug, Palette, Code2, Clock, Trophy } from 'lucide-react';
import Header from '../components/Header';

const Dashboard = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [queueStatus, setQueueStatus] = useState<MatchQueueStatus | null>(null);
  const [debugQueueStatus, setDebugQueueStatus] = useState<MatchQueueStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [isPolling, setIsPolling] = useState(false);
  const [isDebugPolling, setIsDebugPolling] = useState(false);
  const [creatingMatch, setCreatingMatch] = useState<'dsa' | 'debug' | null>(null);

  const fetchUserData = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      console.log("Dashboard: Fetched user data:", {
        username: currentUser.username,
        current_rating: currentUser.current_rating,
        debug_rating: currentUser.debug_rating
      });
      setUser(currentUser);
    } catch (err) {
      console.error("Failed to fetch user data", err);
      // Fall back to cached user so dashboard isn't blank
      const cachedUser = authService.getUser();
      if (cachedUser) setUser(cachedUser);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        await fetchUserData();
      } catch (err) {
        console.error("Failed to fetch dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [location.pathname]); // Re-fetch when pathname changes

  // Refresh user data when window regains focus
  useEffect(() => {
    window.addEventListener('focus', fetchUserData);
    
    return () => {
      window.removeEventListener('focus', fetchUserData);
    };
  }, []);

  const joinQueue = async () => {
    if (isPolling) return;
    try {
      await matchmakingService.joinQueue('1v1', 'dsa');
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

  const joinDebugQueue = async () => {
    if (isDebugPolling) return;
    try {
      await matchmakingService.joinQueue('1v1', 'debug');
      setDebugQueueStatus({ in_queue: true, joined_at: new Date().toISOString() });
      setIsDebugPolling(true);
      
      // Real polling for match
      const pollInterval = setInterval(async () => {
        try {
          const status = await matchmakingService.getQueueStatus();
          if (status.match_id) {
            clearInterval(pollInterval);
            navigate('/arena', { state: { matchId: status.match_id, challengeType: 'debug' } });
            setIsDebugPolling(false);
          } else if (!status.in_queue) {
            clearInterval(pollInterval);
            setDebugQueueStatus(null);
            setIsDebugPolling(false);
          }
        } catch (e) {
          console.error("Debug polling error", e);
        }
      }, 2000);

      // Timeout safety
      setTimeout(() => {
        clearInterval(pollInterval);
        setIsDebugPolling(false);
      }, 60000);

    } catch (err) {
      console.error("Failed to join debug queue", err);
    }
  };

  const startPracticeMatch = async () => {
    try {
      setCreatingMatch('dsa');
      const match = await matchmakingService.createPracticeMatch('intermediate');
      navigate('/arena', { state: { matchId: match.id || match.match_id } });
    } catch (err) {
      console.error("Failed to start practice match", err);
      // Fallback
      navigate('/arena');
    } finally {
      setCreatingMatch(null);
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
      
      <Header user={user} />

      {/* Hero Stats Section */}
      <div className="glass-panel p-8 mb-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-danger/10 rounded-full blur-3xl"></div>
        
        <div className="relative">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-3xl font-bold text-white mb-2">Welcome back, {user.username}!</h2>
              <p className="text-text-secondary">Ready to dominate the arena?</p>
            </div>
            <div className="flex gap-3">
              <div className="px-6 py-4 rounded-xl bg-primary/20 border border-primary/30 backdrop-blur-sm w-[110px] flex-shrink-0">
                <div className="flex flex-col items-center gap-1">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-primary to-primary/60 flex-center shrink-0">
                    <Code2 size={16} className="text-white" />
                  </div>
                  <p className="text-xs text-text-muted whitespace-nowrap">DSA ELO</p>
                  <p className="text-lg font-bold text-primary">{user.current_rating}</p>
                </div>
              </div>
              <div className="px-6 py-4 rounded-xl bg-danger/20 border border-danger/30 backdrop-blur-sm w-[110px] flex-shrink-0">
                <div className="flex flex-col items-center gap-1">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-danger to-danger/60 flex-center shrink-0">
                    <Bug size={16} className="text-white" />
                  </div>
                  <p className="text-xs text-text-muted whitespace-nowrap">Debug ELO</p>
                  <p className="text-lg font-bold text-danger">{user.debug_rating || 300}</p>
                </div>
              </div>
              <div className="px-6 py-4 rounded-xl bg-yellow-500/20 border border-yellow-500/30 backdrop-blur-sm opacity-60 w-[110px] flex-shrink-0">
                <div className="flex flex-col items-center gap-1">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-yellow-500 to-yellow-600 flex-center shrink-0">
                    <Database size={16} className="text-white" />
                  </div>
                  <p className="text-xs text-text-muted whitespace-nowrap">DBMS ELO</p>
                  <p className="text-lg font-bold text-yellow-500">----</p>
                </div>
              </div>
              <div className="px-6 py-4 rounded-xl bg-green-500/20 border border-green-500/30 backdrop-blur-sm opacity-60 w-[110px] flex-shrink-0">
                <div className="flex flex-col items-center gap-1">
                  <div className="h-8 w-8 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex-center shrink-0">
                    <Palette size={16} className="text-white" />
                  </div>
                  <p className="text-xs text-text-muted whitespace-nowrap">UI ELO</p>
                  <p className="text-lg font-bold text-green-500">----</p>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Stats Bar */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-primary/20 flex-center">
                  <Users className="text-primary" size={24} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{(user.matches_played || 0) + (user.debug_matches_played || 0)}</p>
                  <p className="text-xs text-text-muted">Total Battles</p>
                </div>
              </div>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-success/20 flex-center">
                  <Award className="text-success" size={24} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{(user.wins || 0) + (user.debug_wins || 0)}</p>
                  <p className="text-xs text-text-muted">Victories</p>
                </div>
              </div>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-warning/20 flex-center">
                  <Activity className="text-warning" size={24} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">
                    {((user.matches_played || 0) + (user.debug_matches_played || 0)) > 0 
                      ? Math.round((((user.wins || 0) + (user.debug_wins || 0)) / ((user.matches_played || 0) + (user.debug_matches_played || 0))) * 100) 
                      : 0}%
                  </p>
                  <p className="text-xs text-text-muted">Win Rate</p>
                </div>
              </div>
            </div>
            <div className="bg-white/5 rounded-lg p-4 border border-white/10">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-lg bg-accent/20 flex-center">
                  <Trophy className="text-accent" size={24} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{Math.max(user.current_rating, user.debug_rating || 300)}</p>
                  <p className="text-xs text-text-muted">Peak Rating</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        
        {/* Left Column - Arena Stats */}
        <div className="lg:col-span-1 space-y-4">
          
          {/* DSA Arena Stats */}
          <div className="glass-panel p-6 relative overflow-hidden">
            <div className="relative">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-primary to-primary/60 flex-center">
                  <Code2 size={24} className="text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">DSA Arena</h3>
                  <p className="text-xs text-text-muted">Data Structures & Algorithms</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-text-muted text-sm">Rating</span>
                  <span className="text-2xl font-bold text-primary">{user.current_rating}</span>
                </div>
                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-primary to-primary/60 rounded-full transition-all"
                    style={{ width: `${Math.min((user.current_rating / 2000) * 100, 100)}%` }}
                  ></div>
                </div>
                
                <div className="grid grid-cols-3 gap-3 pt-2">
                  <div className="text-center">
                    <p className="text-xl font-bold text-white">{user.matches_played || 0}</p>
                    <p className="text-xs text-text-muted">Matches</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-success">{user.wins || 0}</p>
                    <p className="text-xs text-text-muted">Wins</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-danger">{user.losses || 0}</p>
                    <p className="text-xs text-text-muted">Losses</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Debug Arena Stats */}
          <div className="glass-panel p-6 relative overflow-hidden">
            <div className="relative">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-danger to-danger/60 flex-center">
                  <Bug size={24} className="text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Debug Arena</h3>
                  <p className="text-xs text-text-muted">Bug Hunting & Fixing</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-text-muted text-sm">Rating</span>
                  <span className="text-2xl font-bold text-danger">{user.debug_rating || 300}</span>
                </div>
                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-danger to-danger/60 rounded-full transition-all"
                    style={{ width: `${Math.min(((user.debug_rating || 300) / 2000) * 100, 100)}%` }}
                  ></div>
                </div>
                
                <div className="grid grid-cols-3 gap-3 pt-2">
                  <div className="text-center">
                    <p className="text-xl font-bold text-white">{user.debug_matches_played || 0}</p>
                    <p className="text-xs text-text-muted">Matches</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-success">{user.debug_wins || 0}</p>
                    <p className="text-xs text-text-muted">Wins</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-danger">{user.debug_losses || 0}</p>
                    <p className="text-xs text-text-muted">Losses</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* DBMS Arena Stats */}
          <div className="glass-panel p-6 relative overflow-hidden opacity-60">
            <div className="relative">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-yellow-500 to-yellow-600 flex-center">
                  <Database size={24} className="text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">DBMS Arena</h3>
                  <p className="text-xs text-text-muted">SQL & Database Optimization</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-text-muted text-sm">Rating</span>
                  <span className="text-2xl font-bold text-yellow-500">----</span>
                </div>
                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-full transition-all" style={{ width: '0%' }}></div>
                </div>
                
                <div className="grid grid-cols-3 gap-3 pt-2">
                  <div className="text-center">
                    <p className="text-xl font-bold text-white">0</p>
                    <p className="text-xs text-text-muted">Matches</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-success">0</p>
                    <p className="text-xs text-text-muted">Wins</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-danger">0</p>
                    <p className="text-xs text-text-muted">Losses</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* UI Arena Stats */}
          <div className="glass-panel p-6 relative overflow-hidden opacity-60">
            <div className="relative">
              <div className="flex items-center gap-3 mb-6">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex-center">
                  <Palette size={24} className="text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">UI Arena</h3>
                  <p className="text-xs text-text-muted">Frontend Design Challenges</p>
                </div>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-text-muted text-sm">Rating</span>
                  <span className="text-2xl font-bold text-green-500">----</span>
                </div>
                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-full transition-all" style={{ width: '0%' }}></div>
                </div>
                
                <div className="grid grid-cols-3 gap-3 pt-2">
                  <div className="text-center">
                    <p className="text-xl font-bold text-white">0</p>
                    <p className="text-xs text-text-muted">Matches</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-success">0</p>
                    <p className="text-xs text-text-muted">Wins</p>
                  </div>
                  <div className="text-center">
                    <p className="text-xl font-bold text-danger">0</p>
                    <p className="text-xs text-text-muted">Losses</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Right Column - Arena Selection */}
        <div className="lg:col-span-2 space-y-4">
        
          {/* DSA Arena Card */}
          <div className="glass-panel p-6 hover:border-primary/50 transition-all relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-40 h-40 bg-primary/5 rounded-full blur-3xl group-hover:bg-primary/10 transition-all"></div>
            
            <div className="relative">
              <div className="flex items-start gap-4 mb-6">
                <div className="h-14 w-14 rounded-full bg-gradient-to-br from-primary to-primary/60 flex-center shrink-0">
                  <Code2 size={28} className="text-white" />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-2xl font-bold text-white">DSA Arena</h3>
                    <div className="px-3 py-1 rounded-lg bg-primary/20 border border-primary/30">
                      <span className="text-primary text-sm font-semibold">{user.current_rating} ELO</span>
                    </div>
                  </div>
                  <p className="text-text-secondary mb-6">Master data structures and algorithms through competitive coding challenges</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <button 
                  onClick={joinQueue}
                  disabled={!!queueStatus?.in_queue}
                  className="btn btn-primary px-6 py-3 flex items-center gap-2 flex-1"
                >
                  {queueStatus?.in_queue ? (
                    <>
                      <Activity size={18} className="animate-spin" />
                      Finding Opponent...
                    </>
                  ) : (
                    <>
                      <Users size={18} />
                      1v1 Battle
                      <ChevronRight size={18} />
                    </>
                  )}
                </button>
                <button 
                  onClick={startPracticeMatch}
                  disabled={creatingMatch === 'dsa'}
                  className="btn btn-secondary px-6 py-3 flex items-center gap-2 border border-white/10"
                >
                  {creatingMatch === 'dsa' ? (
                    <>
                      <Activity size={18} className="animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Activity size={18} />
                      Solo Practice
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* Debug Arena Card */}
          <div className="glass-panel p-6 hover:border-danger/50 transition-all relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-40 h-40 bg-danger/5 rounded-full blur-3xl group-hover:bg-danger/10 transition-all"></div>
            
            <div className="relative">
              <div className="flex items-start gap-4 mb-6">
                <div className="h-14 w-14 rounded-full bg-gradient-to-br from-danger to-danger/60 flex-center shrink-0">
                  <Bug size={28} className="text-white" />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-2xl font-bold text-white">Debug Arena</h3>
                    <div className="px-3 py-1 rounded-lg bg-danger/20 border border-danger/30">
                      <span className="text-danger text-sm font-semibold">{user.debug_rating || 300} ELO</span>
                    </div>
                  </div>
                  <p className="text-text-secondary mb-6">Hunt down bugs and fix broken code under intense time pressure</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3">
                <button 
                  onClick={joinDebugQueue}
                  disabled={!!debugQueueStatus?.in_queue}
                  className="btn btn-danger px-6 py-3 flex items-center gap-2 flex-1"
                >
                  {debugQueueStatus?.in_queue ? (
                    <>
                      <Activity size={18} className="animate-spin" />
                      Finding Opponent...
                    </>
                  ) : (
                    <>
                      <Users size={18} />
                      1v1 Battle
                      <ChevronRight size={18} />
                    </>
                  )}
                </button>
                <button 
                  onClick={() => {
                    setCreatingMatch('debug');
                    matchmakingService.createPracticeMatch('intermediate', 'debug')
                      .then(match => navigate('/arena', { state: { matchId: match.id || match.match_id, challengeType: 'debug' } }))
                      .catch(err => console.error("Failed to start debug match", err))
                      .finally(() => setCreatingMatch(null));
                  }}
                  disabled={creatingMatch === 'debug'}
                  className="btn btn-secondary px-6 py-3 flex items-center gap-2 border border-white/10"
                >
                  {creatingMatch === 'debug' ? (
                    <>
                      <Activity size={18} className="animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Activity size={18} />
                      Solo Practice
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>

          {/* DBMS Arena Card */}
          <div className="glass-panel p-6 hover:border-yellow-500/50 transition-all relative overflow-hidden opacity-60">
            <div className="absolute top-0 right-0 w-40 h-40 bg-yellow-500/5 rounded-full blur-3xl"></div>
            
            <div className="relative">
              <div className="flex items-start gap-4 mb-6">
                <div className="h-14 w-14 rounded-full bg-gradient-to-br from-yellow-500 to-yellow-600 flex-center shrink-0">
                  <Database size={28} className="text-white" />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-2xl font-bold text-white">DBMS Arena</h3>
                    <div className="px-3 py-1 rounded-lg bg-yellow-500/20 border border-yellow-500/30">
                      <span className="text-yellow-500 text-sm font-semibold">---- ELO</span>
                    </div>
                  </div>
                  <p className="text-text-secondary mb-6">Master SQL queries and database optimization challenges</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3 mb-3">
                <button disabled className="btn btn-secondary px-6 py-3 flex items-center gap-2 flex-1 opacity-50 cursor-not-allowed">
                  <Users size={18} />
                  1v1 Battle
                </button>
                <button disabled className="btn btn-secondary px-6 py-3 flex items-center gap-2 border border-white/10 opacity-50 cursor-not-allowed">
                  <Activity size={18} />
                  Solo Practice
                </button>
              </div>
              <div className="flex items-center gap-2 text-sm text-yellow-500">
                <Clock size={16} />
                <span>Coming Q2 2026</span>
              </div>
            </div>
          </div>

          {/* UI Arena Card */}
          <div className="glass-panel p-6 hover:border-green-500/50 transition-all relative overflow-hidden opacity-60">
            <div className="absolute top-0 right-0 w-40 h-40 bg-green-500/5 rounded-full blur-3xl"></div>
            
            <div className="relative">
              <div className="flex items-start gap-4 mb-6">
                <div className="h-14 w-14 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex-center shrink-0">
                  <Palette size={28} className="text-white" />
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-2xl font-bold text-white">UI Arena</h3>
                    <div className="px-3 py-1 rounded-lg bg-green-500/20 border border-green-500/30">
                      <span className="text-green-500 text-sm font-semibold">---- ELO</span>
                    </div>
                  </div>
                  <p className="text-text-secondary mb-6">Build pixel-perfect interfaces from designs in competitive sprints</p>
                </div>
              </div>
              
              <div className="flex items-center gap-3 mb-3">
                <button disabled className="btn btn-secondary px-6 py-3 flex items-center gap-2 flex-1 opacity-50 cursor-not-allowed">
                  <Users size={18} />
                  1v1 Battle
                </button>
                <button disabled className="btn btn-secondary px-6 py-3 flex items-center gap-2 border border-white/10 opacity-50 cursor-not-allowed">
                  <Activity size={18} />
                  Solo Practice
                </button>
              </div>
              <div className="flex items-center gap-2 text-sm text-green-500">
                <Clock size={16} />
                <span>Coming Q3 2026</span>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};

export default Dashboard;
