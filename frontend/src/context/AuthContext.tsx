import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import apiClient, { setAccessToken } from '../api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, pass: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const login = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', pass);

      const res = await apiClient.post('/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const accessToken = res.data.access_token;
      setToken(accessToken);
      setAccessToken(accessToken);

      // Fetch user profile
      const meRes = await apiClient.get<User>('/auth/me');
      setUser(meRes.data);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    setAccessToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
};
