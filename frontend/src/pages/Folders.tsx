import { useEffect, useState, type FormEvent } from 'react';
import api from '../services/api';
import DropboxFolderPicker from '../components/DropboxFolderPicker';
import type { Folder } from '../types/folder';

const DOC_TYPES = ['factura', 'albaran', 'otros'];

export default function Folders() {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [name, setName] = useState('');
  const [dropboxPath, setDropboxPath] = useState('');
  const [docType, setDocType] = useState('factura');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const load = async () => {
    const { data } = await api.get<Folder[]>('/folders');
    setFolders(data);
  };

  useEffect(() => {
    load();
  }, []);

  const create = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      await api.post('/folders', { name, dropbox_path: dropboxPath, doc_type: docType });
      setName('');
      setDropboxPath('');
      setDocType('factura');
      await load();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'No se pudo crear la carpeta');
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id: number) => {
    await api.delete(`/folders/${id}`);
    await load();
  };

  return (
    <div className="max-w-2xl">
      <h1 className="mb-1 text-2xl font-bold text-gray-800">Carpetas de Dropbox</h1>
      <p className="mb-6 text-sm text-gray-500">
        Define las rutas de Dropbox donde se guardarán los adjuntos.
      </p>

      <form onSubmit={create} className="mb-8 space-y-3 rounded-lg border border-gray-200 bg-white p-5">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Nombre</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="Facturas Enero 2026"
            className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Ruta en Dropbox</label>
          <DropboxFolderPicker value={dropboxPath} onChange={setDropboxPath} />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Tipo</label>
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          >
            {DOC_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        {error && <div className="rounded bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

        <button
          type="submit"
          disabled={saving || !dropboxPath}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? 'Creando…' : 'Crear carpeta'}
        </button>
      </form>

      <h2 className="mb-2 text-sm font-semibold text-gray-700">Carpetas ({folders.length})</h2>
      {folders.length === 0 ? (
        <p className="text-sm text-gray-400">Aún no hay carpetas.</p>
      ) : (
        <ul className="divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
          {folders.map((f) => (
            <li key={f.id} className="flex items-center justify-between px-4 py-3">
              <div>
                <div className="text-sm font-medium text-gray-800">{f.name}</div>
                <div className="text-xs text-gray-500">
                  <code>{f.dropbox_path}</code> · {f.doc_type}
                </div>
              </div>
              <button
                onClick={() => remove(f.id)}
                className="rounded border border-red-300 px-2 py-1 text-xs text-red-600 hover:bg-red-50"
              >
                Eliminar
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
