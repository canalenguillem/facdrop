import { useState } from 'react';
import api from '../services/api';
import type { DropboxEntry } from '../types/folder';

interface Props {
  value: string;
  onChange: (path: string) => void;
}

export default function DropboxFolderPicker({ value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const [path, setPath] = useState('');
  const [entries, setEntries] = useState<DropboxEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const load = async (p: string) => {
    setLoading(true);
    setError('');
    try {
      const { data } = await api.get<DropboxEntry[]>('/folders/dropbox/browse', {
        params: { path: p },
      });
      setEntries(data);
      setPath(p);
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'No se pudo leer Dropbox');
    } finally {
      setLoading(false);
    }
  };

  const openBrowser = () => {
    setOpen(true);
    load('');
  };

  const goUp = () => {
    const parent = path.split('/').slice(0, -1).join('/');
    load(parent);
  };

  const useCurrent = () => {
    onChange(path === '' ? '/' : path);
    setOpen(false);
  };

  return (
    <div>
      <div className="flex gap-2">
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="/Empresa/Facturas/Enero2026"
          className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        <button
          type="button"
          onClick={openBrowser}
          className="rounded border border-gray-300 px-3 py-2 text-sm text-gray-700 hover:bg-gray-50"
        >
          Explorar
        </button>
      </div>

      {open && (
        <div className="mt-2 rounded-lg border border-gray-200 bg-white p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-xs text-gray-500">
              Ruta actual: <code>{path === '' ? '/' : path}</code>
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={goUp}
                disabled={path === ''}
                className="rounded border border-gray-300 px-2 py-1 text-xs disabled:opacity-40"
              >
                ↑ Subir
              </button>
              <button
                type="button"
                onClick={useCurrent}
                className="rounded bg-blue-600 px-2 py-1 text-xs text-white hover:bg-blue-700"
              >
                Usar esta carpeta
              </button>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded border border-gray-300 px-2 py-1 text-xs"
              >
                Cerrar
              </button>
            </div>
          </div>

          {error && <div className="text-xs text-red-600">{error}</div>}
          {loading ? (
            <div className="text-xs text-gray-400">Cargando…</div>
          ) : (
            <ul className="max-h-48 overflow-y-auto text-sm">
              {entries.length === 0 && !error && (
                <li className="px-2 py-1 text-xs text-gray-400">(sin subcarpetas)</li>
              )}
              {entries.map((e) => (
                <li key={e.path}>
                  <button
                    type="button"
                    onClick={() => load(e.path)}
                    className="w-full rounded px-2 py-1 text-left hover:bg-gray-50"
                  >
                    📁 {e.name}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
