import type { ReactNode } from 'react';

function Section({ n, title, children }: { n: number; title: string; children: ReactNode }) {
  return (
    <section className="mb-8">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-gray-800">
        <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-600 text-sm text-white">
          {n}
        </span>
        {title}
      </h2>
      <div className="ml-9 space-y-2 text-sm text-gray-700">{children}</div>
    </section>
  );
}

function Ext({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="font-medium text-blue-600 underline hover:text-blue-800"
    >
      {children}
    </a>
  );
}

export default function Help() {
  return (
    <div className="max-w-3xl">
      <h1 className="mb-1 text-2xl font-bold text-gray-800">Ayuda · Primeros pasos</h1>
      <p className="mb-6 text-sm text-gray-500">
        Fracdrop guarda en Dropbox los adjuntos (facturas, albaranes…) de los correos de Gmail que
        tú elijas. Se configura una vez y luego funciona solo.
      </p>

      <div className="mb-8 rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
        <span className="font-semibold text-gray-800">En resumen:</span> organizas tus correos en
        Gmail con etiquetas → conectas Gmail y Dropbox → eliges carpetas y reglas → la app sube los
        documentos a Dropbox.
      </div>

      <Section n={1} title="En Gmail: organiza tus correos con filtros y etiquetas">
        <p>
          Fracdrop <strong>no crea ni mueve nada en Gmail</strong>: solo lee de las etiquetas que le
          indiques. Por eso, primero organiza tú tus correos en Gmail con <strong>filtros</strong>.
        </p>
        <p>
          Crea <strong>tantos filtros como grupos de mensajes</strong> quieras clasificar, y que
          cada filtro <strong>aplique una etiqueta</strong> (ej. facturas de un proveedor →
          «Facturas»; albaranes → «Albaranes»).
        </p>
        <p className="font-medium text-gray-800">Cómo crear un filtro en Gmail:</p>
        <ol className="list-decimal space-y-1 pl-5">
          <li>En Gmail, ⚙️ → <strong>Ver todos los ajustes</strong> → <strong>Filtros y direcciones bloqueadas</strong>.</li>
          <li>Pulsa <strong>Crear un filtro nuevo</strong>.</li>
          <li>Define el criterio (ej. <em>De: proveedor@ejemplo.com</em>) → <strong>Crear filtro</strong>.</li>
          <li>Marca <strong>Aplicar la etiqueta</strong> y elige o crea una etiqueta.</li>
          <li>Repite con cada grupo de mensajes que quieras separar.</li>
        </ol>
      </Section>

      <Section n={2} title="Crea tu cuenta">
        <p>
          Abre el enlace de invitación que has recibido. Tu email ya viene fijado; elige usuario y
          contraseña, y pulsa <strong>Crear cuenta</strong>.
        </p>
      </Section>

      <Section n={3} title="Conecta tu Gmail">
        <p>La app necesita una <strong>Contraseña de aplicación</strong> de Google (no tu contraseña normal):</p>
        <ol className="list-decimal space-y-1 pl-5">
          <li>Activa la <strong>Verificación en dos pasos</strong> en <Ext href="https://myaccount.google.com/security">myaccount.google.com/security</Ext> (si aún no la tienes). Es imprescindible.</li>
          <li>Ve a <Ext href="https://myaccount.google.com/apppasswords">myaccount.google.com/apppasswords</Ext> y crea una contraseña para «Correo». Copia las 16 letras.</li>
          <li>En <strong>Perfil → Gmail</strong>: pon tu dirección y pega la contraseña → <strong>Guardar</strong> → <strong>Probar conexión</strong> (debe salir ✅).</li>
        </ol>
      </Section>

      <Section n={4} title="Conecta tu Dropbox">
        <p className="text-gray-500">
          ¿No tienes cuenta de Dropbox? Créala aquí:{' '}
          <Ext href="https://www.dropbox.com/referrals/AAC-HbKpvUuTNv4Nkqtcmlu5cTnlY5e2LFM?src=global9">
            crear cuenta de Dropbox
          </Ext>
          .
        </p>
        <p>Una vez la tengas, es solo un botón:</p>
        <ol className="list-decimal space-y-1 pl-5">
          <li>Ve a <strong>Perfil</strong>.</li>
          <li>Pulsa <strong>Conectar con Dropbox</strong>.</li>
          <li>En la ventana de Dropbox, pulsa <strong>Permitir</strong> para autorizar.</li>
          <li>Volverás a la app con Dropbox <strong>conectado</strong>.</li>
        </ol>
        <p className="text-gray-500">
          La conexión es <strong>permanente</strong>: no caduca y no tendrás que volver a hacer nada.
        </p>
      </Section>

      <Section n={5} title="Elige qué etiquetas vigilar">
        <p>
          En <strong>Etiquetas</strong>, pulsa <strong>🔄 Sincronizar</strong> y marca las etiquetas
          de Gmail que quieres que la app revise (las que creaste con los filtros del paso 1).
        </p>
      </Section>

      <Section n={6} title="Define tus carpetas de Dropbox">
        <p>
          En <strong>Carpetas</strong>, dale un nombre y usa <strong>Explorar</strong> para elegir
          una carpeta de Dropbox que ya tengas (o escribe una ruta nueva). Opcional: marca{' '}
          <strong>Organizar por fecha</strong> para guardar en subcarpetas <code>AAAA/MM/DD</code>.
        </p>
      </Section>

      <Section n={7} title="Crea tus reglas">
        <p>
          En <strong>Reglas</strong>, cada regla conecta una etiqueta (y opcionalmente
          remitente/asunto) con una carpeta de Dropbox. Usa <strong>Probar</strong> para
          comprobarla. Si tienes varias, ordénalas por prioridad con ↑/↓.
        </p>
      </Section>

      <Section n={8} title="¡Listo!">
        <p>
          En <strong>Historial</strong>, elige el rango de fechas y pulsa <strong>Procesar ahora</strong>.
          Verás cada correo como <em>procesado</em>, <em>sin regla</em> o <em>error</em>, y los
          documentos aparecerán en tu Dropbox. En etiquetas con mucho volumen, procesa{' '}
          <strong>mes a mes</strong>.
        </p>
      </Section>

      <div className="mt-6 rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
        <p className="mb-2 font-semibold text-gray-800">Bueno saber</p>
        <ul className="list-disc space-y-1 pl-5">
          <li>Solo se guardan <strong>documentos</strong> (PDF, Word, Excel, CSV…). Las imágenes (logos de firma) se ignoran.</li>
          <li>Tus contraseñas se guardan <strong>cifradas</strong>; la app nunca las muestra.</li>
          <li>La app <strong>nunca toca tus correos</strong> en Gmail: solo los lee.</li>
        </ul>
      </div>
    </div>
  );
}
