export interface EmailLog {
  id: number;
  gmail_message_id: string;
  from_email: string | null;
  subject: string | null;
  source_label: string | null;
  doc_type: string | null;
  status: string | null;
  rule_applied_id: number | null;
  dropbox_folder_id: number | null;
  dropbox_file_path: string | null;
  error_message: string | null;
  processed_at: string;
}

export interface ProcessResult {
  total: number;
  procesado: number;
  sin_regla: number;
  error: number;
  skipped: number;
}

export interface EmailStats {
  total: number;
  procesado: number;
  sin_regla: number;
  error: number;
}
