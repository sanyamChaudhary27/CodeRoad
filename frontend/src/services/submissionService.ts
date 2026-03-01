import api from '../lib/api';

export interface SubmissionRequest {
  challenge_id: string;
  code: string;
  language: string;
  time_to_solve_ms?: number;
  keystroke_speed_avg?: number;
  copy_paste_events?: number;
  deletion_ratio?: number;
}

export interface SubmissionResponse {
  id: string;
  challenge_id: string;
  player_id: string;
  status: 'pending' | 'executing' | 'success' | 'runtime_error' | 'timeout';
  code: string;
  language: string;
  test_cases_passed: number;
  execution_time_ms: number | null;
  error_message: string | null;
  score: number;
  ai_assisted_probability: number | null;
  created_at: string;
  concluded_at: string | null;
}

export const submissionService = {
  async submitCode(data: SubmissionRequest): Promise<SubmissionResponse> {
    const response = await api.post('/submissions', data);
    return response.data;
  },

  // GET route used by frontend polling loop to await background task completion
  async getSubmission(submissionId: string): Promise<SubmissionResponse> {
    const response = await api.get(`/submissions/${submissionId}`);
    return response.data;
  }
};
