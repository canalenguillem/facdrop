export interface Folder {
  id: number;
  name: string;
  dropbox_path: string;
  doc_type: string;
  organize_by_date: boolean;
  created_at: string;
}

export interface DropboxEntry {
  name: string;
  path: string;
}
