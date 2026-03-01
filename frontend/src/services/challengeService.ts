import api from '../lib/api';

export interface TestCase {
  id: string;
  input: string;
  expected_output: string;
  category: string;
  description: string;
  is_hidden: boolean;
}

export interface CoverageMetrics {
  total_test_cases: number;
  categories: Record<string, number>;
  coverage_score: number;
}

export interface Challenge {
  id: string;
  title: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  domain: string;
  constraints: Record<string, string> | string[];
  input_format: string;
  output_format: string;
  example_input: string;
  example_output: string;
  time_limit_seconds: number;
  test_cases: TestCase[];
  coverage_metrics?: CoverageMetrics;
  boilerplate_code?: string;
  generated_at?: string;
}

export const challengeService = {
  async generateChallenge(difficulty?: string, domain?: string): Promise<Challenge> {
    const response = await api.post('/challenges/generate', {
      difficulty,
      domain
    });
    return response.data;
  },

  async getChallenge(challengeId: string): Promise<Challenge> {
    const response = await api.get(`/challenges/${challengeId}`);
    return response.data;
  },

  async listChallenges(difficulty?: string, domain?: string, limit?: number): Promise<Challenge[]> {
    const params = new URLSearchParams();
    if (difficulty) params.append('difficulty', difficulty);
    if (domain) params.append('domain', domain);
    if (limit) params.append('limit', limit.toString());

    // Based on the guide, it could be /api/challenges or /api/v1/challenges. The guide showed both. BaseURL manages /v1
    const response = await api.get(`/challenges?${params.toString()}`);
    return response.data;
  }
};
