import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { challengeService, type Challenge } from '../services/challengeService';
import { submissionService, type SubmissionResponse } from '../services/submissionService';
import { matchmakingService, type PlayerMatchInfo } from '../services/matchmakingService';
import { Play, CheckCircle2, XCircle, Clock, AlertTriangle, ShieldAlert, Terminal as TerminalIcon, User as UserIcon, Trophy, Activity, RefreshCw } from 'lucide-react';
import { authService, type User } from '../services/authService';

const Arena = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [matchId, setMatchId] = useState<string | null>(location.state?.matchId || null);
  const [opponent, setOpponent] = useState<PlayerMatchInfo | null>(null);
  const [code, setCode] = useState<string>('def solve():\n    # Write your code here\n    pass');
  const [opponentCode, setOpponentCode] = useState('// Opponent is typing...');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [status, setStatus] = useState<'idle' | 'generating' | 'submitting' | 'polling' | 'searching'>('generating');
  const [submissionResult, setSubmissionResult] = useState<SubmissionResponse | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [timeLeft, setTimeLeft] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [searchTime, setSearchTime] = useState<number>(30);

  useEffect(() => {
    const initializeArena = async () => {
      console.log("Arena INITIALIZING - S5 Sync Fix");
      
      // Prevent multiple concurrent initializations
      if (status === 'polling' || status === 'submitting') return;

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
              
              const opponentSource = isUserPlayer1 
                ? (matchDetails.player2 || {}) 
                : (matchDetails.player1 || {});

              localOpponent = {
                player_id: opponentSource.player_id || (isUserPlayer1 ? matchDetails.player2_id : matchDetails.player1_id),
                username: opponentSource.username || 'Opponent',
                current_rating: opponentSource.current_rating || 1200,
                submissions_count: opponentSource.submissions_count || 0,
                is_done: opponentSource.is_done || false
              };
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
     if (timeLeft === null || timeLeft <= 0 || status === 'submitting') return;
     
     const timerId = setInterval(() => {
       setTimeLeft(prev => (prev !== null && prev > 0) ? prev - 1 : 0);
     }, 1000);
     
     return () => clearInterval(timerId);
  }, [timeLeft, status]);

  // Periodic Refresh for Match Stats
  useEffect(() => {
    if (!matchId || matchId === "prototype_match_id") return;
    
    const refreshInterval = setInterval(async () => {
      try {
        const matchDetails = await matchmakingService.getMatch(matchId);
        const currentUser = user || await authService.getCurrentUser();
        
        // Update opponent stats (submission counts) using enriched flat fields
        const opponentInfo = matchDetails.player1_id === currentUser.id 
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
        
        if (matchDetails.player2_id) {
          setOpponent(opponentInfo);
        }
      } catch (e) {
        console.warn("Refresh failed", e);
      }
    }, 5000);
    
    return () => clearInterval(refreshInterval);
  }, [matchId, user]);

  // WebSocket Integration
  useEffect(() => {
    if (!matchId) return;

    const socketUrl = `ws://localhost:8000/ws/${matchId}`;
    const socket = new WebSocket(socketUrl);

    socket.onopen = () => {
      console.log('WebSocket Connected to match:', matchId);
      setWs(socket);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'CODE_SYNC') {
          setOpponentCode(data.code);
        }
      } catch (err) {
        console.warn('Failed to parse WS message:', event.data);
      }
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

  if (!challenge || status === 'generating' || status === 'searching') {
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
    <div className="min-h-screen flex flex-col p-4 animate-fade-in">
      
      {/* Top HUD */}
      <div className="glass-panel mb-4 p-4 flex items-center justify-between border-b-2 border-primary/30 bg-bg-panel/40 select-none">
        <div className="flex items-center gap-4">
          <div className="p-2 bg-primary/10 rounded-full border border-primary/20">
             <UserIcon size={20} className="text-primary" />
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-bold text-white leading-tight">{user?.username || 'Guest'}</p>
            <p className="text-[10px] text-text-muted font-mono uppercase tracking-wider">Rating: <span className="text-success">{user?.current_rating}</span></p>
          </div>
        </div>

        <div className="flex flex-col items-center">
          <div className={`p-2 px-4 rounded-xl border flex-center flex-col gap-0.5 min-w-[140px] ${timeLeft !== null && timeLeft < 30 ? 'bg-danger/10 border-danger/40 animate-pulse' : 'bg-bg-dark/80 border-border-light shadow-inner-white'}`}>
             <div className="flex items-center gap-1.5 text-text-muted uppercase tracking-[0.2em] text-[9px] font-bold">
               <Clock size={10} /> Time Remaining
             </div>
             <span className={`text-2xl font-mono font-bold tracking-widest ${(timeLeft !== null && timeLeft < 30) ? 'text-danger' : 'text-white'}`}>
                {timeLeft !== null ? `${Math.floor(timeLeft / 60)}:${(timeLeft % 60).toString().padStart(2, '0')}` : '--:--'}
             </span>
          </div>
        </div>

        <div className="flex items-center gap-4 text-right">
          <div className="hidden sm:block">
            <p className="text-sm font-bold text-white leading-tight">{opponent ? opponent.username : 'Solo Training'}</p>
            <div className="flex items-center gap-2 justify-end mt-0.5">
               <span className="text-[9px] bg-bg-dark px-1.5 py-0.5 rounded border border-border-light text-text-muted font-mono">
                 {opponent ? `ELO: ${opponent.current_rating}` : 'UNRANKED'}
               </span>
               {opponent && (
                 <span className="text-[9px] bg-primary/10 px-1.5 py-0.5 rounded border border-primary/30 text-primary font-mono tracking-tighter uppercase font-bold">
                   {opponent.submissions_count || 0} Subs
                 </span>
               )}
            </div>
          </div>
          <div className="p-2 bg-accent/10 rounded-full border border-accent/20">
             <Trophy size={20} className="text-accent" />
          </div>
        </div>
      </div>

      {/* Breadcrumbs / Actions Row */}
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
        
        {/* Left Pane - Problem Description */}
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

          <h3 className="text-sm uppercase tracking-wider text-text-muted mb-3 font-bold">Constraints & Boundaries</h3>
          <ul className="list-disc pl-5 mb-6 text-sm text-text-secondary space-y-1">
             {challenge.constraints && Object.entries(challenge.constraints).map(([_, v], i) => (
                <li key={i}><span className="text-white font-mono">{String(v)}</span></li>
             ))}
             <li>Time Limit: <span className="text-warning">{challenge.time_limit_seconds || 120}s</span></li>
          </ul>

          <h3 className="text-sm uppercase tracking-wider text-text-muted mb-3 font-bold">Example Scenarios</h3>
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
                      <span className="text-xs text-text-secondary block mb-1">Expected Output</span>
                      <pre className="text-sm font-mono text-success bg-black/40 p-2 rounded">{tc.expected_output}</pre>
                    </div>
                  </div>
                  {tc.description && <p className="text-xs text-text-muted mt-2 mt-2 pt-2 border-t border-border-light">{tc.description}</p>}
               </div>
             ))}
          </div>
        </div>

        {/* Center Column - Code Editor */}
        <div className="flex flex-col gap-4">
          <div className="glass-panel flex-1 flex flex-col overflow-hidden relative">
            <div className="bg-bg-dark border-b border-border-light p-2 px-4 flex-between items-center text-sm">
              <span className="text-text-secondary font-mono flex items-center gap-2">
                 <TerminalIcon size={14} /> solution.py
              </span>
              <span className="badge badge-primary">Python 3</span>
            </div>
            
            <textarea
              className="flex-1 w-full bg-transparent text-white font-mono p-4 resize-none focus:outline-none"
              spellCheck={false}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="# Write your Python code here"
              style={{ lineHeight: '1.5', color: 'white', caretColor: 'var(--primary)' }}
            />
            
            <div className="absolute bottom-4 right-4">
              <button 
                onClick={handleSubmitCode} 
                className="btn btn-primary shadow-glow transition-all"
                disabled={isSubmitting || code.trim() === ''}
              >
                {isSubmitting ? (
                  <><Clock className="animate-spin" size={18} /> Executing...</>
                ) : (
                  <><Play size={18} fill="currentColor" /> Compile & Run</>
                )}
              </button>
            </div>
          </div>

          {/* Terminal Output */}
          <div className="glass-panel h-64 overflow-y-auto flex flex-col font-mono text-sm relative">
             <div className="bg-bg-dark border-b border-border-light p-2 px-4 sticky top-0 uppercase tracking-widest text-xs text-text-muted font-bold z-10">
               Execution Terminal
             </div>
             
             <div className="p-4 flex-1">
                {!submissionResult && status === 'idle' && (
                  <div className="flex flex-col gap-2">
                    <span className="text-text-secondary">&gt; Awaiting execution command...</span>
                    {error && (
                      <div className="text-danger mt-2 p-3 bg-danger/10 border border-danger/20 rounded font-mono text-xs animate-in fade-in slide-in-from-top-1">
                        <div className="flex items-center gap-2 mb-1 font-bold">
                          <XCircle size={14} /> SYSTEM_EXCEPTION_TRACEBACK
                        </div>
                        <pre className="whitespace-pre-wrap break-all opacity-90">{error}</pre>
                      </div>
                    )}
                  </div>
                )}
               
               {status === 'polling' && (
                 <div className="flex items-center gap-2 text-warning animate-pulse">
                   &gt; Requesting secure execution container...<br/>
                   &gt; Compiling against {challenge.test_cases?.length || '?'} parallel test suites...<br/>
                   &gt; Awaiting ML validation heuristics...
                 </div>
               )}

               {submissionResult && (
                 <div className="space-y-4 animate-fade-in">
                   <div className="flex items-center gap-3 border-b border-border-light pb-3">
                     {submissionResult.status === 'success' ? (
                       <><CheckCircle2 size={24} className="text-success" /> <span className="text-xl font-bold text-success">Verification Successful</span></>
                     ) : (
                       <><XCircle size={24} className="text-danger" /> <span className="text-xl font-bold text-danger">Execution Failed</span></>
                     )}
                   </div>
                   
                   <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div>
                        <span className="text-xs text-text-muted block">Tests Passed</span>
                        <span className="text-white text-lg">{submissionResult.test_cases_passed} / {challenge.test_cases?.length || '?'}</span>
                      </div>
                      <div>
                        <span className="text-xs text-text-muted block">Runtime</span>
                        <span className="text-white text-lg">{submissionResult.execution_time_ms ? `${submissionResult.execution_time_ms}ms` : 'N/A'}</span>
                      </div>
                      <div>
                        <span className="text-xs text-text-muted block">Integrity Score</span>
                        <div className="flex items-center gap-2">
                           {submissionResult.ai_assisted_probability !== null && submissionResult.ai_assisted_probability > 70 ? (
                             <><ShieldAlert size={16} className="text-danger" /><span className="text-danger text-lg">{submissionResult.ai_assisted_probability.toFixed(0)}% AI</span></>
                           ) : (
                             <span className="text-success text-lg">Human</span>
                           )}
                        </div>
                      </div>
                      <div>
                        <span className="text-xs text-text-muted block">Elo Impact</span>
                        <span className={submissionResult.score > 0 ? "text-success text-lg" : "text-danger text-lg"}>
                           {submissionResult.score > 0 ? `+${submissionResult.score}` : submissionResult.score}
                        </span>
                      </div>
                   </div>

                   {submissionResult.status !== 'success' && submissionResult.error_message && (
                     <div className="mt-4 p-3 bg-danger/10 border border-danger/20 rounded">
                        <span className="text-xs text-danger uppercase tracking-wider block mb-1 font-bold flex items-center gap-2">
                          <AlertTriangle size={14} /> Traceback Context
                        </span>
                        <pre className="text-xs text-danger/90 whitespace-pre-wrap">{submissionResult.error_message}</pre>
                     </div>
                   )}
                 </div>
               )}
             </div>
          </div>
        </div>

        {/* Right Column - Opponent Feed */}
        {opponent && (
          <div className="flex flex-col gap-4">
          {/* AI/Opponent Editor - Only show if not solo match */}
        {opponent?.player_id && (
          <div className="flex-1 flex flex-col min-w-0 border-l border-border-light relative">
            <div className="flex-between p-3 px-4 glass-panel border-0 rounded-none border-b border-border-light">
              <div className="flex items-center gap-3">
                <div className="h-6 w-6 rounded-full bg-danger/20 flex-center">
                  <Activity size={12} className="text-danger" />
                </div>
                <span className="text-sm font-bold text-white tracking-wide">
                  OPPONENT TERMINAL
                </span>
              </div>
              <div className="flex items-center gap-4">
                 <span className="text-xs text-text-muted font-mono">ID: {opponent.player_id.slice(0, 8)}</span>
              </div>
            </div>
            
            <div className="flex-1 overflow-hidden bg-bg-panel/40 backdrop-blur-sm relative group">
              <div className="absolute inset-0 flex-center flex-col p-8 text-center opacity-40 group-hover:opacity-60 transition-opacity pointer-events-none">
                 <Activity size={32} className="text-primary mb-4 animate-pulse" />
                 <p className="text-sm text-primary font-mono lowercase tracking-widest">
                   &gt; live_sync: active<br/>
                   &gt; state: processing
                 </p>
              </div>
              <div className="h-full w-full p-4 pointer-events-none opacity-20 filter blur-[1px]">
                <pre className="text-xs font-mono text-primary">
                  {opponentCode || `def solve(arr, x):\n  # opponent thinking...\n  # analyzing patterns\n  for i in range(len(arr)):\n    if arr[i] == x:\n      return i\n  return -1`}
                </pre>
              </div>
            </div>
          </div>
        )}

      </div>
        )}

      </div>
    </div>
  );
};
    
// Final component export
export default Arena;
