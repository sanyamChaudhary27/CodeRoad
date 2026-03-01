import api from '../lib/api';

export interface MatchQueueStatus {
  in_queue: boolean;
  queue_id?: string;
  joined_at?: string;
  wait_time_seconds?: number;
  estimated_wait_seconds?: number;
  match_found?: boolean;
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

export interface LeaderboardResponse {
  leaderboard: LeaderboardPlayer[];
  total_players: number;
  limit: number;
  offset: number;
}

export const matchmakingService = {
  async joinQueue(preferred_format: string = '1v1', min_rating?: number, max_rating?: number) {
    const response = await api.post('/matches/queue/join', {
      preferred_format,
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

  async getGlobalLeaderboard(limit: number = 100, offset: number = 0): Promise<LeaderboardResponse> {
    const response = await api.get(`/leaderboard/global?limit=${limit}&offset=${offset}`);
    return response.data;
  }
};
