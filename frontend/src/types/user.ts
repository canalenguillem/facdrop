export interface User {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  is_admin: boolean;
  role: string;
  gmail_connected: boolean;
  dropbox_connected: boolean;
  created_at: string;
}

export interface Invitation {
  id: number;
  email: string;
  role: string;
  status: string;
  expires_at: string;
  accepted_at: string | null;
  created_at: string;
  invite_link: string | null;
  email_sent: boolean | null;
}
