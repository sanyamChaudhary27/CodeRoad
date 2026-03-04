import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService, type User as AuthUser } from '../services/authService';
import { matchmakingService, type MatchQueueStatus } from '../services/matchmakingService';
import { Activity, Users, ChevronRight, Award, Database, Bug, Palette, Code2, Clock, Trophy } from 'lucide-react';
import Header from '../components/Header';

const Dashboard = () => {
  const navigate = useNavigate();
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
      setUser(currentUser);
    } catch (err) {
      console.error("Failed to fetch user data", err);
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
  }, []);

  // Refresh user data when returning to dashboard
  useEffect(() => {
    // Listen for focus events (when user returns to tab/window)
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

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="glass-panel p-5 flex flex-col items-center justify-center text-center">
          <Award className="text-warning mb-2" size={24} />
          <p className="text-3xl font-bold text-white">{user.wins || 0}</p>
          <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Victories</p>
        </div>
        <div className="glass-panel p-5 flex flex-col items-center justify-center text-center">
          <Activity className="text-accent mb-2" size={24} />
          <p className="text-3xl font-bold text-white">{(user.matches_played || 0) > 0 ? Math.round(((user.wins || 0) / (user.matches_played || 1)) * 100) : 0}%</p>
          <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Win Rate</p>
        </div>
        <div className="glass-panel p-5 flex flex-col items-center justify-center text-center">
          <Users className="text-primary mb-2" size={24} />
          <p className="text-3xl font-bold text-white">{user.matches_played || 0}</p>
          <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Matches</p>
        </div>
        <div className="glass-panel p-5 flex flex-col items-center justify-center text-center">
          <Trophy className="text-success mb-2" size={24} />
          <p className="text-3xl font-bold text-white">{user.current_rating}</p>
          <p className="text-xs text-text-muted uppercase tracking-wider mt-1">Elo</p>
        </div>
      </div>

      {/* Arena Selection Title */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-2">Choose Your Arena</h2>
        <p className="text-text-secondary text-lg">Select a challenge type and compete in 1v1 battles or practice solo</p>
      </div>

      {/* Arena Cards - Full Width */}
      <div className="space-y-4 mb-12">
        
        {/* DSA Arena Card */}
        <div className="glass-panel p-6 hover:border-primary/50 transition-all relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl"></div>
          
          <div className="relative flex items-center gap-6">
            <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex-center shrink-0">
              <Code2 size={32} className="text-white" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-white mb-2">DSA Arena</h3>
              <p className="text-text-secondary mb-4">Data Structures & Algorithms challenges - Test your problem-solving skills</p>
              
              <div className="flex items-center gap-3">
                <button 
                  onClick={joinQueue}
                  disabled={!!queueStatus?.in_queue}
                  className="btn btn-primary px-6 py-3 flex items-center gap-2"
                >
                  {queueStatus?.in_queue ? 'Finding Opponent...' : '1v1 Battle'}
                  {!queueStatus?.in_queue && <ChevronRight size={18} />}
                </button>
                <button 
                  onClick={startPracticeMatch}
                  disabled={creatingMatch === 'dsa'}
                  className="btn btn-secondary px-6 py-3 flex items-center gap-2 border border-white/10"
                >
                  {creatingMatch === 'dsa' ? (
                    <>
                      <Activity size={18} className="animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Activity size={18} />
                      Solo Practice
                    </>
                  )}
                </button>
                <div className="ml-auto flex items-center gap-4">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-text-muted">Difficulty:</span>
                    <span className="text-success font-semibold">Dynamic</span>
                  </div>
                  {/* ELO Badge */}
                  <div className="px-4 py-2 rounded-lg bg-primary/20 border border-primary/30 backdrop-blur-sm">
                    <div className="flex items-center gap-2">
                      <Trophy size={16} className="text-primary" />
                      <span className="text-primary font-bold">{user.current_rating} ELO</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Debug Arena Card */}
        <div className="glass-panel p-6 hover:border-danger/50 transition-all relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-danger/5 rounded-full blur-2xl"></div>
          
          <div className="relative flex items-center gap-6">
            <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-danger to-danger/60 flex-center shrink-0">
              <Bug size={32} className="text-white" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-white mb-2">Debug Arena</h3>
              <p className="text-text-secondary mb-4">Find and fix bugs in code under time pressure - Test your debugging skills</p>
              
              <div className="flex items-center gap-3">
                <button 
                  onClick={joinDebugQueue}
                  disabled={!!debugQueueStatus?.in_queue}
                  className="btn btn-danger px-6 py-3 flex items-center gap-2"
                >
                  {debugQueueStatus?.in_queue ? 'Finding Opponent...' : '1v1 Battle'}
                  {!debugQueueStatus?.in_queue && <ChevronRight size={18} />}
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
                      Generating...
                    </>
                  ) : (
                    <>
                      <Activity size={18} />
                      Solo Practice
                    </>
                  )}
                </button>
                <div className="ml-auto flex items-center gap-4">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-text-muted">Difficulty:</span>
                    <span className="text-danger font-semibold">Dynamic</span>
                  </div>
                  {/* Debug ELO Badge */}
                  <div className="px-4 py-2 rounded-lg bg-danger/20 border border-danger/30 backdrop-blur-sm">
                    <div className="flex items-center gap-2">
                      <Trophy size={16} className="text-danger" />
                      <span className="text-danger font-bold">{user.debug_rating || 300} ELO</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* DBMS Arena Card */}
        <div className="glass-panel p-6 hover:border-blue-500/50 transition-all relative overflow-hidden opacity-60">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full blur-2xl"></div>
          
          <div className="relative flex items-center gap-6">
            <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex-center shrink-0">
              <Database size={32} className="text-white" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-white mb-2">DBMS Arena</h3>
              <p className="text-text-secondary mb-4">SQL queries and database optimization challenges</p>
              
              <div className="flex items-center gap-3">
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed">
                  1v1 Battle
                </button>
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed border border-white/10">
                  Solo Practice
                </button>
                <div className="ml-auto flex items-center gap-4">
                  <div className="flex items-center gap-2 text-sm text-warning">
                    <Clock size={16} />
                    <span>Coming Q2 2026</span>
                  </div>
                  {/* ELO Badge */}
                  <div className="px-4 py-2 rounded-lg bg-blue-500/20 border border-blue-500/30 backdrop-blur-sm">
                    <div className="flex items-center gap-2">
                      <Trophy size={16} className="text-blue-400" />
                      <span className="text-blue-400 font-bold">1200 ELO</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* UI Arena Card */}
        <div className="glass-panel p-6 hover:border-purple-500/50 transition-all relative overflow-hidden opacity-60">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full blur-2xl"></div>
          
          <div className="relative flex items-center gap-6">
            <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 flex-center shrink-0">
              <Palette size={32} className="text-white" />
            </div>
            
            <div className="flex-1">
              <h3 className="text-2xl font-bold text-white mb-2">UI Arena</h3>
              <p className="text-text-secondary mb-4">Build pixel-perfect interfaces from designs in competitive sprints</p>
              
              <div className="flex items-center gap-3">
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed">
                  1v1 Battle
                </button>
                <button disabled className="btn btn-secondary px-6 py-3 opacity-50 cursor-not-allowed border border-white/10">
                  Solo Practice
                </button>
                <div className="ml-auto flex items-center gap-4">
                  <div className="flex items-center gap-2 text-sm text-warning">
                    <Clock size={16} />
                    <span>Coming Q3 2026</span>
                  </div>
                  {/* ELO Badge */}
                  <div className="px-4 py-2 rounded-lg bg-purple-500/20 border border-purple-500/30 backdrop-blur-sm">
                    <div className="flex items-center gap-2">
                      <Trophy size={16} className="text-purple-400" />
                      <span className="text-purple-400 font-bold">1200 ELO</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
};

export default Dashboard;
