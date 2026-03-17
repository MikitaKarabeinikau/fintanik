import api from './api';

const authService = {
  /**
   * Login with password
   */
  login: async (password) => {
    const response = await api.post('/api/auth/login', { password });
    const { access_token } = response.data;
    
    // Store token in localStorage
    localStorage.setItem('token', access_token);
    
    return access_token;
  },

  /**
   * Logout - remove token
   */
  logout: () => {
    localStorage.removeItem('token');
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('token');
  },

  /**
   * Get current token
   */
  getToken: () => {
    return localStorage.getItem('token');
  },

  /**
   * Verify token is valid
   */
  verifyToken: async () => {
    try {
      const response = await api.get('/api/auth/verify');
      return response.data;
    } catch (error) {
      // Token is invalid or expired
      authService.logout();
      throw error;
    }
  }
};

export default authService;
