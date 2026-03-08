import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { challengeService, type Challenge } from '../services/challengeService';
import { submissionService, type SubmissionResponse } from '../services/submissionService';
import { matchmakingService, type PlayerMatchInfo } from '../services/matchmakingService';
import { Play, CheckCircle2, XCircle, Clock, AlertTriangle, Terminal as TerminalIcon, User as UserIcon, Trophy, Activity, RefreshCw } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { authService, type User } from '../services/authService';

// Final Results Component (Moved to top for hoisting/scope clarity)
const MatchResults = ({ data, user, onDashboard, challengeType }: { data: any, user: User, onDashboard: () => void, challengeType?: 'dsa' | 'debug' }) => {
  const isDraw = data.result === 'draw_draw' || data.result?.includes('draw');
  const isWinner = !isDraw && data.winner_id === user.id;
  
  // Resolve which player data is the user — use multiple fallbacks
  const isPlayer1 = (data.player1_id || data.player1?.player_id) === user.id;
  const ratingUpdate = isPlayer1 ? data.rating_updates?.player1 : data.rating_updates?.player2;
  const myScore = isPlayer1 ? data.player1_score : data.player2_score;
  
  // Determine which rating to display based on challenge type
  const isDebugChallenge = challengeType === 'debug' || data.challenge_type === 'debug';
  const displayRating = ratingUpdate?.new_rating || (isDebugChallenge ? user.debug_rating : user.current_rating);
  const ratingLabel = isDebugChallenge ? 'Debug Rating' : 'DSA Rating';

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-overlay-90 backdrop-blur-xl animate-fade-in p-4 overflow-y-auto">
      <div className="glass-panel p-8 md:p-12 max-w-lg w-full border-primary/40 shadow-glow-2xl relative overflow-hidden text-center animate-scale-in bg-bg-panel/90">
        {/* Victory/Defeat Background Glow */}
        <div className={`absolute -top-32 -left-32 w-96 h-96 rounded-full blur-[120px] opacity-20 ${isWinner ? 'bg-success' : isDraw ? 'bg-warning' : 'bg-danger'}`}></div>
        <div className={`absolute -bottom-32 -right-32 w-96 h-96 rounded-full blur-[120px] opacity-10 ${isWinner ? 'bg-primary' : isDraw ? 'bg-primary/50' : 'bg-warning'}`}></div>
        
        <div className="relative z-10">
          <div className="mb-8 flex justify-center">
            {isWinner ? (
              <div className="bg-success/20 p-6 rounded-full border-2 border-success/40 shadow-glow-sm shadow-success/30 animate-bounce">
                <Trophy size={64} className="text-success" />
              </div>
            ) : isDraw ? (
              <div className="bg-warning/20 p-6 rounded-full border-2 border-warning/40 shadow-glow-sm shadow-warning/30">
                <Activity size={64} className="text-warning" />
              </div>
            ) : (
              <div className="bg-danger/20 p-6 rounded-full border-2 border-danger/40 shadow-glow-sm shadow-danger/30">
                <XCircle size={64} className="text-danger" />
              </div>
            )}
          </div>

          <h2 className="text-6xl font-black italic tracking-tighter text-white mb-2 uppercase leading-none filter drop-shadow-xl">
            {isWinner ? 'Victory' : isDraw ? 'Draw' : 'Defeat'}
          </h2>
          <p className="text-text-secondary text-xs mb-10 tracking-[0.4em] uppercase font-black opacity-60">
            {isWinner ? 'System dominance established' : isDraw ? 'Parity reached' : 'Neural connection severed'}
          </p>

          <div className="grid grid-cols-1 gap-4 mb-10">
            <div className="flex items-center justify-between p-4 bg-bg-dark/40 rounded-xl border border-white/5">
               <span className="text-[10px] uppercase tracking-[0.2em] text-text-muted font-bold">Accuracy</span>
               <span className="text-2xl font-black text-white">{myScore?.toFixed(0)}%</span>
            </div>
            
            <div className={`flex items-center justify-between p-4 rounded-xl border ${ratingUpdate?.rating_change >= 0 ? 'bg-success/5 border-success/20' : 'bg-danger/5 border-danger/20'}`}>
               <span className={`text-[10px] uppercase tracking-[0.2em] font-bold ${ratingUpdate?.rating_change >= 0 ? 'text-success' : 'text-danger'}`}>{ratingLabel} Impact</span>
               <div className="flex items-center gap-3">
                 <span className={`text-2xl font-black tabular-nums ${ratingUpdate?.rating_change >= 0 ? 'text-success' : 'text-danger'}`}>
                   {ratingUpdate?.rating_change >= 0 ? `+${ratingUpdate.rating_change}` : ratingUpdate?.rating_change || 0}
                 </span>
                 <span className="text-xs text-text-muted font-mono opacity-50">({displayRating || '---'})</span>
               </div>
            </div>
          </div>

          <button 
            onClick={onDashboard} 
            className="btn btn-primary w-full py-4 text-lg font-black uppercase tracking-widest shadow-glow hover:translate-y-[-2px] active:translate-y-[0] transition-all border-b-4 border-black/20"
          >
            Return to Terminal
          </button>
        </div>
      </div>
    </div>
  );
};

