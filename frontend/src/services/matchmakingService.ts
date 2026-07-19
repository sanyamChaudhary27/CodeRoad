import api from '../lib/api';

export interface MatchQueueStatus {
  in_queue: boolean;
  queue_id?: string;
  joined_at?: string;
  wait_time_seconds?: number;
  estimated_wait_seconds?: number;
  match_found?: boolean;
  match_id?: string;
}

export interface LeaderboardPlayer {
  rank: number;
  player_id: string;
  username: string;
  current_rating: number;
  wins: number;
  losses: number;
  win_rate: number;
  matches_played: number;
  rating_confidence: number;
  badges: string[];
}

export interface PlayerMatchInfo {
  player_id: string;
  username: string;
  current_rating: number;
  submissions_count: number;
  is_done: boolean;
}

export interface RatingUpdate {
  rating_change: number;
  new_rating: number;
}

export interface MatchDetails {
  match_id?: string;
  id?: string;
  status: string;
  format?: string;
  match_format?: string;
  challenge_type?: 'dsa' | 'debug';
  challenge_id?: string;
  created_at?: string;
  time_remaining?: number;
  time_limit_seconds?: number;
  player1?: PlayerMatchInfo | null;
  player2?: PlayerMatchInfo | null;
  player1_id?: string;
  player2_id?: string;
  player1_username?: string;
  player2_username?: string;
  player1_rating?: number;
  player2_rating?: number;
  player1_submissions?: number;
  player2_submissions?: number;
  player1_done?: boolean;
  player2_done?: boolean;
  player1_score?: number;
  player2_score?: number;
  winner_id?: string;
  result?: string;
  rating_updates?: { player1?: RatingUpdate; player2?: RatingUpdate };
}

export interface PlayerMatchHistory {
  matches: MatchDetails[];
  total_count: number;
}

export interface PracticeMatchResponse {
  match_id?: string;
  id?: string;
  challenge_id?: string;
}

export interface LeaderboardResponse {
  leaderboard: LeaderboardPlayer[];
  total_players: number;
  limit: number;
  offset: number;
}

export const matchmakingService = {
  async joinQueue(preferred_format: string = '1v1', challengeType: string = 'dsa', min_rating?: number, max_rating?: number) {
    const response = await api.post('/matches/queue/join', {
      preferred_format,
      challenge_type: challengeType,
      ...(min_rating && { min_rating }),
      ...(max_rating && { max_rating })
    });
    return response.data;
  },

  async leaveQueue() {
    const response = await api.post('/matches/queue/leave');
    return response.data;
  },

  async getQueueStatus(): Promise<MatchQueueStatus> {
    const response = await api.get('/matches/queue/status');
    return response.data;
  },

  async getGlobalLeaderboard(limit: number = 100, offset: number = 0, challengeType: string = 'dsa'): Promise<LeaderboardResponse> {
    const response = await api.get(`/leaderboard/global?limit=${limit}&offset=${offset}&challenge_type=${challengeType}`);
    return response.data;
  },

  async getMatch(matchId: string): Promise<MatchDetails> {
    const response = await api.get(`/matches/${matchId}`);
    return response.data;
  },

  async getPlayerMatches(limit: number = 50): Promise<PlayerMatchHistory> {
    const response = await api.get(`/matches/player/history?limit=${limit}`);
    return response.data;
  },

  async createPracticeMatch(difficulty: string = 'intermediate', challengeType: string = 'dsa', challengeId?: string): Promise<PracticeMatchResponse> {
    const params = new URLSearchParams({ difficulty, challenge_type: challengeType });
    if (challengeId) {
      params.append('challenge_id', challengeId);
    }
    const response = await api.post(`/matches/practice?${params.toString()}`);
    return response.data;
  },

  async markPlayerDone(matchId: string) {
    const response = await api.post(`/matches/${matchId}/done`);
    return response.data;
  }
};
