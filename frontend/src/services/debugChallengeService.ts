import api from '../lib/api';

export interface DebugChallenge {
  id: string;
  title: string;
  description: string;
  difficulty: string;
  domain: string;
  challenge_type: string;
  broken_code: string;
  bug_count: number;
  bug_types: string[];
  constraints: Record<string, string>;
  input_format: string;
  output_format: string;
  example_input?: string;
  example_output?: string;
  time_limit_seconds: number;
  boilerplate_code: string;
  test_cases: Array<{
    id: string;
    input: string;
    expected_output: string;
    category: string;
    description: string;
    is_hidden: boolean;
  }>;
  coverage_metrics?: Record<string, any>;
  generated_at: string;
}

export const debugChallengeService = {
  /**
   * Generate a new debug challenge
   */
  async generateDebugChallenge(difficulty: string = 'intermediate', domain?: string): Promise<DebugChallenge> {
    const response = await api.post('/challenges/generate', {
      difficulty,
      domain,
      challenge_type: 'debug'
    });
    return response.data;
  },

  /**
   * Get a debug challenge by ID
   */
  async getDebugChallenge(challengeId: string): Promise<DebugChallenge> {
    const response = await api.get(`/challenges/${challengeId}`);
    return response.data;
  }
};