const Arena = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [matchId, setMatchId] = useState<string | null>(location.state?.matchId || null);
  const [challengeType, setChallengeType] = useState<'dsa' | 'debug'>(location.state?.challengeType || 'dsa');
  const [opponent, setOpponent] = useState<PlayerMatchInfo | null>(null);
  const [code, setCode] = useState<string>('def solve():\n    # Write your code here\n    pass');
  const [opponentCode, setOpponentCode] = useState('// Opponent is typing...');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [status, setStatus] = useState<'idle' | 'generating' | 'submitting' | 'polling' | 'searching' | 'loading_skeleton'>('idle');
  const [submissionResult, setSubmissionResult] = useState<SubmissionResponse | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number>(30);
  const [isDone, setIsDone] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [matchData, setMatchData] = useState<any>(null);
  const [userSubmissions, setUserSubmissions] = useState<number>(0);

  useEffect(() => {
    const initializeArena = async () => {
      console.log("Arena INITIALIZING - S5 Sync Fix");
      
      // Prevent multiple concurrent initializations
      if (status === 'polling' || status === 'submitting') return;

      // Set generating status to trigger skeleton loading
      setStatus('generating');

      let localMatchId = matchId;
      let localChallenge: Challenge | null = null;
      let localOpponent: PlayerMatchInfo | null = null;
      let localTimeLeft = 120;
      let isMultiplayer = false;

      try {
        const currentUser = await authService.getCurrentUser();
        setUser(currentUser);

        // 1. Resolve Match ID if not provided
        if (!localMatchId) {
          const history = await matchmakingService.getPlayerMatches(5);
          if (history?.matches) {
            const activeMatch = history.matches.find((m: any) => {
              const isValid = !['concluded', 'cancelled', 'timeout'].includes(m.status);
              const isRecent = (new Date().getTime() - new Date(m.created_at).getTime()) < 5 * 60 * 1000;
              return isValid && isRecent;
            });
            if (activeMatch) {
              localMatchId = activeMatch.match_id;
            }
          }
        }

        // 2. Practice Match Fallback
        if (!localMatchId) {
          console.log("S5: Creating fresh practice match");
          const practice = await matchmakingService.createPracticeMatch('intermediate');
          localMatchId = practice.match_id || practice.id;
        }

        // 3. Fetch Match & Challenge Details
        if (localMatchId) {
          try {
            const matchDetails = await matchmakingService.getMatch(localMatchId);
            console.log("S5: Match details loaded", matchDetails);
            
            // Detect challenge type from match details
            if (matchDetails.challenge_type === 'debug') {
              setChallengeType('debug');
            } else if (matchDetails.challenge_type === 'dsa') {
              setChallengeType('dsa');
            }
            
            // API Response uses 'format', not 'match_format'
            const matchFormat = matchDetails.format || matchDetails.match_format || '1v1';
            
            // A match is multiplayer if it's 1v1 and has a second player object
            // Use .player_id check to be extra safe
            const hasOpponent = !!(matchDetails.player2?.player_id || matchDetails.player2_id);
            isMultiplayer = matchFormat === '1v1' && hasOpponent;
            
            if (isMultiplayer) {
              // The opponent is whoever IS NOT the current user
              const p1_id = matchDetails.player1?.player_id || matchDetails.player1_id;
              const isUserPlayer1 = p1_id === currentUser.id;
              
              // Use flat fields from backend (player2_username, player2_rating, etc.)
              localOpponent = {
                player_id: isUserPlayer1 ? matchDetails.player2_id : matchDetails.player1_id,
                username: isUserPlayer1 ? (matchDetails.player2_username || 'Opponent') : (matchDetails.player1_username || 'Opponent'),
                current_rating: isUserPlayer1 ? (matchDetails.player2_rating || 1200) : (matchDetails.player1_rating || 1200),
                submissions_count: isUserPlayer1 ? (matchDetails.player2_submissions || 0) : (matchDetails.player1_submissions || 0),
                is_done: isUserPlayer1 ? (matchDetails.player2_done || false) : (matchDetails.player1_done || false)
              };
              
              console.log("S5: Opponent data set:", localOpponent);
              console.log("S5: Match details:", {
                player1_username: matchDetails.player1_username,
                player1_rating: matchDetails.player1_rating,
                player2_username: matchDetails.player2_username,
                player2_rating: matchDetails.player2_rating,
                isUserPlayer1
              });
            }

            // Sync timer with backend
            if (matchDetails.time_remaining !== undefined) {
              localTimeLeft = matchDetails.time_remaining;
            } else if (matchDetails.time_limit_seconds) {
              localTimeLeft = matchDetails.time_limit_seconds;
            }

            if (matchDetails.challenge_id) {
              localChallenge = await challengeService.getChallenge(matchDetails.challenge_id);
            }
          } catch (e) {
            console.error("S5: Match fetch failed", e);
          }
        }

        // 4. Challenge Fallback
        if (!localChallenge) {
          localChallenge = await challengeService.generateChallenge('intermediate', 'arrays');
        }

        // 5. Final State Commit
        setMatchId(localMatchId);
        setChallenge(localChallenge);
        setOpponent(localOpponent);
        setTimeLeft(localTimeLeft); 
        if (localChallenge?.boilerplate_code) setCode(localChallenge.boilerplate_code);

        // Start search timer for multiplayer, or go directly to idle
        if (isMultiplayer && status !== 'idle') {
          setSearchTime(5); 
          setStatus('searching');
        } else {
          setStatus('idle');
        }

      } catch (err) {
        console.error("S5: Critical Init Error", err);
        setError("Failed to load combat data.");
        setStatus('idle');
      }
    };

    initializeArena();
  }, []); // Run ONCE on mount

  // Check if player is already marked as done in this match
  useEffect(() => {
    if (!matchId || !user) return;
    const checkStatus = async () => {
      try {
        const details = await matchmakingService.getMatch(matchId);
        const currentUserIsPlayer1 = details.player1_id === user.id;
        if (currentUserIsPlayer1 ? details.player1_done : details.player2_done) {
          setIsDone(true);
        }
        if (details.status === 'concluded') {
          setMatchData(details);
          setShowResults(true);
        }
      } catch (e) {
        console.error("Match status check failed", e);
      }
    };
    checkStatus();
  }, [matchId, user]);

  // Search Countdown Logic
  useEffect(() => {
    if (status !== 'searching') return;
    
    if (searchTime <= 0) {
      setStatus('idle');
      return;
    }

    const timer = setInterval(() => {
      setSearchTime(prev => prev - 1);
    }, 1000);

    return () => clearInterval(timer);
  }, [status, searchTime]);

  // Timer Countdown Logic
  useEffect(() => {
     if (timeLeft === null || timeLeft <= 0 || status === 'submitting' || isDone) {
        if (timeLeft === 0 && !isDone && matchId) {
          // Auto-finish on timeout
          matchmakingService.markPlayerDone(matchId).catch(console.error);
          setIsDone(true);
        }
        return;
     }
     
     const timerId = setInterval(() => {
       setTimeLeft(prev => (prev !== null && prev > 0) ? prev - 1 : 0);
     }, 1000);
     
     return () => clearInterval(timerId);
  }, [timeLeft, status, isDone, matchId]);

  // Periodic Refresh for Match Stats
  useEffect(() => {
    if (!matchId || matchId === "prototype_match_id") return;
    
    const refreshInterval = setInterval(async () => {
      try {
        const matchDetails = await matchmakingService.getMatch(matchId);
        const currentUser = user || await authService.getCurrentUser();
        
        console.log("Periodic refresh - match details:", {
          player1_username: matchDetails.player1_username,
          player1_rating: matchDetails.player1_rating,
          player1_submissions: matchDetails.player1_submissions,
          player2_username: matchDetails.player2_username,
          player2_rating: matchDetails.player2_rating,
          player2_submissions: matchDetails.player2_submissions
        });
        
        // Update opponent stats (submission counts) using enriched flat fields
        const isUserP1 = matchDetails.player1_id === currentUser.id;
        const opponentInfo = isUserP1
          ? {
              player_id: matchDetails.player2_id,
              username: matchDetails.player2_username || 'Opponent',
              current_rating: matchDetails.player2_rating || 1200,
              submissions_count: matchDetails.player2_submissions || 0,
              is_done: matchDetails.player2_done || false
            }
          : {
              player_id: matchDetails.player1_id,
              username: matchDetails.player1_username || 'Opponent',
              current_rating: matchDetails.player1_rating || 1200,
              submissions_count: matchDetails.player1_submissions || 0,
              is_done: matchDetails.player1_done || false
            };
        
        console.log("Periodic refresh - opponent info:", opponentInfo);
        
        if (matchDetails.player2_id) {
          setOpponent(opponentInfo);
        }

        // Update local user submission count from server - only if server count is higher
        // This prevents overwriting optimistic updates with stale data
        const serverCount = isUserP1 ? (matchDetails.player1_submissions || 0) : (matchDetails.player2_submissions || 0);
        setUserSubmissions(prev => Math.max(prev, serverCount));

        if (matchDetails.status === 'concluded') {
          setMatchData(matchDetails);
          setShowResults(true);
          clearInterval(refreshInterval);
        }
      } catch (e) {
        console.warn("Refresh failed", e);
      }
    }, 3000); // Refresh every 3 seconds for more responsive updates
    
    return () => clearInterval(refreshInterval);
  }, [matchId, user]);

  // WebSocket Integration
  useEffect(() => {
    if (!matchId) return;

    // Use environment variable for WebSocket URL
    const wsBaseUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
    const socketUrl = `${wsBaseUrl}/${matchId}`;
    
    console.log('Connecting to WebSocket:', socketUrl);
    const socket = new WebSocket(socketUrl);

    socket.onopen = () => {
      console.log('WebSocket Connected to match:', matchId);
      setWs(socket);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log('WebSocket message received:', data);
        if (data.type === 'CODE_SYNC') {
          setOpponentCode(data.code);
        }
      } catch (err) {
        console.warn('Failed to parse WS message:', event.data);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = () => {
      console.log('WebSocket Disconnected');
      setWs(null);
    };

    return () => {
      socket.close();
    };
  }, [matchId]);

  // Broadcast code changes
  useEffect(() => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    const timeoutId = setTimeout(() => {
      console.log('→ Broadcasting code update, length:', code.length);
      ws.send(JSON.stringify({
        type: 'CODE_SYNC',
        code: code
      }));
    }, 500); // 500ms debounce

    return () => clearTimeout(timeoutId);
  }, [code, ws]);

  if (error) {
    return (
      <div className="min-h-screen bg-bg-dark flex-center flex-col p-6 text-center">
        <div className="glass-panel p-8 max-w-md border-danger/30">
          <AlertTriangle size={48} className="text-danger mb-4 mx-auto" />
          <h2 className="text-xl font-bold text-white mb-2">Systems Failure</h2>
          <p className="text-text-secondary mb-6">{error}</p>
          <div className="flex gap-4 justify-center">
            <button onClick={() => window.location.reload()} className="btn btn-primary">
              <RefreshCw size={16} className="mr-2" /> Retry
            </button>
            <button onClick={() => navigate('/dashboard')} className="btn btn-secondary">
              Return to Base
            </button>
          </div>
        </div>
      </div>
    );
  }

  const handleSubmitCode = async () => {
    if (!challenge) return;
    setStatus('submitting');
    setSubmissionResult(null);

    try {
      if (!matchId || matchId === "prototype_match_id") {
        console.error("CRITICAL: Submitting without matchId!", { matchId, challengeId: challenge.id });
      }

      // 1. Submit Code Structure
      console.log("EXECUTION: Submitting code", { match_id: matchId, challenge_id: challenge.id });
      const response = await submissionService.submitCode({
        match_id: matchId || "prototype_match_id",
        challenge_id: challenge.id,
        code,
        language: 'python'
      });

      const submissionId = response.submission_id;
      if (!submissionId) {
        throw new Error("Backend did not return a valid submission ID.");
      }
      console.log("Submission created:", submissionId);
      
      // Increment local submission count immediately for instant feedback
      setUserSubmissions(prev => prev + 1);

      setStatus('polling');
      
      // 2. Poll for Background Task completion
      let pollCount = 0;
      const MAX_POLLS = 60; // 60 seconds max
      const pollInterval = setInterval(async () => {
        pollCount++;
        if (pollCount > MAX_POLLS) {
          clearInterval(pollInterval);
          setStatus('idle');
          setError('Evaluation timed out. Please try again.');
          return;
        }
        try {
          const result = await submissionService.getSubmission(submissionId);
          
          if (result.status === 'success' || result.status === 'runtime_error' || result.status === 'timeout') {
            clearInterval(pollInterval);
            setSubmissionResult(result);
            setStatus('idle');
          }
        } catch (pollErr: any) {
          // Stop polling on persistent errors to avoid flooding
          clearInterval(pollInterval);
          console.error("Polling failed:", pollErr);
          setStatus('idle');
        }
      }, 1000);

    } catch (err: any) {
      console.error("Submission failed", err);
      const detailedError = err.response?.data?.detail 
        ? (typeof err.response.data.detail === 'string' 
            ? err.response.data.detail 
            : JSON.stringify(err.response.data.detail, null, 2))
        : err.message || "Submission failed. Please try again.";
      setError(detailedError);
      setStatus('idle');
    }
  };

  const handleFinishMatch = async () => {
    if (!matchId || isDone) return;
    
    try {
      setStatus('polling');
      await matchmakingService.markPlayerDone(matchId);
      setIsDone(true);
      setStatus('idle');
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to signal completion.");
      setStatus('idle');
    }
  };

  // Show skeleton immediately if generating, or after 1 second if still loading
  const [showSkeleton, setShowSkeleton] = useState(false);
  
  useEffect(() => {
    // Show skeleton immediately if status is generating
    if (status === 'generating' && !challenge) {
      setShowSkeleton(true);
      return;
    }
    
    // Otherwise show skeleton after 1 second if still loading
    if (!challenge && (status === 'generating' || status === 'loading_skeleton')) {
      const timer = setTimeout(() => setShowSkeleton(true), 1000);
      return () => clearTimeout(timer);
    } else {
      setShowSkeleton(false);
    }
  }, [challenge, status]);

  if (!challenge || status === 'generating' || status === 'searching' || status === 'loading_skeleton') {
    // Show skeleton UI after 1 second
    if (showSkeleton && status !== 'searching') {
      return (
        <div className="min-h-screen p-4 md:p-6 flex flex-col animate-fade-in bg-bg-dark">
          <div className="flex-1 flex flex-col max-w-7xl mx-auto w-full">
            <div className="flex-between mb-6">
              <button onClick={() => navigate('/dashboard')} className="btn btn-secondary">
                ← Back
              </button>
              <div className="flex items-center gap-3">
                <div className="h-6 w-20 bg-warning/20 rounded animate-pulse"></div>
                <div className="h-6 w-20 bg-primary/20 rounded animate-pulse"></div>
              </div>
            </div>

            <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
              {/* Problem Skeleton */}
              <div className="glass-panel p-6 overflow-y-auto flex flex-col">
                <div className="h-8 w-3/4 bg-white/10 rounded mb-4 animate-pulse"></div>
                <div className="bg-bg-panel-light p-4 rounded-lg border border-border-light mb-6">
                  <div className="space-y-2">
                    <div className="h-4 w-full bg-white/5 rounded animate-pulse"></div>
                    <div className="h-4 w-5/6 bg-white/5 rounded animate-pulse"></div>
                    <div className="h-4 w-4/6 bg-white/5 rounded animate-pulse"></div>
                  </div>
                </div>
                <div className="h-4 w-32 bg-white/10 rounded mb-3 animate-pulse"></div>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-bg-dark rounded p-3 border border-border-light h-20 animate-pulse"></div>
                  <div className="bg-bg-dark rounded p-3 border border-border-light h-20 animate-pulse"></div>
                </div>
                <div className="text-center py-8">
                  <Activity size={48} className="mx-auto mb-4 text-primary animate-spin" />
                  <p className="text-primary font-semibold">AI is generating your challenge...</p>
                  <p className="text-text-muted text-sm mt-2">This usually takes 5-10 seconds</p>
                </div>
              </div>

              {/* Editor Skeleton */}
              <div className="flex flex-col gap-4">
                <div className="glass-panel flex-1 flex flex-col overflow-hidden">
                  <div className="bg-bg-dark border-b border-border-light p-2 px-4 h-10 animate-pulse"></div>
                  <div className="flex-1 bg-bg-dark/50 p-4">
                    <div className="space-y-2">
                      <div className="h-4 w-48 bg-white/5 rounded animate-pulse"></div>
                      <div className="h-4 w-64 bg-white/5 rounded animate-pulse"></div>
                      <div className="h-4 w-40 bg-white/5 rounded animate-pulse"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }
    
    // Show simple loading for first second or searching
    return (
      <div className="min-h-screen flex-center flex-col text-white bg-bg-dark">
         <div className="animate-pulse-glow h-20 w-20 bg-primary/20 flex-center rounded-full mb-6 border border-primary/30">
           {status === 'searching' ? (
             <Activity className="text-primary animate-pulse" size={32} />
           ) : (
             <Clock className="text-primary animate-spin" size={32} />
           )}
         </div>
         <h2 className="text-2xl font-bold mb-2 tracking-tight">
           {status === 'searching' ? 'Establishing Match Integrity' : 'Syncing Neural Pathways'}
         </h2>
         <p className="text-text-muted font-mono text-sm max-w-md text-center opacity-80">
           {status === 'searching' 
             ? `Securing encrypted tunnel for 1v1 combat... ${searchTime}s remaining`
             : 'Generating unique algorithmic challenge from distributed dataset...'}
         </p>
         
         {status === 'searching' && (
           <div className="mt-8 w-64 h-1 bg-white/5 rounded-full overflow-hidden">
             <div 
               className="h-full bg-primary transition-all duration-1000 ease-linear" 
               style={{ width: `${((30 - searchTime) / 30) * 100}%` }}
             />
           </div>
         )}
      </div>
    );
  }

  const isSubmitting = status === 'submitting' || status === 'polling';

  return (
    <div className="bg-mesh-background min-h-screen">
      <div className="bg-mesh"></div>
      

      <div className="min-h-screen flex flex-col p-4 animate-fade-in relative z-0">
        
        {/* Top HUD */}
        <div className="glass-panel mb-6 p-4 flex items-center justify-between border-b-2 border-primary/30 bg-bg-panel/60 shadow-glow-sm relative z-20">
          {/* User Section */}
          <div className="flex items-center gap-4 flex-1">
            <div className="relative">
              <div className="p-2.5 bg-primary/10 rounded-xl border border-primary/20 shadow-inner">
                 <UserIcon size={22} className="text-primary" />
              </div>
              <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-success rounded-full border-2 border-bg-panel"></div>
            </div>
            <div>
              <p className="text-sm font-black text-white tracking-tight uppercase">{user?.username || 'Guest'}</p>
              <div className="flex items-center gap-1.5">
                <span className="text-[10px] text-text-muted font-mono uppercase tracking-widest">Index</span>
                <span className={`text-[10px] font-black px-1.5 rounded ${challengeType === 'debug' ? 'text-danger bg-danger/10' : 'text-success bg-success/10'}`}>
                  {challengeType === 'debug' ? (user?.debug_rating || 300) : user?.current_rating}
                </span>
              </div>
            </div>
          </div>

          {/* Timer Section - Center with Submission Counts */}
          <div className="flex-1 flex justify-center items-center gap-4">
            {/* Left: Your Submissions */}
            <div className="flex flex-col items-center">
              <div className="bg-primary/10 border border-primary/20 rounded-lg px-3 py-1.5">
                <div className="text-[8px] text-text-muted uppercase tracking-widest mb-0.5 text-center">You</div>
                <div className="text-xl font-black text-primary font-mono">{userSubmissions}</div>
              </div>
            </div>

            {/* Center: Timer */}
            <div className={`relative group transition-all duration-500 ${timeLeft !== null && timeLeft < 30 ? 'scale-110' : ''}`}>
              <div className={`p-1 px-6 rounded-2xl border-2 flex flex-col items-center justify-center min-w-[160px] transition-all ${timeLeft !== null && timeLeft < 30 ? 'bg-danger/10 border-danger/60 shadow-glow shadow-danger/40 animate-pulse' : 'bg-bg-dark/90 border-primary/20 shadow-glow shadow-primary/10'}`}>
                 <div className="flex items-center gap-2 text-text-muted uppercase tracking-[0.3em] text-[8px] font-black opacity-60 mb-0.5">
                   <Clock size={10} /> Sync Time
                 </div>
                 <span className={`text-3xl font-mono font-black tracking-[0.2em] leading-none ${(timeLeft !== null && timeLeft < 30) ? 'text-danger' : 'text-white'}`}>
                    {timeLeft !== null ? `${Math.floor(timeLeft / 60)}:${(timeLeft % 60).toString().padStart(2, '0')}` : '--:--'}
                 </span>
              </div>
            </div>

            {/* Right: Opponent Submissions (only in 1v1) */}
            {opponent ? (
              <div className="flex flex-col items-center">
                <div className="bg-accent/10 border border-accent/20 rounded-lg px-3 py-1.5">
                  <div className="text-[8px] text-text-muted uppercase tracking-widest mb-0.5 text-center">Opp</div>
                  <div className="text-xl font-black text-accent font-mono">{opponent.submissions_count}</div>
                </div>
              </div>
            ) : (
              <div className="w-[60px]"></div>
            )}
          </div>

          {/* Match Stats Section - Opponent Info */}
          <div className="flex items-center gap-6 flex-1 justify-end">
             {opponent ? (
               <div className="text-right flex flex-col items-end gap-1">
                 <div className="flex items-center gap-2">
                   <span className="text-sm font-black text-white uppercase tracking-tight">
                     {opponent.username}
                   </span>
                   <div className="w-2 h-2 rounded-full bg-accent animate-pulse"></div>
                 </div>
                 
                 <div className="flex items-center gap-2">
                   <span className="text-[10px] text-text-muted uppercase tracking-widest">Opponent</span>
                   <span className={`text-[10px] font-black px-1.5 rounded ${challengeType === 'debug' ? 'text-danger bg-danger/10' : 'text-success bg-success/10'}`}>
                     {opponent.current_rating}
                   </span>
                 </div>
               </div>
             ) : (
               <div className="text-right flex flex-col items-end gap-1">
                 <div className="flex items-center gap-2">
                   <span className="text-[10px] font-black uppercase tracking-widest text-text-muted">
                     Training Routine
                   </span>
                   <div className="w-2 h-2 rounded-full bg-text-muted"></div>
                 </div>
               </div>
             )}
             
             <div className="flex items-center gap-3">
               {!isDone ? (
                 <button 
                  onClick={handleFinishMatch}
                  disabled={status === 'submitting' || status === 'polling'}
                  className="btn btn-primary h-12 px-6 flex items-center gap-2 shadow-glow group border-b-4 border-black/20 hover:translate-y-[-2px] active:translate-y-[0] transition-all"
                 >
                   <CheckCircle2 size={18} className="group-hover:scale-110 transition-transform" /> 
                   <span className="uppercase text-xs font-black tracking-widest">Conclude</span>
                 </button>
               ) : (
                 <div className="bg-success/10 text-success border border-success/30 h-12 px-6 rounded-lg flex items-center gap-3 font-black text-xs uppercase tracking-widest animate-pulse border-b-4 border-success/40">
                   <Activity size={18} className="animate-spin-slow" /> Awaiting Peer
                 </div>
               )}
             </div>
          </div>
        </div>

        <div className="flex-between mb-4 px-2">
          <button onClick={() => navigate('/dashboard')} className="text-text-secondary hover:text-white flex items-center gap-2 transition-colors">
             &larr; Abort Mission
          </button>
          <div className="flex items-center gap-3">
            <span className="badge badge-warning">{challenge.difficulty}</span>
            <span className="badge badge-primary">{challenge.domain}</span>
          </div>
        </div>

        <div className={`flex-1 grid grid-cols-1 ${opponent ? 'lg:grid-cols-3' : 'lg:grid-cols-2'} gap-4 min-h-0`}>
          <div className="glass-panel p-6 overflow-y-auto flex flex-col">
            <h2 className="text-2xl font-bold text-white mb-2">{challenge.title}</h2>
            <div className="bg-bg-panel-light p-4 rounded-lg border border-border-light mb-6">
              <p className="whitespace-pre-wrap text-text-primary text-sm leading-relaxed">{challenge.description}</p>
            </div>
            <h3 className="text-sm uppercase tracking-wider text-text-muted mb-3 font-bold">I/O Specification</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div className="bg-bg-dark rounded p-3 border border-border-light">
                <span className="text-xs text-text-secondary mb-1 block">Input Format</span>
                <p className="text-sm font-mono text-white whitespace-pre-wrap">{challenge.input_format}</p>
              </div>
              <div className="bg-bg-dark rounded p-3 border border-border-light">
                <span className="text-xs text-text-secondary mb-1 block">Output Format</span>
                <p className="text-sm font-mono text-white whitespace-pre-wrap">{challenge.output_format}</p>
              </div>
            </div>
            <h3 className="text-sm uppercase tracking-wider text-text-muted mb-3 font-bold">Constraints</h3>
            <ul className="list-disc pl-5 mb-6 text-sm text-text-secondary space-y-1">
               {challenge.constraints && Object.entries(challenge.constraints).map(([_, v], i) => (
                  <li key={i}><span className="text-white font-mono">{String(v)}</span></li>
               ))}
               <li>Time Limit: <span className="text-warning">{challenge.time_limit_seconds || 120}s</span></li>
            </ul>
            <h3 className="text-sm uppercase tracking-wider text-text-muted mb-3 font-bold">Examples</h3>
            <div className="space-y-4 mb-4">
               {challenge.test_cases?.filter((t: any) => !t.is_hidden).map((tc: any, idx: number) => (
                 <div key={idx} className="bg-bg-dark rounded p-4 border border-border-light">
                    <div className="flex-between mb-2">
                      <span className="text-xs text-primary font-bold">Example {idx + 1}</span>
                      <span className="badge badge-secondary">{tc.category}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-xs text-text-secondary block mb-1">Input</span>
                        <pre className="text-sm font-mono text-white bg-black/40 p-2 rounded">{tc.input}</pre>
                      </div>
                      <div>
                        <span className="text-xs text-text-secondary block mb-1">Output</span>
                        <pre className="text-sm font-mono text-success bg-black/40 p-2 rounded">{tc.expected_output}</pre>
                      </div>
                    </div>
                 </div>
               ))}
            </div>
          </div>

          <div className="flex flex-col gap-4">
            <div className="glass-panel flex-1 flex flex-col overflow-hidden relative">
              <div className="bg-bg-dark border-b border-border-light p-2 px-4 flex-between items-center text-sm">
                <span className="text-text-secondary font-mono flex items-center gap-2">
                   <TerminalIcon size={14} /> solution.py
                </span>
                <span className="badge badge-primary">Python 3</span>
              </div>
              <div className="flex-1 min-h-0 bg-bg-dark/20">
                <Editor
                  height="100%"
                  defaultLanguage="python"
                  theme="vs-dark"
                  value={code}
                  onChange={(value) => setCode(value || '')}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    padding: { top: 16 },
                    fontFamily: "'Fira Code', monospace",
                    bracketPairColorization: { enabled: true },
                    formatOnType: true,
                    autoClosingBrackets: 'always',
                    suggestOnTriggerCharacters: true,
                    acceptSuggestionOnEnter: 'on',
                    tabSize: 4,
                  }}
                />
              </div>
              <div className="absolute bottom-6 right-6 z-20">
                <button onClick={handleSubmitCode} className="btn btn-primary shadow-glow-lg px-6 py-3 transition-all transform hover:scale-105 active:scale-95" disabled={isSubmitting || code.trim() === ''}>
                  {isSubmitting ? <Clock className="animate-spin" size={18} /> : <Play size={18} fill="currentColor" />} {isSubmitting ? 'Verifying...' : 'Submit Neural Data'}
                </button>
              </div>
            </div>
            <div className="glass-panel h-64 overflow-y-auto flex flex-col font-mono text-sm">
               <div className="bg-bg-dark border-b border-border-light p-2 px-4 sticky top-0 uppercase tracking-widest text-xs text-text-muted font-bold z-10">Terminal</div>
               <div className="p-4 flex-1">
                  {!submissionResult && status === 'idle' && (
                    <div className="flex flex-col gap-2">
                      <span className="text-text-secondary">&gt; Ready for execution...</span>
                      {error && <div className="text-danger mt-2 p-3 bg-danger/10 border border-danger/20 rounded text-xs"><pre className="whitespace-pre-wrap">{error}</pre></div>}
                    </div>
                  )}
                 {status === 'polling' && <div className="text-warning animate-pulse">&gt; Executing test suites...</div>}
                 {submissionResult && (
                   <div className="space-y-4 animate-fade-in">
                     <div className="flex items-center gap-3 border-b border-border-light pb-3">
                       {submissionResult.status === 'success' ? <CheckCircle2 size={24} className="text-success" /> : <XCircle size={24} className="text-danger" />}
                       <span className={`text-xl font-bold ${submissionResult.status === 'success' ? 'text-success' : 'text-danger'}`}>
                         {submissionResult.status === 'success' ? 'Tests Passed' : 'Execution Error'}
                       </span>
                     </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div><span className="text-xs text-text-muted block">Passed</span><span className="text-white text-lg">{submissionResult.test_cases_passed} / {challenge.test_cases?.length || '?'}</span></div>
                        <div><span className="text-xs text-text-muted block">Runtime</span><span className="text-white text-lg">{submissionResult.execution_time_ms ? `${submissionResult.execution_time_ms}ms` : 'N/A'}</span></div>
                        <div><span className="text-xs text-text-muted block">Integrity</span><span className={(submissionResult.ai_assisted_probability ?? 0) > 70 ? "text-danger text-lg" : "text-success text-lg"}>{(submissionResult.ai_assisted_probability ?? 0) > 70 ? 'AI Check' : 'Human'}</span></div>
                        <div><span className="text-xs text-text-muted block">ELO</span><span className={submissionResult.score >= 0 ? "text-success text-lg" : "text-danger text-lg"}>{submissionResult.score >= 0 ? `+${submissionResult.score}` : submissionResult.score}</span></div>
                      </div>
                      {submissionResult.status !== 'success' && submissionResult.error_details && (
                        <div className="mt-4 p-3 bg-danger/10 border border-danger/20 rounded text-xs text-danger overflow-x-auto">
                          <pre className="font-mono whitespace-pre-wrap">{submissionResult.error_details}</pre>
                        </div>
                      )}
                   </div>
                 )}
               </div>
            </div>
          </div>

          {opponent && (
            <div className="flex flex-col gap-4">
              <div className="flex-1 flex flex-col glass-panel border border-border-light relative overflow-hidden">
                <div className="flex-between p-3 px-4 border-b border-border-light bg-bg-panel/40">
                  <div className="flex items-center gap-3">
                    <Activity size={12} className="text-danger animate-pulse" />
                    <span className="text-xs font-bold text-white uppercase tracking-wider">Opponent Feed</span>
                  </div>
                  <span className="text-[10px] text-text-muted font-mono">{opponent.username}</span>
                </div>
                <div className="flex-1 p-4 bg-black/20 backdrop-blur-sm relative group overflow-hidden">
                  <div className="absolute inset-0 flex-center opacity-10 pointer-events-none">
                     <Activity size={48} className="text-primary animate-pulse" />
                  </div>
                  <pre className="text-[10px] font-mono text-primary/60 select-none pointer-events-none">
                    {opponentCode || '// Opponent is analyzing...'}
                  </pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Fixed Overlays moved to end for correct stacking and blurring */}
      {isDone && !showResults && opponent && (
        <div className="fixed inset-0 z-[100] bg-overlay-90 backdrop-blur-xl flex items-center justify-center animate-fade-in">
           <div className="glass-panel p-10 text-center max-w-sm border-primary/60 shadow-glow-2xl relative z-[110] animate-scale-in bg-bg-panel/90">
              <div className="h-20 w-20 rounded-full bg-primary/20 flex-center mx-auto mb-6 border-2 border-primary/40 shadow-glow-md">
                <RefreshCw size={40} className="text-primary animate-spin" />
              </div>
              <h1 className="text-2xl font-black text-white mb-3 uppercase italic tracking-tighter">Synchronizing</h1>
              <p className="text-text-secondary text-sm leading-relaxed opacity-90">
                Peer consensus is being validated across the distributed neural net.
              </p>
              <div className="mt-8 flex flex-col gap-3">
                 <div className="h-1.5 w-full bg-bg-dark rounded-full overflow-hidden border border-white/5">
                    <div className="h-full bg-primary animate-progress-indefinite shadow-glow-sm"></div>
                 </div>
                 <span className="text-[10px] uppercase tracking-[0.4em] text-primary font-black animate-pulse">Syncing...</span>
              </div>
           </div>
        </div>
      )}

      {showResults && matchData && user && (
        <MatchResults data={matchData} user={user} onDashboard={() => navigate('/dashboard')} challengeType={challengeType} />
      )}
    </div>
  );
};

export default Arena;
