import { useEffect, useState, type FormEvent } from 'react';
import api from '../services/api';
import { useAuth } from '../hooks/useAuth';
import type { User, Invitation } from '../types/user';

export default function Users() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('user');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [copied, setCopied] = useState<number | null>(null);

  const load = async () => {
    const [u, i] = await Promise.all([
      api.get<User[]>('/users'),
      api.get<Invitation[]>('/invitations'),
    ]);
    setUsers(u.data);
    setInvitations(i.data);
  };

  useEffect(() => {
    load();
  }, []);

  const noticeFor = (inv: Invitation) =>
    inv.email_sent
      ? `Invitación enviada por email a ${inv.email}.`
      : `Invitación creada, pero no se pudo enviar el email (revisa la config SMTP del servidor). Mientras tanto, usa «Copiar enlace».`;

  const invite = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setNotice('');
    try {
      const { data } = await api.post<Invitation>('/invitations', { email, role });
      setEmail('');
      setRole('user');
      setNotice(noticeFor(data));
      await load();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'No se pudo crear la invitación');
    }
  };

  const revoke = async (id: number) => {
    await api.delete(`/invitations/${id}`);
    await load();
  };
  const resend = async (id: number) => {
    setNotice('');
    const { data } = await api.post<Invitation>(`/invitations/${id}/resend`);
    setNotice(noticeFor(data));
    await load();
  };
  const copy = (inv: Invitation) => {
    if (inv.invite_link) {
      navigator.clipboard.writeText(inv.invite_link);
      setCopied(inv.id);
      setTimeout(() => setCopied(null), 1500);
    }
  };

  const toggleActive = async (u: User) => {
    await api.put(`/users/${u.id}`, { is_active: !u.is_active });
    await load();
  };
  const changeRole = async (u: User, newRole: string) => {
    await api.put(`/users/${u.id}`, { role: newRole });
    await load();
  };
  const removeUser = async (id: number) => {
    setError('');
    try {
      await api.delete(`/users/${id}`);
      await load();
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'No se pudo eliminar');
    }
  };

  return (
    <div className="max-w-4xl">
      <h1 className="mb-4 text-2xl font-bold text-gray-800">Usuarios e invitaciones</h1>

      {error && <div className="mb-4 rounded bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}
      {notice && <div className="mb-4 rounded bg-blue-50 px-3 py-2 text-sm text-blue-800">{notice}</div>}

      {/* Invitar */}
      <form onSubmit={invite} className="mb-6 flex flex-wrap items-end gap-3 rounded-lg border border-gray-200 bg-white p-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Invitar por email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            placeholder="persona@empresa.com"
            className="rounded border border-gray-300 px-3 py-2 text-sm"
          />
        </div>
        <select value={role} onChange={(e) => setRole(e.target.value)} className="rounded border border-gray-300 px-3 py-2 text-sm">
          <option value="user">user</option>
          <option value="admin">admin</option>
        </select>
        <button type="submit" className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">
          Invitar
        </button>
      </form>

      {/* Invitaciones */}
      <h2 className="mb-2 text-sm font-semibold text-gray-700">Invitaciones ({invitations.length})</h2>
      {invitations.length === 0 ? (
        <p className="mb-6 text-sm text-gray-400">No hay invitaciones.</p>
      ) : (
        <ul className="mb-8 divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
          {invitations.map((inv) => (
            <li key={inv.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
              <div className="text-sm">
                <span className="text-gray-800">{inv.email}</span>
                <span className="ml-2 rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{inv.role}</span>
                <span
                  className={`ml-2 rounded px-2 py-0.5 text-xs ${
                    inv.status === 'pending'
                      ? 'bg-yellow-100 text-yellow-700'
                      : inv.status === 'accepted'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {inv.status}
                </span>
              </div>
              {inv.status === 'pending' && (
                <div className="flex gap-2">
                  {inv.invite_link && (
                    <button onClick={() => copy(inv)} className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50">
                      {copied === inv.id ? '¡Copiado!' : 'Copiar enlace'}
                    </button>
                  )}
                  <button onClick={() => resend(inv.id)} className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50">
                    Reenviar
                  </button>
                  <button onClick={() => revoke(inv.id)} className="rounded border border-red-300 px-2 py-1 text-xs text-red-600 hover:bg-red-50">
                    Revocar
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}

      {/* Usuarios */}
      <h2 className="mb-2 text-sm font-semibold text-gray-700">Usuarios ({users.length})</h2>
      <ul className="divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
        {users.map((u) => (
          <li key={u.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3">
            <div className="text-sm">
              <span className="font-medium text-gray-800">{u.username}</span>
              <span className="ml-2 text-gray-500">{u.email}</span>
              {!u.is_active && (
                <span className="ml-2 rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">inactivo</span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <select
                value={u.role}
                onChange={(e) => changeRole(u, e.target.value)}
                disabled={u.id === me?.id}
                className="rounded border border-gray-300 px-2 py-1 text-xs disabled:opacity-50"
              >
                <option value="user">user</option>
                <option value="admin">admin</option>
              </select>
              <button
                onClick={() => toggleActive(u)}
                disabled={u.id === me?.id}
                className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50 disabled:opacity-50"
              >
                {u.is_active ? 'Desactivar' : 'Activar'}
              </button>
              <button
                onClick={() => removeUser(u.id)}
                disabled={u.id === me?.id}
                className="rounded border border-red-300 px-2 py-1 text-xs text-red-600 hover:bg-red-50 disabled:opacity-50"
              >
                Eliminar
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
