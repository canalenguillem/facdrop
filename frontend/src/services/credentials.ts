import api from './api';
import type { CredentialStatus, CredentialTestResult } from '../types/credential';

export async function getStatus(): Promise<CredentialStatus> {
  const { data } = await api.get<CredentialStatus>('/users/me/credentials');
  return data;
}

export async function saveGmail(
  gmail_user_email: string,
  gmail_app_password: string,
): Promise<CredentialStatus> {
  const { data } = await api.put<CredentialStatus>('/users/me/credentials/gmail', {
    gmail_user_email,
    gmail_app_password,
  });
  return data;
}

export async function saveDropbox(dropbox_access_token: string): Promise<CredentialStatus> {
  const { data } = await api.put<CredentialStatus>('/users/me/credentials/dropbox', {
    dropbox_access_token,
  });
  return data;
}

export async function testGmail(): Promise<CredentialTestResult> {
  const { data } = await api.post<CredentialTestResult>('/users/me/credentials/test/gmail');
  return data;
}

export async function testDropbox(): Promise<CredentialTestResult> {
  const { data } = await api.post<CredentialTestResult>('/users/me/credentials/test/dropbox');
  return data;
}

export async function removeGmail(): Promise<CredentialStatus> {
  const { data } = await api.delete<CredentialStatus>('/users/me/credentials/gmail');
  return data;
}

export async function removeDropbox(): Promise<CredentialStatus> {
  const { data } = await api.delete<CredentialStatus>('/users/me/credentials/dropbox');
  return data;
}
