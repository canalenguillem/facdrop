import { useAuth } from '../hooks/useAuth';

export default function Dashboard() {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold text-gray-800">Dashboard</h1>
      <p className="mb-6 text-gray-600">
        Bienvenido, <strong>{user?.username}</strong>.
      </p>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="text-sm text-gray-500">Gmail</div>
          <div
            className={
              user?.gmail_connected ? 'font-semibold text-green-600' : 'font-semibold text-gray-400'
            }
          >
            {user?.gmail_connected ? 'Conectado' : 'No conectado'}
          </div>
        </div>
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="text-sm text-gray-500">Dropbox</div>
          <div
            className={
              user?.dropbox_connected
                ? 'font-semibold text-green-600'
                : 'font-semibold text-gray-400'
            }
          >
            {user?.dropbox_connected ? 'Conectado' : 'No conectado'}
          </div>
        </div>
      </div>

      <p className="mt-6 text-sm text-gray-400">
        Configura tus credenciales en <strong>Perfil</strong>, elige las etiquetas a vigilar y
        crea reglas para enviar los adjuntos a Dropbox.
      </p>
    </div>
  );
}
