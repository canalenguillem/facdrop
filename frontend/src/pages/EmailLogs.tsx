import { useEffect, useState } from 'react';
import api from '../services/api';
import EmailTable from '../components/EmailTable';
import type { EmailLog, EmailStats, ProcessResult } from '../types/email';

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 text-center">
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
      <div className="text-xs text-gray-500">{label}</div>
    </div>
  );
}

export default function EmailLogs() {
  const [emails, setEmails] = useState<EmailLog[]>([]);
  const [stats, setStats] = useState<EmailStats | null>(null);
  const [processing, setProcessing] = useState(false);
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [error, setError] = useState('');

  const load = async () => {
    const [e, s] = await Promise.all([
      api.get<EmailLog[]>('/emails'),
      api.get<EmailStats>('/emails/stats'),
    ]);
    setEmails(e.data);
    setStats(s.data);
  };

  useEffect(() => {
    load();
  }, []);

  const process = async () => {
    setProcessing(true);
    setError('');
    setResult(null);
    try {
      const { data } = await api.post<ProcessResult>('/emails/process');
      setResult(data);
      await load();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'No se pudo procesar');
    } finally {
      setProcessing(false);
    }
  };

  const reprocess = async (id: number) => {
    await api.post(`/emails/${id}/reprocess`);
    await load();
  };

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Historial de correos</h1>
          <p className="text-sm text-gray-500">
            Correos evaluados: procesados, sin regla o con error.
          </p>
        </div>
        <button
          onClick={process}
          disabled={processing}
          className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {processing ? 'Procesando…' : '⚙️ Procesar ahora'}
        </button>
      </div>

      {result && (
        <div className="mb-4 rounded bg-blue-50 px-3 py-2 text-sm text-blue-800">
          Pasada: {result.procesado} procesados, {result.sin_regla} sin regla, {result.error} con
          error, {result.skipped} ya procesados (de {result.total} vistos).
        </div>
      )}
      {error && (
        <div className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}

      {stats && (
        <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatCard label="Total" value={stats.total} color="text-gray-800" />
          <StatCard label="Procesados" value={stats.procesado} color="text-green-600" />
          <StatCard label="Sin regla" value={stats.sin_regla} color="text-gray-500" />
          <StatCard label="Error" value={stats.error} color="text-red-600" />
        </div>
      )}

      <EmailTable emails={emails} onReprocess={reprocess} />
    </div>
  );
}
