import api from '../lib/api';

export interface PublicStats {
  players: number;
  battles: number;
  challenges: number;
  active_battles: number;
}

export const publicStatsService = {
  async getStats(): Promise<PublicStats> {
    const response = await api.get('/stats');
    return response.data;
  },
};
