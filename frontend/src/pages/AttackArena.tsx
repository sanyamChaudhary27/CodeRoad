import { useEffect, useMemo, useState } from 'react';
import Editor from '@monaco-editor/react';
import {
  AlertTriangle,
  ArrowRight,
  Check,
  CircleDot,
  FlaskConical,
  LoaderCircle,
  ShieldCheck,
  Sparkles,
  Swords,
  X,
  Zap,
} from 'lucide-react';

import Header from '../components/Header';
import { authService, type User } from '../services/authService';
import {
  attackRoundService,
  type AttackRoundResponse,
  type ExecutionView,
} from '../services/attackRoundService';
import './AttackArena.css';

const BUGGY_SOLUTION = `def solve(arr):
    # Common Kadane implementation that accidentally allows an empty subarray.
    best = 0
    current = 0

    for value in arr:
        current = max(0, current + value)
        best = max(best, current)

    return best`;

const ROBUST_SOLUTION = `def solve(arr):
    # The problem requires a non-empty subarray, so initialize from arr[0].
    best = arr[0]
    current = arr[0]

    for value in arr[1:]:
        current = max(value, current + value)
        best = max(best, current)

    return best`;

const resultClass = (execution: ExecutionView) =>
  execution.passed ? 'attack-result attack-result--pass' : 'attack-result attack-result--fail';

const ResultPill = ({ execution }: { execution: ExecutionView }) => (
  <div className={resultClass(execution)} title={execution.diagnostic || execution.status}>
    {execution.passed ? <Check size={14} /> : <X size={14} />}
    <span>{execution.output || execution.status}</span>
  </div>
);

