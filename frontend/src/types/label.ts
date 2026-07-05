export interface GmailLabelAvailable {
  gmail_label_id: string;
  gmail_label_name: string;
}

export interface WatchedLabel {
  id: number;
  gmail_label_id: string;
  gmail_label_name: string;
  is_active: boolean;
  created_at: string;
}
