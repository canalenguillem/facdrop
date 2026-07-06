import { useAuth } from '../hooks/useAuth';

export default function Navbar({ onMenu }: { onMenu: () => void }) {
  const { user, signout } = useAuth();

  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-4 md:px-6">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenu}
          aria-label="Abrir menú"
          className="rounded p-1 text-gray-600 hover:bg-gray-100 md:hidden"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <span className="text-lg font-bold text-blue-700">Fracdrop</span>
      </div>
      <div className="flex items-center gap-3 text-sm">
        {user && (
          <span className="hidden text-gray-600 sm:inline">
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
