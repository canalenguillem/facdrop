import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { connectDropbox } from '../services/credentials';

export default function DropboxCallback() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState('');

  useEffect(() => {
    const code = params.get('code');
    const err = params.get('error');
    if (err) {
      setError(`Dropbox devolvió: ${err}`);
      return;
    }
    if (!code) {
      setError('No se recibió el código de autorización.');
      return;
    }
    connectDropbox(code)
      .then(() => navigate('/profile'))
      .catch((e: any) => setError(e.response?.data?.detail ?? 'No se pudo conectar con Dropbox'));
  }, [params, navigate]);

  return (
    <div className="flex h-screen items-center justify-center bg-gray-100">
      <div className="w-full max-w-sm rounded-lg bg-white p-8 text-center shadow">
        {error ? (
          <>
            <p className="mb-4 text-sm text-red-700">{error}</p>
            <button
              onClick={() => navigate('/profile')}
              className="rounded border border-gray-300 px-4 py-2 text-sm"
            >
              Volver al perfil
            </button>
          </>
        ) : (
          <p className="text-sm text-gray-500">Conectando con Dropbox…</p>
        )}
      </div>
    </div>
  );
}
