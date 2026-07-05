import CredentialInput from '../components/CredentialInput';
import { useCredentials } from '../hooks/useCredentials';
import { useAuth } from '../hooks/useAuth';
import {
  saveGmail,
  saveDropbox,
  testGmail,
  testDropbox,
  removeGmail,
  removeDropbox,
} from '../services/credentials';

export default function Profile() {
  const { status, loading, refresh } = useCredentials();
  const { user, refresh: refreshUser } = useAuth();

  // Tras cualquier cambio, refrescamos estado de credenciales y usuario (badges).
  const after = async () => {
    await refresh();
    await refreshUser();
  };

  if (loading || !status) {
    return <div className="text-gray-500">Cargando…</div>;
  }

  return (
    <div className="max-w-3xl">
      <h1 className="mb-1 text-2xl font-bold text-gray-800">Perfil</h1>
      <p className="mb-6 text-sm text-gray-500">
        {user?.username} · {user?.email}
      </p>

      <h2 className="mb-3 text-lg font-semibold text-gray-700">Credenciales de servicio</h2>
      <p className="mb-4 text-sm text-gray-500">
        Se guardan encriptadas; la app nunca las muestra en claro, solo el estado de conexión.
      </p>

      <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
        <CredentialInput
          service="gmail"
          title="Gmail"
          help="Contraseña de aplicación de Google (16 caracteres). Requiere verificación en dos pasos activada."
          secretLabel="Gmail App Password"
          secretPlaceholder="abcd efgh ijkl mnop"
          connected={status.gmail_connected}
          userEmail={status.gmail_user_email}
          testStatus={status.gmail_test_status}
          lastTested={status.gmail_last_tested}
          onSave={async ({ email, secret }) => {
            await saveGmail(email ?? '', secret);
            await after();
          }}
          onTest={async () => {
            const r = await testGmail();
            await after();
            return r;
          }}
          onRemove={async () => {
            await removeGmail();
            await after();
          }}
        />

        <CredentialInput
          service="dropbox"
          title="Dropbox"
          help="Access Token de una app de Dropbox con permisos files.content.write y files.content.read."
          secretLabel="Dropbox Access Token"
          secretPlaceholder="sl.xxxxxxxx…"
          connected={status.dropbox_connected}
          testStatus={status.dropbox_test_status}
          lastTested={status.dropbox_last_tested}
          onSave={async ({ secret }) => {
            await saveDropbox(secret);
            await after();
          }}
          onTest={async () => {
            const r = await testDropbox();
            await after();
            return r;
          }}
          onRemove={async () => {
            await removeDropbox();
            await after();
          }}
        />
      </div>
    </div>
  );
}
