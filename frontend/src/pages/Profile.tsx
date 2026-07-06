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
  getDropboxAuthorizeUrl,
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

      {status.dropbox_oauth_available && (
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3 rounded-lg border border-blue-200 bg-blue-50 p-4">
          <div className="text-sm text-blue-900">
            <strong>Recomendado:</strong> conecta Dropbox de forma permanente (no caduca). No hace
            falta crear apps ni pegar tokens.
          </div>
          <button
            onClick={async () => {
              window.location.href = await getDropboxAuthorizeUrl();
            }}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700"
          >
            {status.dropbox_connected ? 'Reconectar Dropbox' : 'Conectar con Dropbox'}
          </button>
        </div>
      )}

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
          title="Dropbox (avanzado)"
          help="Lo normal es usar el botón «Conectar con Dropbox» de arriba. Esto es una alternativa avanzada: pega manualmente un Access Token de una app «Full Dropbox» (caduca y hay que renovarlo a mano)."
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
