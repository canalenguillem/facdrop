import { useState } from 'react';
import type { CredentialTestResult } from '../types/credential';

interface Props {
  service: 'gmail' | 'dropbox';
  title: string;
  help: string;
  secretLabel: string;
  secretPlaceholder: string;
  connected: boolean;
  userEmail?: string | null;
  testStatus?: string | null;
  lastTested?: string | null;
  onSave: (values: { email?: string; secret: string }) => Promise<void>;
  onTest: () => Promise<CredentialTestResult>;
  onRemove: () => Promise<void>;
}

export default function CredentialInput({
  service,
  title,
  help,
  secretLabel,
  secretPlaceholder,
  connected,
  userEmail,
  testStatus,
  lastTested,
  onSave,
  onTest,
  onRemove,
}: Props) {
  const [email, setEmail] = useState(userEmail ?? '');
  const [secret, setSecret] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  const run = async (fn: () => Promise<void>) => {
    setBusy(true);
    setMsg(null);
    try {
      await fn();
    } catch (err: any) {
      setMsg({ ok: false, text: err.response?.data?.detail ?? 'Error' });
    } finally {
      setBusy(false);
    }
  };

  const handleSave = () =>
    run(async () => {
      if (service === 'gmail' && !email) throw { response: { data: { detail: 'Falta el email' } } };
      if (!secret) throw { response: { data: { detail: 'Falta la credencial' } } };
      await onSave({ email, secret });
      setSecret('');
      setMsg({ ok: true, text: 'Credencial guardada' });
    });

  const handleTest = () =>
    run(async () => {
      const res = await onTest();
      setMsg({
        ok: res.status === 'success',
        text: res.status === 'success' ? 'Conexión correcta ✅' : `Falló: ${res.error_message ?? ''}`,
      });
    });

  const handleRemove = () =>
    run(async () => {
      await onRemove();
      setEmail('');
      setSecret('');
      setMsg({ ok: true, text: 'Credencial eliminada' });
    });

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">{title}</h3>
        <span
          className={`rounded-full px-2 py-0.5 text-xs ${
            connected ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
          }`}
        >
          {connected ? 'Conectado' : 'No conectado'}
        </span>
      </div>

      <p className="mb-4 text-xs text-gray-500">{help}</p>

      {service === 'gmail' && (
        <>
          <label className="mb-1 block text-sm font-medium text-gray-700">Cuenta de Gmail</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="tucorreo@gmail.com"
            className="mb-3 w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
        </>
      )}

      <label className="mb-1 block text-sm font-medium text-gray-700">{secretLabel}</label>
      <input
        type="password"
        value={secret}
        onChange={(e) => setSecret(e.target.value)}
        placeholder={secretPlaceholder}
        className="mb-4 w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
      />

      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleSave}
          disabled={busy}
          className="rounded bg-blue-600 px-3 py-1.5 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          Guardar
        </button>
        <button
          onClick={handleTest}
          disabled={busy || !connected}
          className="rounded border border-gray-300 px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
        >
          Probar conexión
        </button>
        <button
          onClick={handleRemove}
          disabled={busy || !connected}
          className="rounded border border-red-300 px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 disabled:opacity-50"
        >
          Eliminar
        </button>
      </div>

      {msg && (
        <div className={`mt-3 text-sm ${msg.ok ? 'text-green-600' : 'text-red-600'}`}>
          {msg.text}
        </div>
      )}

      {connected && testStatus && (
        <div className="mt-2 text-xs text-gray-400">
          Última prueba: {testStatus}
          {lastTested ? ` (${new Date(lastTested).toLocaleString()})` : ''}
        </div>
      )}
    </div>
  );
}