const AttackArena = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isProfileLoading, setIsProfileLoading] = useState(true);
  const [solutionA, setSolutionA] = useState(BUGGY_SOLUTION);
  const [solutionB, setSolutionB] = useState(ROBUST_SOLUTION);
  const [result, setResult] = useState<AttackRoundResponse | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    authService
      .getCurrentUser()
      .then(setUser)
      .catch(() => setError('Could not load your profile. Please sign in again.'))
      .finally(() => setIsProfileLoading(false));
  }, []);

  const winnerLabel = useMemo(() => {
    if (!result) return null;
    if (result.winner === 'solution_a') return 'Solution A';
    if (result.winner === 'solution_b') return 'Solution B';
    if (result.winner === 'baseline_failed') return 'Ordinary suite failed';
    return 'No winner';
  }, [result]);

  const runAttack = async () => {
    setIsRunning(true);
    setError(null);
    setResult(null);
    try {
      const response = await attackRoundService.analyze({
        problem_id: 'max-subarray',
        solution_a: { label: 'Solution A', code: solutionA, language: 'python' },
        solution_b: { label: 'Solution B', code: solutionB, language: 'python' },
      });
      setResult(response);
    } catch (requestError: unknown) {
      const fallback = 'The attack round could not run.';
      if (
        typeof requestError === 'object' &&
        requestError !== null &&
        'response' in requestError
      ) {
        const response = (requestError as { response?: { data?: { detail?: string } } }).response;
        setError(response?.data?.detail || fallback);
      } else {
        setError(fallback);
      }
    } finally {
      setIsRunning(false);
    }
  };

  if (isProfileLoading) {
    return (
      <div className="attack-loading">
        <LoaderCircle className="attack-spin" size={34} />
        <span>Loading adversarial arena…</span>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="attack-loading attack-loading--error">
        <AlertTriangle size={34} />
        <strong>We could not open the arena.</strong>
        <span>{error || 'Please sign in again.'}</span>
      </div>
    );
  }

  return (
    <main className="attack-page">
      <div className="attack-orb attack-orb--one" />
      <div className="attack-orb attack-orb--two" />
      <div className="attack-shell">
        <Header user={user} />

        <section className="attack-hero">
          <div>
            <div className="attack-eyebrow"><Sparkles size={15} /> Build Week · OpenAI-assisted</div>
            <h1>Passing tests is only the <span>first round.</span></h1>
            <p>
              Both solutions clear the ordinary suite. Cached OpenAI hypotheses and deterministic
              templates attack their assumptions; isolated tools decide what is actually true.
            </p>
          </div>
          <div className="attack-proof-card">
            <ShieldCheck size={28} />
            <div>
              <strong>Model proposes. Code proves.</strong>
              <span>No model-written expected outputs are trusted.</span>
            </div>
          </div>
        </section>

        <section className="attack-problem-card">
          <div className="attack-problem-heading">
            <div>
              <span className="attack-kicker">THE DUEL</span>
              <h2>Maximum Subarray</h2>
            </div>
            <span className="attack-difficulty">INTERMEDIATE</span>
          </div>
          <p>
            Return the largest sum of a <strong>non-empty contiguous subarray</strong>. Input is one
            space-separated integer array, and each solution exposes <code>solve(arr)</code>.
          </p>
          <div className="attack-constraints">
            <span>1 ≤ n ≤ 30</span><span>−100 ≤ value ≤ 100</span><span>non-empty answer</span>
          </div>
        </section>

        <section className="attack-editors">
          <article className="attack-editor-card attack-editor-card--a">
            <header><span>A</span><div><strong>Solution A</strong><small>Python 3</small></div></header>
            <Editor
              height="390px"
              language="python"
              theme="vs-dark"
              value={solutionA}
              onChange={(value) => setSolutionA(value || '')}
              options={{ minimap: { enabled: false }, fontSize: 13, automaticLayout: true, scrollBeyondLastLine: false }}
            />
          </article>

          <div className="attack-versus"><Swords size={22} /><span>VS</span></div>

          <article className="attack-editor-card attack-editor-card--b">
            <header><span>B</span><div><strong>Solution B</strong><small>Python 3</small></div></header>
            <Editor
              height="390px"
              language="python"
              theme="vs-dark"
              value={solutionB}
              onChange={(value) => setSolutionB(value || '')}
              options={{ minimap: { enabled: false }, fontSize: 13, automaticLayout: true, scrollBeyondLastLine: false }}
            />
          </article>
        </section>

        <section className="attack-launch">
          <div>
            <FlaskConical size={24} />
            <div><strong>Ordinary suite → candidate generation → deterministic oracle → isolated execution</strong><span>Model prewarming never delays a verified result.</span></div>
          </div>
          <button onClick={runAttack} disabled={isRunning || !solutionA.trim() || !solutionB.trim()}>
            {isRunning ? <LoaderCircle className="attack-spin" size={19} /> : <Zap size={19} fill="currentColor" />}
            {isRunning ? 'Running isolated checks…' : 'Attack both solutions'}
            {!isRunning && <ArrowRight size={18} />}
          </button>
        </section>

        {error && (
          <section className="attack-error">
            <AlertTriangle size={22} />
            <div><strong>Attack round unavailable</strong><p>{error}</p></div>
          </section>
        )}

        {result && (
          <section className="attack-results">
            <div className="attack-stage-heading">
              <div><span>01</span><div><small>ORDINARY TESTS</small><h2>Both enter the tie-break</h2></div></div>
              <div className={result.baseline_passed ? 'attack-stage-status attack-stage-status--pass' : 'attack-stage-status attack-stage-status--fail'}>
                {result.baseline_passed ? <Check size={16} /> : <X size={16} />}
                {result.baseline_passed ? 'Both passed' : 'Baseline failed'}
              </div>
            </div>

            <div className="attack-test-grid">
              {result.ordinary_trials.map((trial) => (
                <article key={trial.values.join(',')}>
                  <code>[{trial.values.join(', ')}]</code>
                  <span>expected {trial.expected_output}</span>
                  <div><ResultPill execution={trial.solution_a} /><ResultPill execution={trial.solution_b} /></div>
                </article>
              ))}
            </div>

            {result.baseline_passed && (
              <>
                <div className="attack-stage-heading attack-stage-heading--second">
                  <div><span>02</span><div><small>ADVERSARIAL SWARM</small><h2>{result.candidates_verified} verified attacks</h2></div></div>
                  <div className="attack-source"><CircleDot size={14} />{result.generation_source === 'openai' ? result.model : 'Zero-credit fallback'}</div>
                </div>
                <p className="attack-generation-note">{result.generation_note}</p>

                <div className="attack-swarm">
                  {result.attack_trials.map((trial, index) => (
                    <article className={trial.distinguished ? 'attack-particle attack-particle--witness' : 'attack-particle'} key={`${trial.values.join(',')}-${index}`} style={{ animationDelay: `${index * 70}ms` }}>
                      <header><span>{trial.category}</span>{trial.distinguished && <strong>WITNESS</strong>}</header>
                      <code>[{trial.values.join(', ')}]</code>
                      <p>{trial.rationale}</p>
                      <div className="attack-particle-results"><ResultPill execution={trial.solution_a} /><ResultPill execution={trial.solution_b} /></div>
                    </article>
                  ))}
                </div>
              </>
            )}

            <div className={`attack-verdict attack-verdict--${result.winner}`}>
              <div className="attack-verdict-icon">{result.winner === 'draw' ? <CircleDot size={32} /> : <ShieldCheck size={34} />}</div>
              <div>
                <span>ROBUSTNESS VERDICT</span>
                <h2>{winnerLabel}</h2>
                <p>{result.verdict}</p>
                {result.witness && (
                  <div className="attack-witness-line">
                    Verified input <code>[{result.witness.values.join(', ')}]</code>
                    <ArrowRight size={15} /> oracle output <code>{result.witness.expected_output}</code>
                  </div>
                )}
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
};

export default AttackArena;
