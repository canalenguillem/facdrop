/**
 * App raíz — FASE 1: solo un placeholder para verificar que el frontend arranca.
 * En la Fase 8 se añadirá el router (Login, Register, Dashboard, Labels, Rules,
 * Folders, EmailLogs, Profile, Users, Settings).
 */
function App() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 text-gray-800">
      <h1 className="text-3xl font-bold">Fracdrop</h1>
      <p className="mt-2 text-gray-500">
        Esqueleto Fase 1 — el frontend arranca correctamente.
      </p>
      <p className="mt-1 text-sm text-gray-400">
        API: {import.meta.env.VITE_API_URL ?? 'no configurada'}
      </p>
    </div>
  );
}

export default App;
