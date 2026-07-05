export interface CredentialStatus {
  gmail_connected: boolean;
  gmail_user_email: string | null;
  gmail_last_tested: string | null;
  gmail_test_status: string | null;
  dropbox_connected: boolean;
  dropbox_last_tested: string | null;
  dropbox_test_status: string | null;
}

export interface CredentialTestResult {
  service: string;
  status: 'success' | 'failed';
  error_message: string | null;
}
