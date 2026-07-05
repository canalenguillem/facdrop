import type { EmailLog } from '../types/email';

interface Props {
  emails: EmailLog[];
  onReprocess: (id: number) => void;
}

function StatusBadge({ status }: { status: string | null }) {
  const map: Record<string, string> = {
    procesado: 'bg-green-100 text-green-700',
    sin_regla: 'bg-gray-100 text-gray-600',
    error: 'bg-red-100 text-red-700',
  };
  const cls = (status && map[status]) || 'bg-gray-100 text-gray-600';
  return <span className={`rounded px-2 py-0.5 text-xs ${cls}`}>{status ?? '—'}</span>;
}

export default function EmailTable({ emails, onReprocess }: Props) {
  if (emails.length === 0) {
    return <p className="text-sm text-gray-400">Aún no hay correos procesados.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-gray-200 bg-gray-50 text-xs uppercase text-gray-500">
          <tr>
            <th className="px-4 py-2">Estado</th>
            <th className="px-4 py-2">Remitente</th>
            <th className="px-4 py-2">Asunto</th>
            <th className="px-4 py-2">Etiqueta</th>
            <th className="px-4 py-2">Destino Dropbox</th>
            <th className="px-4 py-2">Fecha</th>
            <th className="px-4 py-2"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {emails.map((e) => (
            <tr key={e.id} className="align-top">
              <td className="px-4 py-2">
                <StatusBadge status={e.status} />
                {e.status === 'error' && e.error_message && (
                  <div className="mt-1 max-w-[16rem] text-xs text-red-500">{e.error_message}</div>
                )}
              </td>
              <td className="px-4 py-2 text-gray-700">{e.from_email ?? '—'}</td>
              <td className="px-4 py-2 text-gray-700">{e.subject ?? '—'}</td>
              <td className="px-4 py-2 text-gray-500">{e.source_label ?? '—'}</td>
              <td className="px-4 py-2 text-gray-500">
                {e.dropbox_file_path ? <code className="text-xs">{e.dropbox_file_path}</code> : '—'}
              </td>
              <td className="px-4 py-2 text-xs text-gray-400">
                {new Date(e.processed_at).toLocaleString()}
              </td>
              <td className="px-4 py-2">
                <button
                  onClick={() => onReprocess(e.id)}
                  className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50"
                >
                  Reprocesar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
