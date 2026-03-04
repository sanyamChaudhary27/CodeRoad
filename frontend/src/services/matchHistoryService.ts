import api from '../lib/api';

export interface MatchPlayer {
  player_id: string;
  username: string;
  current_rating: number;
  submissions_count: number;
  is_done: boolean;
}

export interface Match {
  match_id: string;
  status: string;
  format: string;
  player1: MatchPlayer;
  player2: MatchPlayer | null;
  challenge_id: string;
  challenge_title: string | null;
  challenge_description: string | null;
  difficulty_level: string | null;
  time_limit_seconds: number;
  time_remaining: number;
  created_at: string;
  started_at: string | null;
  concluded_at: string | null;
  winner_id: string | null;
  player1_score: number | null;
  player2_score: number | null;
  result: string | null;
}

export interface MatchHistoryResponse {
  matches: Match[];
  total_count: number;
}

class MatchHistoryService {
  async getMatchHistory(limit: number = 50): Promise<MatchHistoryResponse> {
    const response = await api.get(`/matches/player/history?limit=${limit}`);
    return response.data;
  }

  async getMatchDetails(matchId: string): Promise<Match> {
    const response = await api.get(`/matches/${matchId}`);
    return response.data;
  }

  async getChallengeDetails(challengeId: string) {
    const response = await api.get(`/challenges/${challengeId}`);
    return response.data;
  }

  getMatchResult(match: Match, currentUserId: string): 'win' | 'loss' | 'draw' | 'ongoing' {
    if (match.status !== 'concluded') return 'ongoing';
    if (!match.winner_id) return 'draw';
    return match.winner_id === currentUserId ? 'win' : 'loss';
  }

  getOpponent(match: Match, currentUserId: string): MatchPlayer | null {
    if (!match.player2) return null;
    return match.player1.player_id === currentUserId ? match.player2 : match.player1;
  }

  getPlayerScore(match: Match, currentUserId: string): number | null {
    if (match.player1.player_id === currentUserId) return match.player1_score;
    return match.player2_score;
  }
}

export const matchHistoryService = new MatchHistoryService();
