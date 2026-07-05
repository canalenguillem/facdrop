export interface Rule {
  id: number;
  name: string;
  doc_type: string;
  source_label_id: number;
  dropbox_folder_id: number;
  from_email: string | null;
  subject_contains: string | null;
  has_attachment: boolean;
  is_active: boolean;
  priority: number;
  created_at: string;
}

export interface RuleInput {
  name: string;
  doc_type: string;
  source_label_id: number;
  dropbox_folder_id: number;
  from_email?: string | null;
  subject_contains?: string | null;
  has_attachment: boolean;
  is_active: boolean;
  priority: number;
}

export interface RuleTestResult {
  matched: boolean;
  rule_id: number | null;
  rule_name: string | null;
}
