import api from '../lib/api';

export interface User {
  id: string;
  username: string;
  email: string;
  current_rating: number;
  matches_played?: number;
  wins?: number;
  losses?: number;
  created_at?: string;
  profile_picture?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  player: User;
}

export const authService = {
  async register(data: any): Promise<AuthResponse> {
    const response = await api.post('/auth/register', data);
    this.setSession(response.data);
    return response.data;
  },

  async login(data: any): Promise<AuthResponse> {
    const response = await api.post('/auth/login', data);
    this.setSession(response.data);
    return response.data;
  },

  async getCurrentUser(): Promise<User> {
    const response = await api.get('/auth/me');
    // Update local storage user profile with latest data
    localStorage.setItem('user', JSON.stringify(response.data));
    return response.data;
  },

  async updateProfilePicture(profilePicture: string): Promise<any> {
    const response = await api.put('/auth/profile-picture', { profile_picture: profilePicture });
    // Refresh user data
    await this.getCurrentUser();
    return response.data;
  },

  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  setSession(authData: AuthResponse) {
    localStorage.setItem('token', authData.access_token);
    localStorage.setItem('user', JSON.stringify(authData.player));
  },
  
  isAuthenticated(): boolean {
    return !!localStorage.getItem('token');
  },
  
  getUser(): User | null {
    const storedUser = localStorage.getItem('user');
    return storedUser ? JSON.parse(storedUser) : null;
  }
};
