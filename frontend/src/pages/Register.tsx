import { useEffect, useState, type FormEvent } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { validateInvite, register, type InviteInfo } from '../services/auth';
import { useAuth } from '../hooks/useAuth';

export default function Register() {
  const [params] = useSearchParams();
  const token = params.get('token') ?? '';
  const navigate = useNavigate();
  const { refresh } = useAuth();

  const [invite, setInvite] = useState<InviteInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [invalid, setInvalid] = useState('');

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!token) {
      setInvalid('Falta el token de invitación.');
      setLoading(false);
      return;
    }
    validateInvite(token)
      .then(setInvite)
      .catch((err) => setInvalid(err.response?.data?.detail ?? 'Invitación inválida o caducada.'))
      .finally(() => setLoading(false));
  }, [token]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setSaving(true);
    try {
      await register({ token, username, password });
      await refresh();
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'No se pudo completar el registro');
    } finally {
      setSaving(false);
    }
  };

  const field = 'mb-4 w-full rounded border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="w-full max-w-sm rounded-lg bg-white p-8 shadow">
        <h1 className="mb-1 text-2xl font-bold text-blue-700">Fracdrop</h1>
        <p className="mb-6 text-sm text-gray-500">Crea tu cuenta</p>

        {loading && <p className="text-sm text-gray-400">Validando invitación…</p>}

        {!loading && invalid && (
          <div className="rounded bg-red-50 px-3 py-2 text-sm text-red-700">{invalid}</div>
        )}

        {!loading && invite && (
          <form onSubmit={submit}>
            {error && (
              <div className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
            )}

            <label className="mb-1 block text-sm font-medium text-gray-700">Email (fijado)</label>
            <input value={invite.email} disabled className={`${field} bg-gray-50 text-gray-500`} />

            <label className="mb-1 block text-sm font-medium text-gray-700">Usuario</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              className={field}
              placeholder="tu_usuario"
            />

            <label className="mb-1 block text-sm font-medium text-gray-700">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className={field}
              placeholder="mínimo 8 caracteres"
            />

            <button
              type="submit"
              disabled={saving}
              className="w-full rounded bg-blue-600 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? 'Creando…' : 'Crear cuenta'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
