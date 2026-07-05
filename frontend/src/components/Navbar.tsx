import { useAuth } from '../hooks/useAuth';

export default function Navbar() {
  const { user, signout } = useAuth();

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <span className="text-lg font-bold text-blue-700">Fracdrop</span>
      <div className="flex items-center gap-4 text-sm">
        {user && (
          <span className="text-gray-600">
            {user.username}
            {user.is_admin && (
              <span className="ml-2 rounded bg-blue-100 px-2 py-0.5 text-xs text-blue-700">
                admin
              </span>
            )}
          </span>
        )}
        <button
          onClick={signout}
          className="rounded border border-gray-300 px-3 py-1 text-gray-700 hover:bg-gray-50"
        >
          Salir
        </button>
      </div>
    </header>
  );
}
