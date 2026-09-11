import axios from 'axios';

/**
 * SECURITY ARCHITECTURE NOTE ON TOKEN STORAGE:
 * JWT Access Tokens are kept IN-MEMORY in the AuthContext React state rather than
 * localStorage.
 * 
 * TRADEOFF ANALYSIS:
 * 1. Storing JWT in localStorage makes tokens vulnerable to Cross-Site Scripting (XSS)
 *    exfiltration scripts.
 * 2. In-Memory storage protects against XSS token theft, ensuring sensitive fraud
 *    investigation capabilities cannot be hijacked by malicious browser scripts.
 * 3. The trade-off is that refreshing the browser tab requires re-fetching an access token
 *    via the /auth/refresh endpoint (or stored refresh cookie/token), providing a much
 *    higher security posture suitable for bank-grade intelligence tools.
 */

let inMemoryToken: string | null = null;

export const setAccessToken = (token: string | null) => {
  inMemoryToken = token;
};

export const getAccessToken = () => inMemoryToken;

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  if (inMemoryToken) {
    config.headers.Authorization = `Bearer ${inMemoryToken}`;
  }
  return config;
});

export default apiClient;
