import { useState } from 'react';
import LabelSelector from '../components/LabelSelector';
import { useLabels } from '../hooks/useLabels';
import type { GmailLabelAvailable, WatchedLabel } from '../types/label';

export default function Labels() {
  const { watched, available, syncing, sync, watch, unwatch, toggle } = useLabels();
  const [error, setError] = useState('');

  const doSync = async () => {
    setError('');
    try {
      await sync();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'No se pudieron traer las etiquetas de Gmail');
    }
  };

  const handleUnwatch = async (id: number) => {
    setError('');
    try {
      await unwatch(id);
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'No se pudo quitar la etiqueta');
    }
  };

  const onToggleAvailable = async (label: GmailLabelAvailable, isWatched: boolean) => {
    const existing = watched.find((w) => w.gmail_label_id === label.gmail_label_id);
    if (isWatched && existing) {
      await handleUnwatch(existing.id);
    } else {
      await watch(label);
    }
  };

  return (
    <div className="max-w-2xl">
      <h1 className="mb-1 text-2xl font-bold text-gray-800">Etiquetas de Gmail a vigilar</h1>
      <p className="mb-4 text-sm text-gray-500">
        La app solo lee de las etiquetas que marques aquí. Nunca mueve ni borra correos.
      </p>

      <button
        onClick={doSync}
        disabled={syncing}
        className="mb-4 rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {syncing ? 'Sincronizando…' : '🔄 Sincronizar etiquetas'}
      </button>

      {error && (
        <div className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      <h2 className="mb-2 text-sm font-semibold text-gray-700">Todas tus etiquetas</h2>
      <LabelSelector available={available} watched={watched} onToggle={onToggleAvailable} />

      <h2 className="mb-2 mt-6 text-sm font-semibold text-gray-700">
        Vigiladas ({watched.length})
      </h2>
      {watched.length === 0 ? (
        <p className="text-sm text-gray-400">Aún no vigilas ninguna etiqueta.</p>
      ) : (
        <ul className="divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
          {watched.map((w: WatchedLabel) => (
            <li key={w.id} className="flex items-center justify-between px-4 py-2">
              <span className="text-sm text-gray-700">
                {w.gmail_label_name}
                {!w.is_active && (
                  <span className="ml-2 rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                    pausada
                  </span>
                )}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => toggle(w.id)}
                  className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50"
                >
                  {w.is_active ? 'Pausar' : 'Activar'}
                </button>
                <button
                  onClick={() => handleUnwatch(w.id)}
                  className="rounded border border-red-300 px-2 py-1 text-xs text-red-600 hover:bg-red-50"
                >
                  Quitar
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
