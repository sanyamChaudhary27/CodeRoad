import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { challengeService, type Challenge } from '../services/challengeService';
import { submissionService, type SubmissionResponse } from '../services/submissionService';
import { Play, CheckCircle2, XCircle, Clock, AlertTriangle, ShieldAlert } from 'lucide-react';

const Arena = () => {
  const navigate = useNavigate();
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [code, setCode] = useState<string>('def solve():\n    # Write your code here\n    pass');
  const [status, setStatus] = useState<'idle' | 'generating' | 'submitting' | 'polling'>('generating');
  const [submissionResult, setSubmissionResult] = useState<SubmissionResponse | null>(null);

  useEffect(() => {
    const fetchChallenge = async () => {
      try {
        const data = await challengeService.generateChallenge('intermediate', 'arrays');
        setChallenge(data);
      } catch (err) {
        console.error("Error generating challenge", err);
        // Fallback or navigate away
      } finally {
        setStatus('idle');
      }
    };
    fetchChallenge();
  }, []);

  const handleSubmit = async () => {
    if (!challenge) return;
    setStatus('submitting');
    setSubmissionResult(null);

    try {
      // 1. Submit Code Structure
      const response = await submissionService.submitCode({
        challenge_id: challenge.id,
        code,
        language: 'python'
      });

      setStatus('polling');
      
      // 2. Poll for Background Task completion
      const pollInterval = setInterval(async () => {
        const result = await submissionService.getSubmission(response.id);
        
        if (result.status === 'success' || result.status === 'runtime_error' || result.status === 'timeout') {
          clearInterval(pollInterval);
          setSubmissionResult(result);
          setStatus('idle');
        }
      }, 1000);

    } catch (err) {
      console.error("Submission failed", err);
      setStatus('idle');
    }
  };

  if (!challenge) {
    return (
      <div className="min-h-screen flex-center flex-col text-white">
         <div className="animate-pulse-glow h-16 w-16 bg-primary/20 flex-center rounded-full mb-4">
           <Clock className="text-primary animate-spin" />
         </div>
         <p>Generating adaptive scenario...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col p-4 animate-fade-in">
      
      {/* Top Bar Navigate Back */}
      <div className="flex-between mb-4 px-2">
        <button onClick={() => navigate('/dashboard')} className="text-text-secondary hover:text-white flex items-center gap-2 transition-colors">
           &larr; Abort Mission
        </button>
        <div className="flex items-center gap-3">
          <span className="badge badge-warning">{challenge.difficulty}</span>
          <span className="badge badge-primary">{challenge.domain}</span>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
        
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
             {Object.entries(challenge.constraints).map(([k, v], i) => (
                <li key={i}><span className="text-white font-mono">{String(v)}</span></li>
             ))}
             <li>Time Limit: <span className="text-warning">{challenge.time_limit_seconds}s</span></li>
          </ul>

          <h3 className="text-sm uppercase tracking-wider text-text-muted mb-3 font-bold">Example Scenarios</h3>
          <div className="space-y-4 mb-4">
             {challenge.test_cases?.filter(t => !t.is_hidden).map((tc, idx) => (
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

        {/* Right Pane - Code Editor & Terminal */}
        <div className="flex flex-col gap-4">
          
          {/* Editor Area */}
          <div className="glass-panel flex-1 flex flex-col overflow-hidden relative">
            <div className="bg-bg-dark border-b border-border-light p-2 px-4 flex-between items-center text-sm">
              <span className="text-text-secondary font-mono flex items-center gap-2">
                 <Terminal size={14} /> solution.py
              </span>
              <span className="badge badge-primary">Python 3</span>
            </div>
            
            <textarea
              className="flex-1 w-full bg-transparent text-white font-mono p-4 resize-none focus:outline-none"
              spellCheck={false}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="# Write your Python code here"
              style={{ lineHeight: '1.5' }}
            />
            
            <div className="absolute bottom-4 right-4">
              <button 
                onClick={handleSubmit} 
                className="btn btn-primary shadow-glow transition-all"
                disabled={status === 'submitting' || status === 'polling' || code.trim() === ''}
              >
                {status === 'submitting' || status === 'polling' ? (
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
                 <span className="text-text-secondary">&gt; Awaiting execution command...</span>
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

      </div>
    </div>
  );
};
    
// Needed terminal icon 
import { Terminal } from 'lucide-react';
export default Arena;
