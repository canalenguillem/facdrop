export interface Folder {
  id: number;
  name: string;
  dropbox_path: string;
  doc_type: string;
  created_at: string;
}

export interface DropboxEntry {
  name: string;
  path: string;
}
