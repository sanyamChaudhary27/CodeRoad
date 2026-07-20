import api from '../lib/api';

export type AttackCategory =
  | 'boundary'
  | 'sign'
  | 'ordering'
  | 'duplicate'
  | 'magnitude'
  | 'structure';

export interface AttackProblem {
  id: string;
  title: string;
  statement: string;
  input_format: string;
  constraints: string[];
  ordinary_tests: number[][];
  boilerplate_code: string;
}

export interface ExecutionView {
  status: string;
  output: string;
  execution_time_ms: number | null;
  passed: boolean;
  diagnostic: string | null;
}

export interface BaselineTrial {
  values: number[];
  expected_output: string;
  solution_a: ExecutionView;
  solution_b: ExecutionView;
}

export interface AttackTrial extends BaselineTrial {
  category: AttackCategory;
  rationale: string;
  targets_assumption: string;
  distinguished: boolean;
}

export interface AttackRoundResponse {
  problem: AttackProblem;
  generation_source: 'nvidia-nim' | 'deterministic-fallback';
  model: string | null;
  generation_note: string;
  baseline_passed: boolean;
  ordinary_trials: BaselineTrial[];
  attack_trials: AttackTrial[];
  candidates_proposed: number;
  candidates_verified: number;
  witness: AttackTrial | null;
  winner: 'solution_a' | 'solution_b' | 'draw' | 'baseline_failed';
  verdict: string;
}

export interface AttackRoundRequest {
  problem_id: 'max-subarray';
  solution_a: { label: string; code: string; language: 'python' };
  solution_b: { label: string; code: string; language: 'python' };
}

export const attackRoundService = {
  async listProblems(): Promise<AttackProblem[]> {
    const response = await api.get('/attack-rounds/problems');
    return response.data;
  },

  async analyze(request: AttackRoundRequest): Promise<AttackRoundResponse> {
    const response = await api.post('/attack-rounds/analyze', request);
    return response.data;
  },
};
