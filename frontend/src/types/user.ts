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
