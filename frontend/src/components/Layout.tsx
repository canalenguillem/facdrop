import { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

export default function Layout() {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex h-screen flex-col">
      <Navbar onMenu={() => setOpen(true)} />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar open={open} onClose={() => setOpen(false)} />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
