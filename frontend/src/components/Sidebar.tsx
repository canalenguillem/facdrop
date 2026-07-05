import { NavLink } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

interface Item {
  to: string;
  label: string;
  adminOnly?: boolean;
}

const ITEMS: Item[] = [
  { to: '/', label: 'Dashboard' },
  { to: '/labels', label: 'Etiquetas' },
  { to: '/folders', label: 'Carpetas' },
  { to: '/rules', label: 'Reglas' },
  { to: '/emails', label: 'Historial' },
  { to: '/profile', label: 'Perfil' },
  { to: '/users', label: 'Usuarios', adminOnly: true },
];

export default function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="w-52 bg-gray-900 text-gray-300 flex flex-col py-4">
      <nav className="flex-1 space-y-1 px-3">
        {ITEMS.filter((i) => !i.adminOnly || user?.is_admin).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `block rounded px-3 py-2 text-sm ${
                isActive ? 'bg-blue-600 text-white' : 'hover:bg-gray-800'
              }`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
