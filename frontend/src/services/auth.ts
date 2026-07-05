import api from './api';
import type { User } from '../types/user';

interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
}

function storeTokens(data: TokenResponse) {
  localStorage.setItem('access_token', data.access_token);
  if (data.refresh_token) {
    localStorage.setItem('refresh_token', data.refresh_token);
  }
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/auth/login', { email, password });
  storeTokens(data);
  return data;
}

export function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
}

export async function getMe(): Promise<User> {
  const { data } = await api.get<User>('/users/me');
  return data;
}

export interface InviteInfo {
  email: string;
  role: string;
  expires_at: string;
}

export async function validateInvite(token: string): Promise<InviteInfo> {
  const { data } = await api.get<InviteInfo>(`/auth/invite/${token}`);
  return data;
}

export async function register(payload: {
  token: string;
  username: string;
  password: string;
}): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>('/auth/register', payload);
  storeTokens(data);
  return data;
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token');
}
