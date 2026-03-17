import { useState, useEffect } from 'react';
import authService from '../services/authService';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(
    authService.isAuthenticated()
  );
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verify token on mount
    const verifyAuth = async () => {
      if (authService.isAuthenticated()) {
        try {
          await authService.verifyToken();
          setIsAuthenticated(true);
        } catch (error) {
          setIsAuthenticated(false);
        }
      }
      setIsLoading(false);
    };

    verifyAuth();
  }, []);

  const login = async (password) => {
    await authService.login(password);
    setIsAuthenticated(true);
  };

  const logout = () => {
    authService.logout();
    setIsAuthenticated(false);
  };

  return {
    isAuthenticated,
    isLoading,
    login,
    logout
  };
};
