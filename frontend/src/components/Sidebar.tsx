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
  { to: '/help', label: 'Ayuda' },
];

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function Sidebar({ open, onClose }: Props) {
  const { user } = useAuth();

  const nav = (
    <nav className="flex-1 space-y-1 px-3">
      {ITEMS.filter((i) => !i.adminOnly || user?.is_admin).map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === '/'}
          onClick={onClose}
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
  );

  return (
    <>
      {/* Escritorio: barra fija */}
      <aside className="hidden w-52 shrink-0 flex-col bg-gray-900 py-4 text-gray-300 md:flex">
        {nav}
      </aside>

      {/* Móvil: cajón deslizante con fondo oscuro */}
      {open && (
        <div className="fixed inset-0 z-40 md:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={onClose} />
          <aside className="absolute inset-y-0 left-0 flex w-60 flex-col bg-gray-900 py-4 text-gray-300 shadow-xl">
            {nav}
          </aside>
        </div>
      )}
    </>
  );
}
